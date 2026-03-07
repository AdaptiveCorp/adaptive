import logging

from fastapi import FastAPI

from adaptive.endpoints import forests, projects, users, vulnerabilities

logging.getLogger("adaptive").setLevel(logging.DEBUG)

# Créer l'app FastAPI
app = FastAPI(title="AD Lab Deployment API")

# Inclure les routes
app.include_router(vulnerabilities.router)
app.include_router(users.router)
app.include_router(forests.router)
app.include_router(projects.router)
