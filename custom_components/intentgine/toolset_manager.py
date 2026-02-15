"""Toolset manager for Intentgine integration."""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, area_registry as ar

from .const import TOOLSET_PREFIX, TOOLSET_VERSION, TOOLSET_GLOBAL

_LOGGER = logging.getLogger(__name__)


class ToolsetManager:
    """Manage toolsets for Home Assistant entities."""

    def __init__(self, hass: HomeAssistant, api_client):
        """Initialize toolset manager."""
        self.hass = hass
        self.api_client = api_client
        self.toolsets = {}

    def get_exposed_entities(self):
        """Get all entities exposed to voice assistants."""
        entity_reg = er.async_get(self.hass)
        exposed = []

        for entity in entity_reg.entities.values():
            if entity.options.get("conversation", {}).get("should_expose", False):
                state = self.hass.states.get(entity.entity_id)
                if state:
                    exposed.append(
                        {
                            "entity_id": entity.entity_id,
                            "name": state.attributes.get(
                                "friendly_name", entity.entity_id
                            ),
                            "domain": entity.domain,
                            "area_id": entity.area_id,
                        }
                    )

        return exposed

    def group_entities_by_area(self, entities):
        """Group entities by area."""
        by_area = {}
        no_area = []

        for entity in entities:
            area_id = entity.get("area_id")
            if area_id:
                by_area.setdefault(area_id, []).append(entity)
            else:
                no_area.append(entity)

        if no_area:
            by_area["global"] = no_area

        return by_area

    def generate_tools_for_entities(self, entities):
        """Generate domain-based tools for entities."""
        tools = []

        # Group entities by domain
        by_domain = {}
        for entity in entities:
            by_domain.setdefault(entity["domain"], []).append(entity)

        # Create one tool per domain
        for domain, domain_entities in by_domain.items():
            if domain == "light":
                tools.append(
                    {
                        "name": "control_light",
                        "description": "Control lights in this area",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "entity_id": {
                                    "type": "string",
                                    "enum": [e["entity_id"] for e in domain_entities],
                                    "description": "Which light to control",
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["turn_on", "turn_off", "toggle"],
                                    "description": "Action to perform",
                                },
                                "brightness": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 255,
                                    "description": "Brightness level (0-255, optional)",
                                },
                                "color_temp": {
                                    "type": "number",
                                    "description": "Color temperature in mireds (optional)",
                                },
                            },
                            "required": ["entity_id", "action"],
                        },
                    }
                )

            elif domain == "switch":
                tools.append(
                    {
                        "name": "control_switch",
                        "description": "Control switches in this area",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "entity_id": {
                                    "type": "string",
                                    "enum": [e["entity_id"] for e in domain_entities],
                                    "description": "Which switch to control",
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["turn_on", "turn_off", "toggle"],
                                    "description": "Action to perform",
                                },
                            },
                            "required": ["entity_id", "action"],
                        },
                    }
                )

            elif domain == "climate":
                tools.append(
                    {
                        "name": "control_climate",
                        "description": "Control climate devices in this area",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "entity_id": {
                                    "type": "string",
                                    "enum": [e["entity_id"] for e in domain_entities],
                                    "description": "Which climate device to control",
                                },
                                "temperature": {
                                    "type": "number",
                                    "description": "Target temperature (optional)",
                                },
                                "hvac_mode": {
                                    "type": "string",
                                    "enum": [
                                        "heat",
                                        "cool",
                                        "auto",
                                        "off",
                                        "heat_cool",
                                    ],
                                    "description": "HVAC mode (optional)",
                                },
                            },
                            "required": ["entity_id"],
                        },
                    }
                )

            elif domain == "cover":
                tools.append(
                    {
                        "name": "control_cover",
                        "description": "Control covers in this area",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "entity_id": {
                                    "type": "string",
                                    "enum": [e["entity_id"] for e in domain_entities],
                                    "description": "Which cover to control",
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["open", "close", "stop", "toggle"],
                                    "description": "Action to perform",
                                },
                                "position": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 100,
                                    "description": "Position percentage (optional)",
                                },
                            },
                            "required": ["entity_id", "action"],
                        },
                    }
                )

            elif domain == "scene":
                tools.append(
                    {
                        "name": "activate_scene",
                        "description": "Activate a scene",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "entity_id": {
                                    "type": "string",
                                    "enum": [e["entity_id"] for e in domain_entities],
                                    "description": "Which scene to activate",
                                }
                            },
                            "required": ["entity_id"],
                        },
                    }
                )

        return tools

    async def sync_all(self):
        """Sync all toolsets and classification set."""
        _LOGGER.info("Starting toolset sync")

        exposed = self.get_exposed_entities()
        if not exposed:
            _LOGGER.warning("No exposed entities found")
            return

        by_area = self.group_entities_by_area(exposed)
        area_reg = ar.async_get(self.hass)

        # Create classification set for area routing
        area_classes = []
        for area_id in by_area.keys():
            if area_id == "global":
                area_classes.append(
                    {
                        "label": "global",
                        "description": "Scenes, automations, or whole-home commands",
                    }
                )
            else:
                area = area_reg.async_get_area(area_id)
                area_name = area.name if area else area_id
                area_classes.append(
                    {"label": area_id, "description": f"Commands about the {area_name}"}
                )

        # Create or update classification set with extraction enabled
        try:
            await self.api_client.create_classification_set(
                name="Home Assistant Area Router",
                signature="ha-area-router-v1",
                classes=area_classes,
                enable_extraction=True,
            )
            _LOGGER.info(
                "Created classification set with %d areas (extraction enabled)",
                len(area_classes),
            )
        except Exception:
            try:
                await self.api_client.update_classification_set(
                    signature="ha-area-router-v1",
                    name="Home Assistant Area Router",
                    classes=area_classes,
                    enable_extraction=True,
                )
                _LOGGER.info(
                    "Updated classification set with %d areas (extraction enabled)",
                    len(area_classes),
                )
            except Exception as err:
                _LOGGER.error("Failed to create/update classification set: %s", err)

        # Create toolsets (one per area)
        for area_id, entities in by_area.items():
            tools = self.generate_tools_for_entities(entities)
            if not tools:
                continue

            if area_id == "global":
                signature = TOOLSET_GLOBAL
                name = "Home Assistant - Global"
            else:
                area = area_reg.async_get_area(area_id)
                area_name = area.name if area else area_id
                signature = f"{TOOLSET_PREFIX}-{area_id}-{TOOLSET_VERSION}"
                name = f"Home Assistant - {area_name}"

            try:
                await self.api_client.update_toolset(signature, name, tools)
                _LOGGER.info("Updated toolset %s with %d tools", signature, len(tools))
            except Exception:
                try:
                    await self.api_client.create_toolset(name, signature, tools)
                    _LOGGER.info(
                        "Created toolset %s with %d tools", signature, len(tools)
                    )
                except Exception as err:
                    _LOGGER.error("Failed to create toolset %s: %s", signature, err)

            self.toolsets[signature] = tools

        _LOGGER.info("Toolset sync complete")

    def get_all_toolset_signatures(self):
        """Get all toolset signatures."""
        return list(self.toolsets.keys())
