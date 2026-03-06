import logging

from fastapi import FastAPI
from lab_ad.database.connection import Base, engine

from adaptive.endpoints import forests, projects, users, vulnerabilities

# Créer les tables dans la base
Base.metadata.create_all(bind=engine)

logging.getLogger("adaptive").setLevel(logging.DEBUG)

# Créer l'app FastAPI
app = FastAPI(title="AD Lab Deployment API")

# Inclure les routes
app.include_router(vulnerabilities.router)
app.include_router(users.router)
app.include_router(forests.router)
app.include_router(projects.router)


@app.get("/")
def root():
    return {"message": "API Active Directory Lab"}
