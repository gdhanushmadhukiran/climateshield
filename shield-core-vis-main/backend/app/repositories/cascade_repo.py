"""Cascade graph repository."""

from typing import List
from sqlalchemy.orm import Session
from app.models.cascade import CascadeNodeModel, CascadeEdgeModel


class CascadeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_nodes(self) -> List[CascadeNodeModel]:
        return self.db.query(CascadeNodeModel).all()

    def get_edges(self) -> List[CascadeEdgeModel]:
        return self.db.query(CascadeEdgeModel).all()
