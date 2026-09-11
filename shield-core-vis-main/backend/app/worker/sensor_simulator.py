"""Configurable IoT sensor telemetry simulator for ClimateShield development and live demonstration."""

import time
import uuid
import json
import argparse
from datetime import datetime, timezone
import httpx
import paho.mqtt.client as mqtt

from app.core.config import settings
from app.core.logging import logger


class SensorSimulator:
    def __init__(self, api_base_url: str = "http://127.0.0.1:8000/api/v1"):
        self.api_base_url = api_base_url

    def generate_packet(
        self,
        node_code: str,
        water_level_m: float,
        rainfall_mm: float = 0.0,
        temperature_c: float = 28.5,
        battery_pct: int = 94,
        signal_pct: int = 98,
        lat: float = 17.750,
        lng: float = 83.340,
    ) -> dict:
        return {
            "message_id": str(uuid.uuid4()),
            "node_code": node_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "water_level_m": water_level_m,
            "rainfall_mm": rainfall_mm,
            "temperature_c": temperature_c,
            "latitude": lat,
            "longitude": lng,
            "battery_percent": battery_pct,
            "signal_percent": signal_pct,
            "is_simulated": True,
        }

    def dispatch_http(self, payload: dict) -> dict:
        url = f"{self.api_base_url}/telemetry/ingest"
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()

    def run_rapid_rise_scenario(self, interval_seconds: float = 2.0):
        """Demonstrates rapid water level surge on RN-01 (Upstream) approaching 4.50m threshold."""
        logger.info("[SIMULATOR] === STARTING RAPID_RISE SCENARIO (UPSTREAM RN-01) ===")
        levels = [4.10, 4.18, 4.28, 4.36, 4.44, 4.49]
        rainfalls = [12.0, 18.5, 24.0, 32.0, 45.0, 52.0]

        for idx, (wl, rf) in enumerate(zip(levels, rainfalls)):
            pkt = self.generate_packet(
                node_code="RN-01",
                water_level_m=wl,
                rainfall_mm=rf,
                temperature_c=27.8,
                battery_pct=92,
                signal_pct=95,
                lat=17.750,
                lng=83.340,
            )
            try:
                res = self.dispatch_http(pkt)
                logger.info(
                    f"[RAPID_RISE Step {idx+1}/{len(levels)}] Level: {wl}m | Rise Rate: {res.get('rate_of_rise_m_per_hour')}m/h | "
                    f"Est Time to Threshold: {res.get('time_to_threshold_minutes')}min"
                )
            except Exception as e:
                logger.error(f"[SIMULATOR] Error sending packet: {e}")

            if idx < len(levels) - 1:
                time.sleep(interval_seconds)

        logger.info("[SIMULATOR] === RAPID_RISE SCENARIO COMPLETED ===")

    def run_sensor_degraded_scenario(self):
        """Demonstrates degraded sensor due to low battery and weak LoRa signal."""
        logger.info("[SIMULATOR] === STARTING SENSOR_DEGRADED SCENARIO (RN-02) ===")
        pkt = self.generate_packet(
            node_code="RN-02",
            water_level_m=2.85,
            rainfall_mm=4.0,
            temperature_c=29.1,
            battery_pct=14,  # Critical low battery -> DEGRADED
            signal_pct=18,   # Weak signal
            lat=17.735,
            lng=83.330,
        )
        res = self.dispatch_http(pkt)
        logger.info(f"[SENSOR_DEGRADED] Result: status={res.get('status')} quality={res.get('quality')}")

    def run_sensor_offline_scenario(self):
        """Simulates sensor silence by stopping telemetry from RN-03."""
        logger.info("[SIMULATOR] === SENSOR_OFFLINE DEMO SCENARIO ===")
        logger.info("[SIMULATOR] Halting telemetry for RN-03 (Estuary Outfall South). Health monitor will flag OFFLINE upon timeout.")


def main():
    parser = argparse.ArgumentParser(description="ClimateShield IoT Sensor Simulator")
    parser.add_argument(
        "--scenario",
        choices=["rapid_rise", "degraded", "offline", "normal"],
        default="rapid_rise",
        help="Demo scenario to execute",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Interval between steps in seconds",
    )
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000/api/v1",
        help="FastAPI base URL",
    )
    args = parser.parse_args()

    sim = SensorSimulator(api_base_url=args.api_url)

    if args.scenario == "rapid_rise":
        sim.run_rapid_rise_scenario(interval_seconds=args.interval)
    elif args.scenario == "degraded":
        sim.run_sensor_degraded_scenario()
    elif args.scenario == "offline":
        sim.run_sensor_offline_scenario()
    else:
        logger.info("Executing default single normal packet...")
        pkt = sim.generate_packet("RN-01", water_level_m=4.12, rainfall_mm=6.0)
        print(sim.dispatch_http(pkt))


if __name__ == "__main__":
    main()
