from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.api.environment.database import Base

if TYPE_CHECKING:
    from adaptive.api.models.domain import Domain
    from adaptive.api.models.project import Project


class Forest(Base):
    """Forêt Active Directory — appartient à un Project."""

    __tablename__ = "forests"

    id: Mapped[int] = mapped_column(primary_key=True)
    fqdn: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped[Project] = relationship("Project", back_populates="forests")

    domains: Mapped[list[Domain]] = relationship(
        "Domain",
        back_populates="forest",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Forest id={self.id} fqdn={self.fqdn!r}>"
