# Home Assistant Intentgine Integration - Architecture

**Version**: 1.0  
**Last Updated**: 2026-02-12

## Overview

This document describes the technical architecture of the Home Assistant Intentgine integration.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Home Assistant                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Intentgine Integration                      │    │
│  │                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │ Config Flow  │  │   API Client │  │ Toolset  │ │    │
│  │  │              │  │              │  │ Manager  │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │    │
│  │                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │   Command    │  │ Conversation │  │ Lovelace │ │    │
│  │  │   Handler    │  │    Agent     │  │  Cards   │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Home Assistant Core Services                │    │
│  │  (light, climate, scene, automation, etc.)          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
                ┌───────────────────────┐
                │   Intentgine API      │
                │  api.intentgine.dev   │
                └───────────────────────┘
```

## Component Architecture

### 1. Integration Entry Point (`__init__.py`)

**Responsibilities**:
- Integration lifecycle management
- Component initialization
- Service registration
- Event listener setup

**Key Functions**:
```python
async def async_setup_entry(hass, entry):
    """Set up Intentgine from a config entry."""
    # Initialize API client
    # Initialize toolset manager
    # Register services
    # Set up event listeners
    # Schedule initial sync
    
async def async_unload_entry(hass, entry):
    """Unload Intentgine config entry."""
    # Clean up resources
    # Unregister services
    # Cancel scheduled tasks
```

### 2. Config Flow (`config_flow.py`)

**Responsibilities**:
- User-facing configuration UI
- API key validation
- Options management

**Flow Steps**:
1. User Input: API key, endpoint URL
2. Validation: Test API connection
3. Success: Create config entry
4. Options: Allow reconfiguration

**Key Classes**:
```python
class IntentgineConfigFlow(config_entries.ConfigFlow):
    """Handle config flow for Intentgine."""
    
    async def async_step_user(self, user_input):
        """Handle initial step."""
        
    async def async_step_validate(self, user_input):
        """Validate API credentials."""
        
class IntentgineOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""
    
    async def async_step_init(self, user_input):
        """Manage options."""
```

### 3. API Client (`api_client.py`)

**Responsibilities**:
- HTTP communication with Intentgine API
- Request/response handling
- Error handling and retries
- Rate limiting awareness

**Key Methods**:
```python
class IntentgineAPIClient:
    def __init__(self, api_key, endpoint):
        self.api_key = api_key
        self.endpoint = endpoint
        self.session = aiohttp.ClientSession()
    
    async def resolve(self, query, toolsets, banks=None):
        """Call /v1/resolve endpoint."""
        
    async def respond(self, query, toolsets, persona=None):
        """Call /v1/respond endpoint."""
        
    async def classify(self, data, classification_set):
        """Call /v1/classify endpoint."""
        
    async def create_toolset(self, name, signature, tools):
        """Create a new toolset."""
        
    async def update_toolset(self, signature, tools):
        """Update existing toolset."""
        
    async def get_toolset(self, signature):
        """Get toolset by signature."""
        
    async def list_toolsets(self):
        """List all toolsets."""
        
    async def delete_toolset(self, signature):
        """Delete a toolset."""
```

### 4. Toolset Manager (`toolset_manager.py`)

**Responsibilities**:
- Generate tools from HA entities
- Synchronize toolsets with Intentgine API
- Track toolset state and changes
- Handle entity updates

**Key Methods**:
```python
class ToolsetManager:
    def __init__(self, hass, api_client):
        self.hass = hass
        self.api_client = api_client
        self.toolsets = {}  # Cache of current toolsets
        
    async def sync_all(self):
        """Sync all toolsets with current HA state."""
        
    async def sync_area(self, area_id):
        """Sync toolset for specific area."""
        
    def generate_tools_for_entities(self, entities):
        """Generate Intentgine tools from HA entities."""
        
    def get_exposed_entities(self):
        """Get all entities exposed to voice assistants."""
        
    def group_entities_by_area(self, entities):
        """Group entities by their area."""
        
    async def handle_entity_change(self, event):
        """Handle entity registry updates."""
```

### 5. Command Handler (`command_handler.py`)

**Responsibilities**:
- Process natural language commands
- Map resolved tools to HA service calls
- Execute service calls
- Handle errors and provide feedback

**Key Methods**:
```python
class CommandHandler:
    def __init__(self, hass, api_client, toolset_manager):
        self.hass = hass
        self.api_client = api_client
        self.toolset_manager = toolset_manager
        
    async def handle_command(self, query, context=None):
        """Process a natural language command."""
        # 1. Get relevant toolsets
        # 2. Call Intentgine API
        # 3. Map to HA service call
        # 4. Execute service call
        # 5. Return result
        
    def map_tool_to_service(self, tool_name, parameters):
        """Map Intentgine tool to HA service call."""
        
    async def execute_service_call(self, domain, service, data):
        """Execute HA service call with error handling."""
        
    def validate_entity_access(self, entity_id):
        """Ensure entity is exposed for voice control."""
```

### 6. Conversation Agent (`conversation.py`)

**Responsibilities**:
- Integrate with HA conversation system
- Intercept voice/text commands
- Provide conversational responses

**Key Classes**:
```python
class IntentgineConversationAgent(conversation.AbstractConversationAgent):
    """Intentgine conversation agent."""
    
    async def async_process(self, user_input):
        """Process user input through Intentgine."""
        # Use CommandHandler to process
        # Return conversation response
        
    @property
    def supported_languages(self):
        """Return supported languages."""
        return ["en"]  # Expand based on Intentgine support
```

### 7. Lovelace Cards

#### Command Card (`lovelace/intentgine-command-card.js`)

Simple text input + button interface.

**Features**:
- Text input field
- Submit button
- Loading state
- Success/error messages
- Command history (optional)

#### Chat Card (`lovelace/intentgine-chat-card.js`)

Conversational chat interface.

**Features**:
- Message history
- User/assistant message bubbles
- Typing indicator
- Action confirmations
- Persona selection

## Data Flow

### Command Execution Flow

```
User Input
    │
    ▼
┌─────────────────────┐
│  Lovelace Card /    │
│  Conversation Agent │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Command Handler    │
└─────────────────────┘
    │
    ├─► Get Toolsets (from ToolsetManager)
    │
    ▼
┌─────────────────────┐
│  API Client         │
│  POST /v1/resolve   │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Intentgine API     │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Command Handler    │
│  (map tool to svc)  │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  HA Service Call    │
│  (light.turn_on)    │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Device Action      │
└─────────────────────┘
    │
    ▼
User Feedback
```

### Toolset Synchronization Flow

```
Trigger (entity change, manual, scheduled)
    │
    ▼
┌─────────────────────┐
│  Toolset Manager    │
│  sync_all()         │
└─────────────────────┘
    │
    ├─► Get exposed entities
    ├─► Group by area
    │
    ▼
For each area:
    │
    ├─► Generate tools
    ├─► Compute content hash
    │
    ▼
┌─────────────────────┐
│  API Client         │
│  get_toolset()      │
└─────────────────────┘
    │
    ▼
Compare hashes
    │
    ├─► If changed ──► update_toolset()
    └─► If new ──────► create_toolset()
```

## Tool Generation Strategy

### Entity Domain Mapping

Each HA entity domain maps to specific tool patterns:

#### Light Domain
```python
{
    "name": "turn_on_light_living_room_main",
    "description": "Turn on the main light in the living room",
    "parameters": {
        "type": "object",
        "properties": {
            "brightness": {
                "type": "number",
                "description": "Brightness 0-255",
                "minimum": 0,
                "maximum": 255
            },
            "color_temp": {
                "type": "number",
                "description": "Color temperature in mireds"
            },
            "rgb_color": {
                "type": "array",
                "description": "RGB color [r,g,b]",
                "items": {"type": "number", "minimum": 0, "maximum": 255},
                "minItems": 3,
                "maxItems": 3
            }
        }
    }
}
```

#### Climate Domain
```python
{
    "name": "set_temperature_bedroom",
    "description": "Set temperature in the bedroom",
    "parameters": {
        "type": "object",
        "properties": {
            "temperature": {
                "type": "number",
                "description": "Target temperature"
            },
            "hvac_mode": {
                "type": "string",
                "enum": ["heat", "cool", "auto", "off"],
                "description": "HVAC mode"
            }
        },
        "required": ["temperature"]
    }
}
```

#### Scene Domain
```python
{
    "name": "activate_scene_movie_time",
    "description": "Activate the movie time scene",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}
```

### Tool Naming Convention

Format: `{action}_{domain}_{entity_name}`

Examples:
- `turn_on_light_living_room_main`
- `turn_off_switch_kitchen_coffee_maker`
- `set_temperature_climate_bedroom`
- `activate_scene_good_morning`

### Area-Based Organization

Toolsets organized by area for better context and caching:

- `ha-living-room-v1`: All living room entities
- `ha-bedroom-v1`: All bedroom entities
- `ha-kitchen-v1`: All kitchen entities
- `ha-global-v1`: Area-less entities, scenes, automations

## Service Call Mapping

### Mapping Table

```python
TOOL_TO_SERVICE_MAP = {
    "turn_on_light": ("light", "turn_on"),
    "turn_off_light": ("light", "turn_off"),
    "toggle_light": ("light", "toggle"),
    "set_temperature": ("climate", "set_temperature"),
    "set_hvac_mode": ("climate", "set_hvac_mode"),
    "turn_on_switch": ("switch", "turn_on"),
    "turn_off_switch": ("switch", "turn_off"),
    "activate_scene": ("scene", "turn_on"),
    "trigger_automation": ("automation", "trigger"),
    "open_cover": ("cover", "open_cover"),
    "close_cover": ("cover", "close_cover"),
    # ... etc
}
```

### Parameter Transformation

Some parameters need transformation:

```python
def transform_parameters(tool_name, params):
    """Transform Intentgine params to HA service data."""
    
    # Extract entity_id from tool name
    entity_id = extract_entity_id_from_tool_name(tool_name)
    
    service_data = {"entity_id": entity_id}
    
    # Copy relevant parameters
    if "brightness" in params:
        service_data["brightness"] = params["brightness"]
    
    if "temperature" in params:
        service_data["temperature"] = params["temperature"]
    
    # ... etc
    
    return service_data
```

## Error Handling

### Error Categories

1. **API Errors**: Intentgine API issues
2. **Resolution Errors**: No tool matched or ambiguous
3. **Service Errors**: HA service call failures
4. **Permission Errors**: Entity not exposed

### Error Response Format

```python
{
    "success": False,
    "error": {
        "type": "resolution_failed",
        "message": "I don't understand that command",
        "details": "No matching tool found for query"
    }
}
```

### Retry Strategy

- **API timeouts**: Retry up to 3 times with exponential backoff
- **Rate limits**: Queue command and retry after delay
- **Service unavailable**: Fail immediately with clear message

## Configuration Storage

### Config Entry Data

```python
{
    "api_key": "sk_live_...",
    "endpoint": "https://api.intentgine.dev",
    "sync_frequency": "daily",  # or "hourly", "manual"
    "enable_area_toolsets": True,
    "default_persona": "helpful"
}
```

### Runtime State

Stored in `hass.data[DOMAIN]`:

```python
{
    "api_client": IntentgineAPIClient(...),
    "toolset_manager": ToolsetManager(...),
    "command_handler": CommandHandler(...),
    "last_sync": datetime(...),
    "toolset_cache": {...}
}
```

## Performance Considerations

### Caching

1. **Toolset Cache**: Cache toolset signatures and content hashes in memory
2. **Entity Cache**: Cache exposed entity list (invalidate on registry change)
3. **API Response Cache**: Intentgine handles semantic caching automatically

### Optimization

1. **Lazy Sync**: Only sync changed toolsets
2. **Batch Updates**: Group multiple entity changes into single sync
3. **Async Operations**: All API calls are async, non-blocking
4. **Debouncing**: Debounce entity change events (wait 5s for more changes)

### Resource Limits

- Max toolsets: Based on Intentgine plan
- Max tools per toolset: 100 (recommended)
- Max concurrent API calls: 5
- Sync timeout: 30 seconds

## Security

### API Key Storage

- Stored in HA's secure credential storage
- Never logged or exposed in frontend
- Encrypted at rest

### Entity Access Control

- Only exposed entities can be controlled
- Read access to all entities (for context)
- Respects HA's existing permission system

### Input Validation

- Sanitize all user input
- Validate entity IDs before service calls
- Validate API responses before processing

## Testing Strategy

### Unit Tests

- `test_api_client.py`: API client methods
- `test_toolset_manager.py`: Tool generation logic
- `test_command_handler.py`: Service call mapping
- `test_config_flow.py`: Configuration flow

### Integration Tests

- Mock Intentgine API responses
- Test full command flow
- Test toolset synchronization
- Test error handling

### Manual Testing

- Real Home Assistant instance
- Real Intentgine API
- Various entity types and configurations
- Edge cases and error scenarios

## Deployment

### File Structure

```
custom_components/intentgine/
├── __init__.py
├── manifest.json
├── config_flow.py
├── const.py
├── api_client.py
├── toolset_manager.py
├── command_handler.py
├── conversation.py
├── strings.json
├── translations/
│   └── en.json
└── lovelace/
    ├── intentgine-command-card.js
    └── intentgine-chat-card.js
```

### Dependencies

```json
{
  "requirements": ["aiohttp>=3.8.0"],
  "dependencies": []
}
```

### Version Strategy

- Semantic versioning: MAJOR.MINOR.PATCH
- Breaking changes: Bump MAJOR
- New features: Bump MINOR
- Bug fixes: Bump PATCH
