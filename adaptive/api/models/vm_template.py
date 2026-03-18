from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.api.environment.database import Base

if TYPE_CHECKING:
    from adaptive.api.models.server import Server


class VmTemplate(Base):
    """Represents a VM template available for cloning."""

    __tablename__ = "vm_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    vm_id: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    servers: Mapped[list[Server]] = relationship("Server", back_populates="vm_template")

    def __repr__(self) -> str:
        return f"<VmTemplate id={self.id} name={self.name!r} vm_id={self.vm_id}>"
