"""Intentgine API client."""

import logging
import time
import aiohttp
from typing import Any

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
            # Use a more permissive SSL context and explicit timeout
            import ssl

            ssl_context = ssl.create_default_context()
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
            _LOGGER.info("Created new aiohttp session for endpoint: %s", self.endpoint)
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
        _LOGGER.info("Exchanging API key for JWT at %s", url)

        try:
            _LOGGER.info("About to POST to %s", url)
            async with session.post(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                _LOGGER.info("Auth response status: %s", resp.status)
                if resp.status == 401:
                    raise Exception("Invalid API key")
                if resp.status >= 400:
                    text = await resp.text()
                    raise Exception(f"Auth exchange failed ({resp.status}): {text}")
                data = await resp.json()
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
                if resp.status == 401:
                    # Token may have expired, clear and retry once
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

    async def resolve(
        self, query: str, toolsets: list[str], banks: list[str] = None
    ) -> dict:
        """Resolve query to tool call."""
        data = {"query": query, "toolsets": toolsets}
        if banks:
            data["banks"] = banks
        return await self._request("POST", "/v1/resolve", data)

    async def classify(
        self, data_text: str, classification_set: str, context: str = None
    ) -> dict:
        """Classify text."""
        data = {"data": data_text, "classification_set": classification_set}
        if context:
            data["context"] = context
        return await self._request("POST", "/v1/classify", data)

    async def respond(
        self, query: str, toolsets: list[str], persona: str = None
    ) -> dict:
        """Resolve and generate response."""
        data = {"query": query, "toolsets": toolsets}
        if persona:
            data["persona"] = persona
        return await self._request("POST", "/v1/resolve-respond", data)

    async def classify_respond(
        self,
        data_text: str,
        classification_set: str = None,
        classes: list[dict] = None,
        context: str = None,
    ) -> dict:
        """Classify text and generate conversational response."""
        data = {"data": data_text}
        if classification_set:
            data["classification_set"] = classification_set
        elif classes:
            data["classes"] = classes
        else:
            raise ValueError("Either classification_set or classes must be provided")
        if context:
            data["context"] = context
        return await self._request("POST", "/v1/classify-respond", data)

    async def create_toolset(
        self, name: str, signature: str, tools: list[dict], description: str = None
    ) -> dict:
        """Create a toolset."""
        data = {"name": name, "signature": signature, "tools": tools}
        if description:
            data["description"] = description
        return await self._request("POST", "/v1/toolsets", data)

    async def update_toolset(
        self, signature: str, name: str, tools: list[dict], description: str = None
    ) -> dict:
        """Update a toolset."""
        data = {"name": name, "tools": tools}
        if description:
            data["description"] = description
        return await self._request("PUT", f"/v1/toolsets/{signature}", data)

    async def get_toolset(self, signature: str) -> dict:
        """Get a toolset."""
        return await self._request("GET", f"/v1/toolsets/{signature}")

    async def list_toolsets(self) -> list[dict]:
        """List all toolsets."""
        _LOGGER.info("list_toolsets() called - starting request flow")
        try:
            result = await self._request("GET", "/v1/toolsets")
            _LOGGER.info("list_toolsets() completed successfully")
            return result
        except Exception as e:
            _LOGGER.error("list_toolsets() failed: %s", e)
            raise

    async def create_classification_set(
        self,
        name: str,
        signature: str,
        classes: list[dict],
        description: str = None,
        enable_extraction: bool = False,
    ) -> dict:
        """Create a classification set."""
        data = {
            "name": name,
            "signature": signature,
            "classes": classes,
            "enable_extraction": enable_extraction,
        }
        if description:
            data["description"] = description
        return await self._request("POST", "/v1/classification-sets", data)

    async def update_classification_set(
        self,
        signature: str,
        name: str,
        classes: list[dict],
        description: str = None,
        enable_extraction: bool = False,
    ) -> dict:
        """Update a classification set."""
        data = {
            "name": name,
            "classes": classes,
            "enable_extraction": enable_extraction,
        }
        if description:
            data["description"] = description
        return await self._request("PUT", f"/v1/classification-sets/{signature}", data)

    async def list_banks(self) -> list[dict]:
        """List all memory banks."""
        return await self._request("GET", "/v1/banks")

    async def create_bank(self, name: str, description: str = None) -> dict:
        """Create a memory bank."""
        data = {"name": name}
        if description:
            data["description"] = description
        return await self._request("POST", "/v1/banks", data)

    async def assign_bank(self, bank_id: str) -> dict:
        """Assign a memory bank to the current app."""
        return await self._request("POST", f"/v1/banks/{bank_id}/assign")

    async def correct(
        self,
        query: str,
        correct_tool: str,
        target_bank: str,
        correct_params: dict = None,
    ) -> dict:
        """Submit a correction to a memory bank."""
        data = {
            "query": query,
            "correct_tool": correct_tool,
            "target_bank": target_bank,
        }
        if correct_params:
            data["correct_params"] = correct_params
        return await self._request("POST", "/v1/correct", data)

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
