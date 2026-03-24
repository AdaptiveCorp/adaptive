import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import ProjectNotFoundError
from adaptive.api.models.applied_template import AppliedTemplate
from adaptive.api.models.project import Project
from adaptive.api.schemas.common import MessageResponse
from adaptive.api.schemas.project import (
    DeployResponse,
    ProjectCreate,
    ProjectDetail,
    ProjectResponse,
)
from adaptive.api.services.deployment_service import deploy_project as run_deployment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=payload.name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    forests = project.forests
    domains = [d for f in forests for d in f.domains]
    servers = [s for d in domains for s in d.servers]
    users = [u for d in domains for u in d.users]
    applied_vulns = db.query(AppliedTemplate).filter(AppliedTemplate.project_id == project_id).all()

    return {
        "project": project,
        "forests": forests,
        "domains": domains,
        "servers": servers,
        "users": users,
        "vulnerabilities_count": len(applied_vulns),
    }


@router.delete("/{project_id}", response_model=MessageResponse)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/deploy", response_model=DeployResponse)
def deploy_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    try:
        return run_deployment(project, db)
    except Exception:
        db.rollback()
        raise
