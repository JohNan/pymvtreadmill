# AGENTS.md

## 🤖 AI Agent & Developer Guide

### 1. Project Mission
This repository hosts a Python library for controlling **Mobvoi** and **Horizon** treadmills via Bluetooth Low Energy (BLE).
- **Origin**: Ported from [qdomyos-zwift](https://github.com/cagnulein/qdomyos-zwift) (C++).
- **Goal**: A modern, asyncio-native Python driver for 2026+ standards.

### 2. Architecture & Tech Stack
- **Language**: Python 3.13+ (Strict requirement).
- **Core Library**: `bleak` (BLE).
- **Concurrency**: `asyncio` with **Structured Concurrency** (`asyncio.TaskGroup`).
- **Typing**: Strict static typing using modern syntax (`type`, `|`, `Self`).

### 3. Critical Protocol Knowledge
* **UUIDs**:
    * Service: `0000ffb0-0000-1000-8000-00805f9b34fb`
    * Read/Notif: `0000ffb2...`
    * Write: `0000ffb1...`
* **Data Parsing**:
    * **Mobvoi**: Speed resolution **0.01 km/h** (Bytes 3-4).
    * **Horizon**: Speed resolution **0.1 km/h**.
    * *Agent Note*: Default to Mobvoi resolution but allow configuration.

### 4. Coding Standards (Modern Python)
1.  **Type Aliases**: Use the `type` keyword (Python 3.12+).
    ```python
    type Packet = bytearray | bytes
    ```
2.  **Unions**: Use `|` operator, never `Union`.
    ```python
    def parse(data: bytes | None) -> float: ...
    ```
3.  **Concurrency**: Prefer `asyncio.TaskGroup` over `asyncio.gather`.
    ```python
    async with asyncio.TaskGroup() as tg:
        tg.create_task(self.read_loop())
        tg.create_task(self.keep_alive())
    ```
4.  **Enums**: Use `StrEnum` for command constants.

### 5. Verification Commands
Before submitting code:
- **Linting**: `ruff check .` (Preferred over flake8 for speed/modernity).
- **Formatting**: `black .`
- **Type Check**: `mypy .`
