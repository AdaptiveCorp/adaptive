from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import DomainNotFoundError, VmTemplateNotFoundError
from adaptive.api.models.domain import Domain
from adaptive.api.models.server import Server, ServerStatus
from adaptive.api.models.vm_template import VmTemplate
from adaptive.api.schemas.server import ServerCreate, ServerResponse

router = APIRouter(prefix="/domains/{domain_id}/servers", tags=["servers"])


@router.post("/", response_model=ServerResponse)
def create_server(
    domain_id: int,
    payload: ServerCreate,
    db: Session = Depends(get_db),
):
    domain = db.get(Domain, domain_id)
    if not domain:
        raise DomainNotFoundError(domain_id)

    if payload.vm_template_id is not None:
        vm_template = db.get(VmTemplate, payload.vm_template_id)
        if not vm_template:
            raise VmTemplateNotFoundError(payload.vm_template_id)

    server = Server(
        fqdn=payload.fqdn,
        is_dc=payload.is_dc,
        ip=payload.ip,
        gtw=payload.gtw,
        dns=payload.dns,
        domain_id=domain_id,
        vm_template_id=payload.vm_template_id,
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return server


@router.get("/", response_model=list[ServerResponse])
def list_servers(domain_id: int, db: Session = Depends(get_db)):
    domain = db.get(Domain, domain_id)
    if not domain:
        raise DomainNotFoundError(domain_id)

    return db.query(Server).filter(Server.domain_id == domain_id).all()
