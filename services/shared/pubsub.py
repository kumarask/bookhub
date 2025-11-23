"""
Lightweight pub/sub helpers used across services.

This module provides a minimal publish/subscribe abstraction intended for
development and testing environments. It allows services to emit domain
events without requiring a full messaging infrastructure.

The behavior of the pub/sub system is controlled by the `PUBSUB_MODE`
environment variable:

    PUBSUB_MODE="stub"  (default)
        Events are printed to stdout and no external system is used.

    PUBSUB_MODE="gcp"
        Intended for Google Cloud Pub/Sub, but not yet implemented.

This module is typically used by API endpoints to broadcast domain
events such as `review.created`, `review.updated`, and `review.deleted`.

All public functions include concise docstrings describing their
arguments, return values, and raised exceptions where applicable.
"""

import asyncio
import json
import os

PUBSUB_MODE = os.getenv("PUBSUB_MODE", "stub")


async def publish(topic: str, payload: dict):
    """
    Publish a message to the configured pub/sub system.

    Depending on the configured PUBSUB_MODE:
        - "stub": Prints the message to stdout and returns immediately.
        - "gcp": Raises NotImplementedError (scaffold placeholder).

    Args:
        topic (str): The event topic or channel to publish to.
        payload (dict): The event payload, which must be JSON-serializable.

    Raises:
        NotImplementedError: If PUBSUB_MODE="gcp", since GCP Pub/Sub
            support is not implemented in this scaffold.

    Returns:
        None: The stub mode performs a lightweight asynchronous no-op.
    """
    if PUBSUB_MODE == "gcp":
        raise NotImplementedError(
            "GCP Pub/Sub publish not implemented in scaffold. See README."
        )
    else:
        print(f"[PUBSUB-STUB] publish -> topic={topic} payload={json.dumps(payload)}")
        await asyncio.sleep(0)
