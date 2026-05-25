from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import (
    GroupNotFoundError,
    GroupTargetRequiredError,
    TemplateNotFoundError,
    UserNotFoundError,
)
from adaptive.api.models.applied_template import AppliedTemplate, TemplateStatus
from adaptive.api.models.group import Group
from adaptive.api.models.template import Template
from adaptive.api.models.user import User
from adaptive.api.schemas.group import GroupCreate, GroupMembershipUpdate, GroupResponse

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
    Créer un groupe logique (avec membres utilisateurs).
    """
    if not payload.domain_id and not payload.server_id:
        raise GroupTargetRequiredError()
    if payload.domain_id and payload.server_id:
        raise GroupTargetRequiredError()

    group = Group(
        name=payload.name,
        description=payload.description,
        domain_id=payload.domain_id,
        server_id=payload.server_id,
    )

    if payload.user_ids:
        users = db.query(User).filter(User.id.in_(payload.user_ids)).all()
        group.users.extend(users)

    db.add(group)
    db.commit()
    db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        user_ids=[u.id for u in group.users],
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
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        user_ids=[u.id for u in group.users],
        domain_id=group.domain_id,
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
        raise GroupNotFoundError(group_id=group_id)

    template_name = "add_groups"
    template = db.query(Template).filter(Template.code == template_name).first()

    if not template:
        raise TemplateNotFoundError(template_name=template_name)

    applied_template = (
        db.query(AppliedTemplate)
        .filter(AppliedTemplate.group_id == group.id, AppliedTemplate.template_id == template.id)
        .first()
    )

    if applied_template:
        applied_template.status = TemplateStatus.REVERTED_PENDING
    else:
        db.delete(group)

    db.commit()

    return {"success": True}


@router.post("/{group_id}/members", response_model=GroupResponse)
def add_membership(
    group_id: int,
    payload: GroupMembershipUpdate,
    db: Session = Depends(get_db),
):
    """
    Ajouter des utilisateurs à un groupe existant.
    """
    group = db.get(Group, group_id)
    if not group:
        raise GroupNotFoundError(group_id=group_id)

    existing_user_ids = {u.id for u in group.users}

    if payload.user_ids:
        new_user_ids = set(payload.user_ids) - existing_user_ids
        if new_user_ids:
            new_users = db.query(User).filter(User.id.in_(new_user_ids)).all()
            group.users.extend(new_users)

    db.commit()
    db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        user_ids=[u.id for u in group.users],
        domain_id=group.domain_id,
    )


@router.delete("/{group_id}/{user_id}", response_model=dict)
def delete_user_membership(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Supprimer un membership avec l'utilisateur.
    """
    group = db.get(Group, group_id)
    user = db.get(User, user_id)

    if not group:
        raise GroupNotFoundError(group_id=group_id)

    if not user:
        raise UserNotFoundError(user_id=user_id)

    template_name = "add_group_members"
    template = db.query(Template).filter(Template.code == template_name).first()

    if not template:
        raise TemplateNotFoundError(template_name=template_name)

    applied_template = (
        db.query(AppliedTemplate)
        .filter(
            AppliedTemplate.group_id == group.id,
            AppliedTemplate.user_id == user.id,
            AppliedTemplate.template_id == template.id,
        )
        .first()
    )

    if applied_template:
        applied_template.status = TemplateStatus.REVERTED_PENDING
    else:
        group.users.remove(user)

    db.commit()

    return {"success": True}
