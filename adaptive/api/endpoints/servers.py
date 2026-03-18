from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.models.domain import Domain
from adaptive.api.models.server import Server
from adaptive.api.models.vm_template import VmTemplate

router = APIRouter(prefix="/domains/{domain_id}/servers", tags=["servers"])


@router.post("/")
def create_server(
    domain_id: int,
    fqdn: str,
    is_dc: bool = False,
    ip: str | None = None,
    gtw: str | None = None,
    dns: str | None = None,
    vm_template_id: int | None = None,
    db: Session = Depends(get_db),
):
    domain = db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    if vm_template_id is not None:
        vm_template = db.get(VmTemplate, vm_template_id)
        if not vm_template:
            raise HTTPException(status_code=404, detail=f"VmTemplate id={vm_template_id} not found")

    server = Server(
        fqdn=fqdn,
        is_dc=is_dc,
        ip=ip,
        gtw=gtw,
        dns=dns,
        domain_id=domain_id,
        vm_template_id=vm_template_id,
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return {
        "id": server.id,
        "fqdn": server.fqdn,
        "is_dc": server.is_dc,
        "ip": server.ip,
        "domain_id": server.domain_id,
        "vm_template_id": server.vm_template_id,
        "vm_template_name": server.vm_template.name if server.vm_template else None,
    }


@router.get("/")
def list_servers(domain_id: int, db: Session = Depends(get_db)):
    domain = db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    servers = db.query(Server).filter(Server.domain_id == domain_id).all()
    return [
        {
            "id": s.id,
            "fqdn": s.fqdn,
            "is_dc": s.is_dc,
            "ip": s.ip,
            "vm_id": s.vm_id,
            "domain_id": s.domain_id,
            "vm_template_id": s.vm_template_id,
            "vm_template_name": s.vm_template.name if s.vm_template else None,
        }
        for s in servers
    ]
