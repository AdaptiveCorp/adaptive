from fastapi import FastAPI
from .api.routes import router
from lab_ad.database.connection import engine, Base

# Créer les tables dans la base
Base.metadata.create_all(bind=engine)

# Créer l'app FastAPI
app = FastAPI(title="AD Lab Deployment API")

# Inclure les routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "API Active Directory Lab"}
