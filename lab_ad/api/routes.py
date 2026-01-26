from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database import orm_models
#from ..services.vulnerability_service import VulnerabilityService
from ..database.seed_vulnerabilities import seed_vulnerability_templates
from ..integrations import dc_promote,deploy_lab,restart_vm
#from ..integrations.ansible_generator import generate_playbook_content
#from ..integrations.ansible_runner import run_playbook_from_memory
from .utils import get_dcs_grouped_by_domain, get_domain
import traceback
import time

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
    project = db.query(orm_models.DBProject).filter(orm_models.DBProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    forests = db.query(orm_models.DBForest).filter(orm_models.DBForest.project_id == project_id).all()
    domains = db.query(orm_models.DBDomain).filter(orm_models.DBDomain.project_id == project_id).all()
    servers = db.query(orm_models.DBServer).filter(orm_models.DBServer.project_id == project_id).all()
    users = db.query(orm_models.DBUser).filter(orm_models.DBUser.project_id == project_id).all()
    vulnerabilities = db.query(orm_models.DBAppliedVulnerability).filter(
        orm_models.DBAppliedVulnerability.project_id == project_id
    ).all()
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at
        },
        "forests": [{"id": f.id, "fqdn": f.fqdn} for f in forests],
        "domains": [{"id": d.id, "fqdn": d.fqdn, "forest_id": d.forest_id} for d in domains],
        "servers": [{"id": s.id, "fqdn": s.fqdn, "is_dc": s.is_dc, "ip": s.ip} for s in servers],
        "users": [{"id": u.id, "username": u.username} for u in users],
        "vulnerabilities_count": len(vulnerabilities)
    }


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Supprimer un projet et tous ses objets associés
    """
    project = db.query(orm_models.DBProject).filter(orm_models.DBProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


# ==================== FORÊTS ====================
@router.post("/projects/{project_id}/forest")
def add_forest(project_id: int, fqdn: str, db: Session = Depends(get_db)):
    """
    Ajouter une forêt Active Directory à un projet
    """
    # Vérifier que le projet existe
    project = db.query(orm_models.DBProject).filter(orm_models.DBProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    forest = orm_models.DBForest(project_id=project_id, fqdn=fqdn)
    db.add(forest)
    db.commit()
    db.refresh(forest)
    return {"id": forest.id, "fqdn": forest.fqdn, "project_id": forest.project_id}


@router.get("/projects/{project_id}/forest")
def list_forests(project_id: int = None, db: Session = Depends(get_db)):
    """
    Lister les forêts (optionnel: filtrer par projet)
    """
    query = db.query(orm_models.DBForest)
    if project_id:
        query = query.filter(orm_models.DBForest.project_id == project_id)
    
    forests = query.all()
    return [{"id": f.id, "fqdn": f.fqdn, "project_id": f.project_id} for f in forests]


# ==================== DOMAINES ====================
@router.post("/projects/{project_id}/forest/{forest_id}/domain")
def add_domain(project_id: int, forest_id: int, fqdn: str, db: Session = Depends(get_db)):
    """
    Ajouter un domaine à une forêt
    """

    # Vérifier que la forêt existe
    forest = db.query(orm_models.DBForest).filter(orm_models.DBForest.id == forest_id).first()
    if not forest:
        raise HTTPException(status_code=404, detail="Forest not found")
    
    domain = orm_models.DBDomain(
        project_id=project_id,
        forest_id=forest_id,
        fqdn=fqdn
    )
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return {"id": domain.id, "fqdn": domain.fqdn, "forest_id": domain.forest_id}


@router.get("/projects/{project_id}/forest/{forest_id}/domain")
def list_domains(project_id: int, forest_id: int, db: Session = Depends(get_db)):
    """
    Lister les domaines d'une forêt dans un projet
    """
    query = db.query(orm_models.DBDomain)
    query = query.filter(
        orm_models.DBDomain.project_id == project_id,
        orm_models.DBDomain.forest_id == forest_id
    )
    domains = query.all()

    return [{"id": d.id, "fqdn": d.fqdn, "forest_id": d.forest_id} for d in domains]



# ==================== SERVEURS ====================
@router.post("/projects/{project_id}/forest/{forest_id}/domain/{domain_id}/server")
def add_server(
    project_id: int,
    forest_id: int,
    domain_id: int,
    fqdn: str,
    is_dc: bool = False,
    ip: str = None,
    gateway: str = None,
    dns: str = None,
    db: Session = Depends(get_db)
):
    """
    Ajouter un serveur à un domaine
    """

    # Vérifier que le domaine existe
    query = db.query(orm_models.DBDomain)
    query = query.filter(
        orm_models.DBDomain.project_id == project_id,
        orm_models.DBDomain.forest_id == forest_id
    )
    domain = query.first()

    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    server = orm_models.DBServer(
        project_id=project_id,
        forest_id=forest_id,
        domain_id=domain_id,
        fqdn=fqdn,
        is_dc=is_dc,
        ip=ip,
        gateway=gateway,
        dns=dns
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return {
        "id": server.id,
        "fqdn": server.fqdn,
        "is_dc": server.is_dc,
        "ip": server.ip,
        "domain_id": server.domain_id
    }


@router.get("/projects/{project_id}/forest/{forest_id}/domain/{domain_id}/servers")
def list_domain_servers(domain_id: int, forest_id: int, project_id: int, db: Session = Depends(get_db)):
    """
    Lister les serveurs  d'un domain
    """
    query = db.query(orm_models.DBServer)
    query = query.filter(
        orm_models.DBServer.project_id == project_id,
        orm_models.DBServer.forest_id == forest_id,
        orm_models.DBServer.domain_id == domain_id
    )

    servers = query.all()
    return [{
        "id": s.id,
        "fqdn": s.fqdn,
        "is_dc": s.is_dc,
        "ip": s.ip
    } for s in servers]

@router.get("/projects/{project_id}/forest/{forest_id}/servers")
def list_forest_servers(forest_id: int, project_id: int, db: Session = Depends(get_db)):
    """
    Lister les serveurs  d'une fôret
    """
    query = db.query(orm_models.DBServer)
    query = query.filter(
        orm_models.DBServer.project_id == project_id,
        orm_models.DBServer.forest_id == forest_id
    )

    servers = query.all()
    return [{
        "id": s.id,
        "fqdn": s.fqdn,
        "is_dc": s.is_dc,
        "ip": s.ip
    } for s in servers]

# ==================== UTILISATEURS ====================
@router.post("/projects/{project_id}/forest/{forest_id}/domain/{domain_id}/user")
def add_user(
    project_id: int,
    forest_id: int,
    domain_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Ajouter un utilisateur Active Directory
    """
    query = db.query(orm_models.DBServer)
    query = db.query(orm_models.DBDomain)
    query = query.filter(
        orm_models.DBDomain.project_id == project_id,
        orm_models.DBDomain.forest_id == forest_id,
        orm_models.DBDomain.id == domain_id
    )

    domain = query.first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    user = orm_models.DBUser(
        project_id=project_id,
        forest_id=forest_id,
        domain_id=domain_id,
        username=username,
        password=password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "domain_id": user.domain_id
    }


@router.get("/projects/{project_id}/forest/{forest_id}/domain/{domain_id}/user")
def list_users(project_id: int, forest_id: int ,domain_id: int, db: Session = Depends(get_db)):
    """
    Lister les utilisateurs d'un domain
    """
    query = db.query(orm_models.DBDomain)
    query = query.filter(
        orm_models.DBDomain.project_id == project_id,
        orm_models.DBDomain.forest_id == forest_id,
        orm_models.DBDomain.id == domain_id
    )

    domain = query.first()
    query = db.query(orm_models.DBUser)

    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    query = db.query(orm_models.DBUser)
    query = query.filter(
        orm_models.DBUser.project_id == project_id,
        orm_models.DBUser.forest_id == forest_id,
        orm_models.DBUser.domain_id == domain_id
    )

    users = query.all()
    return [{
        "id": u.id,
        "username": u.username
    } for u in users]


# ==================== VULNÉRABILITÉS ====================
@router.get("/vulnerabilities/")
def list_available_vulnerabilities(db: Session = Depends(get_db)):
    """
    Lister toutes les vulnérabilités disponibles dans le catalogue
    """
    templates = db.query(orm_models.DBVulnerabilityTemplate).all()
    
    return [{
        "code": t.code,
        "name": t.name,
        "description": t.description,
        "category": t.category,
        "required_params": t.required_params
    } for t in templates]


@router.get("/projects/{project_id}/vulnerabilities/")
def list_applied_vulnerabilities(project_id: int, db: Session = Depends(get_db)):
    """
    Lister toutes les vulnérabilités appliquées à un projet
    """
    applied_vulns = db.query(orm_models.DBAppliedVulnerability).filter(
        orm_models.DBAppliedVulnerability.project_id == project_id
    ).all()
    
    result = []
    for av in applied_vulns:
        template = db.query(orm_models.DBVulnerabilityTemplate).filter(
            orm_models.DBVulnerabilityTemplate.id == av.template_id
        ).first()
        
        result.append({
            "id": av.id,
            "code": template.code if template else "unknown",
            "name": template.name if template else "Unknown",
            "target_user_id": av.target_user_id,
            "source_user_id": av.source_user_id,
            "params": av.params,
            "created_at": av.created_at
        })
    
    return result


@router.delete("/projects/{project_id}/vulnerabilities/{vuln_id}")
def remove_applied_vulnerability(vuln_id: int, db: Session = Depends(get_db)):
    """
    Supprimer une vulnérabilité appliquée
    """
    vuln = db.query(orm_models.DBAppliedVulnerability).filter(
        orm_models.DBAppliedVulnerability.id == vuln_id
    ).first()
    
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    db.delete(vuln)
    db.commit()
    return {"message": "Vulnerability removed successfully"}



@router.post("/admin/reload_vulnerabilities")
def reload_vulnerabilities():
    """
    Recharger les vulnérabilités depuis le fichier YAML
    (à appeler après modification du fichier vulnerabilities.yaml)
    """
    try:
        seed_vulnerability_templates()
        return {"message": "Vulnerabilities reloaded successfully from YAML"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading vulnerabilities: {str(e)}")



@router.post("/projects/{project_id}/deploy")
def deploy_project(project_id: int, db: Session = Depends(get_db)):
    """
    Déployer un projet complet (génère et exécute le playbook Ansible)
    """
    project = db.query(orm_models.DBProject).filter(orm_models.DBProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:

        # ========================= DC PROMO ========================= #
        
        result = deploy_lab(project_id, db) # Cloner les VMs
    
        time.sleep(60)

        all_dcs = get_dcs_grouped_by_domain(project_id, db) # list des DCs

        for dcs in all_dcs :
            is_primary = True
           
            domain = get_domain(dcs[0].domain_id,db)

            for dc in dcs :
                server_ip = dc.ip
                dc_hostname = dc.fqdn
                domain_fqdn = domain.fqdn
                domain_netbios = domain_fqdn.split('.')[1]
                dsrm_password = "Pat@te10000!"
                is_first_dc = is_primary
                domain_admin = 'Administrator'

                result = dc_promote(server_ip, # Promotion du dc
                                    dc_hostname,
                                    domain_fqdn,
                                    domain_netbios,
                                    dsrm_password,
                                    is_first_dc,
                                    domain_admin)
                
                if result["success"]:
                    result = restart_vm(dc.vm_id)  # Redémarre la VM

                else :
                    return {
                        "project": project.name,
                        "deployment_result": result
                    }
                
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





                

        return {
            "project": project.name,
            "deployment_result": result
        }
    except Exception as e:
        project.status = "error"
        db.commit()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Deployment error: {str(e)}")



# ==================== HEALTH CHECK ====================
@router.get("/health")
def health_check():
    """
    Vérifier que l'API fonctionne
    """
    return {"status": "healthy", "service": "AD Lab Deployment API"}
