from pydantic import BaseModel


class VmTemplateCreate(BaseModel):
    name: str
    vm_id: int
    description: str | None = None


class VmTemplateResponse(BaseModel):
    id: int
    name: str
    vm_id: int
    description: str | None

    model_config = {"from_attributes": True}

class VmTemplateUpdate(BaseModel):
    name: str | None = None
    vm_id: int | None = None
    description: str | None = None
    