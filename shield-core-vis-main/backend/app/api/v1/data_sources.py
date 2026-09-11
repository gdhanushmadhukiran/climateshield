"""Data sources endpoint."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.data_source_repo import DataSourceRepository
from app.schemas.data_source import DataSourceResponse

router = APIRouter(tags=["Data Sources"])


@router.get("/data-sources", response_model=List[DataSourceResponse], summary="List connected data ingestion sources")
def get_data_sources(db: Session = Depends(get_db)):
    repo = DataSourceRepository(db)
    sources = repo.get_all()
    return [
        DataSourceResponse(
            id=s.id,
            name=s.name,
            sourceType=s.source_type,
            status=s.status,
            latencyMs=s.latency_ms,
            reliability=s.reliability,
            lastUpdatedAt=s.last_updated_at.isoformat(),
        )
        for s in sources
    ]
