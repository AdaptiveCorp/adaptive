import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from adaptive.api.database.seed_templates import seed_templates
from adaptive.api.endpoints import (
    domains,
    forests,
    internals,
    projects,
    servers,
    users,
    vm_templates,
    vulnerabilities,
)

logging.getLogger("adaptive").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Seeding templates from YAML...")
    seed_templates()
    logger.info("Templates seeded")
    yield


app = FastAPI(title="Adaptive", lifespan=lifespan)

app.include_router(projects.router)
app.include_router(forests.router)
app.include_router(domains.router)
app.include_router(servers.router)
app.include_router(users.router)
app.include_router(vm_templates.router)
app.include_router(vulnerabilities.router)
app.include_router(internals.router)
