"""Direct Fluidra cloud client matching the local bridge client interface."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import json
from typing import Any
from urllib import error, request

import boto3
from botocore.exceptions import ClientError

from .const import DEFAULT_DEVICE_ID, MODE_TO_VALUE

COGNITO_REGION = "eu-west-1"
COGNITO_CLIENT_ID = "4s2pr20gcl9fac5okd84q0e1h1"
API_BASE_URL = "https://api.fluidra-emea.com"


class FluidraCloudClientError(Exception):
    """Raised when a direct Fluidra cloud call fails."""


class FluidraCloudClient:
    """Small async direct client for Fluidra cloud REST endpoints."""

    def __init__(self, username: str, password: str, *, device_id: str | None = None, timeout: float = 30.0) -> None:
        self.username = username
        self.password = password
        self.device_id = (device_id or "").strip() or None
        self.timeout = timeout
        self.access_token: str | None = None
        self.token_expiry: datetime | None = None

    async def _authenticate_if_needed(self) -> None:
        if self.access_token and self.token_expiry and datetime.now() + timedelta(minutes=10) < self.token_expiry:
            return
        await asyncio.to_thread(self._authenticate_sync)

    def _authenticate_sync(self) -> None:
        try:
            client = boto3.client("cognito-idp", region_name=COGNITO_REGION)
            response = client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": self.username, "PASSWORD": self.password},
            )
            result = response["AuthenticationResult"]
            self.access_token = result["AccessToken"]
            self.token_expiry = datetime.now() + timedelta(seconds=int(result.get("ExpiresIn", 3600)))
        except ClientError as exc:
            raise FluidraCloudClientError("invalid_auth") from exc
        except Exception as exc:
            raise FluidraCloudClientError(str(exc)) from exc

    async def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        await self._authenticate_if_needed()
        return await asyncio.to_thread(self._request_sync, method, path, payload)

    def _request_sync(self, method: str, path: str, payload: dict[str, Any] | None) -> Any:
        data = None if payload is None else json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": self.access_token or "",
            "x-access-token": self.access_token or "",
            "User-Agent": "Fluidra/1.0",
        }
        req = request.Request(API_BASE_URL + path, data=data, method=method, headers=headers)
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode()
                return json.loads(body) if body else {}
        except error.HTTPError as exc:
            try:
                body = json.loads(exc.read().decode())
            except Exception:
                body = {"message": str(exc)}
            raise FluidraCloudClientError(f"HTTP {exc.code}: {body}") from exc
        except Exception as exc:
            raise FluidraCloudClientError(str(exc)) from exc

    async def _ensure_device_id(self) -> str:
        if self.device_id:
            return self.device_id
        devices = await self.request("GET", "/generic/devices")
        items = devices if isinstance(devices, list) else (devices.get("data") or devices.get("devices") or [] if isinstance(devices, dict) else [])
        if items:
            self.device_id = str(items[0].get("id") or items[0].get("deviceId") or DEFAULT_DEVICE_ID)
        if not self.device_id:
            raise FluidraCloudClientError("no_device")
        return self.device_id

    async def state(self) -> dict[str, Any]:
        device_id = await self._ensure_device_id()
        return {"backend": "cloud-direct", "device_id": device_id, "device_type": "connected", "device": {"id": device_id}}

    async def capabilities(self) -> dict[str, Any]:
        device_id = await self._ensure_device_id()
        return {"backend": "cloud-direct", "device_id": device_id, "components": {}, "modes": MODE_TO_VALUE, "modes_by_value": {str(v): k for k, v in MODE_TO_VALUE.items()}}

    async def components(self) -> list[dict[str, Any]]:
        device_id = await self._ensure_device_id()
        result = await self.request("GET", f"/generic/devices/{device_id}/components?deviceType=connected")
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return result.get("data") or result.get("components") or []
        return []

    async def component(self, component_id: int) -> dict[str, Any]:
        device_id = await self._ensure_device_id()
        try:
            result = await self.request("GET", f"/generic/devices/{device_id}/components/{component_id}?deviceType=connected")
            if isinstance(result, dict):
                return result
        except FluidraCloudClientError:
            pass
        for component in await self.components():
            if int(component.get("id", -1)) == int(component_id):
                return component
        return {"id": component_id, "error": "missing from cloud component snapshot"}

    async def set_component(self, component_id: int, desired_value: int) -> dict[str, Any]:
        device_id = await self._ensure_device_id()
        return await self.request("PUT", f"/generic/devices/{device_id}/components/{component_id}?deviceType=connected", {"desiredValue": desired_value})

    async def power(self, on: bool, *, wait: bool = False) -> dict[str, Any]:
        return await self.set_component(13, 1 if on else 0)

    async def set_temperature(self, celsius: float, *, wait: bool = False) -> dict[str, Any]:
        return await self.set_component(15, int(round(celsius * 10)))

    async def set_mode(self, mode: str, *, wait: bool = False) -> dict[str, Any]:
        return await self.set_component(14, MODE_TO_VALUE[mode])
