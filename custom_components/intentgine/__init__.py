"""The Intentgine integration."""

import logging
import os
import traceback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .api_client import IntentgineAPIClient
from .toolset_manager import ToolsetManager
from .command_handler import CommandHandler
from .conversation import async_setup_conversation_agent

_LOGGER = logging.getLogger(__name__)

FRONTEND_REGISTERED = False


def _write_error(msg: str):
    """Write error to file for debugging."""
    try:
        with open("/config/intentgine_setup_error.txt", "a") as f:
            f.write(f"{msg}\n")
    except:
        pass


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Intentgine from a config entry."""
    _LOGGER.info("=== Intentgine async_setup_entry START ===")
    _write_error("=== async_setup_entry START ===")

    try:
        # Register frontend static files (once)
        global FRONTEND_REGISTERED
        if not FRONTEND_REGISTERED:
            _LOGGER.info("Registering frontend...")
            www_path = os.path.join(os.path.dirname(__file__), "www")
            if os.path.isdir(www_path):
                hass.http.register_static_path(
                    f"/intentgine", www_path, cache_headers=True
                )
                _LOGGER.debug("Registered frontend static path: /intentgine")
            FRONTEND_REGISTERED = True
            _LOGGER.info("Frontend registered")

        _LOGGER.info("Creating API client...")
        _write_error(
            f"Creating API client with endpoint: {entry.data.get('endpoint', 'https://api.intentgine.dev')}"
        )
        api_client = IntentgineAPIClient(
            entry.data["api_key"],
            entry.data.get("endpoint", "https://api.intentgine.dev"),
        )
        _LOGGER.info("API client created")

        _LOGGER.info("Creating toolset manager...")
        toolset_manager = ToolsetManager(hass, api_client)
        _LOGGER.info("Toolset manager created")

        _LOGGER.info("Creating command handler...")
        command_handler = CommandHandler(hass, api_client, toolset_manager)
        _LOGGER.info("Command handler created")

        _LOGGER.info("Setting up hass.data...")
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            "api_client": api_client,
            "toolset_manager": toolset_manager,
            "command_handler": command_handler,
        }
        _LOGGER.info("hass.data configured")

        # Initial sync - non-blocking, errors logged but don't fail setup
        _LOGGER.info("Starting toolset sync...")
        try:
            await toolset_manager.sync_all()
            _LOGGER.info("Toolset sync completed")
        except Exception as err:
            _LOGGER.warning("Initial toolset sync failed (will retry later): %s", err)
            _write_error(f"Toolset sync failed: {err}\n{traceback.format_exc()}")

        # Set up conversation agent
        _LOGGER.info("Setting up conversation agent...")
        try:
            await async_setup_conversation_agent(hass, entry)
            _LOGGER.info("Conversation agent registered")
        except Exception as err:
            _LOGGER.warning("Could not register conversation agent: %s", err)
            _write_error(f"Conversation agent failed: {err}\n{traceback.format_exc()}")

        # Register services
        _LOGGER.info("Registering services...")

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
        _LOGGER.info("Services registered")

        _LOGGER.info("=== Intentgine async_setup_entry SUCCESS ===")
        _write_error("=== async_setup_entry SUCCESS ===")
        return True

    except Exception as err:
        _LOGGER.error("=== Intentgine async_setup_entry FAILED ===")
        _LOGGER.error("Error: %s", err)
        _LOGGER.error("Traceback: %s", traceback.format_exc())
        _write_error(
            f"=== async_setup_entry FAILED ===\nError: {err}\n{traceback.format_exc()}"
        )
        raise


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
