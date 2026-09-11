"""Initial schema for ClimateShield PostgreSQL/PostGIS foundation

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Cities
    op.create_table(
        "cities",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False, server_default="India"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 2. Zones
    op.create_table(
        "zones",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("population", sa.Integer(), nullable=False),
        sa.Column("area_km2", sa.Float(), nullable=False),
        sa.Column("dominant_hazard", sa.String(50), nullable=False),
        sa.Column("centroid_lat", sa.Float(), nullable=False),
        sa.Column("centroid_lng", sa.Float(), nullable=False),
        sa.Column("polygon_geojson", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_zones_code", "zones", ["code"])

    # 3. Risk Scores
    op.create_table(
        "risk_scores",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("zone_id", sa.String(50), sa.ForeignKey("zones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("velocity_per_hour", sa.Float(), nullable=False),
        sa.Column("data_quality", sa.String(20), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_risk_scores_zone_id", "risk_scores", ["zone_id"])
    op.create_index("ix_risk_scores_observed_at", "risk_scores", ["observed_at"])
    op.create_index("ix_risk_scores_zone_observed", "risk_scores", ["zone_id", "observed_at"])

    # 4. Risk Drivers
    op.create_table(
        "risk_drivers",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("risk_score_id", sa.String(50), sa.ForeignKey("risk_scores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("contribution", sa.Float(), nullable=False),
        sa.Column("trend", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_risk_drivers_risk_score_id", "risk_drivers", ["risk_score_id"])

    # 5. Assets
    op.create_table(
        "assets",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("asset_type", sa.String(50), nullable=False),
        sa.Column("criticality", sa.String(20), nullable=False),
        sa.Column("zone_id", sa.String(50), sa.ForeignKey("zones.id"), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_assets_zone_id", "assets", ["zone_id"])

    # 6. Incidents
    op.create_table(
        "incidents",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("ref", sa.String(50), unique=True, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("hazard_type", sa.String(50), nullable=False),
        sa.Column("zone_id", sa.String(50), sa.ForeignKey("zones.id"), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_incidents_ref", "incidents", ["ref"])
    op.create_index("ix_incidents_zone_id", "incidents", ["zone_id"])

    # 7. Alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("ref", sa.String(50), unique=True, nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("channels", sa.String(255), nullable=False),
        sa.Column("delivery_status", sa.String(50), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("acknowledged_by", sa.String(100), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("zone_id", sa.String(50), sa.ForeignKey("zones.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alerts_ref", "alerts", ["ref"])
    op.create_index("ix_alerts_zone_id", "alerts", ["zone_id"])

    # 8. Sensor Nodes
    op.create_table(
        "sensor_nodes",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("zone_id", sa.String(50), sa.ForeignKey("zones.id"), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("battery_pct", sa.Integer(), nullable=False),
        sa.Column("signal_pct", sa.Integer(), nullable=False),
        sa.Column("last_packet_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sensor_nodes_code", "sensor_nodes", ["code"])

    # 9. River Nodes
    op.create_table(
        "river_nodes",
        sa.Column("sensor_id", sa.String(50), sa.ForeignKey("sensor_nodes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("segment", sa.String(20), nullable=False),
        sa.Column("threshold_m", sa.Float(), nullable=False),
        sa.Column("travel_time_min", sa.Integer(), nullable=False),
        sa.Column("downstream_node_id", sa.String(50), nullable=True),
    )

    # 10. Sensor Observations
    op.create_table(
        "sensor_observations",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("sensor_id", sa.String(50), sa.ForeignKey("sensor_nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metric", sa.String(50), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("quality", sa.String(20), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sensor_obs_sensor_metric_time", "sensor_observations", ["sensor_id", "metric", "observed_at"])

    # 11. Data Sources
    op.create_table(
        "data_sources",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("reliability", sa.Float(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 12. Forecasts & Forecast Points
    op.create_table(
        "forecasts",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("zone_id", sa.String(50), sa.ForeignKey("zones.id"), nullable=False),
        sa.Column("hazard", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("horizon_hours", sa.Integer(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "forecast_points",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("forecast_id", sa.String(50), sa.ForeignKey("forecasts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("lower", sa.Integer(), nullable=False),
        sa.Column("upper", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
    )
    op.create_index("ix_forecast_points_forecast_id", "forecast_points", ["forecast_id"])

    # 13. Cascade Nodes & Edges
    op.create_table(
        "cascade_nodes",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("risk", sa.String(20), nullable=False),
    )
    op.create_table(
        "cascade_edges",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("from_node_id", sa.String(50), nullable=False),
        sa.Column("to_node_id", sa.String(50), nullable=False),
        sa.Column("likelihood", sa.Float(), nullable=False),
        sa.Column("lag_minutes", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("cascade_edges")
    op.drop_table("cascade_nodes")
    op.drop_table("forecast_points")
    op.drop_table("forecasts")
    op.drop_table("data_sources")
    op.drop_table("sensor_observations")
    op.drop_table("river_nodes")
    op.drop_table("sensor_nodes")
    op.drop_table("alerts")
    op.drop_table("incidents")
    op.drop_table("assets")
    op.drop_table("risk_drivers")
    op.drop_table("risk_scores")
    op.drop_table("zones")
    op.drop_table("cities")
