from pydantic import BaseModel
from typing import List


class GroupCreate(BaseModel):
    name: str
    description: str | None = None
    user_ids: List[int] = []
    member_group_ids: List[int] = []
    domain_id: int | None = None
    server_id: int | None = None

class GroupResponse(BaseModel) :
    id: int
    name: str
    description: str | None = None
    user_ids: List[int]
    member_group_ids: List[int]
    domain_id: int | None = None
    server_id: int | None = None

    model_config = {"from_attributes": True}