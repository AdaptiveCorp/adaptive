from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.models.applied_template import AppliedTemplate
from api.models.template import Template, TemplateType

from ..environment.database import get_db

router = APIRouter(
    prefix="/vulnerabilities",
    tags=["vulnerabilities"],
)


@router.get("/")
def list_vulnerabilities(db: Session = Depends(get_db)):
    """
    Lister le catalogue de vulnérabilités disponibles.
    """
    vulns = db.query(Template).filter(Template.type == TemplateType.VULNERABILITY).all()
    return [
        {
            "id": v.id,
            "code": v.code,
            "name": v.name,
            "description": v.description,
            "category": v.category,
        }
        for v in vulns
    ]


@router.get("/projects/{project_id}")
def list_applied_vulnerabilities(project_id: int, db: Session = Depends(get_db)):
    """
    Lister toutes les vulnérabilités appliquées à un projet.
    """
    applied = (
        db.query(AppliedTemplate)
        .join(Template)
        .filter(
            AppliedTemplate.project_id == project_id,
            Template.type == TemplateType.VULNERABILITY,
        )
        .all()
    )

    return [
        {
            "id": at.id,
            "template": {
                "code": at.template.code,
                "name": at.template.name,
            },
            "user_id": at.user_id,
            "domain_id": at.domain_id,
            "server_id": at.server_id,
            "forest_id": at.forest_id,
            "params": at.params,
            "created_at": at.created_at,
        }
        for at in applied
    ]


@router.delete("/{vuln_id}")
def remove_applied_vulnerability(vuln_id: int, db: Session = Depends(get_db)):
    """
    Supprimer une vulnérabilité appliquée.
    """
    applied = db.get(AppliedTemplate, vuln_id)
    if not applied:
        raise HTTPException(status_code=404, detail="Applied vulnerability not found")

    db.delete(applied)
    db.commit()
    return {"message": "Vulnerability removed successfully"}
