from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_obs.observability import (
    LogSearchArgs,
    LogsErrorCountArgs,
    ObservabilityClient,
    TracesGetArgs,
    TracesListArgs,
)

LOGS_URL = os.environ.get("NANOBOT_OBS_LOGS_URL", "http://victorialogs:9428").rstrip("/")
TRACES_URL = os.environ.get("NANOBOT_OBS_TRACES_URL", "http://victoriatraces:10428").rstrip("/")

mcp = FastMCP("obs")


async def _with_client(fn):
    client = ObservabilityClient(LOGS_URL, TRACES_URL)
    try:
        return await fn(client)
    finally:
        await client.aclose()


@mcp.tool()
async def logs_search(
    keyword: str | None = None,
    service_name: str | None = None,
    severity: str | None = None,
    minutes: int = 10,
    limit: int = 20,
) -> str:
    args = LogSearchArgs(
        keyword=keyword,
        service_name=service_name,
        severity=severity,
        minutes=minutes,
        limit=limit,
    )

    async def run(client: ObservabilityClient):
        return await client.logs_search(args)

    data = await _with_client(run)
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def logs_error_count(
    service_name: str | None = None,
    minutes: int = 10,
    limit: int = 10,
) -> str:
    args = LogsErrorCountArgs(
        service_name=service_name,
        minutes=minutes,
        limit=limit,
    )

    async def run(client: ObservabilityClient):
        return await client.logs_error_count(args)

    data = await _with_client(run)
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def traces_list(
    service_name: str,
    minutes: int = 10,
    limit: int = 10,
) -> str:
    args = TracesListArgs(
        service_name=service_name,
        minutes=minutes,
        limit=limit,
    )

    async def run(client: ObservabilityClient):
        return await client.traces_list(args)

    data = await _with_client(run)
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def traces_get(trace_id: str) -> str:
    args = TracesGetArgs(trace_id=trace_id)

    async def run(client: ObservabilityClient):
        return await client.traces_get(args)

    data = await _with_client(run)
    return json.dumps(data, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())
