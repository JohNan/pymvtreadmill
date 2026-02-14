import asyncio
import logging
import struct
from enum import StrEnum
from typing import Self

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

# --- Constants ---

class TreadmillUUID(StrEnum):
    """Bluetooth UUIDs for Mobvoi and Horizon Treadmills."""
    SERVICE = "0000ffb0-0000-1000-8000-00805f9b34fb"
    READ = "0000ffb2-0000-1000-8000-00805f9b34fb"
    WRITE = "0000ffb1-0000-1000-8000-00805f9b34fb"

# --- Exceptions ---

class TreadmillError(Exception):
    """Base exception for pymvtreadmill."""
    pass

class TreadmillConnectionError(TreadmillError):
    """Raised when connection fails or is lost."""
    pass

# --- Client ---

# Modern Type Alias (Python 3.12+)
type TreadmillData = bytearray | bytes

class TreadmillClient:
    def __init__(self, name_filter: str = "Mobvoi") -> None:
        self.client: BleakClient | None = None
        self.speed: float = 0.0
        self.is_running: bool = False
        self._name_filter = name_filter
        # Configure logging to standard out for this script
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
        self._logger = logging.getLogger("pymvtreadmill")

    async def connect(self, address: str | None = None) -> Self:
        """Connects to the treadmill. Returns self for chaining."""
        device: BLEDevice | None = None
        
        if address:
            device = await BleakScanner.find_device_by_address(address)
        else:
            self._logger.info(f"Scanning for devices containing '{self._name_filter}'...")
            device = await BleakScanner.find_device_by_filter(
                lambda d, _: d.name and (self._name_filter in d.name or "Home Treadmill" in d.name)
            )

        if not device:
            raise TreadmillConnectionError(f"No device found matching '{self._name_filter}'.")

        self.client = BleakClient(device, disconnected_callback=self._on_disconnect)
        await self.client.connect()
        self._logger.info(f"Connected to {device.name} ({device.address})")
        
        # Start listening
        await self.client.start_notify(TreadmillUUID.READ, self._handle_data)
        return self

    async def disconnect(self) -> None:
        """Disconnects from the BLE device."""
        if self.client:
            await self.client.disconnect()

    async def set_speed(self, speed_kmh: float) -> None:
        """Sets the treadmill speed in km/h."""
        if not self.client or not self.client.is_connected:
            raise TreadmillConnectionError("Not connected.")

        # Mobvoi uses 0.01 resolution (e.g. 250 = 2.5 km/h)
        val = int(speed_kmh * 100)
        
        # Structure: [0x02, High, Low, Spacer]
        # Using struct for cleaner packing: 'B' = unsigned char, 'H' = unsigned short (Big Endian)
        payload = struct.pack(">BHB", 0x02, val, 0x00)
        
        await self.client
 
