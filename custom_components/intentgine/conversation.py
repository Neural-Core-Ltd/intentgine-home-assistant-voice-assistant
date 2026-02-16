"""Conversation entity for Intentgine."""

import logging
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up conversation entities."""
    async_add_entities([IntentgineConversationEntity(hass, config_entry)])


class IntentgineConversationEntity(
    conversation.ConversationEntity,
    conversation.AbstractConversationAgent,
):
    """Intentgine conversation agent entity."""

    _attr_has_entity_name = True
    _attr_name = None  # Use device name

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the entity."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_conversation"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": "Intentgine",
            "manufacturer": "Intentgine",
            "model": "Voice Control",
            "entry_type": "service",
        }

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return supported languages."""
        return ["en"]

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        conversation.async_set_agent(self.hass, self.entry, self)
        _LOGGER.info("Intentgine conversation agent registered")

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()
        _LOGGER.info("Intentgine conversation agent unregistered")

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        command_handler = self.hass.data[DOMAIN][self.entry.entry_id]["command_handler"]

        try:
            result = await command_handler.handle_command(user_input.text)

            intent_response = intent.IntentResponse(language=user_input.language)

            if result.get("success"):
                if result.get("corrected"):
                    response_text = (
                        f"Corrected. I executed {result.get('tool', 'the command')} "
                        f"instead of {result.get('original_tool', 'the previous command')}."
                    )
                elif result.get("extracted") and result.get("results"):
                    tools = [r.get("tool", "?") for r in result["results"]]
                    response_text = f"Done. I executed {', '.join(tools)}."
                else:
                    response_text = (
                        f"Done. I executed {result.get('tool', 'the command')}."
                    )
                intent_response.async_set_speech(response_text)
            else:
                error = result.get("error", "Command failed")
                intent_response.async_set_speech(f"Sorry, {error}")

            return conversation.ConversationResult(
                response=intent_response, conversation_id=user_input.conversation_id
            )

        except Exception as err:
            _LOGGER.error("Conversation processing failed: %s", err)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_speech("Sorry, I encountered an error.")
            return conversation.ConversationResult(
                response=intent_response, conversation_id=user_input.conversation_id
            )
