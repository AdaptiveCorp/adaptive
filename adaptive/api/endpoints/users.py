from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import (
    DomainNotFoundError,
    ServerNotFoundError,
    UserTargetConflictError,
    UserTargetRequiredError,
    UserNotFoundError,
)
from adaptive.api.models.applied_template import AppliedTemplate
from adaptive.api.models.domain import Domain
from adaptive.api.models.server import Server
from adaptive.api.models.user import User
from adaptive.api.schemas.user import UserCreate, UserResponse
from adaptive.api.services.deployment_service import ansible_deploy_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserResponse)
def add_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Ajouter un utilisateur AD — rattaché soit à un domaine, soit à un serveur.
    """
    if not payload.domain_id and not payload.server_id:
        raise UserTargetRequiredError()
    if payload.domain_id and payload.server_id:
        raise UserTargetConflictError()

    if payload.domain_id:
        domain = db.get(Domain, payload.domain_id)
        if not domain:
            raise DomainNotFoundError(payload.domain_id)
        username = payload.firstname[0].lower() + "." + payload.lastname.lower()
        user = User(
            domain_id=payload.domain_id,
            firstname=payload.firstname,
            lastname=payload.lastname,
            username=username,
            password=payload.password,
        )
    else:
        server = db.get(Server, payload.server_id)
        if not server:
            raise ServerNotFoundError(payload.server_id)
        # user = User(server_id=payload.server_id, username=username, password=payload.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}")
def deploy_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    result = ansible_deploy_user(user, db)
    if result:
        return {"success": result.success}

    else:
        return {"success": False, "message": "An error ocured during deployement of user"}


@router.get("/", response_model=list[UserResponse])
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

    return query.all()
