from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from adaptive.api.environment.database import Base

if TYPE_CHECKING:
    from adaptive.api.models.domain import Domain
    from adaptive.api.models.forest import Forest
    from adaptive.api.models.project import Project
    from adaptive.api.models.server import Server
    from adaptive.api.models.template import Template
    from adaptive.api.models.user import User


class AppliedTemplate(Base):
    """Instances de templates appliqués à un objet du lab (User, Server, Domain, Forest)."""

    __tablename__ = "applied_templates"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped[Project] = relationship("Project")

    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"), nullable=False)
    template: Mapped[Template] = relationship("Template", back_populates="applied")

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[User | None] = relationship("User", foreign_keys=[user_id])

    domain_id: Mapped[int | None] = mapped_column(ForeignKey("domains.id"), nullable=True)
    domain: Mapped[Domain | None] = relationship("Domain")

    server_id: Mapped[int | None] = mapped_column(ForeignKey("servers.id"), nullable=True)
    server: Mapped[Server | None] = relationship("Server")

    forest_id: Mapped[int | None] = mapped_column(ForeignKey("forests.id"), nullable=True)
    forest: Mapped[Forest | None] = relationship("Forest")

    params: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    status: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<AppliedTemplate id={self.id} template_id={self.template_id}>"
