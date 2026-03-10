from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.environment.database import Base

if TYPE_CHECKING:
    from api.models.forest import Forest
    from api.models.server import Server
    from api.models.user import User


class Domain(Base):
    """Domaine AD — appartient à une Forêt."""

    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    fqdn: Mapped[str] = mapped_column(String(255), nullable=False)

    forest_id: Mapped[int] = mapped_column(ForeignKey("forests.id"), nullable=False)
    forest: Mapped[Forest] = relationship("Forest", back_populates="domains")

    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="domain",
        cascade="all, delete-orphan",
    )

    servers: Mapped[list[Server]] = relationship(
        "Server",
        back_populates="domain",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Domain id={self.id} fqdn={self.fqdn!r}>"
