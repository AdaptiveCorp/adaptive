from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adaptive.api.models.domain import Domain
from adaptive.api.models.server import Server
from adaptive.api.models.user import User

from ..environment.database import get_db
from adaptive.api.endpoints.utils import get_root_dc
from adaptive.api.infrastructure import AnsibleService, ProxmoxProvider, ServerInfo
from adaptive.api.services.deployment_service import ansible_deploy_user



router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/")
def add_user(
    firstname: str,
    lastname: str,
    password: str,
    domain_id: int | None = None,
    server_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Ajouter un utilisateur AD — rattaché soit à un domaine, soit à un serveur.
    """
    if not domain_id and not server_id:
        raise HTTPException(status_code=400, detail="domain_id ou server_id requis")
    if domain_id and server_id:
        raise HTTPException(
            status_code=400, detail="Fournir domain_id ou server_id, pas les deux"
        )

    if domain_id:
        domain = db.get(Domain, domain_id)
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        username = firstname[0].lower() + "." + lastname.lower()
        user = User(domain_id=domain_id, firstname=firstname, lastname=lastname, username=username, password=password)
    else:
        server = db.get(Server, server_id)
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        #user = User(server_id=server_id, username=username, password=password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "domain_id": user.domain_id,
        "server_id": user.server_id,
    }

@router.post("/{user_id}")
def deploy_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    result  = ansible_deploy_user(user, db)
    if result : 
        return {"success" : result.success}
    
    else : 
        return {"success" : False, "message" : "An error ocured during deployement of user"}
    

@router.get("/")
def list_users(
    domain_id: int | None = None,
    server_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Lister les utilisateurs, filtré par domaine ou serveur.
    """
    query = db.query(User)
    if domain_id:
        query = query.filter(User.domain_id == domain_id)
    if server_id:
        query = query.filter(User.server_id == server_id)

    users = query.all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "domain_id": u.domain_id,
            "server_id": u.server_id,
        }
        for u in users
    ]
