import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pymvtreadmill.client import TreadmillClient
from bleak.backends.device import BLEDevice

@pytest.mark.asyncio
async def test_find_device_by_filter_case_insensitive():
    with patch("pymvtreadmill.client.BleakScanner.find_device_by_filter", new_callable=AsyncMock) as mock_find:

        # Setup a mock device to be returned so connect doesn't raise exception immediately
        mock_device = MagicMock(spec=BLEDevice)
        mock_device.name = "Mobvoi Treadmill"
        mock_device.address = "00:00:00:00:00:00"
        mock_find.return_value = mock_device

        # Setup BleakClient mock to avoid actual connection attempts
        with patch("pymvtreadmill.client.BleakClient") as MockBleakClient:
             # Configure the instance returned by the constructor
             mock_client_instance = MockBleakClient.return_value
             mock_client_instance.connect = AsyncMock()
             mock_client_instance.start_notify = AsyncMock()

             client = TreadmillClient(name_filter="Mobvoi")
             await client.connect()

        # Get the filter function passed to find_device_by_filter
        # The call is: await BleakScanner.find_device_by_filter(lambda ...)
        args, _ = mock_find.call_args
        filter_func = args[0]

        # Test cases that should match (Case Insensitive)

        # 1. Exact match (Should pass)
        d1 = MagicMock(spec=BLEDevice)
        d1.name = "Mobvoi Treadmill"
        assert filter_func(d1, None) is True, "Exact match 'Mobvoi Treadmill' failed"

        # 2. Lowercase match (Should pass, but currently fails)
        d2 = MagicMock(spec=BLEDevice)
        d2.name = "mobvoi treadmill"
        assert filter_func(d2, None) is True, "Lowercase match 'mobvoi treadmill' failed"

        # 3. Uppercase match (Should pass, but currently fails)
        d3 = MagicMock(spec=BLEDevice)
        d3.name = "MOBVOI TREADMILL"
        assert filter_func(d3, None) is True, "Uppercase match 'MOBVOI TREADMILL' failed"

        # 4. Home Treadmill match (Case Insensitive)
        d4 = MagicMock(spec=BLEDevice)
        d4.name = "home treadmill"
        assert filter_func(d4, None) is True, "Lowercase match 'home treadmill' failed"

        # 5. No match
        d5 = MagicMock(spec=BLEDevice)
        d5.name = "Other Device"
        assert filter_func(d5, None) is False, "Unrelated device matched"

        # 6. None name
        d6 = MagicMock(spec=BLEDevice)
        d6.name = None
        assert filter_func(d6, None) is False, "None name matched"
