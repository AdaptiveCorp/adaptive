import logging

from fastapi import FastAPI

from adaptive.endpoints import domains, forests, projects, servers, users, vulnerabilities

logging.getLogger("adaptive").setLevel(logging.DEBUG)

app = FastAPI(title="AD Lab Deployment API")

app.include_router(projects.router)
app.include_router(forests.router)
app.include_router(domains.router)
app.include_router(servers.router)
app.include_router(users.router)
app.include_router(vulnerabilities.router)
