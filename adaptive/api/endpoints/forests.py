from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.environment.database import get_db
from api.models.forest import Forest
from api.models.project import Project

router = APIRouter(prefix="/projects/{project_id}/forests", tags=["forests"])


@router.post("/")
def create_forest(project_id: int, fqdn: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    forest = Forest(fqdn=fqdn, project_id=project_id)
    db.add(forest)
    db.commit()
    db.refresh(forest)
    return {"id": forest.id, "fqdn": forest.fqdn, "project_id": forest.project_id}


@router.get("/")
def list_forests(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    forests = db.query(Forest).filter(Forest.project_id == project_id).all()
    return [
        {"id": f.id, "fqdn": f.fqdn, "project_id": f.project_id}
        for f in forests
    ]
