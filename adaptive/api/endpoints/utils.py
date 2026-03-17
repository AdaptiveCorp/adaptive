from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from adaptive.api.environment.database import get_db
from adaptive.api.models.domain import Domain
from adaptive.api.models.forest import Forest
from adaptive.api.models.project import Project
from adaptive.api.models.server import Server


def get_root_dc(domain: Domain, db: Session = Depends(get_db)) -> Server:
    stmt = select(Server).where(
        Server.domain_id == domain.id,
        Server.is_dc == True
    )
    server = db.scalars(stmt).first()
    if not server:
        raise HTTPException(status_code=404, detail="Root DC not found")
    return server


def get_project_or_404(project_id: int, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def get_forest_or_404(forest_id: int, db: Session = Depends(get_db)) -> Forest:
    forest = db.get(Forest, forest_id)
    if not forest:
        raise HTTPException(status_code=404, detail="Forest not found")
    return forest


def get_domain_or_404(domain_id: int, db: Session = Depends(get_db)) -> Domain:
    domain = db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain


def get_server_or_404(server_id: int, db: Session = Depends(get_db)) -> Server:
    server = db.get(Server, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server
