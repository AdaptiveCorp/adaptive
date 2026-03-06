import time
import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import orm_models
from ..database.connection import get_db

# from ..services.vulnerability_service import VulnerabilityService
from ..integrations import dc_promote, deploy_lab, restart_vm

# from ..integrations.ansible_generator import generate_playbook_content
# from ..integrations.ansible_runner import run_playbook_from_memory
from .utils import get_dcs_grouped_by_domain, get_domain

router = APIRouter()


@router.post("/project")
def create_project(name: str, db: Session = Depends(get_db)):
    """
    Créer un nouveau projet AD.
    --> Première validation
    """
    project = orm_models.DBProject(name=name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, "name": project.name, "created_at": project.created_at}


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    """
    Lister tous les projets
    --> Première validation
    """
    projects = db.query(orm_models.DBProject).all()
    return [{"id": p.id, "name": p.name, "created_at": p.created_at} for p in projects]


@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Récupérer les détails d'un projet avec tous ses objets
    --> Première validation
    """
    project = (
        db.query(orm_models.DBProject)
        .filter(orm_models.DBProject.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    forests = (
        db.query(orm_models.DBForest)
        .filter(orm_models.DBForest.project_id == project_id)
        .all()
    )
    domains = (
        db.query(orm_models.DBDomain)
        .filter(orm_models.DBDomain.project_id == project_id)
        .all()
    )
    servers = (
        db.query(orm_models.DBServer)
        .filter(orm_models.DBServer.project_id == project_id)
        .all()
    )
    users = (
        db.query(orm_models.DBUser)
        .filter(orm_models.DBUser.project_id == project_id)
        .all()
    )
    vulnerabilities = (
        db.query(orm_models.DBAppliedVulnerability)
        .filter(orm_models.DBAppliedVulnerability.project_id == project_id)
        .all()
    )

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at,
        },
        "forests": [{"id": f.id, "fqdn": f.fqdn} for f in forests],
        "domains": [
            {"id": d.id, "fqdn": d.fqdn, "forest_id": d.forest_id} for d in domains
        ],
        "servers": [
            {"id": s.id, "fqdn": s.fqdn, "is_dc": s.is_dc, "ip": s.ip} for s in servers
        ],
        "users": [{"id": u.id, "username": u.username} for u in users],
        "vulnerabilities_count": len(vulnerabilities),
    }


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Supprimer un projet et tous ses objets associés
    """
    project = (
        db.query(orm_models.DBProject)
        .filter(orm_models.DBProject.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


@router.post("/projects/{project_id}/deploy")
def deploy_project(project_id: int, db: Session = Depends(get_db)):
    """
    Déployer un projet complet (génère et exécute le playbook Ansible)
    """
    project = (
        db.query(orm_models.DBProject)
        .filter(orm_models.DBProject.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # ========================= DC PROMO ========================= #

        result = deploy_lab(project_id, db)  # Cloner les VMs

        time.sleep(60)

        all_dcs = get_dcs_grouped_by_domain(project_id, db)  # list des DCs

        for dcs in all_dcs:
            is_primary = True

            domain = get_domain(dcs[0].domain_id, db)

            for dc in dcs:
                server_ip = dc.ip
                dc_hostname = dc.fqdn
                domain_fqdn = domain.fqdn
                domain_netbios = domain_fqdn.split(".")[1]
                dsrm_password = "Pat@te10000!"
                is_first_dc = is_primary
                domain_admin = "Administrator"

                result = dc_promote(
                    server_ip,  # Promotion du dc
                    dc_hostname,
                    domain_fqdn,
                    domain_netbios,
                    dsrm_password,
                    is_first_dc,
                    domain_admin,
                )

                if result["success"]:
                    result = restart_vm(dc.vm_id)  # Redémarre la VM

                else:
                    return {"project": project.name, "deployment_result": result}

            # ========================= Add Users ========================= #
            # all_primary_dcs =
            # pour chaque dc dans all_primary_dcs
            # recupère les utilisateurs sous forme de liste, avec firstname, lastname
            # apelle fonction dans ansible pour provider tout ça

            # ========================= Ajouter les vulns sur les users Kerberoast-AsRepRoast ========================= #
            # -------------------------------------------------
            # -------------------------------------------------
            # -------------------------------------------------
            # -------------------------------------------------

        return {"project": project.name, "deployment_result": result}
    except Exception as e:
        project.status = "error"
        db.commit()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Deployment error: {str(e)}")
