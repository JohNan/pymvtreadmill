import logging
import struct
from collections.abc import Awaitable, Callable
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
    def __init__(
        self,
        name_filter: str = "Mobvoi",
        on_speed_change: Callable[[float], Awaitable[None]] | None = None,
        on_raw_data: Callable[[bytes], Awaitable[None]] | None = None,
        on_inclination_change: Callable[[float], Awaitable[None]] | None = None,
        on_distance_change: Callable[[int], Awaitable[None]] | None = None,
    ) -> None:
        self.client: BleakClient | None = None
        self.speed: float = 0.0
        self.inclination: float | None = None
        self.distance: int | None = None
        self.total_distance: int = 0
        self.last_run_distance: int | None = None
        self.is_running: bool = False
        self._last_raw_data: bytes | None = None
        self._name_filter = name_filter
        self._on_speed_change = on_speed_change
        self._on_raw_data = on_raw_data
        self._on_inclination_change = on_inclination_change
        self._on_distance_change = on_distance_change

        # Protocol detection
        self._protocol: str | None = None  # "ftms" or "proprietary"
        self._read_char: str | None = None
        self._write_char: str | None = None

        # Configure logging to standard out for this script
        self._logger = logging.getLogger("pymvtreadmill")

    @property
    def last_raw_data(self) -> bytes | None:
        """Returns the last received raw data packet."""
        return self._last_raw_data

    async def connect(self, address: str | None = None) -> Self:
        """Connects to the treadmill. Returns self for chaining."""
        device: BLEDevice | None = None

        if address:
            device = await BleakScanner.find_device_by_address(address)
        else:
            self._logger.info(f"Scanning for devices containing '{self._name_filter}'...")
            device = await BleakScanner.find_device_by_filter(
                lambda d, _: d.name is not None
                and (
                    self._name_filter.lower() in d.name.lower()
                    or "home treadmill" in d.name.lower()
                )
            )

        if not device:
            raise TreadmillConnectionError(f"No device found matching '{self._name_filter}'.")

        self.client = BleakClient(device, disconnected_callback=self._on_disconnect)
        await self.client.connect()
        self._logger.info(f"Connected to {device.name} ({device.address})")

        # Log all services and characteristics for discovery
        self._logger.info("Discovered Services:")
        for service in self.client.services:
            self._logger.info(f"Service: {service.uuid} ({service.description})")
            for char in service.characteristics:
                self._logger.info(
                    f"  - Char: {char.uuid} (Props: {char.properties}) - {char.description}"
                )

        # Determine protocol based on available services
        services = self.client.services
        if services.get_service(TreadmillUUID.FTMS_SERVICE):
            self._logger.info("Detected FTMS Service (Standard).")
            self._protocol = "ftms"
            self._read_char = TreadmillUUID.FTMS_DATA
            self._write_char = TreadmillUUID.FTMS_CONTROL
        elif services.get_service(TreadmillUUID.SERVICE):
            self._logger.info("Detected Proprietary Service (Mobvoi).")
            self._protocol = "proprietary"
            self._read_char = TreadmillUUID.READ
            self._write_char = TreadmillUUID.WRITE
        else:
            self._logger.warning("No known service found, defaulting to proprietary.")
            self._protocol = "proprietary"
            self._read_char = TreadmillUUID.READ
            self._write_char = TreadmillUUID.WRITE

        # Start listening
        await self.client.start_notify(self._read_char, self._handle_data)
        return self

    async def disconnect(self) -> None:
        """Disconnects from the BLE device."""
        if self.client:
            await self.client.disconnect()

    async def set_speed(self, speed_kmh: float) -> None:
        """Sets the treadmill speed in km/h."""
        if not self.client or not self.client.is_connected:
            raise TreadmillConnectionError("Not connected.")

        if not self._write_char:
            raise TreadmillConnectionError("Write characteristic not configured.")

        # Mobvoi uses 0.01 resolution (e.g. 250 = 2.5 km/h)
        val = int(speed_kmh * 100)

        if self._protocol == "ftms":
            # FTMS: Op Code 0x02 (Set Target Speed), Speed (uint16, Little Endian)
            # Packet: [0x02, Low, High]
            payload = struct.pack("<BH", 0x02, val)
        else:
            # Proprietary: [0x02, High, Low, Spacer]
            # Big Endian
            payload = struct.pack(">BHB", 0x02, val, 0x00)

        await self.client.write_gatt_char(self._write_char, payload)

    async def _handle_data(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Parses notification data from the treadmill."""
        self._last_raw_data = bytes(data)
        if self._on_raw_data:
            await self._on_raw_data(self._last_raw_data)

        # AGENTS.md: Speed resolution 0.01 km/h (Bytes 3-4).
        if len(data) < 4:
            return

        try:
            is_ftms = self._protocol == "ftms"
            endian = "<" if is_ftms else ">"

            # Parse Flags (Bytes 1-2)
            flags = struct.unpack(f"{endian}H", data[0:2])[0]

            # Bit 1: Average Speed Present
            avg_speed_present = bool(flags & 0x0002)
            # Bit 2: Total Distance Present
            total_distance_present = bool(flags & 0x0004)
            # Bit 3: Inclination and Ramp Angle Setting Present
            inclination_present = bool(flags & 0x0008)

            # Speed is always present at bytes 3-4 (index 2-3)
            # Bytes 3-4 (1-based) -> index 2 and 3 (0-based)
            raw_speed = struct.unpack(f"{endian}H", data[2:4])[0]
            self.speed = raw_speed / 100.0
            # Assuming if we get data, it might mean it's running or at least active
            # self.is_running = self.speed > 0

            if self._on_speed_change:
                await self._on_speed_change(self.speed)

            index = 4

            # Skip Average Speed if present (2 bytes)
            if avg_speed_present:
                index += 2

            # Parse Total Distance if present (3 bytes)
            if total_distance_present and len(data) >= index + 3:
                # 3 bytes
                dist_bytes = data[index : index + 3]
                if is_ftms:
                    # Little Endian 24-bit
                    new_distance = dist_bytes[0] | (dist_bytes[1] << 8) | (dist_bytes[2] << 16)
                else:
                    # Big Endian 24-bit
                    new_distance = (dist_bytes[0] << 16) | (dist_bytes[1] << 8) | dist_bytes[2]

                if self.distance is not None:
                    if new_distance >= self.distance:
                        # Normal increment
                        self.total_distance += new_distance - self.distance
                    else:
                        # Reset detected (new_distance < self.distance)
                        # Save the last run distance if it was non-zero
                        if self.distance > 0:
                            self.last_run_distance = self.distance
                        # Accumulate the new distance (assuming reset to 0 then up to new_distance)
                        self.total_distance += new_distance
                else:
                    # First packet received
                    self.total_distance = new_distance

                self.distance = new_distance
                index += 3
                if self._on_distance_change:
                    await self._on_distance_change(self.distance)

            # Parse Inclination if present (2 bytes) + Ramp Angle (2 bytes)
            if inclination_present and len(data) >= index + 4:
                # Inclination is signed 16-bit, 0.1% resolution
                raw_inclination = struct.unpack(f"{endian}h", data[index : index + 2])[0]
                self.inclination = raw_inclination / 10.0
                index += 4  # Skip Ramp Angle (2 bytes) which follows Inclination
                if self._on_inclination_change:
                    await self._on_inclination_change(self.inclination)

            self._logger.debug(
                f"Received data ({self._protocol}): {data.hex()} -> Speed: {self.speed} km/h, "
                f"Inclination: {self.inclination}%, Distance: {self.distance}m"
            )
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
