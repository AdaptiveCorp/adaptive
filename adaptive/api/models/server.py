from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.api.environment.database import Base

if TYPE_CHECKING:
    from adaptive.api.models.domain import Domain
    from adaptive.api.models.user import User
    from adaptive.api.models.vm_template import VmTemplate


class Server(Base):
    """Représente un serveur Active Directory."""

    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    fqdn: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_dc: Mapped[bool] = mapped_column(default=False, nullable=False)
    vm_id: Mapped[int | None] = mapped_column(nullable=True)

    ip: Mapped[str | None] = mapped_column(String(45))  # IPv4 ou IPv6
    gtw: Mapped[str | None] = mapped_column(String(45))  # gateway
    dns: Mapped[str | None] = mapped_column(String(45))

    domain_id: Mapped[int | None] = mapped_column(ForeignKey("domains.id"), nullable=True)
    domain: Mapped[Domain | None] = relationship("Domain", back_populates="servers")

    vm_template_id: Mapped[int | None] = mapped_column(ForeignKey("vm_templates.id"), nullable=True)
    vm_template: Mapped[VmTemplate | None] = relationship("VmTemplate", back_populates="servers")

    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="server",
        cascade="all, delete-orphan",
    )

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("servers.id"), nullable=True)
    servers: Mapped[list[Server]] = relationship(
        "Server",
        back_populates="parent_server",
        cascade="all, delete-orphan",
    )
    parent_server: Mapped[Server | None] = relationship(
        "Server",
        back_populates="servers",
        remote_side="Server.id",
    )

    @property
    def vm_template_name(self) -> str | None:
        return self.vm_template.name if self.vm_template else None

    def __repr__(self) -> str:
        return f"<Server id={self.id} fqdn={self.fqdn!r} is_dc={self.is_dc}>"
