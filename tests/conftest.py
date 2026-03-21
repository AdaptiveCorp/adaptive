import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Monkey-patch the database module BEFORE the app is imported.
# seed_templates() uses `from database import SessionLocal` at import time,
# so we must replace engine/SessionLocal before main.py triggers that import.
# ---------------------------------------------------------------------------
from adaptive.api.environment import database as db_module

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(TEST_ENGINE, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = sessionmaker(bind=TEST_ENGINE)

db_module.engine = TEST_ENGINE
db_module.SessionLocal = TestSessionLocal


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def _create_tables():
    """Create all tables once for the test session."""
    # Import every model so Base.metadata registers their tables.
    import adaptive.api.models.applied_template  # noqa: F401
    import adaptive.api.models.domain  # noqa: F401
    import adaptive.api.models.forest  # noqa: F401
    import adaptive.api.models.project  # noqa: F401
    import adaptive.api.models.server  # noqa: F401
    import adaptive.api.models.template  # noqa: F401
    import adaptive.api.models.user  # noqa: F401
    import adaptive.api.models.vm_template  # noqa: F401
    from adaptive.api.environment.database import Base

    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture()
def client(_create_tables):
    """TestClient backed by an in-memory SQLite database."""
    from starlette.testclient import TestClient

    from adaptive.api.database import seed_templates as seed_module
    from adaptive.api.environment.database import get_db
    from adaptive.api.main import app

    # Patch seed_templates' own SessionLocal reference (captured via `from ... import`)
    seed_module.SessionLocal = TestSessionLocal

    def _override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()
