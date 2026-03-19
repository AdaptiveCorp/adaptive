from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import (
    DomainNoDCError,
    DomainNotFoundError,
    ForestNotFoundError,
    ProjectNotFoundError,
    ServerNotFoundError,
)
from adaptive.api.models.domain import Domain
from adaptive.api.models.forest import Forest
from adaptive.api.models.project import Project
from adaptive.api.models.server import Server


def get_root_dc(domain: Domain, db: Session = Depends(get_db)) -> Server:
    stmt = select(Server).where(Server.domain_id == domain.id, Server.is_dc.is_(True))
    server = db.scalars(stmt).first()
    if not server:
        raise DomainNoDCError(domain.id)
    return server


def get_project_or_404(project_id: int, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)
    return project


def get_forest_or_404(forest_id: int, db: Session = Depends(get_db)) -> Forest:
    forest = db.get(Forest, forest_id)
    if not forest:
        raise ForestNotFoundError(forest_id)
    return forest


def get_domain_or_404(domain_id: int, db: Session = Depends(get_db)) -> Domain:
    domain = db.get(Domain, domain_id)
    if not domain:
        raise DomainNotFoundError(domain_id)
    return domain


def get_server_or_404(server_id: int, db: Session = Depends(get_db)) -> Server:
    server = db.get(Server, server_id)
    if not server:
        raise ServerNotFoundError(server_id)
    return server
