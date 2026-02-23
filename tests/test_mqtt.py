import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from pymvtreadmill.mqtt import TreadmillMQTT
from pymvtreadmill.client import TreadmillClient
import aiomqtt


@pytest.mark.asyncio
async def test_publish_discovery() -> None:
    # Mock TreadmillClient
    treadmill = MagicMock(spec=TreadmillClient)
    treadmill.client = MagicMock()
    treadmill.client.address = "AA:BB:CC:DD:EE:FF"

    # Mock aiomqtt.Client
    mqtt_client = MagicMock(spec=aiomqtt.Client)
    mqtt_client.publish = AsyncMock()

    mqtt = TreadmillMQTT(treadmill, mqtt_client)

    await mqtt.publish_discovery()

    # Check if publish was called 6 times (speed, inclination, distance, total_distance, last_run, connectivity)
    assert mqtt_client.publish.call_count == 6

    # Verify speed config
    # publish(topic, payload=..., retain=True) or publish(topic=..., ...)
    # Inspecting call args

    # Check 1st call (Speed)
    call_args = mqtt_client.publish.call_args_list[0]
    args, kwargs = call_args
    topic = args[0] if args else kwargs["topic"]
    payload = kwargs.get("payload")

    assert topic == "homeassistant/sensor/treadmill_aabbccddeeff_speed/config"
    config = json.loads(payload)
    assert config["name"] == "Speed"
    assert config["unique_id"] == "treadmill_aabbccddeeff_speed"
    assert config["device"]["identifiers"] == ["treadmill_aabbccddeeff"]


@pytest.mark.asyncio
async def test_publish_state() -> None:
    treadmill = MagicMock(spec=TreadmillClient)
    treadmill.client = MagicMock()
    treadmill.client.address = "AA:BB:CC:DD:EE:FF"
    treadmill.speed = 5.5
    treadmill.inclination = 2.0
    treadmill.distance = 100
    treadmill.total_distance = 500
    treadmill.last_run_distance = 400

    mqtt_client = MagicMock(spec=aiomqtt.Client)
    mqtt_client.publish = AsyncMock()

    mqtt = TreadmillMQTT(treadmill, mqtt_client)

    await mqtt.publish_state()

    call_args = mqtt_client.publish.call_args_list[0]
    args, kwargs = call_args
    topic = args[0] if args else kwargs["topic"]
    payload = kwargs.get("payload")

    assert topic == "homeassistant/sensor/treadmill_aabbccddeeff/state"
    state = json.loads(payload)
    assert state["speed"] == 5.5
    assert state["inclination"] == 2.0
    assert state["distance"] == 100
    assert state["total_distance"] == 500
    assert state["last_run_distance"] == 400


@pytest.mark.asyncio
async def test_device_id_sanitization() -> None:
    treadmill = MagicMock(spec=TreadmillClient)
    treadmill.client = MagicMock()
    treadmill.client.address = "11-22-33-44-55-66"  # MacOS style

    mqtt_client = MagicMock(spec=aiomqtt.Client)

    mqtt = TreadmillMQTT(treadmill, mqtt_client)
    assert mqtt.device_id == "112233445566"
