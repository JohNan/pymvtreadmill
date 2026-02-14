# pymvtreadmill 🏃💨

A modern Python 3.13+ library to control and read data from Mobvoi Home Treadmills and Horizon fitness devices.

## Features
- **Real-time Reading**: Parses Speed, Distance, and Status directly from BLE notifications.
- **Modern Async**: Built on `asyncio.TaskGroup` and `bleak`.
- **Control**: Set target speed (km/h) via Python commands.
- **Auto-Reconnect**: Robust connection handling for continuous use.

## Installation
Install the package via pip using the name `pymvtreadmill`.

## Usage
Import `TreadmillClient` from the package. The client is designed to work within an `asyncio` loop and supports the async context manager protocol (`async with`) for automatic connection handling.

## Development
This project strictly requires Python 3.13 or newer.
Please read **AGENTS.md** before contributing to understand the architectural guidelines and protocol details.
