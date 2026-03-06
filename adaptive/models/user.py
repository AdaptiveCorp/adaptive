from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adaptive.environment.database import Base
from adaptive.models.forest import Forest
from adaptive.models.server import Server


class User(Base):
    """Représente un utilisateur Active Directory."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    fqdn: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # ── _forest : Many-to-one, nullable ───────────────────────────────────────
    forest_id: Mapped[int | None] = mapped_column(
        ForeignKey("forests.id"), nullable=True
    )
    forest: Mapped[Forest | None] = relationship("Forest", back_populates="users")

    # ── _users : auto-référentiel parent → enfants ────────────────────────────
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    parent: Mapped[User | None] = relationship(
        "User",
        back_populates="users",
        remote_side="User.id",  # indique que id est le côté "un"
    )

    # ── _servers : One-to-many ─────────────────────────────────────────────────
    servers: Mapped[list[Server]] = relationship(
        "Server",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} fqdn={self.fqdn!r}>"
