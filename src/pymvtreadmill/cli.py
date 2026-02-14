import argparse
import asyncio
import logging
import signal
import sys
from contextlib import AsyncExitStack

import aiomqtt
from pymvtreadmill.client import TreadmillClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("pymvtreadmill-cli")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Mobvoi/Horizon Treadmill to MQTT Bridge")
    parser.add_argument(
        "--treadmill-name",
        type=str,
        default="Mobvoi",
        help="Name filter for the treadmill (default: Mobvoi)",
    )
    parser.add_argument(
        "--mqtt-host",
        type=str,
        help="MQTT broker hostname (required for MQTT)",
    )
    parser.add_argument(
        "--mqtt-port",
        type=int,
        default=1883,
        help="MQTT broker port (default: 1883)",
    )
    parser.add_argument(
        "--mqtt-username",
        type=str,
        help="MQTT username",
    )
    parser.add_argument(
        "--mqtt-password",
        type=str,
        help="MQTT password",
    )
    parser.add_argument(
        "--mqtt-topic",
        type=str,
        default="homeassistant/sensor/treadmill/speed/state",
        help="MQTT topic for speed (default: homeassistant/sensor/treadmill/speed/state)",
    )

    args = parser.parse_args()

    # Exit stack to manage async context managers (MQTT, Treadmill)
    async with AsyncExitStack() as stack:
        mqtt_client: aiomqtt.Client | None = None

        if args.mqtt_host:
            logger.info(f"Connecting to MQTT broker at {args.mqtt_host}:{args.mqtt_port}...")
            mqtt_client = aiomqtt.Client(
                hostname=args.mqtt_host,
                port=args.mqtt_port,
                username=args.mqtt_username,
                password=args.mqtt_password,
            )
            try:
                await stack.enter_async_context(mqtt_client)
                logger.info("Connected to MQTT broker.")
            except Exception as e:
                logger.error(f"Failed to connect to MQTT broker: {e}")
                sys.exit(1)

        async def on_speed_change(speed: float) -> None:
            logger.info(f"Speed update: {speed:.2f} km/h")
            if mqtt_client:
                try:
                    await mqtt_client.publish(args.mqtt_topic, payload=f"{speed:.2f}")
                except Exception as e:
                    logger.error(f"Failed to publish to MQTT: {e}")

        logger.info(f"Connecting to treadmill matching '{args.treadmill_name}'...")
        try:
            client = TreadmillClient(
                name_filter=args.treadmill_name,
                on_speed_change=on_speed_change,
            )
            await stack.enter_async_context(client)
            logger.info("Connected to treadmill.")
        except Exception as e:
            logger.error(f"Failed to connect to treadmill: {e}")
            sys.exit(1)

        # Keep running until interrupted
        stop_event = asyncio.Event()

        def signal_handler() -> None:
            logger.info("Signal received, stopping...")
            stop_event.set()

        loop = asyncio.get_running_loop()
        try:
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows does not support add_signal_handler
            pass

        await stop_event.wait()
        logger.info("Shutting down...")


def run() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
