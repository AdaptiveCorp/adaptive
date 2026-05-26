import json
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptive.api.models.applied_template import AppliedTemplate, TemplateStatus
from adaptive.api.models.project import Project
from adaptive.api.models.template import Template

logger: logging.Logger = logging.getLogger(__name__)


def _create_applied_template(
    db: Session,
    *,
    project_id: int,
    template_code: str,
    domain_id: int | None = None,
    server_id: int | None = None,
    forest_id: int | None = None,
    user_id: int | None = None,
    group_id: int | None = None,
    params: dict | None = None,
) -> AppliedTemplate:
    template = db.query(Template).filter(Template.code == template_code).first()
    if not template:
        raise ValueError(f"Template '{template_code}' not found in database")

    applied = AppliedTemplate(
        project_id=project_id,
        template_id=template.id,
        domain_id=domain_id,
        server_id=server_id,
        forest_id=forest_id,
        user_id=user_id,
        group_id=group_id,
        params=json.dumps(params) if params else None,
        status=TemplateStatus.PENDING,
    )

    db.add(applied)
    db.commit()
    db.refresh(applied)
    logger.info(
        "[TRACKING] Created AppliedTemplate id=%d (template=%s, status=pending)",
        applied.id,
        template_code,
    )
    return applied


def _update_template_status(
    db: Session,
    applied: AppliedTemplate,
    status: TemplateStatus,
    error: str | None = None,
) -> None:
    applied.status = status
    db.commit()
    logger.info(
        "[TRACKING] AppliedTemplate id=%d -> status=%s%s",
        applied.id,
        status.value,
        f" (error: {error})" if error else "",
    )


def get_pending_reverted_template(project: Project, db: Session) -> list[AppliedTemplate]:
    applied_template_reverted = (
        db.query(AppliedTemplate)
        .filter(AppliedTemplate.status == TemplateStatus.REVERTED_PENDING)
        .all()
    )

    return applied_template_reverted


def get_template_for_project(project: Project, db: Session) -> list[AppliedTemplate]:
    stmt = select(AppliedTemplate).where(AppliedTemplate.project_id == project.id)
    return list(db.scalars(stmt).all())
