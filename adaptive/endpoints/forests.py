from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import orm_models
from ..database.connection import get_db

# from ..services.vulnerability_service import VulnerabilityService
# from ..integrations.ansible_generator import generate_playbook_content
# from ..integrations.ansible_runner import run_playbook_from_memory

router = APIRouter()


# ==================== FORÊTS ====================
@router.post("/projects/{project_id}/forest")
def add_forest(project_id: int, fqdn: str, db: Session = Depends(get_db)):
    """
    Ajouter une forêt Active Directory à un projet
    """
    # Vérifier que le projet existe
    project = (
        db.query(orm_models.DBProject)
        .filter(orm_models.DBProject.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    forest = orm_models.DBForest(project_id=project_id, fqdn=fqdn)
    db.add(forest)
    db.commit()
    db.refresh(forest)
    return {"id": forest.id, "fqdn": forest.fqdn, "project_id": forest.project_id}


@router.get("/projects/{project_id}/forest")
def list_forests(project_id: int = None, db: Session = Depends(get_db)):
    """
    Lister les forêts (optionnel: filtrer par projet)
    """
    query = db.query(orm_models.DBForest)
    if project_id:
        query = query.filter(orm_models.DBForest.project_id == project_id)

    forests = query.all()
    return [{"id": f.id, "fqdn": f.fqdn, "project_id": f.project_id} for f in forests]
