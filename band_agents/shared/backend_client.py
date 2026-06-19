"""
Shared HTTP client used by all Band agents to call the FirstJob backend API.
Band agents don't have direct DB access — they go through the REST API.
This keeps a clean separation: Band handles coordination, FastAPI handles data.
"""

import os
import httpx
from loguru import logger


def get_api_client() -> httpx.AsyncClient:
    base_url = os.getenv("FIRSTJOB_API_URL", "http://localhost:8000/api")
    token = os.getenv("FIRSTJOB_SERVICE_TOKEN", "")
    return httpx.AsyncClient(
        base_url=base_url,
        headers={"X-Service-Token": token, "Content-Type": "application/json"},
        timeout=30.0,
    )


async def call_backend(method: str, path: str, **kwargs) -> dict:
    """Generic backend caller with error handling."""
    async with get_api_client() as client:
        response = await getattr(client, method)(path, **kwargs)
        response.raise_for_status()
        return response.json()
