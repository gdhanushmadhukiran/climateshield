"""City endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.city_service import CityService
from app.schemas.city import CityResponse

router = APIRouter(tags=["City"])


@router.get("/city", response_model=CityResponse, summary="Get primary city profile")
def get_city(db: Session = Depends(get_db)):
    service = CityService(db)
    return service.get_city()
