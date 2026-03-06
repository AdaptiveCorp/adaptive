from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.environment.database import Base
from adaptive.models.domain import Domain
from adaptive.models.project import Project
from adaptive.models.user import User


class Forest(Base):
    """Forêt Active Directory — appartient à un Project."""

    __tablename__ = "forests"

    id: Mapped[int] = mapped_column(primary_key=True)
    fqdn: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # ── FK vers Project ─────────────────────────────────────────────────
    lab_project_id: Mapped[int] = mapped_column(
        ForeignKey("lab_projects.id"), nullable=False
    )
    lab_project: Mapped[Project] = relationship("Project", back_populates="forests")

    # ── Domaines de cette forêt ────────────────────────────────────────────
    domains: Mapped[list[Domain]] = relationship(
        "Domain",
        back_populates="forest",
        cascade="all, delete-orphan",
    )

    # ── Utilisateurs de cette forêt ────────────────────────────────────────
    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="forest",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Forest id={self.id} fqdn={self.fqdn!r}>"
