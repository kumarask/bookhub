"""
Lightweight pub/sub helper for Auth Service.

This module provides a simple interface to publish domain events
across microservices. Supports a stub mode for local development
and can be extended to real pub/sub systems like GCP Pub/Sub or Kafka.
"""

import os
import json
import asyncio

PUBSUB_MODE = os.getenv("PUBSUB_MODE", "stub")


async def publish(topic: str, payload: dict):
    """
    Publish an event to the configured pub/sub system.

    Args:
        topic (str): Event topic name.
        payload (dict): Event payload data.

    Raises:
        NotImplementedError: If PUBSUB_MODE is set to 'gcp'.
    """
    if PUBSUB_MODE == "gcp":
        raise NotImplementedError(
            "GCP Pub/Sub publish not implemented. See README for setup."
        )
    else:
        print(f"[PUBSUB-STUB] publish -> topic={topic}, payload={json.dumps(payload)}")
        await asyncio.sleep(0)
