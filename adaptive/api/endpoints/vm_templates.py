from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import (
    VmTemplateInUseError,
    VmTemplateNameConflictError,
    VmTemplateNotFoundError,
)
from adaptive.api.models.vm_template import VmTemplate
from adaptive.api.schemas.vm_template import VmTemplateCreate, VmTemplateResponse, VmTemplateUpdate

router = APIRouter(prefix="/vm-templates", tags=["vm-templates"])


@router.post("/", response_model=VmTemplateResponse)
def create_vm_template(payload: VmTemplateCreate, db: Session = Depends(get_db)):
    existing = db.query(VmTemplate).filter(VmTemplate.name == payload.name).first()
    if existing:
        raise VmTemplateNameConflictError(payload.name)

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
        raise VmTemplateNotFoundError(vm_template_id)
    return vm_template


@router.delete("/{vm_template_id}", status_code=204)
def delete_vm_template(vm_template_id: int, db: Session = Depends(get_db)):
    vm_template = db.get(VmTemplate, vm_template_id)
    if not vm_template:
        raise VmTemplateNotFoundError(vm_template_id)
    if vm_template.servers:
        raise VmTemplateInUseError(vm_template_id, len(vm_template.servers))
    db.delete(vm_template)
    db.commit()

@router.patch("/{vm_template_id}", response_model=VmTemplateResponse)
def update_vm_template(vm_template_id: int, payload: VmTemplateUpdate, db: Session = Depends(get_db)):
    vm_template = db.get(VmTemplate, vm_template_id)
    if not vm_template:
        raise VmTemplateNotFoundError(vm_template_id)

    if payload.name is not None:
        existing = db.query(VmTemplate).filter(
            VmTemplate.name == payload.name,
            VmTemplate.id != vm_template_id
        ).first()
        if existing:
            raise VmTemplateNameConflictError(payload.name)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vm_template, field, value)

    db.commit()
    db.refresh(vm_template)
    return vm_template