import json
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptive.api.infrastructure import AnsibleService
from adaptive.api.infrastructure.base import DeploymentResult
from adaptive.api.models.applied_template import AppliedTemplate, TemplateStatus
from adaptive.api.models.domain import Domain
from adaptive.api.models.project import Project
from adaptive.api.models.template import Template
from adaptive.api.models.user import User
from adaptive.api.services.applied_template import _create_applied_template, _update_template_status
from adaptive.api.services.utils import _bare_ip

logger: logging.Logger = logging.getLogger(__name__)


def get_users_grouped_by_domain(project: Project) -> dict[Domain, list[User]]:
    grouped: dict[Domain, list[User]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            if domain.users:
                grouped[domain] = list(domain.users)
    return grouped


def get_users_not_push_by_domain(project: Project, db: Session) -> dict[Domain, list[User]]:
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

        applied_list = [
            _create_applied_template(
                db,
                project_id=project.id,
                template_code="add_users",
                domain_id=domain.id,
                server_id=dc.id,
                user_id=u.id,
                params={
                    "target_host": _bare_ip(dc.ip),
                    "users_list": [u.username],
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
