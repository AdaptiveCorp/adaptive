import logging
from contextlib import asynccontextmanager

from anyio import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from adaptive.api.database.seed_templates import seed_templates, seed_vm_templates
from adaptive.api.endpoints import (
    domains,
    forests,
    groups,
    internals,
    projects,
    servers,
    users,
    vm_templates,
    vulnerabilities,
)
from adaptive.api.environment.logging import setup_logging
from adaptive.api.exceptions import (
    AdaptiveError,
    AnsibleError,
    ConflictError,
    NotFoundError,
    ProxmoxConnectionError,
    ProxmoxTimeoutError,
    ValidationError,
)

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Seeding templates from YAML...")
    seed_templates()
    seed_vm_templates(str(Path(__file__).parent / "database/vm-templates.yaml"))
    logger.info("Templates seeded")
    yield


app = FastAPI(title="Adaptive", lifespan=lifespan)

_STATUS_MAP: dict[type[AdaptiveError], int] = {
    ValidationError: 400,
    NotFoundError: 404,
    ConflictError: 409,
    ProxmoxConnectionError: 502,
    ProxmoxTimeoutError: 504,
    AnsibleError: 502,
}


@app.exception_handler(AdaptiveError)
async def adaptive_error_handler(request: Request, exc: AdaptiveError) -> JSONResponse:
    status = 500
    for cls in type(exc).__mro__:
        if cls in _STATUS_MAP:
            status = _STATUS_MAP[cls]
            break
    logger.error("%s: %s (detail=%s)", type(exc).__name__, exc.message, exc.detail)
    return JSONResponse(
        status_code=status,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "detail": exc.detail,
        },
    )


app.include_router(projects.router)
app.include_router(forests.router)
app.include_router(domains.router)
app.include_router(servers.router)
app.include_router(users.router)
app.include_router(vm_templates.router)
app.include_router(vulnerabilities.router)
app.include_router(internals.router)
app.include_router(groups.router)
