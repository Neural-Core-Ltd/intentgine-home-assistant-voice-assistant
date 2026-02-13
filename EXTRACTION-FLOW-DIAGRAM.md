# Multi-Intent Command Flow Diagram

## Single-Intent Command Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ User Command: "Turn on kitchen lights"                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Classify (1 request)                                   │
│ POST /v1/classify                                               │
│ {                                                               │
│   "data": "Turn on kitchen lights",                             │
│   "classification_set": "ha-area-router-v1"                     │
│ }                                                               │
│                                                                 │
│ Response:                                                       │
│ {                                                               │
│   "results": [{                                                 │
│     "classification": "kitchen",                                │
│     "extraction_needed": false,                                 │
│     "confidence": 0.98                                          │
│   }]                                                            │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Resolve (1 request)                                    │
│ POST /v1/resolve                                                │
│ {                                                               │
│   "query": "Turn on kitchen lights",                            │
│   "toolsets": ["ha-kitchen-v1"]                                 │
│ }                                                               │
│                                                                 │
│ Response:                                                       │
│ {                                                               │
│   "resolved": {                                                 │
│     "tool": "control_light",                                    │
│     "parameters": {                                             │
│       "entity_id": "light.kitchen_ceiling",                     │
│       "action": "turn_on"                                       │
│     }                                                           │
│   }                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Execute                                                 │
│ light.turn_on(entity_id="light.kitchen_ceiling")                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         ✅ Success
                    Total: 2 requests
```

---

## Multi-Intent Command Flow (With Extraction)

```
┌─────────────────────────────────────────────────────────────────┐
│ User Command: "Turn on kitchen lights and turn off bedroom"    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Classify with Extraction (2 requests)                  │
│ POST /v1/classify                                               │
│ {                                                               │
│   "data": "Turn on kitchen lights and turn off bedroom",        │
│   "classification_set": "ha-area-router-v1"                     │
│ }                                                               │
│                                                                 │
│ Response:                                                       │
│ {                                                               │
│   "results": [{                                                 │
│     "classification": "",                                       │
│     "extraction_needed": true,                                  │
│     "confidence": 0.95,                                         │
│     "extracted": [                                              │
│       {                                                         │
│         "query": "turn on kitchen lights",                      │
│         "classification": "kitchen",                            │
│         "confidence": 0.97                                      │
│       },                                                        │
│       {                                                         │
│         "query": "turn off bedroom lights",                     │
│         "classification": "bedroom",                            │
│         "confidence": 0.96                                      │
│       }                                                         │
│     ]                                                           │
│   }],                                                           │
│   "metadata": {                                                 │
│     "requests_used": 2,                                         │
│     "extraction_performed": true,                               │
│     "sub_classifications_performed": 2                          │
│   }                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
┌───────────────────────────────┐ ┌───────────────────────────────┐
│ Step 2a: Resolve #1           │ │ Step 2b: Resolve #2           │
│ (1 request)                   │ │ (1 request)                   │
│                               │ │                               │
│ POST /v1/resolve              │ │ POST /v1/resolve              │
│ {                             │ │ {                             │
│   "query": "turn on kitchen   │ │   "query": "turn off bedroom  │
│            lights",           │ │            lights",           │
│   "toolsets": ["ha-kitchen-v1"]│ │   "toolsets": ["ha-bedroom-v1"]│
│ }                             │ │ }                             │
│                               │ │                               │
│ Response:                     │ │ Response:                     │
│ {                             │ │ {                             │
│   "resolved": {               │ │   "resolved": {               │
│     "tool": "control_light",  │ │     "tool": "control_light",  │
│     "parameters": {           │ │     "parameters": {           │
│       "entity_id":            │ │       "entity_id":            │
│         "light.kitchen_ceiling"│ │         "light.bedroom_ceiling"│
│       "action": "turn_on"     │ │       "action": "turn_off"    │
│     }                         │ │     }                         │
│   }                           │ │   }                           │
│ }                             │ │ }                             │
└───────────────────────────────┘ └───────────────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Execute Both                                            │
│ 1. light.turn_on(entity_id="light.kitchen_ceiling")             │
│ 2. light.turn_off(entity_id="light.bedroom_ceiling")            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         ✅ Success
                    Total: 4 requests
              (2 classify + 2 resolve)
```

---

## Cost Comparison

### Manual Approach (Without Extraction)

```
User: "Turn on kitchen lights and turn off bedroom lights"

Step 1: Classify main query (1 request)
  → Result: extraction_needed = true, but no extraction performed

Step 2: Client manually splits into 2 commands

Step 3: Classify command #1 (1 request)
  → "turn on kitchen lights" → "kitchen"

Step 4: Classify command #2 (1 request)
  → "turn off bedroom lights" → "bedroom"

Step 5: Resolve command #1 (1 request)
  → ha-kitchen-v1 → control_light

Step 6: Resolve command #2 (1 request)
  → ha-bedroom-v1 → control_light

Step 7: Execute both

Total: 5 requests + 3 HTTP round trips
```

### With Extraction (Current Implementation)

```
User: "Turn on kitchen lights and turn off bedroom lights"

Step 1: Classify with extraction (2 requests, 1 HTTP call)
  → Extracts and classifies both commands in single API call

Step 2: Resolve command #1 (1 request, 1 HTTP call)
  → ha-kitchen-v1 → control_light

Step 3: Resolve command #2 (1 request, 1 HTTP call)
  → ha-bedroom-v1 → control_light

Step 4: Execute both

Total: 4 requests + 3 HTTP round trips
Savings: 1 request, same HTTP calls
```

### Key Benefit

The main benefit is **not having to make N additional classify calls**:
- Manual: 1 + N classify calls + N resolve calls = 1 + 2N requests
- With extraction: 2 classify + N resolve calls = 2 + N requests
- **Saves N requests** (where N = number of intents)

For a 3-intent command:
- Manual: 1 + 6 = 7 requests
- With extraction: 2 + 3 = 5 requests
- **Saves 2 requests (29%)**

---

## Implementation in Command Handler

```python
async def handle_command(self, query: str):
    # Step 1: Classify (with extraction if needed)
    classification_result = await self.api_client.classify(
        query,
        classification_set="ha-area-router-v1",
        context="Home Assistant voice command routing"
    )
    
    result_data = classification_result["results"][0]
    
    # Check if extraction was performed
    if result_data.get("extracted"):
        # Multi-intent: Process each extracted command
        results = []
        for extracted in result_data["extracted"]:
            sub_query = extracted["query"]
            area = extracted["classification"]
            
            # Resolve with area-specific toolset
            toolset_signature = f"ha-{area}-v1"
            resolve_result = await self.api_client.resolve(
                sub_query, 
                [toolset_signature]
            )
            
            # Execute
            success = await self.execute_tool(
                resolve_result["resolved"]["tool"],
                resolve_result["resolved"]["parameters"]
            )
            
            results.append({
                "query": sub_query,
                "success": success,
                "area": area
            })
        
        return {
            "success": all(r["success"] for r in results),
            "extracted": True,
            "results": results
        }
    else:
        # Single-intent: Original behavior
        area = result_data["classification"]
        toolset_signature = f"ha-{area}-v1"
        
        result = await self.api_client.resolve(query, [toolset_signature])
        success = await self.execute_tool(
            result["resolved"]["tool"],
            result["resolved"]["parameters"]
        )
        
        return {
            "success": success,
            "extracted": False,
            "area": area
        }
```

---

## Response Format

### Single-Intent Response
```json
{
  "success": true,
  "extracted": false,
  "tool": "control_light",
  "parameters": {
    "entity_id": "light.kitchen_ceiling",
    "action": "turn_on"
  },
  "area": "kitchen",
  "metadata": {
    "requests_used": 2
  }
}
```

### Multi-Intent Response
```json
{
  "success": true,
  "extracted": true,
  "results": [
    {
      "query": "turn on kitchen lights",
      "success": true,
      "tool": "control_light",
      "parameters": {
        "entity_id": "light.kitchen_ceiling",
        "action": "turn_on"
      },
      "area": "kitchen"
    },
    {
      "query": "turn off bedroom lights",
      "success": true,
      "tool": "control_light",
      "parameters": {
        "entity_id": "light.bedroom_ceiling",
        "action": "turn_off"
      },
      "area": "bedroom"
    }
  ],
  "metadata": {
    "requests_used": 4,
    "extraction_performed": true,
    "sub_classifications_performed": 2
  }
}
```
