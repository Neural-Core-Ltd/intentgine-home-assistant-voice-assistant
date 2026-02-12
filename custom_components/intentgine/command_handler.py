"""Command handler for Intentgine integration."""
import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class CommandHandler:
    """Handle natural language commands."""
    
    def __init__(self, hass: HomeAssistant, api_client, toolset_manager):
        """Initialize command handler."""
        self.hass = hass
        self.api_client = api_client
        self.toolset_manager = toolset_manager
    
    async def handle_command(self, query: str):
        """Process a natural language command with classification."""
        try:
            # Step 1: Classify to determine area (1 request)
            classification_result = await self.api_client.classify(
                query,
                classification_set="ha-area-router-v1",
                context="Home Assistant voice command routing"
            )
            
            area = classification_result["results"][0]["classification"]
            
            # Step 2: Resolve with area-specific toolset (1 request)
            toolset_signature = f"ha-{area}-v1" if area != "global" else "ha-global-v1"
            
            result = await self.api_client.resolve(query, [toolset_signature])
            
            tool_name = result["resolved"]["tool"]
            parameters = result["resolved"]["parameters"]
            
            # Step 3: Execute the tool
            success = await self.execute_tool(tool_name, parameters)
            
            return {
                "success": success,
                "tool": tool_name,
                "parameters": parameters,
                "area": area,
                "metadata": result.get("metadata", {})
            }
        
        except Exception as err:
            _LOGGER.error("Command failed: %s", err)
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
            "stop": "stop_cover"
        }
        
        # For tools without explicit action (like activate_scene)
        if not action:
            if tool_name == "activate_scene":
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
            await self.hass.services.async_call(domain, service, service_data, blocking=True)
            _LOGGER.info("Executed %s.%s on %s", domain, service, entity_id)
            return True
        except Exception as err:
            _LOGGER.error("Service call failed: %s", err)
            return False
