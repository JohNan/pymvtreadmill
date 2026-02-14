# pymvtreadmill 🏃💨

A modern Python 3.13+ library to control and read data from Mobvoi Home Treadmills and Horizon fitness devices.

## Features
- **Real-time Reading**: Parses Speed directly from BLE notifications.
- **Modern Async**: Built on `asyncio` and `bleak`.
- **Control**: Set target speed (km/h) via Python commands.
- **Auto-Reconnect**: Robust connection handling for continuous use.
- **Type Safe**: Fully typed with modern Python 3.13+ syntax.

## Data Protocol

The treadmill sends data as BLE notifications. Currently, only **Speed** is parsed.

| Feature | Resolution | Protocol |
|---|---|---|
| Speed (Mobvoi) | 0.01 km/h | Bytes 3-4 (Big Endian) |
| Speed (Horizon)| 0.1 km/h | Bytes 3-4 (Big Endian) |

*Note: The current implementation defaults to Mobvoi resolution (0.01 km/h).*

## Installation

### Using uv (Recommended)
```bash
uv pip install pymvtreadmill
```

### Using pip
```bash
pip install pymvtreadmill
```

## Usage

```python
import asyncio
from pymvtreadmill import TreadmillClient

async def main():
    async with TreadmillClient() as client:
        print("Connected!")
        # Set speed to 2.5 km/h
        await client.set_speed(2.5)
        # Keep running for a bit
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

This project strictly requires Python 3.13 or newer. We use `uv` for dependency management.

### Setup
```bash
./scripts/setup_env.sh
```

### Verification
```bash
uv run ruff check .
uv run black --check .
uv run mypy .
uv run pytest
```

Please read **AGENTS.md** before contributing to understand the architectural guidelines and protocol details.
