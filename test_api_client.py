#!/usr/bin/env python3
"""Standalone test for the Intentgine API client - no HA dependencies."""

import asyncio
import logging
import time
import aiohttp

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class IntentgineAPIClient:
    """Client for Intentgine API."""

    def __init__(self, api_key: str, endpoint: str):
        """Initialize the API client."""
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.session = None
        self._jwt_token = None
        self._jwt_expires_at = 0

    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _ensure_token(self):
        """Exchange API key for JWT if needed."""
        _LOGGER.debug(
            "_ensure_token called, current token: %s, expires: %s, now: %s",
            bool(self._jwt_token),
            self._jwt_expires_at,
            time.time(),
        )
        if self._jwt_token and time.time() < self._jwt_expires_at - 30:
            _LOGGER.debug("Token still valid, reusing")
            return

        session = await self._get_session()
        url = f"{self.endpoint}/v1/auth"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        _LOGGER.debug("Exchanging API key for JWT at %s", url)

        try:
            async with session.post(url, headers=headers) as resp:
                _LOGGER.debug("Auth response status: %s", resp.status)
                if resp.status == 401:
                    raise Exception("Invalid API key")
                if resp.status >= 400:
                    text = await resp.text()
                    raise Exception(f"Auth exchange failed ({resp.status}): {text}")
                data = await resp.json()
                _LOGGER.debug("Auth response data: %s", data)
                self._jwt_token = data["token"]
                # Parse ISO timestamp to epoch
                from datetime import datetime

                self._jwt_expires_at = datetime.fromisoformat(
                    data["expires_at"].replace("Z", "+00:00")
                ).timestamp()
                _LOGGER.debug("JWT obtained, expires at %s", data["expires_at"])
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during auth: %s", err)
            raise Exception(f"Connection error during auth: {err}")

    async def _request(self, method: str, path: str, data: dict = None) -> dict:
        """Make authenticated API request."""
        _LOGGER.debug("_request called: %s %s", method, path)
        await self._ensure_token()
        session = await self._get_session()
        url = f"{self.endpoint}{path}"
        headers = {
            "Authorization": f"Bearer {self._jwt_token}",
        }
        _LOGGER.debug(
            "Making request to %s with token: %s...",
            url,
            self._jwt_token[:20] if self._jwt_token else None,
        )

        kwargs = {}
        if data is not None:
            headers["Content-Type"] = "application/json"
            kwargs["json"] = data

        try:
            async with session.request(method, url, headers=headers, **kwargs) as resp:
                _LOGGER.debug("Response status: %s", resp.status)
                if resp.status == 401:
                    # Token may have expired, clear and retry once
                    _LOGGER.debug("Got 401, clearing token and retrying")
                    self._jwt_token = None
                    await self._ensure_token()
                    headers["Authorization"] = f"Bearer {self._jwt_token}"
                    async with session.request(
                        method, url, headers=headers, **kwargs
                    ) as retry_resp:
                        if retry_resp.status >= 400:
                            text = await retry_resp.text()
                            raise Exception(f"API error {retry_resp.status}: {text}")
                        return await retry_resp.json()
                if resp.status == 402:
                    raise Exception("Insufficient requests remaining")
                if resp.status >= 400:
                    text = await resp.text()
                    raise Exception(f"API error {resp.status}: {text}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise Exception(f"Connection error: {err}")

    async def list_toolsets(self) -> list[dict]:
        """List all toolsets."""
        return await self._request("GET", "/v1/toolsets")

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()


async def main():
    api_key = "ik_tzghGlJRbfAcCz4mvwopMCMqr6FV4mBSezkK31tJI3eoM6AV"
    endpoint = "https://staging.api.intentgine.dev"

    print(f"Testing with endpoint: {endpoint}")
    print(f"API key: {api_key[:20]}...")
    print()

    client = IntentgineAPIClient(api_key, endpoint)

    try:
        print("Step 1: Calling list_toolsets() (should trigger auth exchange)...")
        toolsets = await client.list_toolsets()
        print(f"SUCCESS: Got {len(toolsets)} toolsets")
        print(f"Toolsets: {toolsets}")
        print()

        print(
            f"JWT token cached: {client._jwt_token[:50] if client._jwt_token else 'NONE'}..."
        )
        print(f"JWT expires at: {client._jwt_expires_at}")

    except Exception as e:
        print(f"FAILED: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
