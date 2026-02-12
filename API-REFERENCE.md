# Intentgine API Quick Reference

**For Home Assistant Integration Development**  
**Source**: Code analysis from `/supabase/functions/`

## Base URL

```
https://api.intentgine.dev
```

## Authentication

All requests require Bearer token authentication:

```
Authorization: Bearer sk_live_YOUR_API_KEY
```

## Core Endpoints

### POST /v1/resolve

Resolve a query to a tool call using registered toolsets.

**Request**:
```json
{
  "query": "Turn on the living room lights",
  "toolsets": ["ha-living-room-v1", "ha-global-v1"],
  "banks": ["optional-memory-bank-id"]
}
```

**Response**:
```json
{
  "resolved": {
    "tool": "turn_on_light_living_room_main",
    "parameters": {
      "brightness": 255
    }
  },
  "metadata": {
    "source": "cache",
    "used_banks": [],
    "latency_ms": 120,
    "requests_used": 1,
    "requests_remaining": 9999,
    "defaults_applied": []
  }
}
```

**Cost**: 1 request

---

### POST /v1/resolve-quick

Resolve a query using inline tools (no toolset registration needed).

**Request**:
```json
{
  "query": "Turn on the lights",
  "tools": [
    {
      "name": "turn_on_lights",
      "description": "Turn on lights in a room",
      "parameters": {
        "type": "object",
        "properties": {
          "room": {"type": "string"}
        }
      }
    }
  ],
  "banks": []
}
```

**Response**: Same as `/v1/resolve`

**Cost**: 1 request

**Use Case**: Testing, ad-hoc queries, before toolsets are set up

---

### POST /v1/respond

Resolve query and generate natural language response.

**Request**:
```json
{
  "query": "Turn on the living room lights",
  "toolsets": ["ha-living-room-v1"],
  "banks": [],
  "persona": "helpful"
}
```

**Response**:
```json
{
  "resolved": {
    "tool": "turn_on_light_living_room_main",
    "parameters": {}
  },
  "response": {
    "text": "I'll turn on the living room lights for you."
  },
  "metadata": {
    "source": "cache",
    "used_banks": [],
    "latency_ms": 150,
    "requests_used": 2,
    "requests_remaining": 9998,
    "defaults_applied": []
  }
}
```

**Cost**: 2 requests

**Use Case**: Conversational interfaces, chat bots

---

### POST /v1/classify

Classify text into predefined categories.

**Request**:
```json
{
  "data": "Turn on the bedroom lights",
  "classification_set": "ha-area-router-v1",
  "context": "Home automation command routing"
}
```

**Response**:
```json
{
  "results": [
    {
      "input": "Turn on the bedroom lights",
      "classification": "bedroom",
      "confidence": 0.95
    }
  ],
  "metadata": {
    "requests_used": 1,
    "source": "cache",
    "requests_remaining": 9999
  }
}
```

**Cost**: 1 request

**Use Case**: Routing commands to area-specific toolsets

---

### POST /v1/classify-batch

Classify multiple texts in one request.

**Request**:
```json
{
  "data": [
    "Turn on bedroom lights",
    "Set living room temperature to 72",
    "Open garage door"
  ],
  "classification_set": "ha-area-router-v1"
}
```

**Response**:
```json
{
  "results": [
    {
      "input": "Turn on bedroom lights",
      "classification": "bedroom",
      "confidence": 0.95
    },
    {
      "input": "Set living room temperature to 72",
      "classification": "living_room",
      "confidence": 0.92
    },
    {
      "input": "Open garage door",
      "classification": "garage",
      "confidence": 0.98
    }
  ],
  "metadata": {
    "requests_used": 1,
    "processed_count": 3,
    "requests_remaining": 9999
  }
}
```

**Cost**: 1 request (regardless of batch size, with deduplication)

---

### POST /v1/correct

Teach the system from corrections.

**Request**:
```json
{
  "query": "Turn on the lights",
  "wrong_tool": "turn_on_switch_lights",
  "correct_tool": "turn_on_light_living_room",
  "bank": "ha-user-corrections"
}
```

**Response**:
```json
{
  "success": true,
  "metadata": {
    "requests_used": 1
  }
}
```

**Cost**: 1 request

**Use Case**: Learning from user corrections

---

## Toolset Management

### POST /v1/toolsets

Create a new toolset.

**Request**:
```json
{
  "name": "Home Assistant - Living Room",
  "signature": "ha-living-room-v1",
  "description": "Controls for living room devices",
  "tools": [
    {
      "name": "turn_on_light_living_room_main",
      "description": "Turn on the main light in the living room",
      "parameters": {
        "type": "object",
        "properties": {
          "brightness": {
            "type": "number",
            "minimum": 0,
            "maximum": 255
          }
        }
      }
    }
  ]
}
```

**Response**:
```json
{
  "id": "uuid",
  "app_id": "uuid",
  "name": "Home Assistant - Living Room",
  "signature": "ha-living-room-v1",
  "description": "Controls for living room devices",
  "tools": [...],
  "content_hash": "abc123...",
  "created_at": "2026-02-12T20:00:00Z",
  "updated_at": "2026-02-12T20:00:00Z"
}
```

---

### GET /v1/toolsets

List all toolsets for the authenticated app.

**Query Parameters**:
- `limit` (optional): Max results (default: 20, max: 100)
- `page` (optional): Page number (default: 1)

**Response**:
```json
[
  {
    "id": "uuid",
    "name": "Home Assistant - Living Room",
    "signature": "ha-living-room-v1",
    "tool_count": 15,
    "created_at": "2026-02-12T20:00:00Z",
    "updated_at": "2026-02-12T20:00:00Z"
  }
]
```

---

### GET /v1/toolsets/{signature}

Get a specific toolset by signature.

**Response**: Full toolset object (same as POST response)

---

### PUT /v1/toolsets/{signature}

Update an existing toolset.

**Request**: Same as POST (name, description, tools)

**Response**: Updated toolset object

**Note**: Content hash is automatically recomputed

---

### DELETE /v1/toolsets/{signature}

Delete a toolset.

**Response**: 204 No Content

---

## Classification Set Management

### POST /v1/classification-sets

Create a new classification set.

**Request**:
```json
{
  "name": "Home Assistant Area Router",
  "signature": "ha-area-router-v1",
  "description": "Routes commands to the correct area",
  "classes": [
    {
      "label": "living_room",
      "description": "Commands about living room devices"
    },
    {
      "label": "bedroom",
      "description": "Commands about bedroom devices"
    },
    {
      "label": "kitchen",
      "description": "Commands about kitchen devices"
    }
  ]
}
```

**Response**:
```json
{
  "id": "uuid",
  "app_id": "uuid",
  "name": "Home Assistant Area Router",
  "signature": "ha-area-router-v1",
  "description": "Routes commands to the correct area",
  "classes": [...],
  "content_hash": "def456...",
  "created_at": "2026-02-12T20:00:00Z",
  "updated_at": "2026-02-12T20:00:00Z"
}
```

---

### GET /v1/classification-sets

List all classification sets.

**Response**: Array of classification set summaries

---

### GET /v1/classification-sets/{signature}

Get a specific classification set.

**Response**: Full classification set object

---

### PUT /v1/classification-sets/{signature}

Update an existing classification set.

**Request**: Same as POST

**Response**: Updated classification set object

---

### DELETE /v1/classification-sets/{signature}

Delete a classification set.

**Response**: 204 No Content

---

## Memory Banks

### POST /v1/banks

Create a new memory bank.

**Request**:
```json
{
  "name": "Home Assistant User Corrections",
  "description": "Learned corrections from user feedback",
  "visibility": "private"
}
```

**Response**:
```json
{
  "bank_id": "uuid",
  "name": "Home Assistant User Corrections",
  "description": "Learned corrections from user feedback",
  "visibility": "private",
  "item_count": 0,
  "last_updated": "2026-02-12T20:00:00Z",
  "created_at": "2026-02-12T20:00:00Z",
  "status": "active"
}
```

---

### GET /v1/banks

List all memory banks.

**Query Parameters**:
- `limit` (optional): Max results (default: 20, max: 100)
- `page` (optional): Page number (default: 1)

---

### GET /v1/banks/{bank_id}

Get a specific memory bank.

---

### DELETE /v1/banks/{bank_id}

Delete a memory bank.

---

### POST /v1/banks/{bank_id}/items

Add items to a memory bank.

**Request**:
```json
{
  "items": [
    {
      "query": "Turn on the lights",
      "tool": "turn_on_light_living_room_main",
      "parameters": {}
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid JSON body"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid or missing API key"
}
```

### 402 Payment Required
```json
{
  "error": "Insufficient requests remaining"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limits

Rate limits depend on your subscription plan:

- **Free**: 1,000 requests/month
- **Starter**: 10,000 requests/month
- **Pro**: 100,000 requests/month
- **Enterprise**: Custom

Rate limit headers:
```
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9999
X-RateLimit-Reset: 1707782400
```

---

## Best Practices

### 1. Use Toolsets for Production

Don't use inline tools (`/v1/resolve-quick`) in production. Create toolsets for:
- Better caching
- Consistent content hashing
- Easier management

### 2. Organize by Context

Group related tools into toolsets:
- By area (living room, bedroom)
- By domain (lights, climate)
- By feature (scenes, automations)

### 3. Leverage Caching

- Similar queries return cached results (fast + free)
- Toolset content hashes enable stable cache keys
- Classification sets enable batch deduplication

### 4. Handle Errors Gracefully

- Always check `metadata.source` (cache vs compute)
- Monitor `requests_remaining`
- Implement retry logic for transient errors
- Provide user-friendly error messages

### 5. Use Memory Banks

- Create a bank for user corrections
- Assign banks to all resolve calls
- System learns and improves over time

### 6. Monitor Usage

- Track `requests_used` per call
- Monitor `requests_remaining`
- Set up alerts before hitting limits
- Optimize to reduce request count

---

## TypeScript Types

For reference, here are the key types from the Intentgine codebase:

```typescript
interface ToolDefinition {
  name: string;
  description: string;
  parameters?: {
    type: "object";
    properties: Record<string, unknown>;
    required?: string[];
  };
}

interface ToolCall {
  tool: string;
  parameters: Record<string, unknown>;
}

interface ClassDefinition {
  label: string;
  description?: string;
}

interface ResolveRequest {
  query: string;
  toolsets: string[];
  banks?: string[];
}

interface ResolveResponse {
  resolved: ToolCall;
  metadata: {
    source: "cache" | "compute";
    used_banks: string[];
    latency_ms: number;
    requests_used: number;
    requests_remaining: number;
    defaults_applied?: string[];
  };
}
```

---

## Testing

### Test API Connection

```bash
curl -X POST https://api.intentgine.dev/v1/resolve-quick \
  -H "Authorization: Bearer sk_live_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Turn on the lights",
    "tools": [{
      "name": "turn_on_lights",
      "description": "Turn on lights",
      "parameters": {"type": "object", "properties": {}}
    }]
  }'
```

### Test Toolset Creation

```bash
curl -X POST https://api.intentgine.dev/v1/toolsets \
  -H "Authorization: Bearer sk_live_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Toolset",
    "signature": "test-v1",
    "tools": [...]
  }'
```

---

## Notes

- All timestamps are ISO 8601 format (UTC)
- All IDs are UUIDs
- Content hashes are SHA-256 hex strings
- Signatures should be unique per app
- Versioning in signatures recommended (e.g., `-v1`, `-v2`)
