"""ClimateShield Route & Deployment Logistics Engine.

Calculates geodesic distances, dynamic route impedance factoring in road waterlogging,
and estimated time of arrival (ETA) for emergency response equipment and crews.
"""

import math
from typing import Dict, Any, Tuple


class RouteLogisticsEngine:
    """Calculates spatial route distances, speed penalties, and ETAs."""

    EARTH_RADIUS_KM = 6371.0
    BASE_URBAN_SPEED_KMH = 35.0  # Normal emergency vehicle speed in urban grid

    @classmethod
    def haversine_distance_km(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle distance between two points on Earth in kilometers."""
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(cls.EARTH_RADIUS_KM * c, 2)

    @classmethod
    def calculate_deployment_eta(
        cls,
        depot_lat: float,
        depot_lng: float,
        target_lat: float,
        target_lng: float,
        mobilization_minutes: int = 15,
        waterlogging_severity: str = "NONE",  # NONE, MODERATE, SEVERE
    ) -> Dict[str, Any]:
        """Calculates distance, effective speed, transit duration, and total ETA."""
        distance_km = cls.haversine_distance_km(depot_lat, depot_lng, target_lat, target_lng)

        # Apply route impedance penalty based on waterlogging / flood hazard
        speed_modifier = 1.0
        route_status = "CLEAR"
        if waterlogging_severity == "SEVERE":
            speed_modifier = 0.50  # 50% slower due to detours / flooded arterial roads
            route_status = "IMPEDED_DETOUR_REQUIRED"
        elif waterlogging_severity == "MODERATE":
            speed_modifier = 0.75  # 25% slower
            route_status = "MODERATE_WATERLOGGING"

        effective_speed = max(10.0, cls.BASE_URBAN_SPEED_KMH * speed_modifier)
        transit_minutes = int(math.ceil((distance_km / effective_speed) * 60.0))
        total_eta_minutes = mobilization_minutes + transit_minutes

        # Recommended corridor selection based on spatial position
        if target_lat > 17.73:
            primary_corridor = "Via Beach Road Arterial / North Link"
            backup_corridor = "Via NH-16 Ring Corridor"
        elif target_lng < 83.25:
            primary_corridor = "Via Industrial Bypass Expressway"
            backup_corridor = "Via Gajuwaka Main Arterial"
        else:
            primary_corridor = "Via Central Heritage Avenue"
            backup_corridor = "Via Port Access Highway"

        return {
            "distance_km": distance_km,
            "mobilization_minutes": mobilization_minutes,
            "transit_minutes": transit_minutes,
            "total_eta_minutes": total_eta_minutes,
            "effective_speed_kmh": round(effective_speed, 1),
            "route_status": route_status,
            "primary_corridor": primary_corridor,
            "backup_corridor": backup_corridor,
        }
