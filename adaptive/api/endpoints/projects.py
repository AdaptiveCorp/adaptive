import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.models.applied_template import AppliedTemplate
from adaptive.api.models.project import Project
from adaptive.api.services.deployment_service import deploy_project as run_deployment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/")
def create_project(name: str, db: Session = Depends(get_db)):
    project = Project(name=name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, "name": project.name, "created_at": project.created_at}


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [{"id": p.id, "name": p.name, "created_at": p.created_at} for p in projects]


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    forests = project.forests
    domains = [d for f in forests for d in f.domains]
    servers = [s for d in domains for s in d.servers]
    users = [u for d in domains for u in d.users]
    applied_vulns = db.query(AppliedTemplate).filter(AppliedTemplate.project_id == project_id).all()

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at,
        },
        "forests": [{"id": f.id, "fqdn": f.fqdn} for f in forests],
        "domains": [{"id": d.id, "fqdn": d.fqdn, "forest_id": d.forest_id} for d in domains],
        "servers": [{"id": s.id, "fqdn": s.fqdn, "is_dc": s.is_dc, "ip": s.ip} for s in servers],
        "users": [{"id": u.id, "username": u.username} for u in users],
        "vulnerabilities_count": len(applied_vulns),
    }


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/deploy")
def deploy_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        return run_deployment(project, db)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        db.rollback()
        logger.exception("Deployment failed for project %d", project_id)
        raise HTTPException(status_code=500, detail=f"Deployment error: {e}") from e
