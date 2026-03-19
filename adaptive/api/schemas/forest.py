from pydantic import BaseModel


class ForestCreate(BaseModel):
    fqdn: str


class ForestResponse(BaseModel):
    id: int
    fqdn: str
    project_id: int

    model_config = {"from_attributes": True}
