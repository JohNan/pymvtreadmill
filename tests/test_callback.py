import asyncio
import pytest
from unittest.mock import Mock
from bleak.backends.characteristic import BleakGATTCharacteristic

from pymvtreadmill.client import TreadmillClient


@pytest.mark.asyncio
async def test_callback_invoked() -> None:
    # Setup
    received_speed: float | None = None
    event = asyncio.Event()

    async def my_callback(speed: float) -> None:
        nonlocal received_speed
        received_speed = speed
        event.set()

    client = TreadmillClient(on_speed_change=my_callback)

    # Mock data
    # 2.5 km/h -> 250 -> 0x00FA
    # Data format: [?, ?, High, Low, ...]
    # Code uses: raw_speed = struct.unpack(">H", data[2:4])[0]
    # So index 2 and 3 are the speed bytes.
    payload = bytearray([0x00, 0x00, 0x00, 0xFA])

    mock_char = Mock(spec=BleakGATTCharacteristic)

    # Trigger handle_data
    await client._handle_data(mock_char, payload)

    assert received_speed == 2.50
    assert client.speed == 2.50
    assert event.is_set()


@pytest.mark.asyncio
async def test_callback_not_set() -> None:
    # Ensure no error if callback is None
    client = TreadmillClient()
    payload = bytearray([0x00, 0x00, 0x00, 0xFA])
    mock_char = Mock(spec=BleakGATTCharacteristic)

    await client._handle_data(mock_char, payload)

    assert client.speed == 2.50


@pytest.mark.asyncio
async def test_raw_data_callback() -> None:
    # Setup
    received_data: bytes | None = None
    event = asyncio.Event()

    async def my_raw_callback(data: bytes) -> None:
        nonlocal received_data
        received_data = data
        event.set()

    client = TreadmillClient(on_raw_data=my_raw_callback)

    # Mock data: Simulating a longer packet (e.g. 10 bytes)
    # [0x00, 0x00, 0x00, 0xFA] (Speed 2.5) + extra bytes
    payload = bytearray([0x00, 0x00, 0x00, 0xFA, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06])

    mock_char = Mock(spec=BleakGATTCharacteristic)

    # Trigger handle_data
    await client._handle_data(mock_char, payload)

    assert received_data == bytes(payload)
    assert client.last_raw_data == bytes(payload)
    assert client.speed == 2.50
    assert event.is_set()
