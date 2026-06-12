"""Async client for the local Fluidra server."""
from __future__ import annotations

import asyncio
from typing import Any
from urllib import request, error
import json


class FluidraLocalClientError(Exception):
    """Raised when the local Fluidra server call fails."""


class FluidraLocalClient:
    """Small async wrapper around the deterministic local server HTTP API."""

    def __init__(self, base_url: str, *, auth_token: str | None = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth_token = (auth_token or "").strip()
        self.timeout = timeout

    async def request(self, method: str, path: str, payload: dict[str, Any] | None = None, *, timeout: float | None = None) -> Any:
        return await asyncio.to_thread(self._request_sync, method, path, payload, timeout or self.timeout)

    def _request_sync(self, method: str, path: str, payload: dict[str, Any] | None, timeout: float) -> Any:
        data = None if payload is None else json.dumps(payload).encode()
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        req = request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except error.HTTPError as exc:
            try:
                body = json.loads(exc.read().decode())
            except Exception:
                body = {"message": str(exc)}
            raise FluidraLocalClientError(f"HTTP {exc.code}: {body}") from exc
        except Exception as exc:
            raise FluidraLocalClientError(str(exc)) from exc

    async def state(self) -> dict[str, Any]:
        return await self.request("GET", "/state")

    async def capabilities(self) -> dict[str, Any]:
        return await self.request("GET", "/capabilities")

    async def component(self, component_id: int) -> dict[str, Any]:
        return await self.request("GET", f"/component/{component_id}")

    async def power(self, on: bool, *, wait: bool = False) -> dict[str, Any]:
        suffix = "?wait=1&timeout=180&interval=10" if wait else ""
        return await self.request("PUT", f"/power{suffix}", {"on": on}, timeout=220 if wait else None)

    async def set_temperature(self, celsius: float, *, wait: bool = False) -> dict[str, Any]:
        suffix = "?wait=1&timeout=180&interval=10" if wait else ""
        return await self.request("PUT", f"/temperature{suffix}", {"celsius": celsius}, timeout=220 if wait else None)

    async def set_mode(self, mode: str, *, wait: bool = False) -> dict[str, Any]:
        suffix = "?wait=1&timeout=180&interval=10" if wait else ""
        return await self.request("PUT", f"/mode{suffix}", {"mode": mode}, timeout=220 if wait else None)
