from enum import StrEnum


class TreadmillUUID(StrEnum):
    """Bluetooth UUIDs for Mobvoi and Horizon Treadmills."""

    SERVICE = "0000ffb0-0000-1000-8000-00805f9b34fb"
    READ = "0000ffb2-0000-1000-8000-00805f9b34fb"
    WRITE = "0000ffb1-0000-1000-8000-00805f9b34fb"
