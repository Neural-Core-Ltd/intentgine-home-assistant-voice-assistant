# Classification Extraction - Quick Reference

## What Is It?

Classification extraction automatically splits multi-intent commands into separate sub-commands, each classified and resolved independently.

**Example**: "Turn on kitchen lights and turn off bedroom lights"
- ✅ Automatically splits into 2 commands
- ✅ Each classified to correct area
- ✅ Each resolved and executed
- ✅ All in one user request

## When Does It Trigger?

Extraction happens when:
- ✅ Classification set has `enable_extraction: true`
- ✅ LLM detects multiple distinct intents
- ✅ Different actions (turn on vs turn off)
- ✅ Different devices (lights vs thermostat)
- ✅ Different areas (kitchen vs bedroom)

Extraction does NOT happen when:
- ❌ Single intent ("turn on kitchen lights")
- ❌ Same action on multiple targets ("turn on all lights")
- ❌ Classification set has `enable_extraction: false`

## Cost

| Command Type | Requests | Example |
|--------------|----------|---------|
| Single-intent | 2 | "Turn on kitchen lights" |
| 2 intents | 4 | "Turn on kitchen and turn off bedroom" |
| 3 intents | 5 | "Turn on kitchen, close bedroom blinds, set living room to 72" |
| N intents | 2 + N | Formula: 2 for classify + N for resolves |

**Savings vs Manual**: N requests saved (no need for N additional classify calls)

## API Response Format

### Without Extraction
```json
{
  "results": [{
    "classification": "kitchen",
    "extraction_needed": false,
    "confidence": 0.98
  }],
  "metadata": {
    "requests_used": 1
  }
}
```

### With Extraction
```json
{
  "results": [{
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

## Code Examples

### Enable Extraction (Toolset Manager)
```python
await self.api_client.create_classification_set(
    name="Home Assistant Area Router",
    signature="ha-area-router-v1",
    classes=area_classes,
    enable_extraction=True  # ← Enable here
)
```

### Handle Extraction (Command Handler)
```python
result_data = classification_result["results"][0]

if result_data.get("extracted"):
    # Multi-intent: Process each extracted command
    for extracted in result_data["extracted"]:
        sub_query = extracted["query"]
        area = extracted["classification"]
        
        # Resolve and execute each
        toolset = f"ha-{area}-v1"
        resolve_result = await self.api_client.resolve(sub_query, [toolset])
        await self.execute_tool(...)
else:
    # Single-intent: Original behavior
    area = result_data["classification"]
    # ... resolve and execute
```

## Testing Commands

| Command | Expected Behavior |
|---------|-------------------|
| "Turn on kitchen lights" | No extraction (single intent) |
| "Turn on kitchen and bedroom lights" | Extract 2 commands |
| "Turn on kitchen lights and turn off bedroom lights" | Extract 2 commands |
| "Turn on kitchen, close bedroom blinds, set living room to 72" | Extract 3 commands |
| "Turn on all lights" | No extraction (single intent) |

## Troubleshooting

### Extraction Not Working
1. Check classification set has `enable_extraction: true`
2. Trigger manual sync: `intentgine.sync_toolsets`
3. Check logs for "extraction enabled" message
4. Verify command has multiple distinct intents

### Unexpected Extraction
1. Check command phrasing (might be ambiguous)
2. Try rephrasing to be more explicit
3. Review logs to see what LLM detected

### Partial Failures
- If one extracted command fails, others still execute
- Check response for individual success flags
- Review logs for specific error messages

## Log Messages

```
INFO: Created classification set with 5 areas (extraction enabled)
INFO: Processing 2 extracted commands
INFO: Executed light.turn_on on light.kitchen_ceiling
INFO: Executed light.turn_off on light.bedroom_ceiling
```

## Files Modified (v1.1.0)

- `api_client.py` - Added `enable_extraction` parameter
- `command_handler.py` - Handle extraction results
- `toolset_manager.py` - Enable extraction on area router
- `README.md` - Document multi-intent commands
- `CHANGELOG.md` - v1.1.0 release notes

## Documentation

- **[EXTRACTION-EXAMPLES.md](EXTRACTION-EXAMPLES.md)** - Comprehensive guide with examples
- **[EXTRACTION-FLOW-DIAGRAM.md](EXTRACTION-FLOW-DIAGRAM.md)** - Visual flow diagrams
- **[EXTRACTION-INTEGRATION-SUMMARY.md](EXTRACTION-INTEGRATION-SUMMARY.md)** - Implementation summary
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## Quick Stats

- **Version**: 1.1.0
- **Release Date**: 2026-02-13
- **Breaking Changes**: None (backward compatible)
- **New Dependencies**: None
- **API Version Required**: v1 with extraction support

## Support

- Check logs: `custom_components/intentgine/`
- Test script: `test_extraction.py`
- GitHub Issues: Report bugs or request features
- Intentgine Docs: [intentgine.dev/docs](https://intentgine.dev/docs)

---

**TL;DR**: Enable extraction on classification sets to automatically handle multi-intent commands. Costs 2 + N requests (where N = number of intents). Saves N requests vs manual approach. Backward compatible.
