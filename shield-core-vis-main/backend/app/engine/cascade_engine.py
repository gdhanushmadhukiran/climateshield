"""ClimateShield Dynamic Cascade Network Engine.

Dynamically models systemic failure propagation across physical assets, networks,
and operational services based on active spatial hazard and risk states.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.cascade import CascadeNodeModel, CascadeEdgeModel
from app.engine.base import clamp


class CascadeEngine:
    """Dynamic infrastructure cascade propagation engine."""

    def __init__(self, db: Session):
        self.db = db

    def recalibrate(self, zone_risks: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Recalibrates cascade graph node risks and edge likelihoods."""
        nodes = self.db.query(CascadeNodeModel).all()
        edges = self.db.query(CascadeEdgeModel).all()

        # Find maximum risk in city
        max_risk = max((z.get("score", 50) for z in zone_risks.values()), default=50)

        # 1. Update Node Risk States dynamically
        for n in nodes:
            nid = n.id.lower()
            if "inflow" in nid or "river" in nid:
                # Direct hydrological driver
                if max_risk >= 80:
                    n.risk = "CRITICAL"
                elif max_risk >= 65:
                    n.risk = "HIGH"
                else:
                    n.risk = "MODERATE"
            elif "pump" in nid or "drainage" in nid:
                # Intermediate infrastructure
                if max_risk >= 80:
                    n.risk = "CRITICAL"
                elif max_risk >= 65:
                    n.risk = "HIGH"
                else:
                    n.risk = "MODERATE"
            elif "substation" in nid or "power" in nid or "road" in nid:
                # Downstream dependencies
                if max_risk >= 80:
                    n.risk = "HIGH"
                elif max_risk >= 65:
                    n.risk = "ELEVATED"
                else:
                    n.risk = "MODERATE"

        # 2. Update Edge Likelihoods and Propagation Lags
        # Higher active risk -> Higher propagation likelihood, Shorter response lag
        for e in edges:
            # Base scale factor: max_risk / 100
            risk_ratio = clamp(max_risk / 100.0, 0.2, 1.0)

            # Likelihood in [0.15, 0.95]
            new_likelihood = round(clamp(0.20 + (0.75 * (risk_ratio ** 1.3)), 0.10, 0.95), 2)
            e.likelihood = new_likelihood

            # Lag minutes: decreases under acute surge
            base_lag = 45
            if "road" in e.to_node_id.lower() or "substation" in e.to_node_id.lower():
                base_lag = 60
            elif "pump" in e.to_node_id.lower():
                base_lag = 25

            # Shorten lag under high risk
            new_lag = max(10, int(round(base_lag * (1.2 - (0.5 * risk_ratio)))))
            e.lag_minutes = new_lag

        self.db.commit()

        return {
            "nodes_updated": len(nodes),
            "edges_updated": len(edges),
            "max_risk_factor": max_risk,
        }
