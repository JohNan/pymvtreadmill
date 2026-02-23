import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pymvtreadmill.client import TreadmillClient
from bleak.backends.device import BLEDevice
from pymvtreadmill.exceptions import TreadmillConnectionError


@pytest.mark.asyncio
async def test_connect_with_ble_device() -> None:
    """Test connecting with a BLEDevice object."""
    mock_device = MagicMock(spec=BLEDevice)
    mock_device.name = "Test Treadmill"
    mock_device.address = "AA:BB:CC:DD:EE:FF"

    client = TreadmillClient()

    with patch("pymvtreadmill.client.BleakClient") as MockBleakClient:
        mock_instance = MockBleakClient.return_value
        mock_instance.connect = AsyncMock()
        mock_instance.start_notify = AsyncMock()
        mock_instance.services = MagicMock()
        # Mock services to return empty or specific service to avoid errors
        mock_instance.services.get_service.return_value = None

        await client.connect(mock_device)

        # Check that BleakClient was initialized with the passed device
        MockBleakClient.assert_called_once()
        args, _ = MockBleakClient.call_args
        assert args[0] == mock_device


@pytest.mark.asyncio
async def test_connect_with_address() -> None:
    """Test connecting with a string address."""
    address = "AA:BB:CC:DD:EE:FF"
    mock_device = MagicMock(spec=BLEDevice)
    mock_device.name = "Test Treadmill"
    mock_device.address = address

    client = TreadmillClient()

    with patch(
        "pymvtreadmill.client.BleakScanner.find_device_by_address", new_callable=AsyncMock
    ) as mock_find:
        mock_find.return_value = mock_device

        with patch("pymvtreadmill.client.BleakClient") as MockBleakClient:
            mock_instance = MockBleakClient.return_value
            mock_instance.connect = AsyncMock()
            mock_instance.start_notify = AsyncMock()
            mock_instance.services = MagicMock()
            mock_instance.services.get_service.return_value = None

            await client.connect(address)

            # Check that scanner was called
            mock_find.assert_called_once_with(address)
            # Check that BleakClient was initialized with the found device
            MockBleakClient.assert_called_once()
            args, _ = MockBleakClient.call_args
            assert args[0] == mock_device


@pytest.mark.asyncio
async def test_connect_with_address_not_found() -> None:
    """Test connecting with a string address that is not found."""
    address = "AA:BB:CC:DD:EE:FF"
    client = TreadmillClient()

    with patch(
        "pymvtreadmill.client.BleakScanner.find_device_by_address", new_callable=AsyncMock
    ) as mock_find:
        mock_find.return_value = None

        with pytest.raises(
            TreadmillConnectionError, match=f"Device with address {address} not found"
        ):
            await client.connect(address)


@pytest.mark.asyncio
async def test_properties_read_only() -> None:
    """Test that properties are read-only."""
    client = TreadmillClient()

    # Verify initial values via properties
    assert client.speed == 0.0
    assert client.inclination is None
    assert client.distance is None
    assert client.total_distance == 0

    # Try to set properties
    with pytest.raises(AttributeError):
        client.speed = 10.0  # type: ignore

    with pytest.raises(AttributeError):
        client.inclination = 5.0  # type: ignore

    with pytest.raises(AttributeError):
        client.distance = 100  # type: ignore


@pytest.mark.asyncio
async def test_properties_values_update() -> None:
    """Test that properties reflect internal state changes."""
    client = TreadmillClient()

    # Simulate internal updates (normally done by _handle_data)
    client._speed = 5.5
    client._inclination = 2.0
    client._distance = 150
    client._total_distance = 1000
    client._is_running = True

    assert client.speed == 5.5
    assert client.inclination == 2.0
    assert client.distance == 150
    assert client.total_distance == 1000
    assert client.is_running is True
