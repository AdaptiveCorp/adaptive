from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    domain_id: int | None = None
    server_id: int | None = None


class GroupResponse(BaseModel):
    name: str
    domain_id: int | None = None
    server_id: int | None = None

    model_config = {"from_attributes": True}
