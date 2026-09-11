"""Deterministic demo seed data for ClimateShield (Visakhapatnam dataset)."""

import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.core.database import Base, engine, SessionLocal
from app.models.city import CityModel
from app.models.zone import RiskZoneModel
from app.models.risk import RiskScoreModel, RiskDriverModel
from app.models.asset import AssetModel
from app.models.incident import IncidentModel
from app.models.alert import AlertModel
from app.models.sensor import SensorNodeModel, SensorObservationModel
from app.models.river import RiverNodeModel
from app.models.forecast import ForecastModel, ForecastPointModel
from app.models.cascade import CascadeNodeModel, CascadeEdgeModel
from app.models.data_source import DataSourceModel
from app.models.resource import ResourceModel
from app.models.action_plan import ActionRecommendationModel


def seed_database(db: Session = None):
    close_at_end = False
    if db is None:
        # Recreate all tables cleanly to reflect model schema changes
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_at_end = True

    try:
        now = datetime.now(timezone.utc)

        # 1. City
        city = CityModel(
            id="city-vizag",
            name="Visakhapatnam",
            country="India",
            timezone="Asia/Kolkata",
            latitude=17.6868,
            longitude=83.2185,
        )
        db.add(city)

        # 2. Risk Zones
        zone_a_poly = [
            [83.310, 17.720],
            [83.350, 17.720],
            [83.355, 17.760],
            [83.305, 17.755],
            [83.310, 17.720],
        ]
        zone_b_poly = [
            [83.180, 17.670],
            [83.240, 17.670],
            [83.235, 17.715],
            [83.175, 17.710],
            [83.180, 17.670],
        ]
        zone_c_poly = [
            [83.270, 17.680],
            [83.315, 17.680],
            [83.310, 17.715],
            [83.265, 17.710],
            [83.270, 17.680],
        ]

        zone_a = RiskZoneModel(
            id="zone-a",
            code="ZONE-A",
            name="MVP Colony - Sector 4",
            population=185000,
            area_km2=14.2,
            dominant_hazard="FLOOD",
            centroid_lat=17.742,
            centroid_lng=83.335,
            polygon_geojson=json.dumps(zone_a_poly),
        )
        zone_b = RiskZoneModel(
            id="zone-b",
            code="ZONE-B",
            name="Gajuwaka Industrial Corridor",
            population=290000,
            area_km2=28.5,
            dominant_hazard="DRAINAGE_STRESS",
            centroid_lat=17.695,
            centroid_lng=83.215,
            polygon_geojson=json.dumps(zone_b_poly),
        )
        zone_c = RiskZoneModel(
            id="zone-c",
            code="ZONE-C",
            name="One Town Heritage Belt",
            population=145000,
            area_km2=8.1,
            dominant_hazard="EXTREME_RAINFALL",
            centroid_lat=17.701,
            centroid_lng=83.298,
            polygon_geojson=json.dumps(zone_c_poly),
        )
        db.add_all([zone_a, zone_b, zone_c])
        db.flush()

        # 3. Risk Scores & Drivers
        score_a = RiskScoreModel(
            id="score-zone-a",
            zone_id="zone-a",
            value=84,
            level="CRITICAL",
            confidence=92,
            velocity_per_hour=4.5,
            data_quality="FRESH",
            observed_at=now,
        )
        score_b = RiskScoreModel(
            id="score-zone-b",
            zone_id="zone-b",
            value=68,
            level="MODERATE",
            confidence=88,
            velocity_per_hour=1.8,
            data_quality="FRESH",
            observed_at=now,
        )
        score_c = RiskScoreModel(
            id="score-zone-c",
            zone_id="zone-c",
            value=72,
            level="HIGH",
            confidence=85,
            velocity_per_hour=2.6,
            data_quality="FRESH",
            observed_at=now,
        )
        db.add_all([score_a, score_b, score_c])
        db.flush()

        drivers_a = [
            RiskDriverModel(
                risk_score_id="score-zone-a",
                metric_name="River level (upstream)",
                metric_value=4.12,
                unit="m",
                contribution=45.0,
                trend="RISING",
            ),
            RiskDriverModel(
                risk_score_id="score-zone-a",
                metric_name="Rainfall rate",
                metric_value=48.5,
                unit="mm/h",
                contribution=30.0,
                trend="RISING",
            ),
            RiskDriverModel(
                risk_score_id="score-zone-a",
                metric_name="Storm surge swell",
                metric_value=1.2,
                unit="m",
                contribution=25.0,
                trend="STABLE",
            ),
        ]
        drivers_b = [
            RiskDriverModel(
                risk_score_id="score-zone-b",
                metric_name="Drainage pump capacity",
                metric_value=62.0,
                unit="%",
                contribution=55.0,
                trend="FALLING",
            ),
            RiskDriverModel(
                risk_score_id="score-zone-b",
                metric_name="Ground saturation",
                metric_value=78.0,
                unit="%",
                contribution=45.0,
                trend="RISING",
            ),
        ]
        drivers_c = [
            RiskDriverModel(
                risk_score_id="score-zone-c",
                metric_name="Surface run-off velocity",
                metric_value=3.2,
                unit="m/s",
                contribution=60.0,
                trend="RISING",
            ),
            RiskDriverModel(
                risk_score_id="score-zone-c",
                metric_name="Inundation depth",
                metric_value=0.35,
                unit="m",
                contribution=40.0,
                trend="STABLE",
            ),
        ]
        db.add_all(drivers_a + drivers_b + drivers_c)

        # 4. Critical Assets
        assets = [
            AssetModel(
                id="asset-1",
                name="King George Hospital",
                asset_type="HOSPITAL",
                criticality="TIER_1",
                zone_id="zone-a",
                latitude=17.708,
                longitude=83.303,
                status="OPERATIONAL",
            ),
            AssetModel(
                id="asset-2",
                name="Port Emergency Operations Center",
                asset_type="EMERGENCY",
                criticality="TIER_1",
                zone_id="zone-c",
                latitude=17.692,
                longitude=83.295,
                status="OPERATIONAL",
            ),
            AssetModel(
                id="asset-3",
                name="Mudasarlova Water Treatment Facility",
                asset_type="WATER",
                criticality="TIER_1",
                zone_id="zone-a",
                latitude=17.755,
                longitude=83.328,
                status="OPERATIONAL",
            ),
            AssetModel(
                id="asset-4",
                name="Simhachalam Power Substation 220kV",
                asset_type="POWER",
                criticality="TIER_2",
                zone_id="zone-b",
                latitude=17.765,
                longitude=83.238,
                status="OPERATIONAL",
            ),
            AssetModel(
                id="asset-5",
                name="Dolphin's Nose Coastal Radar",
                asset_type="EMERGENCY",
                criticality="TIER_1",
                zone_id="zone-c",
                latitude=17.678,
                longitude=83.294,
                status="OPERATIONAL",
            ),
            AssetModel(
                id="asset-6",
                name="MVP Municipal High School Evacuation Center",
                asset_type="SCHOOL",
                criticality="TIER_3",
                zone_id="zone-a",
                latitude=17.739,
                longitude=83.336,
                status="OPERATIONAL",
            ),
        ]
        db.add_all(assets)

        # 5. Incidents
        incidents = [
            IncidentModel(
                id="inc-1",
                ref="INC-2418",
                title="Flooding along Riverfront Road",
                hazard_type="FLOOD",
                zone_id="zone-a",
                severity="EMERGENCY",
                status="OPEN",
                latitude=17.741,
                longitude=83.332,
                reported_at=now - timedelta(minutes=14),
            ),
            IncidentModel(
                id="inc-2",
                ref="INC-2417",
                title="Road waterlogging at Central Junction",
                hazard_type="WATERLOGGING",
                zone_id="zone-b",
                severity="WARNING",
                status="OPEN",
                latitude=17.698,
                longitude=83.218,
                reported_at=now - timedelta(minutes=38),
            ),
            IncidentModel(
                id="inc-3",
                ref="INC-2415",
                title="Drainage stress, North pump station",
                hazard_type="DRAINAGE_STRESS",
                zone_id="zone-b",
                severity="ADVISORY",
                status="IN_RESPONSE",
                latitude=17.712,
                longitude=83.225,
                reported_at=now - timedelta(minutes=62),
            ),
            IncidentModel(
                id="inc-4",
                ref="INC-2411",
                title="Extreme heat exposure, industrial belt",
                hazard_type="HEAT",
                zone_id="zone-c",
                severity="ADVISORY",
                status="RESOLVED",
                latitude=17.690,
                longitude=83.280,
                reported_at=now - timedelta(hours=3),
            ),
        ]
        db.add_all(incidents)

        # 6. Alerts
        alerts = [
            AlertModel(
                id="alt-1",
                ref="ALT-101",
                severity="EMERGENCY",
                title="CRITICAL FLOOD WARNING - MVP COLONY",
                message="River gauge upstream has breached critical 3.8m threshold. Immediate flood mitigation protocol required.",
                channels="SMS,PUSH,IN_APP",
                delivery_status="DELIVERED",
                acknowledged=False,
                zone_id="zone-a",
                created_at=now - timedelta(minutes=20),
            ),
            AlertModel(
                id="alt-2",
                ref="ALT-102",
                severity="WARNING",
                title="STORM DRAINAGE CAPACITY ALERT",
                message="Industrial corridor pump station operating at 92% continuous load.",
                channels="IN_APP,EMAIL",
                delivery_status="DELIVERED",
                acknowledged=False,
                zone_id="zone-b",
                created_at=now - timedelta(minutes=45),
            ),
            AlertModel(
                id="alt-3",
                ref="ALT-103",
                severity="ADVISORY",
                title="HIGH TIDE SWELL ADVISORY",
                message="Astronomical high tide expected at 14:30 IST. Coastal drainage outlets may experience back-flow.",
                channels="IN_APP",
                delivery_status="DELIVERED",
                acknowledged=True,
                acknowledged_by="operator-vizag-01",
                acknowledged_at=now - timedelta(minutes=15),
                zone_id="zone-c",
                created_at=now - timedelta(hours=2),
            ),
        ]
        db.add_all(alerts)

        # 7. Sensors & River Topology
        sensor_upstream = SensorNodeModel(
            id="sensor-river-01",
            code="RIV-UP-01",
            name="Riverfront North Inflow Station",
            zone_id="zone-a",
            latitude=17.750,
            longitude=83.340,
            status="HEALTHY",
            battery_pct=94,
            signal_pct=98,
            last_packet_at=now - timedelta(seconds=45),
        )
        sensor_midstream = SensorNodeModel(
            id="sensor-river-02",
            code="RIV-MID-02",
            name="Central Junction Culvert",
            zone_id="zone-a",
            latitude=17.735,
            longitude=83.330,
            status="HEALTHY",
            battery_pct=89,
            signal_pct=92,
            last_packet_at=now - timedelta(seconds=90),
        )
        sensor_downstream = SensorNodeModel(
            id="sensor-river-03",
            code="RIV-DOWN-03",
            name="Estuary Outfall South",
            zone_id="zone-c",
            latitude=17.710,
            longitude=83.315,
            status="ACTIVE",
            battery_pct=81,
            signal_pct=88,
            last_packet_at=now - timedelta(seconds=120),
        )
        db.add_all([sensor_upstream, sensor_midstream, sensor_downstream])
        db.flush()

        # River Nodes Topology
        river_up = RiverNodeModel(
            sensor_id="sensor-river-01",
            segment="UPSTREAM",
            threshold_m=3.8,
            travel_time_min=0,
            downstream_node_id="sensor-river-02",
        )
        river_mid = RiverNodeModel(
            sensor_id="sensor-river-02",
            segment="MIDSTREAM",
            threshold_m=3.2,
            travel_time_min=35,
            downstream_node_id="sensor-river-03",
        )
        river_down = RiverNodeModel(
            sensor_id="sensor-river-03",
            segment="DOWNSTREAM",
            threshold_m=2.5,
            travel_time_min=70,
            downstream_node_id=None,
        )
        db.add_all([river_up, river_mid, river_down])

        # Observations
        obs = [
            SensorObservationModel(
                sensor_id="sensor-river-01",
                observed_at=now,
                metric="water_level",
                value=4.12,
                unit="m",
                quality="FRESH",
                received_at=now,
            ),
            SensorObservationModel(
                sensor_id="sensor-river-02",
                observed_at=now,
                metric="water_level",
                value=2.85,
                unit="m",
                quality="FRESH",
                received_at=now,
            ),
            SensorObservationModel(
                sensor_id="sensor-river-03",
                observed_at=now,
                metric="water_level",
                value=1.94,
                unit="m",
                quality="FRESH",
                received_at=now,
            ),
        ]
        db.add_all(obs)

        # 8. Data Sources
        data_sources = [
            DataSourceModel(
                id="src-1",
                name="IMD Doppler Weather Radar",
                source_type="WEATHER",
                status="HEALTHY",
                latency_ms=85,
                reliability=99.8,
                last_updated_at=now,
            ),
            DataSourceModel(
                id="src-2",
                name="Copernicus Sentinel-1 / SAR",
                source_type="SATELLITE",
                status="HEALTHY",
                latency_ms=240,
                reliability=99.1,
                last_updated_at=now - timedelta(hours=1),
            ),
            DataSourceModel(
                id="src-3",
                name="INCOIS Coastal Wave Buoy Mesh",
                source_type="IOT",
                status="HEALTHY",
                latency_ms=45,
                reliability=99.5,
                last_updated_at=now,
            ),
            DataSourceModel(
                id="src-4",
                name="Municipal Stormwater GIS Network",
                source_type="GIS",
                status="HEALTHY",
                latency_ms=110,
                reliability=98.9,
                last_updated_at=now - timedelta(hours=2),
            ),
            DataSourceModel(
                id="src-5",
                name="Urban Hydrodynamic Physics Engine",
                source_type="MODEL",
                status="ACTIVE",
                latency_ms=310,
                reliability=96.5,
                last_updated_at=now,
            ),
        ]
        db.add_all(data_sources)

        # 9. Forecast
        forecast = ForecastModel(
            id="fc-zone-a",
            zone_id="zone-a",
            hazard="FLOOD",
            model="HYBRID_PHYSICS_STAT",
            horizon_hours=12,
            issued_at=now,
        )
        db.add(forecast)
        db.flush()

        forecast_points = [
            ForecastPointModel(
                forecast_id="fc-zone-a",
                timestamp=now + timedelta(hours=2),
                value=65,
                lower=58,
                upper=72,
                confidence=94,
            ),
            ForecastPointModel(
                forecast_id="fc-zone-a",
                timestamp=now + timedelta(hours=4),
                value=72,
                lower=64,
                upper=80,
                confidence=91,
            ),
            ForecastPointModel(
                forecast_id="fc-zone-a",
                timestamp=now + timedelta(hours=6),
                value=84,
                lower=76,
                upper=92,
                confidence=87,
            ),
            ForecastPointModel(
                forecast_id="fc-zone-a",
                timestamp=now + timedelta(hours=8),
                value=88,
                lower=79,
                upper=96,
                confidence=82,
            ),
            ForecastPointModel(
                forecast_id="fc-zone-a",
                timestamp=now + timedelta(hours=10),
                value=92,
                lower=81,
                upper=98,
                confidence=78,
            ),
        ]
        db.add_all(forecast_points)

        # 10. Cascade Network Graph
        cascade_nodes = [
            CascadeNodeModel(id="node-river-surge", label="Upstream River Inundation", kind="HAZARD", risk="CRITICAL"),
            CascadeNodeModel(id="node-drainage-pump", label="North Sector Pump Station", kind="SYSTEM", risk="HIGH"),
            CascadeNodeModel(id="node-kgh-hospital", label="King George Hospital Power", kind="ASSET", risk="HIGH"),
            CascadeNodeModel(id="node-ambulance-route", label="Coastal Arterial Transport", kind="SERVICE", risk="MODERATE"),
            CascadeNodeModel(id="node-mvp-residents", label="MVP Colony Low-Lying Residents", kind="POPULATION", risk="CRITICAL"),
        ]
        cascade_edges = [
            CascadeEdgeModel(from_node_id="node-river-surge", to_node_id="node-drainage-pump", likelihood=88.0, lag_minutes=25),
            CascadeEdgeModel(from_node_id="node-drainage-pump", to_node_id="node-ambulance-route", likelihood=74.0, lag_minutes=35),
            CascadeEdgeModel(from_node_id="node-drainage-pump", to_node_id="node-kgh-hospital", likelihood=62.0, lag_minutes=45),
            CascadeEdgeModel(from_node_id="node-river-surge", to_node_id="node-mvp-residents", likelihood=92.0, lag_minutes=30),
        ]
        db.add_all(cascade_nodes + cascade_edges)

        # 11. Response Resources Inventory
        resources = [
            ResourceModel(
                id="res-pump-01",
                name="Mobile Dewatering Pump 5000 GPM (Truck-Mounted)",
                category="PUMP",
                status="AVAILABLE",
                depot_name="Central Disaster Logistics Depot - Gajuwaka",
                latitude=17.695,
                longitude=83.215,
                hourly_cost=180.0,
                mobilization_minutes=15,
            ),
            ResourceModel(
                id="res-pump-02",
                name="Submersible High-Flow Choke Pump 3000 GPM",
                category="PUMP",
                status="AVAILABLE",
                depot_name="Port Area Emergency Staging Yard",
                latitude=17.701,
                longitude=83.298,
                hourly_cost=120.0,
                mobilization_minutes=10,
            ),
            ResourceModel(
                id="res-rescue-01",
                name="NDRF Flood Inundation Rescue Boat Team Alpha",
                category="RESCUE",
                status="AVAILABLE",
                depot_name="Port Area Emergency Staging Yard",
                latitude=17.701,
                longitude=83.298,
                hourly_cost=220.0,
                mobilization_minutes=12,
            ),
            ResourceModel(
                id="res-barrier-01",
                name="Rapid-Deployment Inflatable Flood Barrier Unit (500m)",
                category="BARRIER",
                status="AVAILABLE",
                depot_name="Central Disaster Logistics Depot - Gajuwaka",
                latitude=17.695,
                longitude=83.215,
                hourly_cost=150.0,
                mobilization_minutes=20,
            ),
            ResourceModel(
                id="res-power-01",
                name="Heavy-Duty 750kVA Emergency Generator Rig",
                category="POWER",
                status="AVAILABLE",
                depot_name="Central Disaster Logistics Depot - Gajuwaka",
                latitude=17.695,
                longitude=83.215,
                hourly_cost=250.0,
                mobilization_minutes=25,
            ),
            ResourceModel(
                id="res-crew-01",
                name="SDRF Emergency Municipal Evacuation & Shelter Crew",
                category="CREW",
                status="AVAILABLE",
                depot_name="Municipal Corporation HQ - Asilmetta",
                latitude=17.725,
                longitude=83.310,
                hourly_cost=90.0,
                mobilization_minutes=15,
            ),
        ]
        db.add_all(resources)

        db.commit()
        print("[SEED] Successfully seeded ClimateShield database with deterministic Visakhapatnam dataset!")
    except Exception as e:
        db.rollback()
        print(f"[SEED ERROR] Failed to seed database: {e}")
        raise e
    finally:
        if close_at_end:
            db.close()


if __name__ == "__main__":
    seed_database()
