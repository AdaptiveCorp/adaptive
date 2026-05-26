import ast
import json
import logging

from sqlalchemy.orm import Session

from adaptive.api.infrastructure import AnsibleService
from adaptive.api.infrastructure.base import DeploymentResult
from adaptive.api.models.applied_template import AppliedTemplate, TemplateStatus
from adaptive.api.models.project import Project
from adaptive.api.services.applied_template import (
    _update_template_status,
    get_template_for_project,
)
from adaptive.api.services.servers import get_all_domain_in_project, get_root_dc
from adaptive.api.services.utils import _bare_ip, execute_powershell_winrm

logger: logging.Logger = logging.getLogger(__name__)


def _step_push_vulnerabilities(
    project: Project,
    db: Session,
    deployment_result: DeploymentResult,
) -> DeploymentResult:

    liste_templates = get_template_for_project(project, db)
    liste_domain = get_all_domain_in_project(project, db)

    vuln_templates = [
        t
        for t in liste_templates
        if t.template.category != "infrastructure"
        and t.status in (TemplateStatus.PENDING, TemplateStatus.MODIFIED)
    ]

    if not vuln_templates:
        logger.info("[STEP 4] No vulnerability templates to apply, skipping.")
        return deployment_result

    logger.info(
        "[STEP 4] Pushing %d vulnerability template(s) across %d domain(s)",
        len(vuln_templates),
        len(liste_domain),
    )

    has_failure = False

    for domain in liste_domain:
        dc = get_root_dc(domain, db)
        if not dc.ip:
            logger.error("[STEP 4] DC '%s' has no IP, skipping domain '%s'", dc.fqdn, domain.fqdn)
            has_failure = True
            continue

        for applied in vuln_templates:
            if not applied.params:
                logger.error(
                    "[STEP 4] Template '%s' has no params, skipping",
                    applied.template.code,
                )
                _update_template_status(db, applied, TemplateStatus.ERROR, error="Missing params")
                has_failure = True
                continue

            logger.info(
                "[STEP 4] Applying template '%s' on DC '%s' (domain '%s')",
                applied.template.code,
                dc.fqdn,
                domain.fqdn,
            )
            param_vuln = ast.literal_eval(applied.params)
            powershell_script = applied.template.content

            result = execute_powershell_winrm(_bare_ip(dc.ip), powershell_script, param_vuln, db)

            if not result.success:
                _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
                logger.error(
                    "[STEP 4] Template '%s' failed on '%s': %s",
                    applied.template.code,
                    dc.fqdn,
                    result.error,
                )
                has_failure = True
                continue

            _update_template_status(db, applied, TemplateStatus.APPLIED)
            logger.info(
                "[STEP 4] Template '%s' applied successfully on '%s'",
                applied.template.code,
                dc.fqdn,
            )

    if has_failure:
        deployment_result.success = False
        deployment_result.error = "One or more vulnerability templates failed to apply"

    return deployment_result


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

            result = execute_powershell_winrm(_bare_ip(dc.ip), powershell_script, param_vuln, db)

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


# Youenn "ZLEB" Belz = Chef DRSD
