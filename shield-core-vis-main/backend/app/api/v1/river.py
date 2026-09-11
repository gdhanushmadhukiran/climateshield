"""River sensor nodes endpoint."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.river_service import RiverService
from app.schemas.river import RiverNodeResponse

router = APIRouter(prefix="/river", tags=["River"])


@router.get("/nodes", response_model=List[RiverNodeResponse], summary="List river telemetry sensor nodes")
def get_river_nodes(db: Session = Depends(get_db)):
    service = RiverService(db)
    return service.get_river_nodes()
