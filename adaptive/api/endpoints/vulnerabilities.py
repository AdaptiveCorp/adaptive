import ast
import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adaptive.api.endpoints.utils import get_root_dc
from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import (
    AppliedVulnerabilityNotFoundError,
    DomainNotFoundError,
    VulnerabilityInvalidParamsError,
    VulnerabilityNotFoundError,
)
from adaptive.api.models.applied_template import AppliedTemplate
from adaptive.api.models.template import Template, TemplateType
from adaptive.api.schemas.common import MessageResponse
from adaptive.api.schemas.vulnerability import (
    AppliedVulnerabilityCreateResponse,
    AppliedVulnerabilityResponse,
    VulnerabilityApply,
    VulnerabilityResponse,
)

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
    return (
        db.query(AppliedTemplate)
        .join(Template)
        .filter(
            AppliedTemplate.project_id == project_id,
            Template.type == TemplateType.VULNERABILITY,
        )
        .all()
    )


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

    param_vuln = ast.literal_eval(vuln_template.required_params)
    param_req = payload.params

    if len(param_req) <= 0:
        raise VulnerabilityInvalidParamsError(vuln_template.required_params)

    for keys in param_req:
        if keys not in param_vuln:
            raise VulnerabilityInvalidParamsError(vuln_template.required_params)

    param_req_str = json.dumps(param_req)

    applied_template = AppliedTemplate(
        project_id=project_id,
        template_id=vuln_template.id,
        domain_id=payload.domain_id,
        params=param_req_str,
    )
    db.add(applied_template)
    db.commit()
    db.refresh(domain)

    # result = execute_powershell_winrm(primary_dc.ip, powershell_script, param_req, db)

    return applied_template


@router.post("/{vuln_id}")
def deploy_vulnerability(vuln_id: int, db: Session = Depends(get_db)):

    vuln_template = db.get(AppliedTemplate, vuln_id)

    powershell_script = vuln_template.template.content
    param_vuln = ast.literal_eval(vuln_template.params)

    if vuln_template.domain:
        dc = get_root_dc(vuln_template.domain, db)
        ip = dc.ip

    elif vuln_template.server:
        ip = vuln_template.server.ip

    result = execute_powershell_winrm(ip, powershell_script, param_vuln, db)

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
