logger: logging.Logger = logging.getLogger(__name__)


def get_pending_reverted_template(project: Project, db: Session):
    applied_template_reverted = (
        db.query(AppliedTemplate)
        .filter(AppliedTemplate.status == TemplateStatus.REVERTED_PENDING)
        .all()
    )

    return applied_template_reverted


def _step_reverse_templates(
    project: Project,
    ansible: AnsibleService,
    db: Session,
    pending_reversed_templates: list[AppliedTemplate],
    deployment_result: DeploymentResult,
) -> DeploymentResult:

    if not pending_reversed_templates:
        logger.info("[STEP REVERSE] No templates to reverse, skipping.")
        return deployment_result

    logger.info("[STEP REVERSE] Reversing %d template(s)", len(pending_reversed_templates))

    liste_domain = get_all_domain_in_project(project, db)
    has_failure = False

    for domain in liste_domain:
        dc = get_root_dc(domain, db)
        if not dc.ip:
            logger.error(
                "[STEP REVERSE] DC '%s' has no IP, skipping domain '%s'", dc.fqdn, domain.fqdn
            )
            has_failure = True
            continue

        for applied in pending_reversed_templates:
            # Pas de reverse_content défini
            if not applied.template.reverse_content:
                logger.error(
                    "[STEP REVERSE] Template '%s' has no reverse_content, skipping.",
                    applied.template.code,
                )
                _update_template_status(
                    db, applied, TemplateStatus.ERROR, error="Missing reverse_content"
                )
                has_failure = True
                continue

            # Pas de params sauvegardés
            if not applied.params:
                logger.error(
                    "[STEP REVERSE] Template '%s' has no params, skipping.",
                    applied.template.code,
                )
                _update_template_status(db, applied, TemplateStatus.ERROR, error="Missing params")
                has_failure = True
                continue

            param_vuln = json.loads(applied.params)
            powershell_script = applied.template.reverse_content

            logger.info(
                "[STEP REVERSE] Reversing template '%s' on DC '%s' (domain '%s')",
                applied.template.code,
                dc.fqdn,
                domain.fqdn,
            )

            result = execute_powershell_winrm(dc.ip, powershell_script, param_vuln, db)

            if not result.success:
                # _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
                logger.error(
                    "[STEP REVERSE] Template '%s' failed on '%s': %s",
                    applied.template.code,
                    dc.fqdn,
                    result.error,
                )
                has_failure = True
                continue

            if applied.template.reverse_type == "deletion":
                user = applied.user
                if user:
                    db.delete(user)
                    db.commit()
                group = applied.group
                if group:
                    db.delete(group)
                    db.commit()

            _update_template_status(db, applied, TemplateStatus.REVERTED_APPLIED)
            logger.info(
                "[STEP REVERSE] Template '%s' reversed successfully on '%s'",
                applied.template.code,
                dc.fqdn,
            )

    if has_failure:
        deployment_result.success = False
        deployment_result.error = "One or more templates failed to reverse"

    return deployment_result


def get_template_for_project(project: Project, db: Session) -> list[AppliedTemplate]:
    stmt = select(AppliedTemplate).where(AppliedTemplate.project_id == project.id)
    return list(db.scalars(stmt).all())
