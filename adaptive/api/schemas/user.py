from pydantic import BaseModel


class UserCreate(BaseModel):
    firstname: str
    lastname: str
    password: str
    domain_id: int | None = None
    server_id: int | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    domain_id: int | None
    server_id: int | None

    model_config = {"from_attributes": True}
