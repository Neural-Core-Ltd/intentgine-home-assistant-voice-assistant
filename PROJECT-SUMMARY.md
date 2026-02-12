# Project Summary - Home Assistant Intentgine Integration

**Status**: Requirements & Architecture Complete  
**Next Step**: Begin Phase 1 Implementation  
**Last Updated**: 2026-02-12

## Quick Context

This is a Home Assistant custom integration that enables natural language control of smart home devices using the Intentgine API. Users can type commands like "turn on living room lights" and the integration resolves them to Home Assistant service calls.

## What's Been Done

### ✅ Planning Phase Complete

1. **REQUIREMENTS.md** - Comprehensive requirements document covering:
   - Three implementation approaches (conversation agent, chat interface, simple widget)
   - Security model (only exposed entities)
   - Dynamic toolset management strategy (area-based)
   - API integration details
   - Sync strategy
   - Error handling
   - Testing strategy
   - Success metrics

2. **ARCHITECTURE.md** - Detailed technical design including:
   - System architecture diagram
   - Component breakdown (7 main components)
   - Data flow diagrams
   - Tool generation strategy
   - Service call mapping
   - Error handling patterns
   - Performance considerations
   - Security measures

3. **IMPLEMENTATION.md** - Phase-by-phase tracker with:
   - 4 implementation phases
   - Detailed task breakdown
   - Decision log
   - Performance metrics
   - Development commands

4. **README.md** - User-facing documentation with:
   - Installation instructions
   - Configuration guide
   - Usage examples
   - Troubleshooting
   - Development setup

5. **docs-fixes.md** (project root) - Documents API gaps found:
   - Missing toolset CRUD endpoint documentation
   - Missing classification set CRUD endpoint documentation
   - Missing `/v1/resolve-quick` documentation
   - Corrections needed in Getting Started guide

## Key Architectural Decisions

### 1. Toolset Organization: Area-Based
- One toolset per area (e.g., `ha-living-room-v1`)
- One global toolset for area-less entities
- **Why**: Better context, improved caching, manageable sizes
- **Alternative rejected**: Single global toolset (simpler but less efficient)

### 2. Entity Exposure: Use HA's Existing System
- Only entities marked "exposed to voice assistants" can be controlled
- Read access to all entities (for context)
- **Why**: Respects existing user security settings
- **Alternative rejected**: Custom exposure system (duplicate config)

### 3. Implementation Approach: Progressive Enhancement
- **Phase 1**: Simple dashboard card (guaranteed to work)
- **Phase 3**: Conversation agent integration (if possible)
- **Why**: Faster MVP, can enhance later
- **Alternative rejected**: Start with conversation agent (riskier)

### 4. Classification: Optional Optimization
- Start without classification (simpler)
- Add later if needed for performance
- **Why**: One less API call, simpler code
- **Alternative rejected**: Use classification from start (more complex)

## Tool Generation Strategy

### Entity → Tool Mapping

Each Home Assistant entity becomes multiple tools:

**Light Example**:
```json
{
  "name": "turn_on_light_living_room_main",
  "description": "Turn on the main light in the living room",
  "parameters": {
    "type": "object",
    "properties": {
      "brightness": {"type": "number", "minimum": 0, "maximum": 255},
      "color_temp": {"type": "number"},
      "rgb_color": {"type": "array", "items": {"type": "number"}}
    }
  }
}
```

### Supported Domains (Phase 2)
- light (turn_on, turn_off, set_brightness, set_color)
- switch (turn_on, turn_off)
- climate (set_temperature, set_hvac_mode)
- cover (open, close, set_position)
- scene (activate)
- automation (trigger, enable, disable)
- media_player (play, pause, volume)
- fan (turn_on, turn_off, set_speed)

## Sync Strategy

### Triggers
1. Initial setup (create all toolsets)
2. Entity changes (update affected toolsets)
3. Area changes (update affected toolsets)
4. Manual sync (user-triggered)
5. Periodic sync (daily/hourly)

### Process
1. Get all exposed entities
2. Group by area
3. Generate tools for each area
4. Compare content hash with existing toolset
5. Update only if changed
6. Debounce entity changes (wait 5s for more)

## API Endpoints Used

### Intentgine API

**Primary**:
- `POST /v1/resolve` - Resolve command to tool (1 request)
- `POST /v1/respond` - Resolve + natural response (2 requests)

**Toolset Management** (needs documentation):
- `POST /v1/toolsets` - Create toolset
- `PUT /v1/toolsets/{signature}` - Update toolset
- `GET /v1/toolsets` - List toolsets
- `GET /v1/toolsets/{signature}` - Get toolset
- `DELETE /v1/toolsets/{signature}` - Delete toolset

**Optional**:
- `POST /v1/classify` - Route to area (1 request)
- `POST /v1/correct` - Learn from corrections

## File Structure

```
example-app/
├── REQUIREMENTS.md          ✅ Complete
├── ARCHITECTURE.md          ✅ Complete
├── IMPLEMENTATION.md        ✅ Complete
├── README.md                ✅ Complete
├── custom_components/       ⏭️ Next: Create
│   └── intentgine/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── const.py
│       ├── api_client.py
│       ├── toolset_manager.py
│       ├── command_handler.py
│       ├── conversation.py
│       ├── strings.json
│       ├── translations/
│       │   └── en.json
│       └── lovelace/
│           ├── intentgine-command-card.js
│           └── intentgine-chat-card.js
├── tests/                   ⏭️ Next: Create
│   ├── test_api_client.py
│   ├── test_toolset_manager.py
│   └── test_command_handler.py
└── docs/                    ⏭️ Later
    ├── installation.md
    ├── configuration.md
    └── usage.md
```

## Next Steps (Phase 1)

### 1. Project Setup (30 min)
- Create directory structure
- Create `manifest.json`
- Create `const.py` with constants
- Create `strings.json` and translations

### 2. API Client (2-3 hours)
- Implement `IntentgineAPIClient` class
- Implement `resolve()` method
- Implement error handling and retries
- Write unit tests

### 3. Config Flow (2-3 hours)
- Implement `IntentgineConfigFlow`
- Add API key input and validation
- Add options flow for reconfiguration
- Test in HA UI

### 4. Integration Entry Point (1-2 hours)
- Implement `async_setup_entry()`
- Initialize API client
- Implement `async_unload_entry()`
- Test load/unload

### 5. Basic Tool Generation (3-4 hours)
- Implement `ToolsetManager` class
- Implement entity discovery
- Implement tool generation for lights/switches
- Create single global toolset
- Test with sample entities

### 6. Command Handler (3-4 hours)
- Implement `CommandHandler` class
- Implement tool-to-service mapping
- Implement service call execution
- Add error handling
- Test with real HA

### 7. Simple Lovelace Card (2-3 hours)
- Create `intentgine-command-card.js`
- Implement UI (input, button, feedback)
- Add styling
- Test in HA frontend

**Total Phase 1 Estimate**: 15-20 hours

## Development Environment

### Requirements
- Home Assistant 2024.1+
- Python 3.11+
- Intentgine API key (get from intentgine.dev)

### Setup
```bash
# Navigate to project
cd /home/jr/Code/intent-engine/example-app

# Create HA test config (if needed)
mkdir -p ha-test-config/custom_components

# Symlink integration for testing
ln -s $(pwd)/custom_components/intentgine ha-test-config/custom_components/

# Run HA in dev mode
hass -c ha-test-config/
```

### Testing
```bash
# Run unit tests
pytest tests/

# Check config
hass --script check_config -c ha-test-config/

# Lint
pylint custom_components/intentgine/
black custom_components/intentgine/
```

## Key Resources

### Home Assistant
- [Developer Docs](https://developers.home-assistant.io/)
- [Integration Example](https://github.com/home-assistant/example-custom-config)
- [Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- [Entity Registry](https://developers.home-assistant.io/docs/entity_registry_index)

### Intentgine
- [API Docs](https://docs.intentgine.dev/) (in `/docs` folder)
- [API Implementation](../supabase/functions/) (source of truth)
- [Types](../supabase/functions/_shared/types.ts) (interface contracts)

### HACS
- [HACS Docs](https://hacs.xyz/)
- [Integration Requirements](https://hacs.xyz/docs/publish/integration)

## Known Challenges

### 1. Toolset API Endpoints Not Documented
**Status**: Endpoints exist in code but not in docs  
**Solution**: Infer from code, test during development, document in `docs-fixes.md`  
**Impact**: Low (can work around)

### 2. Conversation Agent Integration Unknown
**Status**: Need to research if HA allows custom conversation agents  
**Solution**: Research in Phase 1, implement in Phase 3 if possible  
**Impact**: Medium (affects UX but not core functionality)

### 3. Tool Generation Complexity
**Status**: Many entity domains with different parameters  
**Solution**: Start with lights/switches, add domains incrementally  
**Impact**: Low (phased approach)

### 4. Sync Performance with Many Entities
**Status**: Unknown how it performs with 100+ entities  
**Solution**: Implement debouncing, lazy sync, test with large configs  
**Impact**: Medium (may need optimization)

## Success Criteria

### Phase 1 MVP
- ✅ User can install integration
- ✅ User can configure with API key
- ✅ User can control lights and switches via text input
- ✅ Commands resolve correctly >80% of the time
- ✅ Service calls execute without errors >90% of the time

### Phase 2 Enhanced
- ✅ Automatic toolset sync works
- ✅ All major domains supported
- ✅ Area-based organization works
- ✅ Performance acceptable with 100+ entities

### Phase 3 Advanced
- ✅ Conversation agent integration (if possible)
- ✅ Chat interface works
- ✅ Memory banks improve accuracy over time

### Phase 4 Release
- ✅ Published to HACS
- ✅ Documentation complete
- ✅ Test coverage >80%
- ✅ Community feedback positive

## Questions to Answer During Implementation

1. **Can we hook into HA's conversation system?**
   - Research `conversation.AbstractConversationAgent`
   - Test if we can register as a conversation agent
   - Document findings

2. **What's the actual toolset API?**
   - Test endpoints during development
   - Document request/response formats
   - Update `docs-fixes.md`

3. **How should we handle entity naming?**
   - Use friendly names or entity IDs in descriptions?
   - How to handle duplicate names?
   - Test what works best with Intentgine

4. **What's the optimal toolset size?**
   - Test with 10, 50, 100 tools per toolset
   - Measure resolution accuracy and speed
   - Document recommendations

5. **Should we use classification?**
   - Implement without first
   - Measure performance
   - Add if needed for optimization

## How to Resume

When picking up this project:

1. **Read this file first** (you're here!)
2. **Review REQUIREMENTS.md** for full context
3. **Check IMPLEMENTATION.md** for current phase tasks
4. **Review ARCHITECTURE.md** for technical details
5. **Start with Phase 1.1** (Project Setup)

All the planning is done. Time to build! 🚀
