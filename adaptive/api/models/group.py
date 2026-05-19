from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Table, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.api.environment.database import Base

if TYPE_CHECKING:
    from adaptive.api.models.user import User
    from adaptive.api.models.domain import Domain
    from adaptive.api.models.server import Server


# Table d’association User <-> Group
group_users = Table(
    "group_users",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

# Table d’association Group <-> Group (group nesting)
group_group_membership = Table(
    "group_group_membership",
    Base.metadata,
    Column("parent_group_id", ForeignKey("groups.id"), primary_key=True),
    Column("member_group_id", ForeignKey("groups.id"), primary_key=True),
)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    domain_id: Mapped[int | None] = mapped_column(ForeignKey("domains.id"), nullable=True)
    domain: Mapped[Domain | None] = relationship(
        "Domain",
        back_populates="groups", 
    )
    
    server_id: Mapped[int | None] = mapped_column(ForeignKey("servers.id"), nullable=True)
    server: Mapped[Server | None] = relationship(
        "Server",
        back_populates="groups",
    )

    # users membres du groupe
    users: Mapped[list[User]] = relationship(
        "User",
        secondary=group_users,
        back_populates="groups",
    )

    # groupes membres (nested groups)
    member_groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary=group_group_membership,
        primaryjoin=id == group_group_membership.c.parent_group_id,
        secondaryjoin=id == group_group_membership.c.member_group_id,
        back_populates="parent_groups",
    )

    # groupes dont CE groupe est membre
    parent_groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary=group_group_membership,
        primaryjoin=id == group_group_membership.c.member_group_id,
        secondaryjoin=id == group_group_membership.c.parent_group_id,
        back_populates="member_groups",
    )

    def __repr__(self) -> str:
        return f"<Group id={self.id} name={self.name!r}>"