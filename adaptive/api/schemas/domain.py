from pydantic import BaseModel


class DomainCreate(BaseModel):
    fqdn: str


class DomainResponse(BaseModel):
    id: int
    fqdn: str
    forest_id: int

    model_config = {"from_attributes": True}
