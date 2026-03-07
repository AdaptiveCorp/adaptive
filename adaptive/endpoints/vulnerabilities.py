from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adaptive.models.applied_vulnerability import AppliedVulnerability
from adaptive.models.vulnerability import Vulnerability

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
    vulns = db.query(Vulnerability).all()
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
    applied_vulns = (
        db.query(AppliedVulnerability)
        .filter(AppliedVulnerability.project_id == project_id)
        .all()
    )

    return [
        {
            "id": av.id,
            "vulnerability": {
                "code": av.vulnerability.code,
                "name": av.vulnerability.name,
            },
            "source_user_id": av.source_user_id,
            "user_id": av.user_id,
            "domain_id": av.domain_id,
            "server_id": av.server_id,
            "forest_id": av.forest_id,
            "params": av.params,
            "created_at": av.created_at,
        }
        for av in applied_vulns
    ]


@router.delete("/{vuln_id}")
def remove_applied_vulnerability(vuln_id: int, db: Session = Depends(get_db)):
    """
    Supprimer une vulnérabilité appliquée.
    """
    vuln = db.get(AppliedVulnerability, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")

    db.delete(vuln)
    db.commit()
    return {"message": "Vulnerability removed successfully"}
