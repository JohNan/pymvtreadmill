import asyncio
import logging
from pymvtreadmill import TreadmillClient


async def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    logger = logging.getLogger("inspect_device")

    async def on_raw_data(data: bytes) -> None:
        logger.info(f"Raw Data: {data.hex()}")

    logger.info("Connecting to treadmill...")
    async with TreadmillClient(on_raw_data=on_raw_data) as _:
        print("Connected! Inspecting data for 20 seconds...")
        # Discovery info is logged by client.connect() automatically at INFO level.

        # Keep running for a bit to capture notifications
        await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())
