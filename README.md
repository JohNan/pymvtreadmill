# pymvtreadmill 🏃💨

A modern Python 3.13+ library to control and read data from Mobvoi Home Treadmills and Horizon fitness devices.

## Features
- **Real-time Reading**: Parses Speed directly from BLE notifications.
- **Modern Async**: Built on `asyncio` and `bleak`.
- **Control**: Set target speed (km/h) via Python commands.
- **Auto-Reconnect**: Robust connection handling for continuous use.
- **Type Safe**: Fully typed with modern Python 3.13+ syntax.
- **MQTT Bridge**: Built-in CLI to bridge treadmill data to MQTT.

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

## MQTT Bridge (CLI)

This package includes a command-line interface (CLI) to bridge treadmill data to an MQTT broker (e.g., for Home Assistant).

### Usage
```bash
pymvtreadmill --help
```

### Arguments
| Argument | Description | Default |
|---|---|---|
| `--treadmill-name` | Name filter for the treadmill | `Mobvoi` |
| `--mqtt-host` | MQTT broker hostname (Required for MQTT) | - |
| `--mqtt-port` | MQTT broker port | `1883` |
| `--mqtt-username` | MQTT username | - |
| `--mqtt-password` | MQTT password | - |
| `--mqtt-topic` | MQTT topic for speed | `homeassistant/sensor/treadmill/speed/state` |

## Running with Docker

You can run the project using Docker. This is useful if you want to run the treadmill controller in an isolated environment.

### Prerequisites
- Docker installed on your machine.
- A Bluetooth adapter compatible with Linux (BlueZ).

### Building the Image
```bash
docker build -t pymvtreadmill .
```

### Running the CLI
To access the Bluetooth adapter from within the container, you need to share the DBus socket and run in privileged mode (or with `NET_ADMIN` capabilities).

By default, the container runs the `pymvtreadmill` CLI. You can pass arguments directly to it.

```bash
# Show help
docker run --rm -it pymvtreadmill --help

# Run as MQTT Bridge
docker run --rm -it \
  --net=host \
  --privileged \
  -v /var/run/dbus:/var/run/dbus \
  pymvtreadmill --mqtt-host 192.168.1.100 --mqtt-username myuser --mqtt-password mypass
```

### Running Custom Scripts
If you want to run a custom python script (like the examples), you need to override the entrypoint:

```bash
docker run --rm -it \
  --entrypoint python \
  --net=host \
  --privileged \
  -v /var/run/dbus:/var/run/dbus \
  -v $(pwd)/my_script.py:/app/my_script.py \
  pymvtreadmill my_script.py
```

## Docker Compose

For a more permanent setup, you can use the provided `docker-compose.yml` file.

1. Edit `docker-compose.yml` to set your MQTT broker details in the `command` section.
2. Run:
   ```bash
   docker-compose up -d
   ```

## Usage (Library)

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
