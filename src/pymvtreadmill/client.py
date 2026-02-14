import logging
import struct
from types import TracebackType
from typing import Self

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic

from .const import TreadmillUUID
from .exceptions import TreadmillConnectionError

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
                lambda d, _: d.name is not None
                and (self._name_filter in d.name or "Home Treadmill" in d.name)
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

        await self.client.write_gatt_char(TreadmillUUID.WRITE, payload)

    def _handle_data(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Parses notification data from the treadmill."""
        # AGENTS.md: Speed resolution 0.01 km/h (Bytes 3-4, Big Endian).
        if len(data) < 4:
            return

        try:
            # Bytes 3-4 (1-based) -> index 2 and 3 (0-based)
            raw_speed = struct.unpack(">H", data[2:4])[0]
            self.speed = raw_speed / 100.0
            # Assuming if we get data, it might mean it's running or at least active
            # self.is_running = self.speed > 0

            # self._logger.debug(f"Received data: {data.hex()} -> Speed: {self.speed} km/h")
        except Exception as e:
            self._logger.error(f"Failed to parse data {data.hex()}: {e}")

    def _on_disconnect(self, client: BleakClient) -> None:
        """Callback when the client disconnects."""
        self._logger.warning(f"Disconnected from {client.address}")
        self.is_running = False

    async def __aenter__(self) -> Self:
        return await self.connect()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.disconnect()
