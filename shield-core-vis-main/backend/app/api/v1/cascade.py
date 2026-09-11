"""Cascade graph endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.cascade_repo import CascadeRepository
from app.schemas.cascade import CascadeGraphResponse, CascadeNodeResponse, CascadeEdgeResponse

router = APIRouter(prefix="/cascade", tags=["Cascade"])


@router.get("/graph", response_model=CascadeGraphResponse, summary="Get systemic failure cascade network graph")
def get_cascade_graph(db: Session = Depends(get_db)):
    repo = CascadeRepository(db)
    nodes = repo.get_nodes()
    edges = repo.get_edges()

    node_responses = [
        CascadeNodeResponse(id=n.id, label=n.label, kind=n.kind, risk=n.risk)
        for n in nodes
    ]
    edge_responses = [
        CascadeEdgeResponse(
            id=e.id,
            **{"from": e.from_node_id},
            to=e.to_node_id,
            likelihood=e.likelihood,
            lagMinutes=e.lag_minutes,
        )
        for e in edges
    ]

    return CascadeGraphResponse(nodes=node_responses, edges=edge_responses)
