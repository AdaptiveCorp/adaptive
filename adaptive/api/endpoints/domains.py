from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import ForestNotFoundError
from adaptive.api.models.domain import Domain
from adaptive.api.models.forest import Forest
from adaptive.api.schemas.domain import DomainCreate, DomainResponse

router = APIRouter(prefix="/forests/{forest_id}/domains", tags=["domains"])


@router.post("/", response_model=DomainResponse)
def create_domain(forest_id: int, payload: DomainCreate, db: Session = Depends(get_db)):
    forest = db.get(Forest, forest_id)
    if not forest:
        raise ForestNotFoundError(forest_id)

    domain = Domain(fqdn=payload.fqdn, forest_id=forest_id)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain


@router.get("/", response_model=list[DomainResponse])
def list_domains(forest_id: int, db: Session = Depends(get_db)):
    forest = db.get(Forest, forest_id)
    if not forest:
        raise ForestNotFoundError(forest_id)

    return db.query(Domain).filter(Domain.forest_id == forest_id).all()
