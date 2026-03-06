from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import orm_models
from ..database.connection import get_db

# from ..services.vulnerability_service import VulnerabilityService
# from ..integrations.ansible_generator import generate_playbook_content
# from ..integrations.ansible_runner import run_playbook_from_memory


router = APIRouter()


# ==================== UTILISATEURS ====================
@router.post("/projects/{project_id}/forest/{forest_id}/domain/{domain_id}/user")
def add_user(
    project_id: int,
    forest_id: int,
    domain_id: int,
    username: str,
    password: str,
    db: Session = Depends(get_db),
):
    """
    Ajouter un utilisateur Active Directory
    """
    query = db.query(orm_models.DBServer)
    query = db.query(orm_models.DBDomain)
    query = query.filter(
        orm_models.DBDomain.project_id == project_id,
        orm_models.DBDomain.forest_id == forest_id,
        orm_models.DBDomain.id == domain_id,
    )

    domain = query.first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    user = orm_models.DBUser(
        project_id=project_id,
        forest_id=forest_id,
        domain_id=domain_id,
        username=username,
        password=password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "domain_id": user.domain_id}


@router.get("/projects/{project_id}/forest/{forest_id}/domain/{domain_id}/user")
def list_users(
    project_id: int, forest_id: int, domain_id: int, db: Session = Depends(get_db)
):
    """
    Lister les utilisateurs d'un domain
    """
    query = db.query(orm_models.DBDomain)
    query = query.filter(
        orm_models.DBDomain.project_id == project_id,
        orm_models.DBDomain.forest_id == forest_id,
        orm_models.DBDomain.id == domain_id,
    )

    domain = query.first()
    query = db.query(orm_models.DBUser)

    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    query = db.query(orm_models.DBUser)
    query = query.filter(
        orm_models.DBUser.project_id == project_id,
        orm_models.DBUser.forest_id == forest_id,
        orm_models.DBUser.domain_id == domain_id,
    )

    users = query.all()
    return [{"id": u.id, "username": u.username} for u in users]
