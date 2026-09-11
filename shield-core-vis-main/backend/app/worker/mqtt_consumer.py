"""Background MQTT subscriber worker for climate and IoT sensor telemetry."""

import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

from app.core.config import settings
from app.core.logging import logger
from app.core.database import SessionLocal
from app.schemas.telemetry import TelemetryPayload
from app.services.telemetry_service import TelemetryService


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info(f"[MQTT] Connected successfully to broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
        topic_telemetry = f"{settings.MQTT_TOPIC_PREFIX}/+/+/telemetry"
        topic_status = f"{settings.MQTT_TOPIC_PREFIX}/+/+/status"
        client.subscribe(topic_telemetry, qos=1)
        client.subscribe(topic_status, qos=1)
        logger.info(f"[MQTT] Subscribed to topics: {topic_telemetry}, {topic_status} with QoS 1")
    else:
        logger.error(f"[MQTT] Connection failed with return code {rc}")


def on_message(client, userdata, msg):
    logger.info(f"[MQTT] Inbound packet on topic '{msg.topic}' (QoS {msg.qos})")
    db = SessionLocal()
    try:
        payload_data = json.loads(msg.payload.decode("utf-8"))
        telemetry = TelemetryPayload(**payload_data)

        service = TelemetryService(db)
        result = service.process_telemetry(telemetry)
        logger.info(
            f"[MQTT INGESTION] Result: status={result.status} msg_id={result.message_id} "
            f"node={result.node_code} rise_rate={result.rate_of_rise_m_per_hour}m/h "
            f"time_to_thresh={result.time_to_threshold_minutes}min quality={result.quality}"
        )
    except json.JSONDecodeError as e:
        logger.error(f"[MQTT MALFORMED] JSON parse error: {e}")
    except Exception as e:
        logger.error(f"[MQTT ERROR] Ingestion failure for topic {msg.topic}: {e}", exc_info=True)
    finally:
        db.close()


def on_disconnect(client, userdata, rc, properties=None):
    logger.warning(f"[MQTT] Disconnected from broker (rc={rc}). Will attempt reconnection...")


def run_mqtt_worker():
    client = mqtt.Client(
        client_id=settings.MQTT_CLIENT_ID,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )

    if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    backoff = 2
    max_backoff = 60

    logger.info(f"[MQTT WORKER] Starting MQTT subscriber worker on {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}...")

    while True:
        try:
            client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
            client.loop_forever()
        except KeyboardInterrupt:
            logger.info("[MQTT WORKER] Stopped by user")
            break
        except Exception as e:
            logger.warning(
                f"[MQTT WORKER] Broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT} unavailable ({e}). "
                f"Retrying in {backoff}s..."
            )
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)


if __name__ == "__main__":
    run_mqtt_worker()
