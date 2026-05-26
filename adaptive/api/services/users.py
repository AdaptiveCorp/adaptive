import logging

logger: logging.Logger = logging.getLogger(__name__)


def get_users_not_push_by_domain(project: Project, db: Session) -> dict[Domain, list[User]]:

    # Récupère tout les templates de type user push
    users = get_users_grouped_by_domain(project)

    for domain, users_list in users.items():
        stmt = (
            select(AppliedTemplate)
            .join(Template)
            .where(
                AppliedTemplate.project_id == project.id,
                (AppliedTemplate.status == TemplateStatus.APPLIED)
                | (AppliedTemplate.status == TemplateStatus.ERROR)
                | (AppliedTemplate.status == TemplateStatus.REVERTED_APPLIED)
                | (AppliedTemplate.status == TemplateStatus.REVERTED_PENDING),
                AppliedTemplate.domain_id == domain.id,
                Template.code == "add_users",
            )
        )

        liste_applied_template = db.execute(stmt).scalars().all()
        username_applied = []

        for applied_template in liste_applied_template:
            params = applied_template.params
            params_json = json.loads(params)
            users_in_applied_template = params_json["users_list"]
            username_applied.extend(users_in_applied_template)

        usernames_not_applied = [
            user for user in users_list if user.username not in username_applied
        ]
        users[domain] = usernames_not_applied

    return users


def _step_add_users(
    project: Project,
    ansible: AnsibleService,
    db: Session,
    users_by_domain: dict[Domain, list[User]] | None,
    deployment_result: DeploymentResult,
) -> DeploymentResult:

    if not users_by_domain:
        logger.info("[STEP 3] No users to create, skipping.")
        return deployment_result

    logger.info("[STEP 3] Starting user creation across %d domain(s)", len(users_by_domain))

    for domain, users in users_by_domain.items():
        dc = next((s for s in domain.servers if s.is_dc and s.ip), None)
        if not dc or not dc.ip:
            logger.error("[STEP 3] No reachable DC for domain '%s', skipping", domain.fqdn)
            continue

        fqdn = dc.fqdn
        base_dn = f"DC={fqdn.split('.')[-2].lower()},DC={fqdn.split('.')[-1].lower()}"

        user_dicts: list[dict[str, str]] = [
            {
                "username": u.username,
                "firstname": u.firstname,
                "lastname": u.lastname,
                "password": u.password,
            }
            for u in users
        ]

        # 1 AppliedTemplate par user, chacun référence son user_id
        applied_list = [
            _create_applied_template(
                db,
                project_id=project.id,
                template_code="add_users",
                domain_id=domain.id,
                server_id=dc.id,
                user_id=u.id,  # ← référence directe à l'user
                params={
                    "target_host": _bare_ip(dc.ip),
                    "users_list": [u.username],  # ← liste à 1 élément
                    "base_dn": base_dn,
                    "domain_fqdn": domain.fqdn,
                },
            )
            for u in users
        ]

        logger.info(
            "[STEP 3] Adding %d user(s) to domain '%s' via DC '%s'",
            len(users),
            domain.fqdn,
            dc.fqdn,
        )

        # L'appel Ansible reste groupé pour l'efficacité
        result = ansible.add_users(
            server_ip=_bare_ip(dc.ip),
            users=user_dicts,
            base_dn=base_dn,
            domain_fqdn=domain.fqdn,
        )

        if not result.success:
            for applied in applied_list:
                _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
            logger.error("[STEP 3] User creation failed on '%s': %s", domain.fqdn, result.error)
            deployment_result.success = False
            deployment_result.error = result.error
            return deployment_result

        for applied in applied_list:
            _update_template_status(db, applied, TemplateStatus.APPLIED)
        logger.info("[STEP 3] Users successfully created on domain '%s'", domain.fqdn)

    return deployment_result


def _step_add_groups(
    project: Project,
    ansible: AnsibleService,
    db: Session,
    groups_by_domain: dict[Domain, list[Group]] | None,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    if not groups_by_domain:
        logger.info("[STEP ADD_GROUPS] No groups to create, skipping.")
        return deployment_result

    for domain, groups in groups_by_domain.items():
        if not groups:
            continue

        dc = next((s for s in domain.servers if s.is_dc and s.ip), None)
        if not dc or not dc.ip:
            logger.error("[STEP ADD_GROUPS] No reachable DC for '%s', skipping", domain.fqdn)
            continue

        fqdn = dc.fqdn
        base_dn = f"DC={fqdn.split('.')[-2].lower()},DC={fqdn.split('.')[-1].lower()}"

        group_dicts: list[dict[str, Any]] = [
            {"name": g.name, "description": g.description or ""} for g in groups
        ]

        # APRÈS (clé "groupnames" — lue correctement par le filtre)
        applied_list = [
            _create_applied_template(
                db,
                project_id=project.id,
                template_code="add_groups",
                domain_id=domain.id,
                server_id=dc.id,
                group_id=g.id,
                params={
                    "target_host": _bare_ip(dc.ip),
                    "groupnames": [g.name],
                    "basedn": base_dn,
                    "domain_fqdn": domain.fqdn,
                },
            )
            for g in groups
        ]

        logger.info(
            "[STEP ADD_GROUPS] Adding %d group(s) to domain '%s' via DC '%s'",
            len(groups),
            domain.fqdn,
            dc.fqdn,
        )

        # L'appel Ansible reste groupé pour l'efficacité
        result = ansible.add_groups(
            server_ip=_bare_ip(dc.ip),
            groups=group_dicts,
            base_dn=base_dn,
            domain_fqdn=domain.fqdn,
        )

        if not result.success:
            for applied in applied_list:
                _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
            logger.error(
                "[STEP ADD_GROUPS] Group creation failed on '%s': %s", domain.fqdn, result.error
            )
            deployment_result.success = False
            deployment_result.error = result.error
            return deployment_result

        for applied in applied_list:
            _update_template_status(db, applied, TemplateStatus.APPLIED)
        logger.info("[STEP ADD_GROUPS] Groups created on domain '%s'", domain.fqdn)

    return deployment_result


def _step_add_group_members(
    project: Project,
    ansible: AnsibleService,
    db: Session,
    groups_by_domain: dict[Domain, list[Group]] | None,
    deployment_result: DeploymentResult,
) -> DeploymentResult:

    if not groups_by_domain:
        logger.info("[STEP ADD_GROUP_MEMBERS] No memberships to set, skipping.")
        return deployment_result

    for domain, groups in groups_by_domain.items():
        groups_with_members = [g for g in groups if g.users]

        if not groups_with_members:
            logger.info(
                "[STEP ADD_GROUP_MEMBERS] No group with members in domain '%s', skipping",
                domain.fqdn,
            )
            continue

        dc = next((s for s in domain.servers if s.is_dc and s.ip), None)
        if not dc or not dc.ip:
            logger.error("[STEP ADD_GROUP_MEMBERS] No reachable DC for '%s', skipping", domain.fqdn)
            continue

        for g in groups_with_members:
            user_members = [(u.username, u.id) for u in g.users]

            for member_name, user_id in user_members:
                applied = _create_applied_template(
                    db,
                    project_id=project.id,
                    template_code="add_group_members",
                    domain_id=domain.id,
                    server_id=dc.id,
                    group_id=g.id,
                    user_id=user_id,
                    params={
                        "target_host": _bare_ip(dc.ip),
                        "group_name": g.name,
                        "members": [member_name],
                    },
                )

                logger.info(
                    "[STEP ADD_GROUP_MEMBERS] Adding member '%s' to group '%s' on domain '%s'",
                    member_name,
                    g.name,
                    domain.fqdn,
                )

                result = ansible.add_group_members(
                    server_ip=_bare_ip(dc.ip),
                    memberships=[{"group_name": g.name, "members": [member_name]}],
                )

                if not result.success:
                    _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
                    deployment_result.success = False
                    deployment_result.error = result.error
                    return deployment_result

                _update_template_status(db, applied, TemplateStatus.APPLIED)
                logger.info(
                    "[STEP ADD_GROUP_MEMBERS] Member '%s' added to group '%s' on domain '%s'",
                    member_name,
                    g.name,
                    domain.fqdn,
                )
    return deployment_result
