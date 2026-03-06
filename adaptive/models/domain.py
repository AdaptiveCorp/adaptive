from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.environment.database import Base
from adaptive.models.forest import Forest
from adaptive.models.project import Project
from adaptive.models.user import User


class Domain(Base):
    """Domaine AD — appartient à une Forêt et un LabProject."""

    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    fqdn: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # ── FK vers Forest ─────────────────────────────────────────────────────
    forest_id: Mapped[int] = mapped_column(ForeignKey("forests.id"), nullable=False)
    forest: Mapped[Forest] = relationship("Forest", back_populates="domains")

    # ── FK vers LabProject (accès direct sans passer par Forest) ───────────
    lab_project_id: Mapped[int] = mapped_column(
        ForeignKey("lab_projects.id"), nullable=False
    )
    lab_project: Mapped[Project] = relationship("LabProject", back_populates="domains")

    # ── Utilisateurs du domaine ────────────────────────────────────────────
    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="domain",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Domain id={self.id} fqdn={self.fqdn!r}>"
