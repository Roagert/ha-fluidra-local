"""Direct Fluidra cloud client matching the local bridge client interface."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import json
from typing import Any
from urllib import error, request

from .const import MODE_TO_VALUE

COGNITO_ENDPOINT = "https://cognito-idp.eu-west-1.amazonaws.com/"
COGNITO_CLIENT_ID = "g3njunelkcbtefosqm9bdhhq1"
API_BASE_URL = "https://api.fluidra-emea.com"
USER_AGENT = "Fluidra/1.0"


class FluidraCloudClientError(Exception):
    """Raised when a direct Fluidra cloud call fails."""


class FluidraCloudMFARequired(FluidraCloudClientError):
    """Raised when Cognito requires a second factor."""

    def __init__(self, challenge_name: str, session: str) -> None:
        super().__init__(challenge_name)
        self.challenge_name = challenge_name
        self.session = session


class FluidraCloudClient:
    """Small async direct client for Fluidra cloud REST endpoints."""

    def __init__(self, username: str, password: str, *, device_id: str | None = None, refresh_token: str | None = None, timeout: float = 30.0) -> None:
        self.username = username
        self.password = password
        self.device_id = (device_id or "").strip() or None
        self.refresh_token = (refresh_token or "").strip() or None
        self.timeout = timeout
        self.access_token: str | None = None
        self.token_expiry: datetime | None = None

    async def _authenticate_if_needed(self) -> None:
        if self.access_token and self.token_expiry and datetime.now() + timedelta(minutes=10) < self.token_expiry:
            return
        await asyncio.to_thread(self._authenticate_sync)

    def _cognito_request(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/x-amz-json-1.1; charset=utf-8",
            "X-Amz-Target": f"AWSCognitoIdentityProviderService.{target}",
            "User-Agent": USER_AGENT,
        }
        req = request.Request(COGNITO_ENDPOINT, data=data, method="POST", headers=headers)
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode()
                return json.loads(body) if body else {}
        except error.HTTPError as exc:
            raw = exc.read().decode(errors="replace")
            try:
                body = json.loads(raw)
            except Exception:
                body = {"message": raw or str(exc)}
            err_type = exc.headers.get("x-amzn-errortype", "")
            message = body.get("message") or body.get("__type") or err_type or str(exc)
            raise FluidraCloudClientError(f"invalid_auth:{message}") from exc

    def _store_auth_result(self, result: dict[str, Any]) -> None:
        self.access_token = result.get("AccessToken")
        new_refresh_token = result.get("RefreshToken")
        if new_refresh_token:
            self.refresh_token = new_refresh_token
        if not self.access_token:
            raise FluidraCloudClientError("invalid_auth:no_access_token")
        self.token_expiry = datetime.now() + timedelta(seconds=int(result.get("ExpiresIn", 3600)))

    def _authenticate_sync(self) -> None:
        try:
            if self.refresh_token:
                try:
                    response = self._cognito_request(
                        "InitiateAuth",
                        {
                            "AuthFlow": "REFRESH_TOKEN_AUTH",
                            "ClientId": COGNITO_CLIENT_ID,
                            "AuthParameters": {"REFRESH_TOKEN": self.refresh_token},
                        },
                    )
                    self._store_auth_result(response.get("AuthenticationResult", {}))
                    return
                except FluidraCloudClientError:
                    self.refresh_token = None

            response = self._cognito_request(
                "InitiateAuth",
                {
                    "AuthFlow": "USER_PASSWORD_AUTH",
                    "ClientId": COGNITO_CLIENT_ID,
                    "AuthParameters": {"USERNAME": self.username, "PASSWORD": self.password},
                },
            )
            result = response.get("AuthenticationResult")
            if result:
                self._store_auth_result(result)
                return
            challenge_name = response.get("ChallengeName", "")
            session = response.get("Session", "")
            if challenge_name in {"SOFTWARE_TOKEN_MFA", "SMS_MFA"} and session:
                raise FluidraCloudMFARequired(challenge_name, session)
            raise FluidraCloudClientError(f"invalid_auth:unexpected_challenge:{challenge_name or 'none'}")
        except FluidraCloudClientError:
            raise
        except Exception as exc:
            raise FluidraCloudClientError(str(exc)) from exc

    async def respond_to_mfa(self, code: str, session: str, challenge_name: str = "SOFTWARE_TOKEN_MFA") -> None:
        """Complete a Cognito MFA challenge and store resulting tokens."""
        await asyncio.to_thread(self._respond_to_mfa_sync, code, session, challenge_name)

    def _respond_to_mfa_sync(self, code: str, session: str, challenge_name: str = "SOFTWARE_TOKEN_MFA") -> None:
        response = self._cognito_request(
            "RespondToAuthChallenge",
            {
                "ChallengeName": challenge_name,
                "ClientId": COGNITO_CLIENT_ID,
                "Session": session,
                "ChallengeResponses": {
                    "USERNAME": self.username,
                    f"{challenge_name}_CODE": code,
                },
            },
        )
        self._store_auth_result(response.get("AuthenticationResult", {}))

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
            "User-Agent": USER_AGENT,
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

    async def devices(self) -> list[dict[str, Any]]:
        """Return Fluidra cloud devices with valid ids."""
        devices = await self.request("GET", "/generic/devices")
        items = devices if isinstance(devices, list) else (devices.get("data") or devices.get("devices") or [] if isinstance(devices, dict) else [])
        if not isinstance(items, list):
            raise FluidraCloudClientError("invalid_devices_response")
        valid_devices: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            device_id = item.get("id") or item.get("deviceId")
            if not device_id:
                continue
            valid_devices.append({**item, "id": str(device_id)})
        if not valid_devices:
            raise FluidraCloudClientError("no_device")
        return valid_devices

    async def _ensure_device_id(self) -> str:
        if self.device_id:
            return self.device_id
        items = await self.devices()
        if items:
            self.device_id = str(items[0]["id"])
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
