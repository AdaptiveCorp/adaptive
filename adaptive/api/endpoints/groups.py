from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.models.group import Group
from adaptive.api.exceptions import (
    GroupTargetRequiredError
)
from adaptive.api.models.user import User
from adaptive.api.schemas.group import GroupCreate, GroupResponse

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)

@router.post("/", response_model=GroupResponse)
def add_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
):
    """
    Créer un groupe logique (avec membres utilisateurs et éventuellement groupes).
    """

    if not payload.domain_id and not payload.server_id:
        raise GroupTargetRequiredError()
    if payload.domain_id and payload.server_id:
        raise GroupTargetRequiredError()
    
    print("DOMAIN ID :", payload.domain_id)
    group = Group(
        name=payload.name,
        description=payload.description,
        domain_id=payload.domain_id,
        server_id=payload.server_id,
    )

    # Ajouter les users membres si des IDs sont fournis
    if payload.user_ids:
        users = db.query(User).filter(User.id.in_(payload.user_ids)).all()
        group.users.extend(users)

    # Ajouter les groupes membres si des IDs sont fournis
    if payload.member_group_ids:
        member_groups = db.query(Group).filter(Group.id.in_(payload.member_group_ids)).all()
        group.member_groups.extend(member_groups)

    db.add(group)
    db.commit()
    db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        user_ids=[u.id for u in group.users],
        member_group_ids=[g.id for g in group.member_groups],
        domain_id=group.domain_id,
    )


@router.get("/", response_model=list[GroupResponse])
def list_groups(
    db: Session = Depends(get_db),
):
    """
    Lister tous les groupes avec leurs membres (ids).
    """
    groups = db.query(Group).all()
    return [
        GroupResponse(
            id=g.id,
            name=g.name,
            description=g.description,
            user_ids=[u.id for u in g.users],
            member_group_ids=[mg.id for mg in g.member_groups],
            domain_id=g.domain_id,
        )
        for g in groups
    ]


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
):
    """
    Récupérer le détail d'un groupe.
    """
    group = db.get(Group, group_id)
    if not group:
        # tu peux créer une GroupNotFoundError comme pour DomainNotFoundError
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        user_ids=[u.id for u in group.users],
        member_group_ids=[mg.id for mg in group.member_groups],
    )


@router.delete("/{group_id}", response_model=dict)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
):
    """
    Supprimer un groupe.
    """
    group = db.get(Group, group_id)
    if not group:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    db.delete(group)
    db.commit()
    return {"success": True}