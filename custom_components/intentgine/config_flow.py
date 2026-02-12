"""Config flow for Intentgine integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_API_KEY, CONF_ENDPOINT, DEFAULT_ENDPOINT
from .api_client import IntentgineAPIClient

_LOGGER = logging.getLogger(__name__)

class IntentgineConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Intentgine."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            endpoint = user_input.get(CONF_ENDPOINT, DEFAULT_ENDPOINT)
            
            # Test API connection
            try:
                client = IntentgineAPIClient(api_key, endpoint)
                await client.list_toolsets()
                await client.close()
                
                return self.async_create_entry(
                    title="Intentgine",
                    data={
                        CONF_API_KEY: api_key,
                        CONF_ENDPOINT: endpoint,
                    }
                )
            except Exception as err:
                _LOGGER.error("Failed to connect: %s", err)
                errors["base"] = "cannot_connect"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): str,
            }),
            errors=errors,
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return IntentgineOptionsFlow(config_entry)

class IntentgineOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""
    
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
    
    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("enable_area_toolsets", default=True): bool,
            })
        )
