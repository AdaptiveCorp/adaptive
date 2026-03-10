from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.models.domain import Domain
from adaptive.api.models.forest import Forest

router = APIRouter(prefix="/forests/{forest_id}/domains", tags=["domains"])


@router.post("/")
def create_domain(forest_id: int, fqdn: str, db: Session = Depends(get_db)):
    forest = db.get(Forest, forest_id)
    if not forest:
        raise HTTPException(status_code=404, detail="Forest not found")

    domain = Domain(fqdn=fqdn, forest_id=forest_id)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return {"id": domain.id, "fqdn": domain.fqdn, "forest_id": domain.forest_id}


@router.get("/")
def list_domains(forest_id: int, db: Session = Depends(get_db)):
    forest = db.get(Forest, forest_id)
    if not forest:
        raise HTTPException(status_code=404, detail="Forest not found")

    domains = db.query(Domain).filter(Domain.forest_id == forest_id).all()
    return [
        {"id": d.id, "fqdn": d.fqdn, "forest_id": d.forest_id}
        for d in domains
    ]
