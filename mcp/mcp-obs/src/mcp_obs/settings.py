from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    logs_url: str
    traces_url: str


def _resolve_url(env_name: str, default: str) -> str:
    value = os.environ.get(env_name, default).strip()
    if not value:
        raise RuntimeError(f"{env_name} is not configured")
    return value.rstrip("/")


def resolve_settings() -> Settings:
    return Settings(
        logs_url=_resolve_url("NANOBOT_OBS_LOGS_URL", "http://victorialogs:9428"),
        traces_url=_resolve_url(
            "NANOBOT_OBS_TRACES_URL", "http://victoriatraces:10428"
        ),
    )
