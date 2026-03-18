from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.models.vm_template import VmTemplate

router = APIRouter(prefix="/vm-templates", tags=["vm-templates"])


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


@router.post("/", response_model=VmTemplateResponse)
def create_vm_template(payload: VmTemplateCreate, db: Session = Depends(get_db)):
    existing = db.query(VmTemplate).filter(VmTemplate.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"VmTemplate with name '{payload.name}' already exists")

    vm_template = VmTemplate(
        name=payload.name,
        vm_id=payload.vm_id,
        description=payload.description,
    )
    db.add(vm_template)
    db.commit()
    db.refresh(vm_template)
    return vm_template


@router.get("/", response_model=list[VmTemplateResponse])
def list_vm_templates(db: Session = Depends(get_db)):
    return db.query(VmTemplate).all()


@router.get("/{vm_template_id}", response_model=VmTemplateResponse)
def get_vm_template(vm_template_id: int, db: Session = Depends(get_db)):
    vm_template = db.get(VmTemplate, vm_template_id)
    if not vm_template:
        raise HTTPException(status_code=404, detail="VmTemplate not found")
    return vm_template


@router.delete("/{vm_template_id}", status_code=204)
def delete_vm_template(vm_template_id: int, db: Session = Depends(get_db)):
    vm_template = db.get(VmTemplate, vm_template_id)
    if not vm_template:
        raise HTTPException(status_code=404, detail="VmTemplate not found")
    if vm_template.servers:
        raise HTTPException(
            status_code=409,
            detail=f"VmTemplate id={vm_template_id} is still used by {len(vm_template.servers)} server(s)",
        )
    db.delete(vm_template)
    db.commit()
