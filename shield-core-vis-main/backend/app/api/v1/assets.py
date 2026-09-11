"""Assets endpoint."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.asset_repo import AssetRepository
from app.schemas.asset import AssetResponse
from app.schemas.common import Coordinates

router = APIRouter(tags=["Assets"])


@router.get("/assets", response_model=List[AssetResponse], summary="List critical infrastructure assets")
def get_assets(db: Session = Depends(get_db)):
    repo = AssetRepository(db)
    assets = repo.get_all()
    return [
        AssetResponse(
            id=a.id,
            name=a.name,
            category=a.asset_type,
            zoneId=a.zone_id,
            criticality=a.criticality,
            coordinates=Coordinates(lat=a.latitude, lng=a.longitude),
            status=a.status,
        )
        for a in assets
    ]
