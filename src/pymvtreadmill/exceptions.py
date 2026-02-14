class TreadmillError(Exception):
    """Base exception for pymvtreadmill."""

    pass


class TreadmillConnectionError(TreadmillError):
    """Raised when connection fails or is lost."""

    pass
