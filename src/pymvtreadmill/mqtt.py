import json
import logging

import aiomqtt
from pymvtreadmill.client import TreadmillClient

logger = logging.getLogger("pymvtreadmill.mqtt")


class TreadmillMQTT:
    def __init__(
        self,
        treadmill_client: TreadmillClient,
        mqtt_client: aiomqtt.Client,
        discovery_prefix: str = "homeassistant",
    ) -> None:
        self.treadmill = treadmill_client
        self.mqtt = mqtt_client
        self.discovery_prefix = discovery_prefix
        self._device_id: str | None = None

    @property
    def device_id(self) -> str:
        if self._device_id:
            return self._device_id

        if self.treadmill.client and self.treadmill.client.address:
            # Sanitize address for use in ID.
            # On macOS, UUIDs might contain dashes. On Linux, MACs contain colons.
            self._device_id = (
                self.treadmill.client.address.replace(":", "").replace("-", "").lower()
            )
            return self._device_id

        return "unknown"

    async def publish_discovery(self) -> None:
        """Publishes Home Assistant discovery configuration."""
        if self.device_id == "unknown":
            logger.warning("Cannot publish discovery: Device ID unknown (not connected?)")
            return

        device_info = {
            "identifiers": [f"treadmill_{self.device_id}"],
            "name": "Mobvoi Treadmill",
            "model": "Mobvoi",
            "manufacturer": "Mobvoi",
        }

        # Common attributes
        base_topic = f"{self.discovery_prefix}/sensor/treadmill_{self.device_id}"
        state_topic = f"{base_topic}/state"
        availability_topic = f"{base_topic}/status"

        # Speed Sensor
        speed_config = {
            "name": "Speed",
            "unique_id": f"treadmill_{self.device_id}_speed",
            "state_topic": state_topic,
            "availability_topic": availability_topic,
            "value_template": "{{ value_json.speed }}",
            "unit_of_measurement": "km/h",
            "device_class": "speed",
            "device": device_info,
        }
        await self.mqtt.publish(
            f"{self.discovery_prefix}/sensor/treadmill_{self.device_id}_speed/config",
            payload=json.dumps(speed_config),
            retain=True,
        )

        # Inclination Sensor
        inclination_config = {
            "name": "Inclination",
            "unique_id": f"treadmill_{self.device_id}_inclination",
            "state_topic": state_topic,
            "availability_topic": availability_topic,
            "value_template": "{{ value_json.inclination }}",
            "unit_of_measurement": "%",
            "icon": "mdi:elevation-rise",
            "device": device_info,
        }
        await self.mqtt.publish(
            f"{self.discovery_prefix}/sensor/treadmill_{self.device_id}_inclination/config",
            payload=json.dumps(inclination_config),
            retain=True,
        )

        # Distance Sensor
        distance_config = {
            "name": "Distance",
            "unique_id": f"treadmill_{self.device_id}_distance",
            "state_topic": state_topic,
            "availability_topic": availability_topic,
            "value_template": "{{ value_json.distance }}",
            "unit_of_measurement": "m",
            "device_class": "distance",
            "state_class": "total_increasing",
            "device": device_info,
        }
        await self.mqtt.publish(
            f"{self.discovery_prefix}/sensor/treadmill_{self.device_id}_distance/config",
            payload=json.dumps(distance_config),
            retain=True,
        )

        # Connectivity Binary Sensor
        connectivity_config = {
            "name": "Connectivity",
            "unique_id": f"treadmill_{self.device_id}_connectivity",
            "state_topic": availability_topic,
            "payload_on": "online",
            "payload_off": "offline",
            "device_class": "connectivity",
            "device": device_info,
        }
        await self.mqtt.publish(
            f"{self.discovery_prefix}/binary_sensor/treadmill_{self.device_id}_connectivity/config",
            payload=json.dumps(connectivity_config),
            retain=True,
        )

        logger.info(f"Published discovery configuration for device {self.device_id}")

    async def publish_state(self) -> None:
        """Publishes the current state of the treadmill sensors."""
        if self.device_id == "unknown":
            return

        payload = {
            "speed": self.treadmill.speed,
            "inclination": self.treadmill.inclination
            if self.treadmill.inclination is not None
            else 0.0,
            "distance": self.treadmill.distance if self.treadmill.distance is not None else 0,
        }
        topic = f"{self.discovery_prefix}/sensor/treadmill_{self.device_id}/state"
        await self.mqtt.publish(topic, payload=json.dumps(payload))
        logger.debug(f"Published state: {payload}")

    async def publish_availability(self, available: bool) -> None:
        """Publishes availability status."""
        if self.device_id == "unknown":
            return

        topic = f"{self.discovery_prefix}/sensor/treadmill_{self.device_id}/status"
        payload = "online" if available else "offline"
        await self.mqtt.publish(topic, payload=payload, retain=True)
        logger.info(f"Published availability: {payload}")
