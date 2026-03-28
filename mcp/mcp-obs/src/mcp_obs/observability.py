from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json

import httpx
from pydantic import BaseModel, Field


class LogSearchArgs(BaseModel):
    keyword: str | None = Field(default=None)
    service_name: str | None = Field(default=None)
    severity: str | None = Field(default=None)
    minutes: int = Field(default=10, ge=1, le=1440)
    limit: int = Field(default=20, ge=1, le=100)


class LogsErrorCountArgs(BaseModel):
    service_name: str | None = Field(default=None)
    minutes: int = Field(default=10, ge=1, le=1440)
    limit: int = Field(default=10, ge=1, le=100)


class TracesListArgs(BaseModel):
    service_name: str
    minutes: int = Field(default=10, ge=1, le=1440)
    limit: int = Field(default=10, ge=1, le=50)


class TracesGetArgs(BaseModel):
    trace_id: str


class ObservabilityClient:
    def __init__(self, logs_url: str, traces_url: str) -> None:
        self.logs_url = logs_url.rstrip("/")
        self.traces_url = traces_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=15.0)

    async def aclose(self) -> None:
        await self.client.aclose()

    async def query_logs(self, query: str, limit: int) -> list[dict]:
        r = await self.client.post(
            f"{self.logs_url}/select/logsql/query",
            data={"query": query, "limit": str(limit)},
        )
        r.raise_for_status()
        rows = []
        for line in r.text.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return rows

    async def logs_search(self, args: LogSearchArgs) -> list[dict]:
        parts = [f"_time:{args.minutes}m"]
        if args.service_name:
            parts.append(f'service.name:{json.dumps(args.service_name)}')
        if args.severity:
            parts.append(f"severity:{args.severity.upper()}")
        if args.keyword:
            if " " in args.keyword:
                parts.append(json.dumps(args.keyword))
            else:
                parts.append(args.keyword)
        parts.append("| fields _time, service.name, severity, event, trace_id, _msg")
        query = " ".join(parts)
        return await self.query_logs(query, args.limit)

    async def logs_error_count(self, args: LogsErrorCountArgs) -> list[dict]:
        parts = [f"_time:{args.minutes}m", "severity:ERROR"]
        if args.service_name:
            parts.append(f'service.name:{json.dumps(args.service_name)}')
        parts.append("| stats by (service.name) count() as error_count | sort by (error_count desc)")
        query = " ".join(parts)
        return await self.query_logs(query, args.limit)

    async def traces_list(self, args: TracesListArgs) -> list[dict]:
        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=args.minutes)
        r = await self.client.get(
            f"{self.traces_url}/select/jaeger/api/traces",
            params={
                "service": args.service_name,
                "limit": str(args.limit),
                "start": str(int(start.timestamp() * 1_000_000)),
                "end": str(int(end.timestamp() * 1_000_000)),
            },
        )
        r.raise_for_status()
        data = r.json().get("data", [])
        result = []
        for trace in data:
            spans = trace.get("spans", [])
            trace_id = trace.get("traceID") or trace.get("traceId") or "unknown"
            result.append(
                {
                    "trace_id": trace_id,
                    "span_count": len(spans),
                }
            )
        return result

    async def traces_get(self, args: TracesGetArgs) -> dict:
        r = await self.client.get(
            f"{self.traces_url}/select/jaeger/api/traces/{args.trace_id}"
        )
        r.raise_for_status()
        data = r.json().get("data", [])
        if not data:
            raise RuntimeError(f"Trace not found: {args.trace_id}")

        trace = data[0]
        spans = trace.get("spans", [])
        processes = trace.get("processes", {})

        span_summaries = []
        for span in spans:
            name = span.get("operationName") or span.get("name") or "unknown"
            process = processes.get(span.get("processID"), {}) if isinstance(processes, dict) else {}
            service_name = process.get("serviceName") or "unknown"
            duration = span.get("duration")
            if duration is None:
                span_summaries.append(f"{service_name} :: {name}")
            else:
                span_summaries.append(f"{service_name} :: {name} ({duration}µs)")

        return {
            "trace_id": args.trace_id,
            "span_count": len(spans),
            "span_summaries": span_summaries,
        }
