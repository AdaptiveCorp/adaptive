from pydantic import BaseModel


class ServerCreate(BaseModel):
    fqdn: str
    is_dc: bool = False
    ip: str | None = None
    gtw: str | None = None
    dns: str | None = None
    vm_template_id: int | None = None


class ServerResponse(BaseModel):
    id: int
    fqdn: str
    is_dc: bool
    ip: str | None
    vm_id: int | None = None
    domain_id: int
    vm_template_id: int | None
    vm_template_name: str | None

    model_config = {"from_attributes": True}
