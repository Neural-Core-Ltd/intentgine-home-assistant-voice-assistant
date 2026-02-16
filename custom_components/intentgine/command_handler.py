"""Command handler for Intentgine integration."""

import logging
import time
from homeassistant.core import HomeAssistant

from .const import CORRECTION_WINDOW_SECONDS

_LOGGER = logging.getLogger(__name__)


class CommandHandler:
    """Handle natural language commands."""

    def __init__(self, hass: HomeAssistant, api_client, toolset_manager):
        """Initialize command handler."""
        self.hass = hass
        self.api_client = api_client
        self.toolset_manager = toolset_manager
        self._last_command: dict | None = None

    def _get_banks(self) -> list[str] | None:
        """Get correction bank list if available."""
        bank_id = self.toolset_manager.correction_bank_id
        return [bank_id] if bank_id else None

    def _save_last_command(self, query: str, tool: str, parameters: dict, area: str):
        """Save command to rolling window for correction detection."""
        self._last_command = {
            "query": query,
            "tool": tool,
            "parameters": parameters,
            "area": area,
            "timestamp": time.time(),
        }

    def _has_recent_command(self) -> bool:
        """Check if there's a recent command within the correction window."""
        if not self._last_command:
            return False
        return (
            time.time() - self._last_command["timestamp"]
        ) < CORRECTION_WINDOW_SECONDS

    async def _handle_correction(self, query: str, use_respond: bool = False):
        """Handle a correction by re-resolving with context and saving to memory bank."""
        prev = self._last_command
        bank_id = self.toolset_manager.correction_bank_id

        # Re-resolve the original query + correction as context, using the same area toolset
        toolset_signature = (
            f"ha-{prev['area']}-v1" if prev["area"] != "global" else "ha-global-v1"
        )

        # Build a combined query: original intent + correction hint
        corrected_query = f"{prev['query']} (correction: {query})"

        if use_respond:
            result = await self.api_client.respond(corrected_query, [toolset_signature])
            response_text = result.get("response", {}).get("text", "")
        else:
            result = await self.api_client.resolve(
                corrected_query, [toolset_signature], banks=self._get_banks()
            )

        tool_name = result["resolved"]["tool"]
        parameters = result["resolved"]["parameters"]

        # Execute the corrected tool
        success = await self.execute_tool(tool_name, parameters)

        # Fire correction to memory bank (original query → correct tool/params)
        if bank_id:
            try:
                await self.api_client.correct(
                    query=prev["query"],
                    correct_tool=tool_name,
                    target_bank=bank_id,
                    correct_params=parameters,
                )
                _LOGGER.info("Correction saved: '%s' → %s", prev["query"], tool_name)
            except Exception as err:
                _LOGGER.warning("Failed to save correction: %s", err)

        # Update rolling window with corrected command
        self._save_last_command(prev["query"], tool_name, parameters, prev["area"])

        response_data = {
            "success": success,
            "tool": tool_name,
            "parameters": parameters,
            "area": prev["area"],
            "corrected": True,
            "original_tool": prev["tool"],
            "extracted": False,
            "metadata": result.get("metadata", {}),
        }

        if use_respond:
            response_data["response"] = response_text

        return response_data

    async def handle_command(
        self, query: str, use_respond: bool = False, use_classify_respond: bool = False
    ):
        """Process a natural language command with classification.

        Args:
            query: Natural language command
            use_respond: If True, use resolve/respond endpoint for natural language responses.
            use_classify_respond: If True, use classify/respond endpoint for chat-like responses.
        """
        # Ensure toolsets are synced (lazy refresh if stale)
        await self.toolset_manager.ensure_synced()

        # If using classify/respond, handle it separately
        if use_classify_respond:
            return await self.handle_command_with_classify_respond(query)

        try:
            # Step 1: Classify to determine area (1-2 requests depending on extraction)
            classification_result = await self.api_client.classify(
                query,
                classification_set="ha-area-router-v1",
                context="Home Assistant voice command routing",
            )

            result_data = classification_result["results"][0]
            area = result_data["classification"]

            # Check for correction classification
            if area == "correction" and self._has_recent_command():
                _LOGGER.info("Correction detected for previous command")
                return await self._handle_correction(query, use_respond)
            elif area == "correction":
                _LOGGER.info("Correction detected but no recent command to correct")
                return {
                    "success": False,
                    "error": "Nothing to correct. No recent command found.",
                }

            banks = self._get_banks()

            # Check if extraction was performed
            if result_data.get("extracted"):
                # Handle multiple extracted commands
                _LOGGER.info(
                    "Processing %d extracted commands", len(result_data["extracted"])
                )
                results = []
                responses = []

                for extracted in result_data["extracted"]:
                    sub_query = extracted["query"]
                    sub_area = extracted["classification"]
                    toolset_signature = (
                        f"ha-{sub_area}-v1" if sub_area != "global" else "ha-global-v1"
                    )

                    if use_respond:
                        respond_result = await self.api_client.respond(
                            sub_query, [toolset_signature]
                        )
                        tool_name = respond_result["resolved"]["tool"]
                        parameters = respond_result["resolved"]["parameters"]
                        response_text = respond_result.get("response", {}).get(
                            "text", ""
                        )
                        responses.append(response_text)
                    else:
                        resolve_result = await self.api_client.resolve(
                            sub_query, [toolset_signature], banks=banks
                        )
                        tool_name = resolve_result["resolved"]["tool"]
                        parameters = resolve_result["resolved"]["parameters"]

                    success = await self.execute_tool(tool_name, parameters)

                    results.append(
                        {
                            "query": sub_query,
                            "success": success,
                            "tool": tool_name,
                            "parameters": parameters,
                            "area": sub_area,
                        }
                    )

                # Save last executed command for correction window
                if results:
                    last = results[-1]
                    self._save_last_command(
                        last["query"], last["tool"], last["parameters"], last["area"]
                    )

                response_data = {
                    "success": all(r["success"] for r in results),
                    "extracted": True,
                    "results": results,
                    "metadata": classification_result.get("metadata", {}),
                }

                if use_respond and responses:
                    response_data["response"] = " ".join(responses)

                return response_data
            else:
                # Single command
                if not area:
                    _LOGGER.error(
                        "No classification found and extraction not performed"
                    )
                    return {
                        "success": False,
                        "error": "Could not classify command. It may contain multiple intents.",
                        "extraction_needed": result_data.get(
                            "extraction_needed", False
                        ),
                    }

                toolset_signature = (
                    f"ha-{area}-v1" if area != "global" else "ha-global-v1"
                )

                if use_respond:
                    result = await self.api_client.respond(query, [toolset_signature])
                    response_text = result.get("response", {}).get("text", "")
                else:
                    result = await self.api_client.resolve(
                        query, [toolset_signature], banks=banks
                    )

                tool_name = result["resolved"]["tool"]
                parameters = result["resolved"]["parameters"]

                success = await self.execute_tool(tool_name, parameters)

                # Save for correction window
                self._save_last_command(query, tool_name, parameters, area)

                response_data = {
                    "success": success,
                    "tool": tool_name,
                    "parameters": parameters,
                    "area": area,
                    "extracted": False,
                    "metadata": result.get("metadata", {}),
                }

                if use_respond:
                    response_data["response"] = response_text

                return response_data

        except Exception as err:
            _LOGGER.error("Command failed: %s", err)
            return {"success": False, "error": str(err)}

    async def handle_command_with_classify_respond(self, query: str):
        """Process command using classify/respond endpoint for chat-like responses."""
        try:
            # Use classify/respond endpoint (2-4 requests depending on extraction)
            result = await self.api_client.classify_respond(
                query,
                classification_set="ha-area-router-v1",
                context="Home Assistant voice command routing",
            )

            response_text = result.get("response", "")
            classifications = result.get("classifications", [])

            # Execute tools for each classification
            results = []
            for classification in classifications:
                area = classification["label"]
                toolset_signature = (
                    f"ha-{area}-v1" if area != "global" else "ha-global-v1"
                )

                # Resolve the specific command for this area
                resolve_result = await self.api_client.resolve(
                    query, [toolset_signature]
                )
                tool_name = resolve_result["resolved"]["tool"]
                parameters = resolve_result["resolved"]["parameters"]

                # Execute the tool
                success = await self.execute_tool(tool_name, parameters)

                results.append(
                    {
                        "success": success,
                        "tool": tool_name,
                        "parameters": parameters,
                        "area": area,
                    }
                )

            return {
                "success": all(r["success"] for r in results),
                "response": response_text,
                "results": results,
                "metadata": result.get("metadata", {}),
            }

        except Exception as err:
            _LOGGER.error("Classify/respond command failed: %s", err)
            return {"success": False, "error": str(err)}

    async def execute_tool(self, tool_name: str, parameters: dict):
        """Execute a tool by calling HA service."""
        entity_id = parameters.get("entity_id")
        action = parameters.get("action")

        if not entity_id:
            _LOGGER.error("Missing entity_id in parameters")
            return False

        # Extract domain from entity_id
        domain = entity_id.split(".")[0]

        # Map action to service
        service_map = {
            "turn_on": "turn_on",
            "turn_off": "turn_off",
            "toggle": "toggle",
            "open": "open_cover",
            "close": "close_cover",
            "stop": "stop_cover",
        }

        # For tools without explicit action
        if not action:
            if tool_name == "activate_scene":
                service = "turn_on"
            elif tool_name == "control_climate":
                # Climate defaults to set_temperature if temperature given, else set_hvac_mode
                if "temperature" in parameters:
                    service = "set_temperature"
                elif "hvac_mode" in parameters:
                    service = "set_hvac_mode"
                else:
                    service = "turn_on"
            else:
                _LOGGER.error("No action specified for tool: %s", tool_name)
                return False
        else:
            service = service_map.get(action, action)

        # Build service data
        service_data = {"entity_id": entity_id}

        # Add optional parameters
        if "brightness" in parameters:
            service_data["brightness"] = parameters["brightness"]
        if "color_temp" in parameters:
            service_data["color_temp"] = parameters["color_temp"]
        if "temperature" in parameters:
            service_data["temperature"] = parameters["temperature"]
        if "hvac_mode" in parameters:
            service_data["hvac_mode"] = parameters["hvac_mode"]
        if "position" in parameters:
            service_data["position"] = parameters["position"]

        try:
            await self.hass.services.async_call(
                domain, service, service_data, blocking=True
            )
            _LOGGER.info("Executed %s.%s on %s", domain, service, entity_id)
            return True
        except Exception as err:
            _LOGGER.error("Service call failed: %s", err)
            return False
