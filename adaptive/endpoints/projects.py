import time
import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adaptive.models.applied_vulnerability import AppliedVulnerability
from adaptive.models.project import Project
from adaptive.models.server import Server

from ..environment.database import get_db
from ..infrastructure.ansible.ansible_provider import dc_promote
from ..infrastructure.proxmox.proxmox import ServerInfo, deploy_lab, restart_vm
from .utils import get_dcs_grouped_by_domain, get_domain

router = APIRouter(prefix="/projects")


@router.post("/")
def create_project(name: str, db: Session = Depends(get_db)):
    """
    Créer un nouveau projet AD.
    --> Première validation
    """
    project = Project(name=name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, "name": project.name, "created_at": project.created_at}


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    """
    Lister tous les projets
    --> Première validation
    """
    projects = db.query(Project).all()
    return [{"id": p.id, "name": p.name, "created_at": p.created_at} for p in projects]


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Récupérer les détails d'un projet avec tous ses objets.
    """
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    forests = project.forests
    domains = [d for f in forests for d in f.domains]
    servers = [s for d in domains for s in d.servers]
    users = [u for d in domains for u in d.users]
    applied_vulns = (
        db.query(AppliedVulnerability)
        .filter(AppliedVulnerability.project_id == project_id)
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
        "vulnerabilities_count": len(applied_vulns),
    }


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Supprimer un projet et tous ses objets associés
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/deploy")
def deploy_project(project_id: int, db: Session = Depends(get_db)):
    """
    Déployer un projet complet (génère et exécute le playbook Ansible)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # ========================= CLONE VMs ========================= #

        # Récupérer tous les serveurs du projet
        forests = project.forests
        domains = [d for f in forests for d in f.domains]
        all_servers = [s for d in domains for s in d.servers]

        if not all_servers:
            raise HTTPException(status_code=400, detail="No servers in project")

        # Préparer les données sans dépendance DB
        server_infos = [
            ServerInfo(id=s.id, fqdn=s.fqdn, ip=s.ip, vm_id=s.vm_id)
            for s in all_servers
        ]

        clone_results = deploy_lab(server_infos)

        # Sauvegarder les vm_id en DB
        for res in clone_results:
            if res.get("success") and res.get("vm_id"):
                server = db.get(Server, res["server_id"])
                if server:
                    server.vm_id = res["vm_id"]
        db.commit()

        time.sleep(60)

        # ========================= DC PROMO ========================= #

        all_dcs = get_dcs_grouped_by_domain(db)

        for dcs in all_dcs:
            is_primary = True

            domain = get_domain(dcs[0].domain_id, db)

            for dc in dcs:
                result = dc_promote(
                    server_ip=dc.ip,
                    dc_hostname=dc.fqdn,
                    domain_fqdn=domain.fqdn,
                    domain_netbios=domain.fqdn.split(".")[0],
                    dsrm_password="Pat@te10000!",
                    is_first_dc=is_primary,
                    domain_admin="Administrator",
                )

                if result["success"]:
                    restart_vm(dc.vm_id)
                else:
                    return {"project": project.name, "deployment_result": result}

                is_primary = False

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
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Deployment error: {str(e)}")
