from pydantic import BaseModel
from typing import List


class GroupMembershipUpdate(BaseModel):
    user_ids: list[int] = []
    member_group_ids: list[int] = []

class GroupCreate(BaseModel):
    name: str
    description: str | None = None
    user_ids: List[int] = []
    domain_id: int | None = None
    server_id: int | None = None

class GroupResponse(BaseModel) :
    id: int
    name: str
    description: str | None = None
    user_ids: List[int]
    domain_id: int | None = None
    server_id: int | None = None

    model_config = {"from_attributes": True}