from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class _ForestSummary(BaseModel):
    id: int
    fqdn: str

    model_config = {"from_attributes": True}


class _DomainSummary(BaseModel):
    id: int
    fqdn: str
    forest_id: int

    model_config = {"from_attributes": True}


class _ServerSummary(BaseModel):
    id: int
    fqdn: str
    is_dc: bool
    ip: str | None

    model_config = {"from_attributes": True}


class _UserSummary(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class ProjectDetail(BaseModel):
    project: ProjectResponse
    forests: list[_ForestSummary]
    domains: list[_DomainSummary]
    servers: list[_ServerSummary]
    users: list[_UserSummary]
    vulnerabilities_count: int
