"""Data source repository."""

from typing import List
from sqlalchemy.orm import Session
from app.models.data_source import DataSourceModel


class DataSourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[DataSourceModel]:
        return self.db.query(DataSourceModel).all()
