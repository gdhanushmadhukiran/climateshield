"""Asset repository."""

from typing import List
from sqlalchemy.orm import Session
from app.models.asset import AssetModel


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[AssetModel]:
        return self.db.query(AssetModel).all()
