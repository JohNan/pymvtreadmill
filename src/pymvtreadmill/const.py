from enum import StrEnum


class TreadmillUUID(StrEnum):
    """Bluetooth UUIDs for Mobvoi and Horizon Treadmills."""

    # Proprietary Service (Big Endian)
    SERVICE = "0000ffb0-0000-1000-8000-00805f9b34fb"
    READ = "0000ffb2-0000-1000-8000-00805f9b34fb"
    WRITE = "0000ffb1-0000-1000-8000-00805f9b34fb"

    # FTMS Service (Little Endian)
    FTMS_SERVICE = "00001826-0000-1000-8000-00805f9b34fb"
    FTMS_DATA = "00002acd-0000-1000-8000-00805f9b34fb"
    FTMS_CONTROL = "00002ad9-0000-1000-8000-00805f9b34fb"
    FTMS_STATUS = "00002ada-0000-1000-8000-00805f9b34fb"
