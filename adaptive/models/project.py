from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.environment.database import Base
from adaptive.models.domain import Domain
from adaptive.models.forest import Forest


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # ── _forests : One-to-many ─────────────────────────────────────────────
    forests: Mapped[list[Forest]] = relationship(
        "Forest",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # ── _domains : One-to-many ─────────────────────────────────────────────
    domains: Mapped[list[Domain]] = relationship(
        "Domain",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<LabProject id={self.id} name={self.name!r}>"
