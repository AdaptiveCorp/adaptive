import ast
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adaptive.api.endpoints.utils import get_root_dc
from adaptive.api.models.applied_template import AppliedTemplate
from adaptive.api.models.domain import Domain
from adaptive.api.models.template import Template, TemplateType

from ..environment.database import get_db

router = APIRouter(
    prefix="/vulnerabilities",
    tags=["vulnerabilities"],
)


class VulnerabilityRequest(BaseModel):
    params: dict[str, Any] = {}


@router.get("/")
def list_vulnerabilities(db: Session = Depends(get_db)):
    """
    Lister le catalogue de vulnérabilités disponibles.
    """
    vulns = db.query(Template).filter(Template.type == TemplateType.VULNERABILITY).all()
    return [
        {
            "id": v.id,
            "code": v.code,
            "name": v.name,
            "description": v.description,
            "category": v.category,
        }
        for v in vulns
    ]


@router.get("/projects/{project_id}")
def list_applied_vulnerabilities(project_id: int, db: Session = Depends(get_db)):
    """
    Lister toutes les vulnérabilités appliquées à un projet.
    """
    applied = (
        db.query(AppliedTemplate)
        .join(Template)
        .filter(
            AppliedTemplate.project_id == project_id,
            Template.type == TemplateType.VULNERABILITY,
        )
        .all()
    )

    return [
        {
            "id": at.id,
            "template": {
                "code": at.template.code,
                "name": at.template.name,
            },
            "user_id": at.user_id,
            "domain_id": at.domain_id,
            "server_id": at.server_id,
            "forest_id": at.forest_id,
            "params": at.params,
            "created_at": at.created_at,
        }
        for at in applied
    ]


@router.post("/projects/{project_id}")
def post_vulnerability(
    project_id: int,
    domain_id: int,
    vuln_id: int,
    request: VulnerabilityRequest,
    db: Session = Depends(get_db),
):
    vuln_template = db.get(Template, vuln_id)

    domain = db.get(Domain, domain_id)

    primary_dc = get_root_dc(domain, db)

    param_vuln = ast.literal_eval(vuln_template.required_params)
    param_req = request.params

    if len(param_req) <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid parameters, required params are : " + vuln_template.required_params,
        )

    for keys in param_req.keys():
        if keys not in param_vuln:
            raise HTTPException(
                status_code=400,
                detail="Invalid parameters, required params are : " + vuln_template.required_params,
            )

    powershell_script = vuln_template.content

    param_req = request.params
    param_req_str = json.dumps(param_req)

    applied_template = AppliedTemplate(
        project_id=project_id,
        template_id=vuln_template.id,
        domain_id=domain_id,
        params=param_req_str,
    )
    db.add(applied_template)
    db.commit()
    db.refresh(domain)

    # result = execute_powershell_winrm(primary_dc.ip, powershell_script, param_req, db)

    return {
        "id": applied_template.id,
        "template_id": applied_template.template_id,
        "params": applied_template.params,
    }


@router.delete("/{vuln_id}")
def remove_applied_vulnerability(vuln_id: int, db: Session = Depends(get_db)):
    """
    Supprimer une vulnérabilité appliquée.
    """
    applied = db.get(AppliedTemplate, vuln_id)
    if not applied:
        raise HTTPException(status_code=404, detail="Applied vulnerability not found")

    db.delete(applied)
    db.commit()
    return {"message": "Vulnerability removed successfully"}
