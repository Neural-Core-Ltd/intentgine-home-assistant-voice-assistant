"""Intentgine API client."""
import logging
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
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _request(self, method: str, path: str, data: dict = None) -> dict:
        """Make API request."""
        session = await self._get_session()
        url = f"{self.endpoint}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with session.request(method, url, json=data, headers=headers) as resp:
                if resp.status == 401:
                    raise Exception("Invalid API key")
                if resp.status == 402:
                    raise Exception("Insufficient requests remaining")
                if resp.status >= 400:
                    text = await resp.text()
                    raise Exception(f"API error {resp.status}: {text}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise Exception(f"Connection error: {err}")
    
    async def resolve(self, query: str, toolsets: list[str], banks: list[str] = None) -> dict:
        """Resolve query to tool call."""
        data = {"query": query, "toolsets": toolsets}
        if banks:
            data["banks"] = banks
        return await self._request("POST", "/v1/resolve", data)
    
    async def classify(self, data_text: str, classification_set: str, context: str = None) -> dict:
        """Classify text."""
        data = {"data": data_text, "classification_set": classification_set}
        if context:
            data["context"] = context
        return await self._request("POST", "/v1/classify", data)
    
    async def respond(self, query: str, toolsets: list[str], persona: str = None) -> dict:
        """Resolve and generate response."""
        data = {"query": query, "toolsets": toolsets}
        if persona:
            data["persona"] = persona
        return await self._request("POST", "/v1/resolve-respond", data)
    
    async def classify_respond(self, data_text: str, classification_set: str = None, classes: list[dict] = None, context: str = None) -> dict:
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
    
    async def create_toolset(self, name: str, signature: str, tools: list[dict], description: str = None) -> dict:
        """Create a toolset."""
        data = {"name": name, "signature": signature, "tools": tools}
        if description:
            data["description"] = description
        return await self._request("POST", "/v1/toolsets", data)
    
    async def update_toolset(self, signature: str, name: str, tools: list[dict], description: str = None) -> dict:
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
        return await self._request("GET", "/v1/toolsets")
    
    async def create_classification_set(self, name: str, signature: str, classes: list[dict], description: str = None, enable_extraction: bool = False) -> dict:
        """Create a classification set."""
        data = {"name": name, "signature": signature, "classes": classes, "enable_extraction": enable_extraction}
        if description:
            data["description"] = description
        return await self._request("POST", "/v1/classification-sets", data)
    
    async def update_classification_set(self, signature: str, name: str, classes: list[dict], description: str = None, enable_extraction: bool = False) -> dict:
        """Update a classification set."""
        data = {"name": name, "classes": classes, "enable_extraction": enable_extraction}
        if description:
            data["description"] = description
        return await self._request("PUT", f"/v1/classification-sets/{signature}", data)
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
