# AGENTS.md

## 🤖 AI Agent & Developer Guide

### 1. Project Mission
**pymvtreadmill** is a modern, async Python library for controlling and reading data from **Mobvoi Home Treadmills** and compatible **Horizon** fitness devices via Bluetooth Low Energy (BLE).
- **Origin**: Ported from [qdomyos-zwift](https://github.com/cagnulein/qdomyos-zwift) (C++).
- **Goal**: Provide a robust, structured-concurrency based driver for integration with Home Assistant, Zwift bridges, or custom dashboards.

### 2. Architecture & Tech Stack
- **Language**: Python 3.13+ (Strict requirement).
- **Core Library**: `bleak` (BLE).
- **Concurrency**: `asyncio` with **Structured Concurrency** (`asyncio.TaskGroup`).
- **Typing**: Strict static typing using modern syntax (`type`, `|`, `Self`).
- **Linting/Formatting**: `ruff` and `black`.

### 3. Critical Protocol Knowledge
* **UUIDs**:
    * Service: `0000ffb0-0000-1000-8000-00805f9b34fb`
    * Read/Notify: `0000ffb2-0000-1000-8000-00805f9b34fb`
    * Write: `0000ffb1-0000-1000-8000-00805f9b34fb`
* **Data Parsing**:
    * **Mobvoi**: Speed resolution **0.01 km/h** (Bytes 3-4, Big Endian).
    * **Horizon**: Speed resolution **0.1 km/h**.
    * *Agent Note*: Default to Mobvoi resolution but allow configuration via `TreadmillConfig`.

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
    ```
4.  **Enums**: Use `StrEnum` for command constants.

### 5. Verification Commands
Before submitting code:
- **Linting**: `ruff check .`
- **Formatting**: `black .`
- **Type Check**: `mypy .`
