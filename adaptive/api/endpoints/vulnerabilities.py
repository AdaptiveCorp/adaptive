import ast
import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptive.api.endpoints.utils import get_root_dc
from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import (
    AppliedVulnerabilityNotFoundError,
    DomainNotFoundError,
    VulnerabilityAlreadyExist,
    VulnerabilityInvalidParamsError,
    VulnerabilityNotFoundError,
)
from adaptive.api.models.applied_template import AppliedTemplate, TemplateStatus
from adaptive.api.models.domain import Domain
from adaptive.api.models.template import Template, TemplateType
from adaptive.api.schemas.common import MessageResponse
from adaptive.api.schemas.vulnerability import (
    AppliedVulnerabilityCreateResponse,
    AppliedVulnerabilityResponse,
    VulnerabilityApply,
    VulnerabilityResponse,
)
from adaptive.api.services.utils import execute_powershell_winrm

router = APIRouter(
    prefix="/vulnerabilities",
    tags=["vulnerabilities"],
)


@router.get("/", response_model=list[VulnerabilityResponse])
def list_vulnerabilities(db: Session = Depends(get_db)):
    """
    Lister le catalogue de vulnérabilités disponibles.
    """
    return db.query(Template).filter(Template.type == TemplateType.VULNERABILITY).all()


@router.get("/projects/{project_id}", response_model=list[AppliedVulnerabilityResponse])
def list_applied_vulnerabilities(project_id: int, db: Session = Depends(get_db)):
    """
    Lister toutes les vulnérabilités appliquées à un projet.
    """
    return db.query(AppliedTemplate).filter(AppliedTemplate.project_id == project_id).all()


@router.post("/projects/{project_id}", response_model=AppliedVulnerabilityCreateResponse)
def post_vulnerability(
    project_id: int,
    payload: VulnerabilityApply,
    db: Session = Depends(get_db),
):
    vuln_template = db.get(Template, payload.vuln_id)
    if not vuln_template:
        raise VulnerabilityNotFoundError(payload.vuln_id)

    domain = db.get(Domain, payload.domain_id)
    if not domain:
        raise DomainNotFoundError(payload.domain_id)

    get_root_dc(domain, db)

    param_vuln = ast.literal_eval(vuln_template.required_params or "[]")
    param_req = payload.params

    if param_vuln and not param_req:
        raise VulnerabilityInvalidParamsError(vuln_template.required_params)

    for key in param_req:
        if key not in param_vuln:
            raise VulnerabilityInvalidParamsError(vuln_template.required_params)

    param_req_str = json.dumps(param_req)

    # Vérifie si ya pas déjà un vuln template qui existe déjà
    stmt = (
        select(AppliedTemplate)
        .join(Template)
        .where(
            AppliedTemplate.project_id == project_id,
            AppliedTemplate.domain_id == domain.id,
            Template.code == vuln_template.code,
            AppliedTemplate.params == param_req_str,  # Améliorer la logique de params
        )
    )
    applied_template = db.execute(stmt).scalars().first()

    if applied_template:
        raise VulnerabilityAlreadyExist(
            applied_vuln_id=applied_template.id,
            applied_vuln_code=applied_template.template.code,
            applied_vuln_params=applied_template.params,
        )

    applied_template = AppliedTemplate(
        project_id=project_id,
        template_id=vuln_template.id,
        domain_id=payload.domain_id,
        params=param_req_str,
        status=TemplateStatus.PENDING,
    )
    db.add(applied_template)
    db.commit()
    db.refresh(domain)

    # result = execute_powershell_winrm(primary_dc.ip, powershell_script, param_req, db)
    return applied_template


@router.post("/{vuln_id}")
def deploy_vulnerability(vuln_id: int, db: Session = Depends(get_db)):
    vuln_template = db.get(AppliedTemplate, vuln_id)
    if not vuln_template:
        raise AppliedVulnerabilityNotFoundError(vuln_id)

    powershell_script = vuln_template.template.content
    param_vuln = ast.literal_eval(vuln_template.params)

    if vuln_template.domain:
        dc = get_root_dc(vuln_template.domain, db)
        ip = dc.ip

    elif vuln_template.server:
        ip = vuln_template.server.ip

    else:
        raise VulnerabilityInvalidParamsError("No domain or server target")

    result = execute_powershell_winrm(ip, powershell_script, param_vuln, db)

    vuln_template.status = TemplateStatus.APPLIED if result.success else TemplateStatus.ERROR
    db.commit()

    return {"etat": result}


@router.delete("/{vuln_id}", response_model=MessageResponse)
def remove_applied_vulnerability(vuln_id: int, db: Session = Depends(get_db)):
    """
    Supprimer une vulnérabilité appliquée.
    """
    applied = db.get(AppliedTemplate, vuln_id)
    if not applied:
        raise AppliedVulnerabilityNotFoundError(vuln_id)

    db.delete(applied)
    db.commit()
    return {"message": "Vulnerability removed successfully"}
