"""ClimateShield Multi-Hazard Spatial Risk Intelligence Engine Package."""

from app.engine.base import (
    ENGINE_VERSION,
    LEVEL_CRITICAL_THRESHOLD,
    LEVEL_HIGH_THRESHOLD,
    LEVEL_MODERATE_THRESHOLD,
    get_risk_level,
    clamp,
    linear_scale,
)
from app.engine.flood_engine import FloodHazardEngine
from app.engine.heat_engine import HeatHazardEngine
from app.engine.secondary_hazard_engine import SecondaryHazardEngine
from app.engine.exposure_engine import ExposureEngine
from app.engine.vulnerability_engine import VulnerabilityEngine
from app.engine.confidence_engine import ConfidenceEngine
from app.engine.composite_risk_engine import CompositeRiskEngine
from app.engine.cascade_engine import CascadeEngine
from app.engine.coordinator import RiskIntelligenceCoordinator
from app.engine.route_logistics import RouteLogisticsEngine
from app.engine.resource_optimizer import ResourceOptimizer
from app.engine.simulation_engine import SimulationEngine

__all__ = [
    "ENGINE_VERSION",
    "LEVEL_CRITICAL_THRESHOLD",
    "LEVEL_HIGH_THRESHOLD",
    "LEVEL_MODERATE_THRESHOLD",
    "get_risk_level",
    "clamp",
    "linear_scale",
    "FloodHazardEngine",
    "HeatHazardEngine",
    "SecondaryHazardEngine",
    "ExposureEngine",
    "VulnerabilityEngine",
    "ConfidenceEngine",
    "CompositeRiskEngine",
    "CascadeEngine",
    "RiskIntelligenceCoordinator",
    "RouteLogisticsEngine",
    "ResourceOptimizer",
    "SimulationEngine",
]
