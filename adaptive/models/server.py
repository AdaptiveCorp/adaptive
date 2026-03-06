from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.environment.database import Base
from adaptive.models.domain import Domain
from adaptive.models.forest import Forest
from adaptive.models.user import User


class Server(Base):
    """Représente un serveur Active Directory."""

    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    fqdn: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_dc: Mapped[bool] = mapped_column(default=False, nullable=False)

    # ── Réseau ─────────────────────────────────────────────────────────────
    ip: Mapped[str | None] = mapped_column(String(45))  # IPv4 ou IPv6
    gtw: Mapped[str | None] = mapped_column(String(45))  # gateway
    dns: Mapped[str | None] = mapped_column(String(45))

    # ── FK vers Domain ─────────────────────────────────────────────────────
    domain_id: Mapped[int | None] = mapped_column(
        ForeignKey("domains.id"), nullable=True
    )
    domain: Mapped[Domain | None] = relationship("Domain", back_populates="servers")

    # ── FK vers Forest ─────────────────────────────────────────────────────
    forest_id: Mapped[int | None] = mapped_column(
        ForeignKey("forests.id"), nullable=True
    )
    forest: Mapped[Forest | None] = relationship("Forest", back_populates="servers")

    # ── _users : utilisateurs hébergés sur ce serveur ──────────────────────
    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="server",
        cascade="all, delete-orphan",
    )

    # ── _servers : auto-référentiel (ex: DC principal → DC secondaires) ────
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("servers.id"), nullable=True
    )
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

    def __repr__(self) -> str:
        return f"<Server id={self.id} fqdn={self.fqdn!r} is_dc={self.is_dc}>"
