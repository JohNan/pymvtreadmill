import pytest
from unittest.mock import MagicMock
from pymvtreadmill.client import TreadmillClient
from bleak.backends.characteristic import BleakGATTCharacteristic

@pytest.mark.asyncio
async def test_accumulators_initialization() -> None:
    client = TreadmillClient()
    assert client.total_distance == 0
    assert client.last_run_distance is None

@pytest.mark.asyncio
async def test_total_distance_increment() -> None:
    client = TreadmillClient()
    mock_char = MagicMock(spec=BleakGATTCharacteristic)

    # 1. Packet: Speed 0, Distance 100
    # Hex: 00 04 00 00 00 00 64 (Flags=0004 -> Distance Present, Speed=0, Dist=100)
    data1 = bytes.fromhex("00 04 00 00 00 00 64")
    await client._handle_data(mock_char, bytearray(data1))

    assert client.distance == 100
    assert client.total_distance == 100

    # 2. Packet: Distance 105 (+5)
    # Hex: 00 04 00 00 00 00 69 (105)
    data2 = bytes.fromhex("00 04 00 00 00 00 69")
    await client._handle_data(mock_char, bytearray(data2))

    assert client.distance == 105
    assert client.total_distance == 105

@pytest.mark.asyncio
async def test_last_run_distance_reset() -> None:
    client = TreadmillClient()
    mock_char = MagicMock(spec=BleakGATTCharacteristic)

    # 1. Run 1: Distance 100
    data1 = bytes.fromhex("00 04 00 00 00 00 64") # 100
    await client._handle_data(mock_char, bytearray(data1))
    assert client.distance == 100
    assert client.total_distance == 100
    assert client.last_run_distance is None

    # 2. Reset (New Run or Stop): Distance 0
    data2 = bytes.fromhex("00 04 00 00 00 00 00") # 0
    await client._handle_data(mock_char, bytearray(data2))

    assert client.distance == 0
    assert client.last_run_distance == 100
    # Total distance shouldn't change if delta is negative (reset) but next packet starts from 0?
    # Wait, my logic plan: if new < old, reset detected. Delta = new_distance (0). Total += 0.
    assert client.total_distance == 100

    # 3. Run 2: Distance 10
    data3 = bytes.fromhex("00 04 00 00 00 00 0A") # 10
    await client._handle_data(mock_char, bytearray(data3))

    assert client.distance == 10
    # Total distance should increase by 10
    assert client.total_distance == 110
    # Last run distance persists
    assert client.last_run_distance == 100

@pytest.mark.asyncio
async def test_last_run_distance_ignore_zero_reset() -> None:
    client = TreadmillClient()
    mock_char = MagicMock(spec=BleakGATTCharacteristic)

    # 1. Run 1: Distance 50
    data1 = bytes.fromhex("00 04 00 00 00 00 32") # 50
    await client._handle_data(mock_char, bytearray(data1))

    # 2. Reset to 0
    data2 = bytes.fromhex("00 04 00 00 00 00 00")
    await client._handle_data(mock_char, bytearray(data2))
    assert client.last_run_distance == 50

    # 3. Stay at 0
    data3 = bytes.fromhex("00 04 00 00 00 00 00")
    await client._handle_data(mock_char, bytearray(data3))

    # Should NOT update to 0
    assert client.last_run_distance == 50
