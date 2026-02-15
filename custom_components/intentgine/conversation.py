"""Conversation agent for Intentgine."""

import logging
from homeassistant.components import conversation
from homeassistant.helpers import intent

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class IntentgineConversationAgent(conversation.AbstractConversationAgent):
    """Intentgine conversation agent."""

    def __init__(self, hass, entry):
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry

    @property
    def attribution(self):
        """Return attribution."""
        return {"name": "Intentgine", "url": "https://intentgine.dev"}

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        command_handler = self.hass.data[DOMAIN][self.entry.entry_id]["command_handler"]

        try:
            result = await command_handler.handle_command(user_input.text)

            intent_response = intent.IntentResponse(language=user_input.language)

            if result.get("success"):
                if result.get("extracted") and result.get("results"):
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

    @property
    def supported_languages(self):
        """Return supported languages."""
        return ["en"]


async def async_setup_conversation_agent(hass, entry):
    """Set up the conversation agent."""
    agent = IntentgineConversationAgent(hass, entry)
    conversation.async_set_agent(hass, entry, agent)
    return True
