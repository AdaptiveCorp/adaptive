from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from adaptive.api.environment.database import get_db
from adaptive.api.exceptions import ProjectNotFoundError
from adaptive.api.models.forest import Forest
from adaptive.api.models.project import Project
from adaptive.api.schemas.forest import ForestCreate, ForestResponse

router = APIRouter(prefix="/projects/{project_id}/forests", tags=["forests"])


@router.post("/", response_model=ForestResponse)
def create_forest(project_id: int, payload: ForestCreate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    forest = Forest(fqdn=payload.fqdn, project_id=project_id)
    db.add(forest)
    db.commit()
    db.refresh(forest)
    return forest


@router.get("/", response_model=list[ForestResponse])
def list_forests(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise ProjectNotFoundError(project_id)

    return db.query(Forest).filter(Forest.project_id == project_id).all()
