from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.environment.database import Base

if TYPE_CHECKING:
    from adaptive.models.domain import Domain
    from adaptive.models.server import Server


class User(Base):
    """Représente un utilisateur Active Directory."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    domain_id: Mapped[int | None] = mapped_column(
        ForeignKey("domains.id"), nullable=True
    )
    domain: Mapped[Domain | None] = relationship("Domain", back_populates="users")

    server_id: Mapped[int | None] = mapped_column(
        ForeignKey("servers.id"), nullable=True
    )
    server: Mapped[Server | None] = relationship("Server", back_populates="users")

    def __repr__(self) -> str:
        return f"<User id={self.id}>"
