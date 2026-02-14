import asyncio
from pymvtreadmill import TreadmillClient


async def main() -> None:
    async with TreadmillClient() as client:
        print("Connected!")
        # Set speed to 2.5 km/h
        await client.set_speed(2.5)
        # Keep running for a bit
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
