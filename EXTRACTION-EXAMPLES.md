# Classification Extraction Examples

This document shows how the Home Assistant integration uses Intentgine's classification extraction feature to handle multi-intent commands.

## What is Classification Extraction?

Classification extraction allows a single command containing multiple intents to be automatically split into separate sub-commands, each classified and resolved independently. This happens transparently in the background with minimal API overhead.

## How It Works

When you issue a command like "turn on kitchen lights and turn off bedroom lights":

1. **Classification with Extraction** (2 requests)
   - The command is sent to the `ha-area-router-v1` classification set (which has `enable_extraction: true`)
   - Intentgine detects multiple intents and extracts them:
     - "turn on kitchen lights" → classified as "kitchen"
     - "turn off bedroom lights" → classified as "bedroom"

2. **Resolution** (N requests, where N = number of extracted commands)
   - Each extracted command is resolved with its area-specific toolset:
     - "turn on kitchen lights" → `ha-kitchen-v1` toolset → `control_light` tool
     - "turn off bedroom lights" → `ha-bedroom-v1` toolset → `control_light` tool

3. **Execution**
   - Both Home Assistant service calls are executed
   - Results are returned together

**Total cost**: 4 requests (2 for classify with extraction + 2 for resolves)

## Example Scenarios

### Scenario 1: Two Lights in Different Areas

**Command**: "Turn on kitchen lights and turn off bedroom lights"

**API Flow**:
```
POST /v1/classify
{
  "data": "Turn on kitchen lights and turn off bedroom lights",
  "classification_set": "ha-area-router-v1"
}

Response:
{
  "results": [{
    "input": "Turn on kitchen lights and turn off bedroom lights",
    "classification": "",
    "extraction_needed": true,
    "confidence": 0.95,
    "extracted": [
      {
        "query": "turn on kitchen lights",
        "classification": "kitchen",
        "confidence": 0.97
      },
      {
        "query": "turn off bedroom lights",
        "classification": "bedroom",
        "confidence": 0.96
      }
    ]
  }],
  "metadata": {
    "requests_used": 2,
    "extraction_performed": true,
    "sub_classifications_performed": 2
  }
}
```

**Then for each extracted command**:
```
POST /v1/resolve
{
  "query": "turn on kitchen lights",
  "toolsets": ["ha-kitchen-v1"]
}

Response:
{
  "resolved": {
    "tool": "control_light",
    "parameters": {
      "entity_id": "light.kitchen_ceiling",
      "action": "turn_on"
    }
  }
}
```

**Home Assistant Execution**:
- `light.turn_on` on `light.kitchen_ceiling`
- `light.turn_off` on `light.bedroom_ceiling`

**Total**: 4 requests (2 classify + 2 resolve)

---

### Scenario 2: Three Actions Across Areas

**Command**: "Turn on kitchen lights, close bedroom blinds, and set living room to 72 degrees"

**Extraction Result**:
```json
{
  "extracted": [
    {
      "query": "turn on kitchen lights",
      "classification": "kitchen",
      "confidence": 0.98
    },
    {
      "query": "close bedroom blinds",
      "classification": "bedroom",
      "confidence": 0.97
    },
    {
      "query": "set living room to 72 degrees",
      "classification": "living_room",
      "confidence": 0.96
    }
  ]
}
```

**Home Assistant Execution**:
- `light.turn_on` on `light.kitchen_ceiling`
- `cover.close_cover` on `cover.bedroom_blinds`
- `climate.set_temperature` on `climate.living_room_thermostat` with `temperature: 72`

**Total**: 5 requests (2 classify + 3 resolve)

---

### Scenario 3: Single Intent (No Extraction)

**Command**: "Turn on kitchen lights"

**API Flow**:
```
POST /v1/classify
{
  "data": "Turn on kitchen lights",
  "classification_set": "ha-area-router-v1"
}

Response:
{
  "results": [{
    "input": "Turn on kitchen lights",
    "classification": "kitchen",
    "extraction_needed": false,
    "confidence": 0.98
  }],
  "metadata": {
    "requests_used": 1,
    "extraction_performed": false
  }
}
```

**Then resolve normally**:
```
POST /v1/resolve
{
  "query": "Turn on kitchen lights",
  "toolsets": ["ha-kitchen-v1"]
}
```

**Total**: 2 requests (1 classify + 1 resolve)

---

## Benefits

### 1. Natural Multi-Intent Commands
Users can speak naturally without needing to issue separate commands:
- ❌ "Turn on kitchen lights" → wait → "Turn off bedroom lights"
- ✅ "Turn on kitchen lights and turn off bedroom lights"

### 2. Efficient API Usage
Extraction happens in a single API call with minimal overhead:
- Manual approach: 1 classify + N additional classifies + N resolves = 1 + 2N requests
- With extraction: 2 classify + N resolves = 2 + N requests
- **Saves N requests** for multi-intent commands

### 3. Transparent to Users
The extraction happens automatically in the background. Users don't need to know about it.

### 4. Accurate Area Routing
Each extracted command is classified independently, ensuring correct area routing even when commands span multiple rooms.

## Implementation Details

### API Client
The `api_client.py` now supports `enable_extraction` parameter when creating/updating classification sets:

```python
await self.api_client.create_classification_set(
    name="Home Assistant Area Router",
    signature="ha-area-router-v1",
    classes=area_classes,
    enable_extraction=True  # Enable extraction
)
```

### Command Handler
The `command_handler.py` checks for extracted results and processes each one:

```python
result_data = classification_result["results"][0]

if result_data.get("extracted"):
    # Handle multiple extracted commands
    for extracted in result_data["extracted"]:
        sub_query = extracted["query"]
        area = extracted["classification"]
        
        # Resolve and execute each
        toolset_signature = f"ha-{area}-v1"
        resolve_result = await self.api_client.resolve(sub_query, [toolset_signature])
        # ... execute tool
else:
    # Single command (original behavior)
    area = result_data["classification"]
    # ... resolve and execute
```

### Toolset Manager
The `toolset_manager.py` enables extraction when syncing the area router classification set:

```python
await self.api_client.create_classification_set(
    name="Home Assistant Area Router",
    signature="ha-area-router-v1",
    classes=area_classes,
    enable_extraction=True
)
```

## Testing

To test extraction, try these commands:

1. **Two areas**: "Turn on kitchen lights and turn off bedroom lights"
2. **Three areas**: "Turn on kitchen, close bedroom blinds, and set living room to 72"
3. **Same area**: "Turn on kitchen lights and set kitchen to 50%" (should extract)
4. **Single intent**: "Turn on kitchen lights" (should NOT extract)

Check the Home Assistant logs to see extraction in action:
```
INFO (MainThread) [custom_components.intentgine.command_handler] Processing 2 extracted commands
```

## Cost Analysis

### Example: 100 Commands per Day

**Scenario A: All single-intent**
- 100 commands × 2 requests = 200 requests/day
- 6,000 requests/month
- **Plan**: Hobbyist ($5/mo) ✅

**Scenario B: 50% multi-intent (2 intents each)**
- 50 single × 2 requests = 100 requests
- 50 multi × 4 requests = 200 requests
- Total: 300 requests/day = 9,000 requests/month
- **Plan**: Hobbyist ($5/mo) ✅

**Scenario C: 50% multi-intent (3 intents each)**
- 50 single × 2 requests = 100 requests
- 50 multi × 5 requests = 250 requests
- Total: 350 requests/day = 10,500 requests/month
- **Plan**: Starter ($29/mo) recommended

## Troubleshooting

### Extraction Not Working

If multi-intent commands aren't being extracted:

1. **Check classification set has extraction enabled**:
   - Trigger a manual sync: `intentgine.sync_toolsets` service
   - Check logs for "extraction enabled" message

2. **Verify command has multiple distinct intents**:
   - "Turn on kitchen and bedroom lights" → should extract
   - "Turn on all lights" → should NOT extract (single intent)

3. **Check API response**:
   - Look for `extraction_needed: true` in classification result
   - Look for `extracted` array in response

### Unexpected Extraction

If single-intent commands are being extracted:

1. **Check command phrasing**:
   - "Turn on kitchen lights and set to 50%" might be interpreted as two intents
   - Try rephrasing: "Set kitchen lights to 50%"

2. **Review extraction logic**:
   - Extraction is determined by the LLM based on the command
   - Different actions (turn on vs turn off) typically trigger extraction
   - Same action on multiple targets may or may not extract

## Future Enhancements

Potential improvements to extraction handling:

1. **Parallel Execution**: Execute all extracted commands in parallel instead of sequentially
2. **Partial Success Handling**: Better feedback when some commands succeed and others fail
3. **Extraction Confidence**: Show users when extraction was performed
4. **Manual Override**: Allow users to disable extraction for specific commands

---

**Note**: This feature requires Intentgine API v1 with classification extraction support (February 2026+).
