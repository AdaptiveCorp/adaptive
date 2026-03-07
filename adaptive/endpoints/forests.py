from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adaptive.environment.database import get_db
from adaptive.models.forest import Forest
from adaptive.models.project import Project

# from ..services.vulnerability_service import VulnerabilityService
# from ..integrations.ansible_generator import generate_playbook_content
# from ..integrations.ansible_runner import run_playbook_from_memory

router = APIRouter(prefix="/projects/{project_id}/forest", tags=["forests"])


@router.post("/")
def add_forest(project_id: int, fqdn: str, session: Session = Depends(get_db)):
    """
    Ajouter une forêt Active Directory à un projet
    """
    # Vérifier que le projet existe
    project = session.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    forest = Forest(project=project, fqdn=fqdn)
    session.add(forest)
    session.commit()
    session.refresh(forest)
    return {"id": forest.id, "fqdn": forest.fqdn, "project_id": forest.project_id}


@router.get("/")
def list_forests(project_id: int, session: Session = Depends(get_db)):
    """
    Lister les forêts (optionnel: filtrer par projet)
    """
    query = session.query(Forest)
    if project_id:
        query = query.filter(Forest.project_id == project_id)

    forests: List[Forest] = query.all()
    return [
        {"id": forest.id, "fqdn": forest.fqdn, "project_id": forest.project_id}
        for forest in forests
    ]
