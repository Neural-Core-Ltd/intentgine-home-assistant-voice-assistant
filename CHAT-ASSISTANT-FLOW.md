# Home Assistant Chat Assistant Flow

## Overview

The Home Assistant integration uses Intentgine's classification extraction to route and execute voice commands across different areas of your home.

---

## Single-Intent Command Flow

**Example**: "Turn on kitchen lights"

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Input                                               │
│    "Turn on kitchen lights"                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Classification (1 request)                               │
│    POST /v1/classify                                        │
│    {                                                        │
│      "data": "Turn on kitchen lights",                      │
│      "classification_set": "ha-area-router-v1"              │
│    }                                                        │
│                                                             │
│    Response:                                                │
│    {                                                        │
│      "classification": "kitchen",                           │
│      "extraction_needed": false                             │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Resolution (1 request)                                   │
│    POST /v1/resolve                                         │
│    {                                                        │
│      "query": "Turn on kitchen lights",                     │
│      "toolsets": ["ha-kitchen-v1"]                          │
│    }                                                        │
│                                                             │
│    Response:                                                │
│    {                                                        │
│      "tool": "control_light",                               │
│      "parameters": {                                        │
│        "entity_id": "light.kitchen_ceiling",                │
│        "action": "turn_on"                                  │
│      }                                                      │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Execution                                                │
│    Home Assistant Service Call:                             │
│    light.turn_on(entity_id="light.kitchen_ceiling")         │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ✅ Light turns on
                    Total: 2 requests
```

---

## Multi-Intent Command Flow (NEW!)

**Example**: "Turn on kitchen lights and turn off bedroom lights"

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Input                                               │
│    "Turn on kitchen lights and turn off bedroom lights"     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Classification with Extraction (2 requests)              │
│    POST /v1/classify                                        │
│    {                                                        │
│      "data": "Turn on kitchen lights and turn off bedroom   │
│               lights",                                      │
│      "classification_set": "ha-area-router-v1"              │
│    }                                                        │
│                                                             │
│    Response:                                                │
│    {                                                        │
│      "classification": "",                                  │
│      "extraction_needed": true,                             │
│      "extracted": [                                         │
│        {                                                    │
│          "query": "turn on kitchen lights",                 │
│          "classification": "kitchen"                        │
│        },                                                   │
│        {                                                    │
│          "query": "turn off bedroom lights",                │
│          "classification": "bedroom"                        │
│        }                                                    │
│      ]                                                      │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ┌─────────────┴─────────────┐
              ↓                           ↓
┌──────────────────────────┐  ┌──────────────────────────┐
│ 3a. Resolve Command #1   │  │ 3b. Resolve Command #2   │
│     (1 request)          │  │     (1 request)          │
│                          │  │                          │
│ POST /v1/resolve         │  │ POST /v1/resolve         │
│ {                        │  │ {                        │
│   "query": "turn on      │  │   "query": "turn off     │
│            kitchen       │  │            bedroom       │
│            lights",      │  │            lights",      │
│   "toolsets":            │  │   "toolsets":            │
│     ["ha-kitchen-v1"]    │  │     ["ha-bedroom-v1"]    │
│ }                        │  │ }                        │
│                          │  │                          │
│ Response:                │  │ Response:                │
│ {                        │  │ {                        │
│   "tool": "control_light"│  │   "tool": "control_light"│
│   "parameters": {        │  │   "parameters": {        │
│     "entity_id":         │  │     "entity_id":         │
│       "light.kitchen_    │  │       "light.bedroom_    │
│        ceiling",         │  │        ceiling",         │
│     "action": "turn_on"  │  │     "action": "turn_off" │
│   }                      │  │   }                      │
│ }                        │  │ }                        │
└──────────────────────────┘  └──────────────────────────┘
              ↓                           ↓
              └─────────────┬─────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Execution (Sequential)                                   │
│    1. light.turn_on(entity_id="light.kitchen_ceiling")      │
│    2. light.turn_off(entity_id="light.bedroom_ceiling")     │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ✅ Both lights controlled
                  Total: 4 requests
              (2 classify + 2 resolve)
```

---

## Component Breakdown

### 1. Toolset Manager
**Responsibility**: Sync Home Assistant entities with Intentgine

- Discovers all entities exposed to voice assistants
- Groups entities by area (kitchen, bedroom, living room, etc.)
- Creates area-specific toolsets (one per area)
- Creates classification set for area routing with **extraction enabled**

**Toolsets Created**:
- `ha-kitchen-v1` - Tools for kitchen devices
- `ha-bedroom-v1` - Tools for bedroom devices
- `ha-living-room-v1` - Tools for living room devices
- `ha-global-v1` - Tools for scenes and whole-home commands

**Classification Set**:
- `ha-area-router-v1` - Routes commands to correct area
- **Extraction enabled** - Automatically splits multi-intent commands

### 2. Command Handler
**Responsibility**: Process natural language commands

**Flow**:
1. Classify command to determine area(s)
2. Check if extraction was performed
3. If extracted:
   - Process each sub-command
   - Resolve each with area-specific toolset
   - Execute all commands
   - Return aggregated results
4. If not extracted:
   - Resolve with single area toolset
   - Execute command
   - Return result

### 3. API Client
**Responsibility**: Communicate with Intentgine API

**Methods**:
- `classify()` - Classify text to determine area
- `resolve()` - Resolve command to tool call
- `create_classification_set()` - Create classification set with extraction
- `create_toolset()` - Create area-specific toolset

---

## Area-Based Routing

### Why Areas?

Home Assistant organizes devices by physical location. The integration mirrors this:

**Without Areas** (naive approach):
- Single toolset with ALL devices
- LLM must choose from 50+ entities
- Slower, less accurate, more expensive

**With Areas** (our approach):
- Classify to area first (kitchen, bedroom, etc.)
- Resolve with area-specific toolset (only 5-10 entities)
- Faster, more accurate, cheaper

### Example Area Toolset

**ha-kitchen-v1**:
```json
{
  "tools": [
    {
      "name": "control_light",
      "parameters": {
        "entity_id": {
          "enum": [
            "light.kitchen_ceiling",
            "light.kitchen_under_cabinet"
          ]
        },
        "action": {
          "enum": ["turn_on", "turn_off", "toggle"]
        }
      }
    }
  ]
}
```

---

## Cost Analysis

### Single-Intent Command
- Classification: 1 request
- Resolution: 1 request
- **Total: 2 requests**

### Multi-Intent Command (2 intents)
- Classification with extraction: 2 requests
- Resolution #1: 1 request
- Resolution #2: 1 request
- **Total: 4 requests**

### Multi-Intent Command (N intents)
- Classification with extraction: 2 requests
- Resolution × N: N requests
- **Total: 2 + N requests**

### Savings vs Manual Approach
**Manual** (without extraction):
- Classify main: 1 request
- Classify sub #1: 1 request
- Classify sub #2: 1 request
- Resolve #1: 1 request
- Resolve #2: 1 request
- **Total: 5 requests** (for 2 intents)

**With Extraction**:
- Classify with extraction: 2 requests
- Resolve #1: 1 request
- Resolve #2: 1 request
- **Total: 4 requests** (for 2 intents)

**Saves 1 request per multi-intent command!**

---

## Example Scenarios

### Scenario 1: Simple Light Control
```
User: "Turn on kitchen lights"
→ Classify: kitchen (1 req)
→ Resolve: control_light(light.kitchen_ceiling, turn_on) (1 req)
→ Execute: light.turn_on
✅ Total: 2 requests
```

### Scenario 2: Multi-Room Control
```
User: "Turn on kitchen lights and turn off bedroom lights"
→ Classify with extraction: (2 req)
  • "turn on kitchen lights" → kitchen
  • "turn off bedroom lights" → bedroom
→ Resolve #1: control_light(light.kitchen_ceiling, turn_on) (1 req)
→ Resolve #2: control_light(light.bedroom_ceiling, turn_off) (1 req)
→ Execute: light.turn_on + light.turn_off
✅ Total: 4 requests
```

### Scenario 3: Complex Multi-Action
```
User: "Turn on kitchen lights, close bedroom blinds, and set living room to 72"
→ Classify with extraction: (2 req)
  • "turn on kitchen lights" → kitchen
  • "close bedroom blinds" → bedroom
  • "set living room to 72" → living_room
→ Resolve #1: control_light(light.kitchen_ceiling, turn_on) (1 req)
→ Resolve #2: control_cover(cover.bedroom_blinds, close) (1 req)
→ Resolve #3: control_climate(climate.living_room, temp=72) (1 req)
→ Execute: light.turn_on + cover.close + climate.set_temperature
✅ Total: 5 requests
```

### Scenario 4: Scene Activation
```
User: "Activate movie time"
→ Classify: global (1 req)
→ Resolve: activate_scene(scene.movie_time) (1 req)
→ Execute: scene.turn_on
✅ Total: 2 requests
```

---

## Key Features

### 1. Automatic Extraction
- Detects multi-intent commands automatically
- Splits into individual sub-commands
- Classifies each sub-command to correct area
- All in single API call (2 requests)

### 2. Area-Based Routing
- Organizes devices by physical location
- Reduces toolset size for better accuracy
- Mirrors Home Assistant's area structure

### 3. Domain-Based Tools
- One tool per device domain (light, switch, climate, etc.)
- Parameters specify which entity and what action
- Supports optional parameters (brightness, temperature, etc.)

### 4. Backward Compatible
- Single-intent commands work exactly as before
- No breaking changes
- Extraction is transparent to users

---

## Technical Details

### Classification Set Configuration
```python
{
  "name": "Home Assistant Area Router",
  "signature": "ha-area-router-v1",
  "enable_extraction": True,  # ← Enables multi-intent support
  "classes": [
    {"label": "kitchen", "description": "Commands about the kitchen"},
    {"label": "bedroom", "description": "Commands about the bedroom"},
    {"label": "living_room", "description": "Commands about the living room"},
    {"label": "global", "description": "Scenes, automations, whole-home"}
  ]
}
```

### Command Handler Logic
```python
# Classify command
result = await classify(query, "ha-area-router-v1")

if result.get("extracted"):
    # Multi-intent: Process each extracted command
    for extracted in result["extracted"]:
        area = extracted["classification"]
        toolset = f"ha-{area}-v1"
        resolved = await resolve(extracted["query"], [toolset])
        await execute(resolved)
else:
    # Single-intent: Process normally
    area = result["classification"]
    toolset = f"ha-{area}-v1"
    resolved = await resolve(query, [toolset])
    await execute(resolved)
```

---

## Summary

The Home Assistant chat assistant now intelligently handles both single and multi-intent commands:

1. **Classifies** commands to determine area(s) - with automatic extraction for multi-intent
2. **Resolves** each command to specific tool calls using area-specific toolsets
3. **Executes** all Home Assistant service calls
4. **Returns** structured results with success/failure for each action

**Cost**: 2 requests for single-intent, 2 + N requests for multi-intent (where N = number of intents)

**Benefit**: Natural multi-room control in a single command with minimal API overhead
