"""River service."""

from typing import List
from sqlalchemy.orm import Session
from app.repositories.river_repo import RiverRepository
from app.schemas.river import RiverNodeResponse


class RiverService:
    def __init__(self, db: Session):
        self.repo = RiverRepository(db)

    def get_river_nodes(self) -> List[RiverNodeResponse]:
        raw_nodes = self.repo.get_all_nodes()
        return [RiverNodeResponse(**node) for node in raw_nodes]
