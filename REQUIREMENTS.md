# Home Assistant Intentgine Integration - Requirements

**Version**: 1.0  
**Last Updated**: 2026-02-12  
**Status**: Planning Phase

## Executive Summary

A Home Assistant custom integration that enables natural language control of Home Assistant devices and automations using the Intentgine API. Users can type or speak commands that are intelligently resolved to Home Assistant service calls.

## Project Goals

1. **Primary**: Enable natural language control of Home Assistant entities via Intentgine API
2. **Secondary**: Demonstrate Intentgine's capabilities as a reference implementation
3. **Tertiary**: Provide open-source integration for the Home Assistant community

## Core Requirements

### 1. Integration Architecture

**Type**: Custom Component (HACS-compatible)  
**Domain**: `intentgine`  
**Platform Support**: All Home Assistant installations (Core, Supervised, OS, Container)

### 2. User Experience Approaches (Priority Order)

#### Approach A: Conversation Agent Integration (PREFERRED)
- Hook into Home Assistant's built-in conversation/voice assistant system
- Register as a conversation agent that can be selected in HA settings
- Intercepts voice/text commands before default processing
- Seamlessly integrates with existing voice assistants (Assist, Alexa, Google)
- **Benefit**: Native UX, works with all existing voice input methods

#### Approach B: Custom Chat Interface (FALLBACK)
- Custom Lovelace card with text input field
- Uses `/v1/respond` endpoint for conversational responses
- Displays both the action taken and natural language confirmation
- **Benefit**: Full control over UX, can show rich responses

#### Approach C: Dashboard Widget (MINIMUM VIABLE)
- Simple Lovelace card with text input + "Run" button
- Resolves command and executes service call
- Shows success/error feedback
- **Benefit**: Simplest implementation, guaranteed to work

**Decision**: Implement Approach A if possible, fall back to B, with C as absolute minimum.

### 3. Security & Permissions

#### Entity Exposure Model
- **Read Access**: All entities (for context and responses)
- **Write Access**: Only entities marked as "exposed to voice assistants" in HA
- Respects Home Assistant's existing `expose_entity` configuration
- Users control what can be controlled via standard HA settings

#### API Key Management
- API key stored in Home Assistant's secure credential storage
- Configurable via integration config flow (UI-based setup)
- Never exposed in logs or frontend

### 4. Intentgine API Integration

#### Dynamic Toolset Management

The integration must dynamically create and update toolsets based on the user's Home Assistant configuration.

**Toolset Strategy**: Area-based organization
- One toolset per area (e.g., `ha-living-room-v1`, `ha-bedroom-v1`, `ha-kitchen-v1`)
- One global toolset for area-less entities and scenes (`ha-global-v1`)
- Toolsets updated when entities are added/removed/reconfigured

**Tool Structure**:
```json
{
  "name": "turn_on_light",
  "description": "Turn on a light in the living room",
  "parameters": {
    "type": "object",
    "properties": {
      "entity_id": {
        "type": "string",
        "enum": ["light.living_room_main", "light.living_room_lamp"],
        "description": "The light to turn on"
      },
      "brightness": {
        "type": "number",
        "description": "Brightness level 0-255",
        "minimum": 0,
        "maximum": 255
      }
    },
    "required": ["entity_id"]
  }
}
```

**Tool Categories**:
1. **Device Controls**: `turn_on`, `turn_off`, `toggle`, `set_temperature`, `set_brightness`, etc.
2. **Scenes**: `activate_scene` with scene entity IDs
3. **Automations**: `trigger_automation`, `enable_automation`, `disable_automation`
4. **Queries**: `get_state`, `get_temperature`, `is_on`, etc. (read-only)

#### Classification Sets (Optional Enhancement)

Use classification to route commands to the correct area/domain:

**Classification Set**: `ha-area-router-v1`
```json
{
  "classes": [
    {"label": "living_room", "description": "Commands about living room devices"},
    {"label": "bedroom", "description": "Commands about bedroom devices"},
    {"label": "kitchen", "description": "Commands about kitchen devices"},
    {"label": "global", "description": "Whole-home commands, scenes, or automations"}
  ]
}
```

**Flow**:
1. Classify query to determine area → 1 request
2. Resolve using area-specific toolset → 1 request
3. Total: 2 requests per command

**Alternative**: Skip classification, use all toolsets in resolve call (may be slower but simpler)

#### API Endpoints Used

1. **POST /v1/resolve** - Primary endpoint for command resolution
   - Input: `query`, `toolsets[]`, optional `banks[]`
   - Output: `resolved.tool`, `resolved.parameters`
   - Cost: 1 request

2. **POST /v1/respond** - For conversational interfaces (Approach B)
   - Input: `query`, `toolsets[]`, optional `persona`
   - Output: `resolved` + `response.text`
   - Cost: 2 requests

3. **POST /v1/classify** - For area routing (optional)
   - Input: `data`, `classification_set`
   - Output: `results[].classification`
   - Cost: 1 request

4. **Toolset Management** (via Console API - needs documentation check):
   - `POST /v1/toolsets` - Create toolset
   - `PUT /v1/toolsets/{signature}` - Update toolset
   - `DELETE /v1/toolsets/{signature}` - Delete toolset
   - `GET /v1/toolsets` - List toolsets

5. **Classification Set Management** (if using):
   - `POST /v1/classification-sets` - Create set
   - `PUT /v1/classification-sets/{signature}` - Update set

### 5. Home Assistant Service Execution

#### Service Call Mapping

Map resolved tools to Home Assistant service calls:

```python
TOOL_TO_SERVICE_MAP = {
    "turn_on_light": "light.turn_on",
    "turn_off_light": "light.turn_off",
    "set_climate_temperature": "climate.set_temperature",
    "activate_scene": "scene.turn_on",
    "trigger_automation": "automation.trigger",
    # ... etc
}
```

#### Parameter Transformation

Transform Intentgine parameters to HA service data:

```python
# Intentgine output:
{
  "tool": "turn_on_light",
  "parameters": {
    "entity_id": "light.living_room_main",
    "brightness": 200
  }
}

# Home Assistant service call:
hass.services.call(
    domain="light",
    service="turn_on",
    service_data={
        "entity_id": "light.living_room_main",
        "brightness": 200
    }
)
```

#### Error Handling

- Invalid entity_id → User-friendly error message
- Service call failure → Log and notify user
- API errors → Graceful degradation with helpful messages
- Rate limiting → Queue commands or notify user

### 6. Configuration & Setup

#### Config Flow (UI-based)

Step 1: API Configuration
- Intentgine API Key (required)
- API Endpoint URL (default: `https://api.intentgine.dev`, allow custom for self-hosted)
- Test connection button

Step 2: Options
- Enable/disable area-based toolsets
- Sync frequency (how often to update toolsets)
- Default persona for responses (if using /v1/respond)

#### Options Flow

Allow users to reconfigure:
- API key rotation
- Sync settings
- Enable/disable specific areas
- Manual sync trigger

### 7. Toolset Synchronization

#### Sync Triggers

1. **Initial Setup**: Create all toolsets on integration load
2. **Entity Changes**: Update toolsets when entities are added/removed/renamed
3. **Area Changes**: Update toolsets when areas are modified
4. **Manual Sync**: User-triggered via integration options
5. **Periodic Sync**: Optional scheduled sync (default: daily)

#### Sync Logic

```python
async def sync_toolsets(hass):
    """Synchronize Home Assistant entities to Intentgine toolsets."""
    
    # Get all exposed entities
    exposed_entities = get_exposed_entities(hass)
    
    # Group by area
    entities_by_area = group_entities_by_area(exposed_entities)
    
    # For each area, create/update toolset
    for area_id, entities in entities_by_area.items():
        tools = generate_tools_for_entities(entities)
        signature = f"ha-{area_id}-v1"
        
        # Check if toolset exists
        existing = await api_client.get_toolset(signature)
        
        if existing:
            # Update if changed
            if tools_changed(existing.tools, tools):
                await api_client.update_toolset(signature, tools)
        else:
            # Create new
            await api_client.create_toolset(
                name=f"Home Assistant - {area_id}",
                signature=signature,
                tools=tools
            )
```

#### Tool Generation

```python
def generate_tools_for_entities(entities):
    """Generate Intentgine tools from HA entities."""
    tools = []
    
    for entity in entities:
        domain = entity.domain
        
        if domain == "light":
            tools.append({
                "name": f"turn_on_{entity.entity_id.replace('.', '_')}",
                "description": f"Turn on {entity.name}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brightness": {"type": "number", "minimum": 0, "maximum": 255},
                        "color_temp": {"type": "number"}
                    }
                }
            })
            tools.append({
                "name": f"turn_off_{entity.entity_id.replace('.', '_')}",
                "description": f"Turn off {entity.name}",
                "parameters": {"type": "object", "properties": {}}
            })
        
        elif domain == "climate":
            # Generate climate control tools
            pass
        
        # ... etc for each domain
    
    return tools
```

### 8. Memory Banks (Future Enhancement)

#### Learning from Corrections

Use `/v1/correct` endpoint to improve accuracy over time:

```python
async def handle_user_correction(query, wrong_tool, correct_tool):
    """Learn from user corrections."""
    await api_client.correct(
        query=query,
        wrong_tool=wrong_tool,
        correct_tool=correct_tool,
        bank="ha-user-corrections"
    )
```

#### Bank Strategy

- `ha-user-corrections`: User-specific corrections
- `ha-common-patterns`: Pre-populated common commands
- Assign both banks to all resolve calls

### 9. Frontend Components

#### Lovelace Card (Approach C - Minimum)

```yaml
type: custom:intentgine-command-card
title: Voice Command
placeholder: "Turn on living room lights"
show_history: true
```

Features:
- Text input field
- Submit button
- Loading state during API call
- Success/error feedback
- Optional: Command history (last 5 commands)

#### Chat Interface (Approach B)

```yaml
type: custom:intentgine-chat-card
title: Home Assistant Chat
persona: friendly
show_resolved_actions: true
```

Features:
- Chat-like interface with message history
- Shows both user input and assistant responses
- Displays resolved actions (e.g., "✓ Turned on living room lights")
- Typing indicator during processing

### 10. Error Handling & Edge Cases

#### API Errors

- **401 Unauthorized**: Invalid API key → Show setup prompt
- **402 Payment Required**: Out of requests → Show billing message with link
- **429 Rate Limited**: Too many requests → Queue or show retry message
- **500 Server Error**: Intentgine issue → Fallback to HA default processing

#### Resolution Failures

- **No tool matched**: "I don't understand that command"
- **Ambiguous command**: Ask for clarification
- **Entity not exposed**: "That device is not available for voice control"

#### Service Call Failures

- **Entity unavailable**: "That device is currently unavailable"
- **Invalid parameters**: "I couldn't set that value"
- **Permission denied**: Should not happen (only exposed entities)

### 11. Performance & Optimization

#### Caching Strategy

- Intentgine handles semantic caching automatically
- Local cache of toolset signatures (avoid re-fetching)
- Cache entity → tool mappings in memory

#### Request Optimization

- Batch toolset updates when possible
- Only sync changed toolsets (compare content hashes)
- Use classification to reduce toolset size per request (optional)

#### Rate Limiting

- Respect user's Intentgine plan limits
- Show remaining requests in integration UI
- Warn when approaching limit

### 12. Installation & Distribution

#### HACS (Home Assistant Community Store)

- Publish as HACS custom integration
- Follow HACS repository structure
- Provide `hacs.json` manifest

#### Manual Installation

- Copy `custom_components/intentgine/` to HA config directory
- Restart Home Assistant
- Add integration via UI

#### Requirements

```json
{
  "domain": "intentgine",
  "name": "Intentgine Voice Control",
  "documentation": "https://github.com/intentgine/ha-integration",
  "requirements": ["aiohttp>=3.8.0"],
  "codeowners": ["@intentgine"],
  "config_flow": true,
  "iot_class": "cloud_polling",
  "version": "1.0.0"
}
```

### 13. Documentation Requirements

#### User Documentation

1. **Installation Guide**
   - HACS installation steps
   - Manual installation steps
   - Initial configuration

2. **Configuration Guide**
   - Getting Intentgine API key
   - Exposing entities to voice control
   - Setting up areas for better organization

3. **Usage Guide**
   - Example commands
   - How to use with different interfaces
   - Troubleshooting common issues

4. **Advanced Topics**
   - Custom toolset strategies
   - Memory banks and learning
   - Integration with other voice assistants

#### Developer Documentation

1. **Architecture Overview**
   - Component structure
   - API client implementation
   - Toolset synchronization logic

2. **Contributing Guide**
   - Development setup
   - Testing procedures
   - Pull request process

3. **API Reference**
   - Internal APIs
   - Extension points

### 14. Testing Strategy

#### Unit Tests

- API client methods
- Tool generation logic
- Parameter transformation
- Error handling

#### Integration Tests

- Full command flow (mock Intentgine API)
- Toolset synchronization
- Service call execution
- Config flow

#### Manual Testing Checklist

- [ ] Install via HACS
- [ ] Configure with valid API key
- [ ] Sync toolsets successfully
- [ ] Execute basic commands (turn on/off)
- [ ] Execute complex commands (set brightness, temperature)
- [ ] Test with unexposed entities (should fail gracefully)
- [ ] Test with invalid commands
- [ ] Test API key rotation
- [ ] Test with multiple areas
- [ ] Test conversation agent integration (if implemented)

### 15. Success Metrics

#### Functional Success

- ✅ Commands resolve correctly >90% of the time
- ✅ Service calls execute without errors >95% of the time
- ✅ Setup takes <5 minutes for average user
- ✅ Toolset sync completes in <30 seconds

#### User Experience Success

- ✅ Natural language commands work as expected
- ✅ Error messages are clear and actionable
- ✅ No noticeable latency (<2s from command to execution)
- ✅ Integration doesn't break existing HA functionality

#### Technical Success

- ✅ No memory leaks
- ✅ Handles 100+ entities without performance degradation
- ✅ Graceful handling of API failures
- ✅ Proper cleanup on integration removal

## Implementation Phases

### Phase 1: Core Foundation (MVP)
- [ ] Basic integration structure
- [ ] Config flow for API key
- [ ] API client implementation
- [ ] Simple toolset generation (global only)
- [ ] Basic command resolution
- [ ] Service call execution
- [ ] Simple Lovelace card (Approach C)

### Phase 2: Enhanced Functionality
- [ ] Area-based toolset organization
- [ ] Automatic toolset synchronization
- [ ] Support for all major entity domains
- [ ] Better error handling and user feedback
- [ ] Command history

### Phase 3: Advanced Features
- [ ] Conversation agent integration (Approach A)
- [ ] Chat interface (Approach B)
- [ ] Classification-based routing
- [ ] Memory banks and learning
- [ ] Advanced parameter handling

### Phase 4: Polish & Distribution
- [ ] Comprehensive documentation
- [ ] HACS publication
- [ ] Example configurations
- [ ] Video tutorials
- [ ] Community support setup

## Open Questions & Decisions Needed

1. **Toolset Granularity**: Area-based vs. domain-based vs. single global?
   - **Decision**: Area-based with global fallback (best balance)

2. **Classification Usage**: Use classification for routing or just resolve with all toolsets?
   - **Decision**: Start without classification, add as optimization if needed

3. **Conversation Agent**: Can we actually hook into HA's conversation system?
   - **Decision**: Research during Phase 1, implement in Phase 3 if possible

4. **Toolset API**: Are there public endpoints for toolset CRUD operations?
   - **Action Required**: Document these endpoints or note if they're console-only

5. **Entity Exposure**: Use HA's existing expose_entity or create our own?
   - **Decision**: Use existing HA exposure settings (respects user's existing config)

## Technical Constraints

1. **Home Assistant Version**: Minimum 2023.1 (for modern config flow)
2. **Python Version**: 3.11+ (HA requirement)
3. **Intentgine API**: Requires active subscription with available requests
4. **Network**: Requires internet connectivity (cloud API)

## Non-Goals (Out of Scope)

- ❌ Local-only operation (Intentgine is cloud-based)
- ❌ Custom LLM training
- ❌ Direct device control without Intentgine API
- ❌ Support for non-exposed entities (security requirement)
- ❌ Billing/subscription management (handled by Intentgine console)

## File Structure

```
example-app/
├── REQUIREMENTS.md (this file)
├── ARCHITECTURE.md (detailed technical design)
├── IMPLEMENTATION.md (implementation progress tracker)
├── README.md (user-facing documentation)
├── custom_components/
│   └── intentgine/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── const.py
│       ├── api_client.py
│       ├── toolset_manager.py
│       ├── command_handler.py
│       ├── conversation.py (if Approach A)
│       ├── translations/
│       │   └── en.json
│       └── lovelace/
│           ├── intentgine-command-card.js
│           └── intentgine-chat-card.js
├── tests/
│   ├── test_api_client.py
│   ├── test_toolset_manager.py
│   └── test_command_handler.py
└── docs/
    ├── installation.md
    ├── configuration.md
    ├── usage.md
    └── troubleshooting.md
```

## Next Steps

1. ✅ Document requirements (this file)
2. ⏭️ Create ARCHITECTURE.md with detailed technical design
3. ⏭️ Research Home Assistant conversation agent integration
4. ⏭️ Document Intentgine toolset management API endpoints
5. ⏭️ Begin Phase 1 implementation
