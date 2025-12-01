"""
Lightweight Pub/Sub helper for the Auth Service.

This module provides a simple interface to publish domain events across
microservices. It supports a stub mode for local development and can be
extended to real pub/sub systems such as GCP Pub/Sub or Kafka.
"""

import json
import asyncio
from app.config import PUBSUB_MODE


async def publish(topic: str, payload: dict):
    """
    Publish an event to the configured Pub/Sub system.

    Args:
        topic (str): Name of the event topic.
        payload (dict): Event payload data.

    Raises:
        NotImplementedError: If PUBSUB_MODE is set to 'gcp' and publishing
                             to GCP Pub/Sub is not implemented.

    Notes:
        - In 'stub' mode, the payload is printed to the console for local
          development/testing.
        - This function is asynchronous and can be awaited in async contexts.
    """
    if PUBSUB_MODE == "gcp":
        raise NotImplementedError(
            "GCP Pub/Sub publish not implemented. See README for setup."
        )
    else:
        print(f"[PUBSUB-STUB] publish -> topic={topic}, payload={json.dumps(payload)}")
        await asyncio.sleep(0)
