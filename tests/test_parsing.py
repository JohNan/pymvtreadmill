
from unittest.mock import MagicMock
import pytest
from bleak.backends.characteristic import BleakGATTCharacteristic
from pymvtreadmill.client import TreadmillClient

@pytest.mark.asyncio
async def test_handle_data_speed_only() -> None:
    # Mocking callbacks
    callback = MagicMock()
    async def on_speed_change(speed: float) -> None:
        callback(speed)

    client = TreadmillClient(on_speed_change=on_speed_change)

    # Speed: 2.5 km/h -> 250 -> 0x00FA
    # Packet: 00 00 00 FA (Flags=0, Speed=2.5)
    # Note: data[2:4] = 00 FA -> 250 -> 2.5
    data = bytes.fromhex("00 00 00 FA")

    mock_char = MagicMock(spec=BleakGATTCharacteristic)
    await client._handle_data(mock_char, bytearray(data))

    assert client.speed == 2.5
    callback.assert_called_with(2.5)

@pytest.mark.asyncio
async def test_handle_data_with_inclination() -> None:
    # Mocking callbacks
    speed_cb = MagicMock()
    inclination_cb = MagicMock()

    async def on_speed_change(speed: float) -> None:
        speed_cb(speed)
    async def on_inclination_change(inclination: float) -> None:
        inclination_cb(inclination)

    client = TreadmillClient(
        on_speed_change=on_speed_change,
        on_inclination_change=on_inclination_change
    )

    # Flags: 00 08 (Bit 3 set -> Inclination present) (Big Endian)
    # Speed: 2.5 km/h -> 00 FA
    # Inclination: 1.0 % -> 10 -> 00 0A
    # Ramp Angle: 00 00 (dummy)
    # Packet: 00 08 00 FA 00 0A 00 00
    data = bytes.fromhex("00 08 00 FA 00 0A 00 00")

    mock_char = MagicMock(spec=BleakGATTCharacteristic)
    await client._handle_data(mock_char, bytearray(data))

    assert client.speed == 2.5
    assert client.inclination == 1.0

    speed_cb.assert_called_with(2.5)
    inclination_cb.assert_called_with(1.0)

@pytest.mark.asyncio
async def test_handle_data_with_distance() -> None:
    # Mocking callbacks
    dist_cb = MagicMock()

    async def on_distance_change(dist: int) -> None:
        dist_cb(dist)

    client = TreadmillClient(on_distance_change=on_distance_change)

    # Flags: 00 04 (Bit 2 set -> Distance present)
    # Speed: 2.5 -> 00 FA
    # Distance: 1234 meters -> 00 04 D2
    # Packet: 00 04 00 FA 00 04 D2
    data = bytes.fromhex("00 04 00 FA 00 04 D2")

    mock_char = MagicMock(spec=BleakGATTCharacteristic)
    await client._handle_data(mock_char, bytearray(data))

    assert client.distance == 1234
    dist_cb.assert_called_with(1234)
