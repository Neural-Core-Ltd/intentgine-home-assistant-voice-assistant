# Natural Language Responses Feature

**Version**: 1.1.0  
**Date**: February 13, 2026

## Overview

The command handler now supports an optional `use_respond` parameter that enables natural language responses instead of just structured tool calls.

## Usage

### Default Behavior (Structured)
```python
result = await command_handler.handle_command("Turn on kitchen lights")
# Returns: {"success": True, "tool": "control_light", ...}
```

### Natural Language Responses
```python
result = await command_handler.handle_command(
    "Turn on kitchen lights",
    use_respond=True
)
# Returns: {"success": True, "response": "I've turned on the kitchen lights", ...}
```

## Examples

### Single-Intent Command

**Without `use_respond` (default)**:
```python
result = await handle_command("Turn on kitchen lights")
```
Response:
```json
{
  "success": true,
  "tool": "control_light",
  "parameters": {
    "entity_id": "light.kitchen_ceiling",
    "action": "turn_on"
  },
  "area": "kitchen",
  "extracted": false
}
```

**With `use_respond=True`**:
```python
result = await handle_command("Turn on kitchen lights", use_respond=True)
```
Response:
```json
{
  "success": true,
  "tool": "control_light",
  "parameters": {
    "entity_id": "light.kitchen_ceiling",
    "action": "turn_on"
  },
  "area": "kitchen",
  "extracted": false,
  "response": "I've turned on the kitchen lights for you."
}
```

### Multi-Intent Command

**Without `use_respond` (default)**:
```python
result = await handle_command("Turn on kitchen lights and turn off bedroom lights")
```
Response:
```json
{
  "success": true,
  "extracted": true,
  "results": [
    {
      "query": "turn on kitchen lights",
      "success": true,
      "tool": "control_light",
      "area": "kitchen"
    },
    {
      "query": "turn off bedroom lights",
      "success": true,
      "tool": "control_light",
      "area": "bedroom"
    }
  ]
}
```

**With `use_respond=True`**:
```python
result = await handle_command(
    "Turn on kitchen lights and turn off bedroom lights",
    use_respond=True
)
```
Response:
```json
{
  "success": true,
  "extracted": true,
  "results": [
    {
      "query": "turn on kitchen lights",
      "success": true,
      "tool": "control_light",
      "area": "kitchen"
    },
    {
      "query": "turn off bedroom lights",
      "success": true,
      "tool": "control_light",
      "area": "bedroom"
    }
  ],
  "response": "I've turned on the kitchen lights for you. I've turned off the bedroom lights."
}
```

## API Endpoints Used

### Default: `/v1/resolve`
- Returns structured tool calls
- No natural language response
- Faster (no response generation)

### With `use_respond=True`: `/v1/respond`
- Returns structured tool calls + natural language response
- Uses app's configured persona
- Slightly slower (includes response generation)

## Cost

**Same cost for both modes**:
- Single-intent: 2 requests
- Multi-intent: 2 + N requests

The `respond` endpoint uses the same number of requests as `resolve`, it just includes response generation.

## Use Cases

### Structured Mode (default)
Best for:
- Automation scripts
- Debugging
- Logging
- When you only need to know what happened

### Natural Language Mode (`use_respond=True`)
Best for:
- Voice assistants
- Chat interfaces
- User-facing applications
- When you want friendly feedback

## Implementation Details

### Command Handler Changes
```python
async def handle_command(self, query: str, use_respond: bool = False):
    """Process a natural language command.
    
    Args:
        query: Natural language command
        use_respond: If True, use respond endpoint for natural language responses.
                    If False (default), use resolve endpoint for structured tool calls.
    """
    # ... classification logic ...
    
    if use_respond:
        result = await self.api_client.respond(query, [toolset_signature])
        response_text = result.get("response", "")
    else:
        result = await self.api_client.resolve(query, [toolset_signature])
    
    # ... execution logic ...
```

### Response Format

**Always includes**:
- `success` (boolean)
- `tool` (string)
- `parameters` (object)
- `area` (string)
- `extracted` (boolean)
- `metadata` (object)

**Additionally includes when `use_respond=True`**:
- `response` (string) - Natural language response

For multi-intent commands, responses are combined with spaces.

## Persona Configuration

The natural language responses use the app's configured persona. Configure this in the Intentgine dashboard:

1. Go to your app settings
2. Navigate to "Personas"
3. Set your preferred persona (friendly, professional, concise, etc.)

Example personas:
- **Friendly**: "I've turned on the kitchen lights for you! 😊"
- **Professional**: "Kitchen lights activated."
- **Concise**: "Done."

## Backward Compatibility

- ✅ Default behavior unchanged (`use_respond=False`)
- ✅ Existing code continues to work
- ✅ Optional parameter, no breaking changes
- ✅ Response structure extended, not changed

## Testing

### Test with Structured Responses
```python
result = await handle_command("Turn on kitchen lights")
assert "tool" in result
assert "response" not in result
```

### Test with Natural Language Responses
```python
result = await handle_command("Turn on kitchen lights", use_respond=True)
assert "tool" in result
assert "response" in result
assert isinstance(result["response"], str)
```

### Test Multi-Intent with Responses
```python
result = await handle_command(
    "Turn on kitchen and bedroom lights",
    use_respond=True
)
assert result["extracted"] == True
assert "response" in result
assert len(result["response"]) > 0
```

## Future Enhancements

Potential improvements:
1. Per-command persona override
2. Response templates
3. Localization support
4. Response streaming for long operations

---

**Status**: ✅ Implemented  
**Version**: 1.1.0  
**Backward Compatible**: Yes
