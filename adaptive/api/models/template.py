from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.environment.database import Base

if TYPE_CHECKING:
    from adaptive.models.applied_template import AppliedTemplate


class TemplateType(str, enum.Enum):
    CONFIG = "config"
    VULNERABILITY = "vulnerability"


class Template(Base):
    """Catalogue des templates disponibles (config infra ou vulnérabilités)."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[TemplateType] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50))

    content: Mapped[str] = mapped_column(Text, nullable=False)

    required_params: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    applied: Mapped[list[AppliedTemplate]] = relationship(
        "AppliedTemplate", back_populates="template"
    )

    def __repr__(self) -> str:
        return f"<Template id={self.id} code={self.code!r} type={self.type!r}>"
