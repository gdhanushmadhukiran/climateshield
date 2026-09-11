"""City service."""

from sqlalchemy.orm import Session
from app.repositories.city_repo import CityRepository
from app.schemas.city import CityResponse
from app.schemas.common import Coordinates
from app.core.exceptions import EntityNotFoundException


class CityService:
    def __init__(self, db: Session):
        self.repo = CityRepository(db)

    def get_city(self) -> CityResponse:
        city = self.repo.get_city()
        if not city:
            raise EntityNotFoundException("City", "default")

        return CityResponse(
            id=city.id,
            name=city.name,
            state="Andhra Pradesh",
            country=city.country,
            timezone=city.timezone,
            coordinates=Coordinates(lat=city.latitude, lng=city.longitude),
            population=2400000,
            areaKm2=540.0,
            criticalAssetsCount=42,
            riskScore=74,
        )
