# Natural Language Responses - Quick Examples

## Single Command

### Structured Response (default)
```python
result = await handle_command("Turn on kitchen lights")
```
```json
{
  "success": true,
  "tool": "control_light",
  "parameters": {"entity_id": "light.kitchen_ceiling", "action": "turn_on"},
  "area": "kitchen"
}
```

### Natural Language Response
```python
result = await handle_command("Turn on kitchen lights", use_respond=True)
```
```json
{
  "success": true,
  "tool": "control_light",
  "parameters": {"entity_id": "light.kitchen_ceiling", "action": "turn_on"},
  "area": "kitchen",
  "response": "I've turned on the kitchen lights for you."
}
```

---

## Multi-Intent Command

### Structured Response (default)
```python
result = await handle_command("Turn on kitchen lights and turn off bedroom lights")
```
```json
{
  "success": true,
  "extracted": true,
  "results": [
    {"query": "turn on kitchen lights", "success": true, "area": "kitchen"},
    {"query": "turn off bedroom lights", "success": true, "area": "bedroom"}
  ]
}
```

### Natural Language Response
```python
result = await handle_command(
    "Turn on kitchen lights and turn off bedroom lights",
    use_respond=True
)
```
```json
{
  "success": true,
  "extracted": true,
  "results": [
    {"query": "turn on kitchen lights", "success": true, "area": "kitchen"},
    {"query": "turn off bedroom lights", "success": true, "area": "bedroom"}
  ],
  "response": "I've turned on the kitchen lights for you. I've turned off the bedroom lights."
}
```

---

## When to Use Each Mode

### Structured Mode (default)
✅ Automation scripts  
✅ Debugging  
✅ Logging  
✅ When you only need to know what happened  

### Natural Language Mode
✅ Voice assistants  
✅ Chat interfaces  
✅ User-facing applications  
✅ When you want friendly feedback  

---

## Cost

**Same cost for both modes**: 2 requests for single-intent, 2 + N for multi-intent

The `respond` endpoint includes response generation at no extra cost.
