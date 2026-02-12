"""The Intentgine integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .api_client import IntentgineAPIClient
from .toolset_manager import ToolsetManager
from .command_handler import CommandHandler
from .conversation import async_setup_conversation_agent

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Intentgine from a config entry."""
    api_client = IntentgineAPIClient(
        entry.data["api_key"],
        entry.data.get("endpoint", "https://api.intentgine.dev")
    )
    
    toolset_manager = ToolsetManager(hass, api_client)
    command_handler = CommandHandler(hass, api_client, toolset_manager)
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api_client": api_client,
        "toolset_manager": toolset_manager,
        "command_handler": command_handler,
    }
    
    # Initial sync
    await toolset_manager.sync_all()
    
    # Set up conversation agent
    try:
        await async_setup_conversation_agent(hass, entry)
        _LOGGER.info("Conversation agent registered")
    except Exception as err:
        _LOGGER.warning("Could not register conversation agent: %s", err)
    
    # Register services
    async def handle_execute_command(call):
        """Handle execute_command service."""
        query = call.data.get("query")
        result = await command_handler.handle_command(query)
        return result
    
    async def handle_sync_toolsets(call):
        """Handle sync_toolsets service."""
        await toolset_manager.sync_all()
    
    hass.services.async_register(DOMAIN, "execute_command", handle_execute_command)
    hass.services.async_register(DOMAIN, "sync_toolsets", handle_sync_toolsets)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unregister services
    hass.services.async_remove(DOMAIN, "execute_command")
    hass.services.async_remove(DOMAIN, "sync_toolsets")
    
    # Close API client session
    api_client = hass.data[DOMAIN][entry.entry_id]["api_client"]
    await api_client.close()
    
    # Remove data
    hass.data[DOMAIN].pop(entry.entry_id)
    
    return True
