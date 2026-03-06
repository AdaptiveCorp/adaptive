from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import orm_models
from ..database.connection import get_db

# from ..services.vulnerability_service import VulnerabilityService
from ..database.seed_vulnerabilities import seed_vulnerability_templates

# from ..integrations.ansible_generator import generate_playbook_content
# from ..integrations.ansible_runner import run_playbook_from_memory

router = APIRouter()


@router.get("/projects/{project_id}/vulnerabilities/")
def list_applied_vulnerabilities(project_id: int, db: Session = Depends(get_db)):
    """
    Lister toutes les vulnérabilités appliquées à un projet
    """
    applied_vulns = (
        db.query(orm_models.DBAppliedVulnerability)
        .filter(orm_models.DBAppliedVulnerability.project_id == project_id)
        .all()
    )

    result = []
    for av in applied_vulns:
        template = (
            db.query(orm_models.DBVulnerabilityTemplate)
            .filter(orm_models.DBVulnerabilityTemplate.id == av.template_id)
            .first()
        )

        result.append(
            {
                "id": av.id,
                "code": template.code if template else "unknown",
                "name": template.name if template else "Unknown",
                "target_user_id": av.target_user_id,
                "source_user_id": av.source_user_id,
                "params": av.params,
                "created_at": av.created_at,
            }
        )

    return result


@router.delete("/projects/{project_id}/vulnerabilities/{vuln_id}")
def remove_applied_vulnerability(vuln_id: int, db: Session = Depends(get_db)):
    """
    Supprimer une vulnérabilité appliquée
    """
    vuln = (
        db.query(orm_models.DBAppliedVulnerability)
        .filter(orm_models.DBAppliedVulnerability.id == vuln_id)
        .first()
    )

    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")

    db.delete(vuln)
    db.commit()
    return {"message": "Vulnerability removed successfully"}


@router.post("/admin/reload_vulnerabilities")
def reload_vulnerabilities():
    """
    Recharger les vulnérabilités depuis le fichier YAML
    (à appeler après modification du fichier vulnerabilities.yaml)
    """
    try:
        seed_vulnerability_templates()
        return {"message": "Vulnerabilities reloaded successfully from YAML"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reloading vulnerabilities: {str(e)}"
        )
