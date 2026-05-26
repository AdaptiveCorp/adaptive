import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptive.api.infrastructure import AnsibleService
from adaptive.api.infrastructure.base import DeploymentResult
from adaptive.api.models.applied_template import AppliedTemplate, TemplateStatus
from adaptive.api.models.domain import Domain
from adaptive.api.models.group import Group
from adaptive.api.models.project import Project
from adaptive.api.models.template import Template
from adaptive.api.services.applied_template import _create_applied_template, _update_template_status
from adaptive.api.services.utils import _bare_ip

logger: logging.Logger = logging.getLogger(__name__)


def get_groups_grouped_by_domain(project: Project) -> dict[Domain, list[Group]]:
    grouped: dict[Domain, list[Group]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            print(domain)
            print(domain.users)
            if domain.groups:
                grouped[domain] = list(domain.groups)
    return grouped


def get_groups_not_push_by_domain(project: Project, db: Session) -> dict[Domain, list[Group]]:
    groups_by_domain = get_groups_grouped_by_domain(project)
    result: dict[Domain, list[Group]] = {}

    for domain, groups_list in groups_by_domain.items():
        stmt = (
            select(AppliedTemplate)
            .join(Template)
            .where(
                AppliedTemplate.project_id == project.id,
                AppliedTemplate.status.in_(
                    [
                        TemplateStatus.APPLIED,
                        TemplateStatus.REVERTED_PENDING,
                        TemplateStatus.REVERTED_APPLIED,
                    ]
                ),
                AppliedTemplate.domain_id == domain.id,
                Template.code == "add_groups",
            )
        )
        applied_templates = db.execute(stmt).scalars().all()

        groupnames_applied: set[str] = set()
        for applied in applied_templates:
            if not applied.params:
                continue

            params = applied.params
            if isinstance(params, str):
                try:
                    params = json.loads(params)
                except json.JSONDecodeError:
                    continue

            if "groupnames" in params:
                groupnames_applied.update(params["groupnames"])
            elif "groupname" in params:
                groupnames_applied.add(params["groupname"])
            elif "groups" in params:
                groupnames_applied.update(params["groups"])

        result[domain] = [g for g in groups_list if g.name not in groupnames_applied]

    return result


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
