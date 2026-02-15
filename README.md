# Intentgine for Home Assistant

Control your Home Assistant devices using natural language powered by [Intentgine](https://intentgine.dev).

## What is This?

A custom Home Assistant integration that lets you control smart home devices with natural language commands. Instead of remembering entity names and service calls, just say what you want:

- "Turn on the living room lights"
- "Set bedroom temperature to 72"
- "Activate movie time scene"
- "Turn on kitchen lights and turn off bedroom lights"

The integration uses Intentgine's Intent-as-a-Service API to understand your commands and map them to Home Assistant service calls.

## Requirements

- Home Assistant 2024.1 or newer
- An [Intentgine](https://intentgine.dev) account with an active subscription
- An Intentgine API key (from your app in the Intentgine console)

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click **Integrations**
3. Click the three dots menu → **Custom repositories**
4. Add this repository URL and select **Integration** as the category
5. Click **Install**
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/intentgine/` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Setup

### Step 1: Get Your API Key

1. Sign up at [intentgine.dev](https://intentgine.dev)
2. Create a new App in the console
3. Copy your API key from the app settings

### Step 2: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Intentgine**
4. Paste your API key
5. (Optional) Change the API endpoint if you're self-hosting
6. Click **Submit**

On first setup, the integration will:
- Exchange your API key for a JWT (used for all subsequent API calls)
- Discover all entities you've exposed to voice assistants
- Create toolsets organized by area on the Intentgine API
- Create a classification set for area-based command routing
- Register as a Home Assistant conversation agent

### Step 3: Expose Entities

The integration can only control entities that are exposed to voice assistants. To expose entities:

1. Go to **Settings** → **Voice Assistants** → **Expose**
2. Toggle on the entities you want to control via Intentgine
3. Run a manual sync: **Developer Tools** → **Services** → `intentgine.sync_toolsets`

### Step 4: Register Lovelace Cards (Optional)

The integration automatically serves its frontend files at `/intentgine/`. To use the dashboard cards, register them as Lovelace resources:

1. Go to **Settings** → **Dashboards** → **Resources** (three dots menu)
2. Add the following resources with type **JavaScript Module**:
   - `/intentgine/intentgine-command-card.js`
   - `/intentgine/intentgine-chat-card.js`

## Usage

### Conversation Agent

The integration registers as a Home Assistant conversation agent. You can select it in **Settings** → **Voice Assistants** to use it with Home Assistant's built-in Assist pipeline, or any voice input method.

When used as a conversation agent, commands go through the classify → resolve → execute pipeline automatically.

### Command Card

Add a simple command input to your dashboard:

```yaml
type: custom:intentgine-command-card
title: Voice Command
placeholder: "What would you like to do?"
show_history: true
```

Type a command and click **Run**. The card shows success/error feedback and optionally keeps a history of the last 5 commands.

### Chat Card

Add a chat-style interface:

```yaml
type: custom:intentgine-chat-card
title: Home Assistant Chat
```

Type messages and get feedback on executed commands.

### Services

The integration exposes two services you can call from automations, scripts, or Developer Tools:

**`intentgine.execute_command`** — Execute a natural language command
```yaml
service: intentgine.execute_command
data:
  query: "Turn on the living room lights"
```

**`intentgine.sync_toolsets`** — Re-sync entities with Intentgine
```yaml
service: intentgine.sync_toolsets
```

## Supported Devices

The integration generates tools for these entity domains:

| Domain | Tool Name | Actions | Extra Parameters |
|--------|-----------|---------|-----------------|
| `light` | `control_light` | turn_on, turn_off, toggle | brightness (0-255), color_temp |
| `switch` | `control_switch` | turn_on, turn_off, toggle | — |
| `climate` | `control_climate` | *(inferred from params)* | temperature, hvac_mode |
| `cover` | `control_cover` | open, close, stop, toggle | position (0-100) |
| `scene` | `activate_scene` | *(always turn_on)* | — |

Climate devices don't require an explicit action — the integration infers `set_temperature` or `set_hvac_mode` from the parameters the API returns.

## How It Works

```
User command
    ↓
1. Classify (POST /v1/classify)
   → Determines which area(s) the command targets
   → Multi-intent commands are automatically split via extraction
    ↓
2. Resolve (POST /v1/resolve) — one per area
   → Maps the command to a specific tool + parameters
    ↓
3. Execute (hass.services.async_call)
   → Calls the Home Assistant service
    ↓
4. Response
   → Success/error feedback to the user
```

**Area-based routing**: The integration creates one toolset per area (e.g., `ha-living_room-v1`, `ha-bedroom-v1`) plus a global toolset (`ha-global-v1`) for entities without an area. A classification set (`ha-area-router-v1`) routes commands to the correct area's toolset.

**Multi-intent extraction**: The classification set has extraction enabled, so commands like "turn on kitchen lights and turn off bedroom lights" are automatically split into separate commands, each routed to the correct area.

**Cost per command**:
- Single-intent: 2 requests (1 classify + 1 resolve)
- Multi-intent: 2 + N requests (1 classify with extraction + N resolves)

**Authentication**: The API key is exchanged for a short-lived JWT via `POST /v1/auth`. The JWT is cached and auto-refreshed before expiry. All subsequent API calls use the JWT.

## Example Commands

### Lights
- "Turn on the living room lights"
- "Turn off all bedroom lights"
- "Set kitchen lights to 50%"

### Climate
- "Set bedroom temperature to 72"
- "Turn on the AC"
- "Set thermostat to heat mode"

### Scenes
- "Activate movie time"
- "Turn on good morning scene"

### Covers
- "Open the garage door"
- "Close bedroom blinds"

### Multi-Intent
- "Turn on kitchen lights and turn off bedroom lights"
- "Set living room to 50% and turn on bedroom lights"

## Troubleshooting

### "Cannot connect" during setup

- Verify your API key in the Intentgine console
- Check that your Home Assistant instance has internet access
- If self-hosting, verify the endpoint URL is correct

### Commands don't work for a device

- Confirm the entity is exposed: **Settings** → **Voice Assistants** → **Expose**
- Run a manual sync: **Developer Tools** → **Services** → `intentgine.sync_toolsets`
- Check the entity's domain is supported (see Supported Devices table above)

### "Insufficient requests remaining"

- Check your usage in the Intentgine console
- Upgrade your plan or wait for the billing cycle to reset

### Commands are slow

- First command after a sync may be slower (cold cache)
- Subsequent similar commands are faster (Intentgine caches semantically)
- Check your internet connection

### Entities not appearing after adding new devices

Run a manual sync:
1. **Developer Tools** → **Services**
2. Select `intentgine.sync_toolsets`
3. Click **Call Service**

Or restart the integration — it syncs on startup.

### Check logs for errors

Go to **Settings** → **System** → **Logs** and filter for `intentgine`.

## Project Structure

```
custom_components/intentgine/
├── __init__.py           # Integration setup, service registration
├── manifest.json         # Integration metadata
├── config_flow.py        # Setup & options UI
├── const.py              # Constants (domain, defaults, prefixes)
├── api_client.py         # Intentgine API client (JWT auth, CRUD)
├── toolset_manager.py    # Entity discovery, toolset generation & sync
├── command_handler.py    # Classify → resolve → execute pipeline
├── conversation.py       # HA conversation agent integration
├── services.yaml         # Service definitions
├── strings.json          # UI strings
├── translations/
│   └── en.json           # English translations
└── www/
    ├── intentgine-command-card.js   # Simple command card
    └── intentgine-chat-card.js      # Chat interface card
```

## Privacy & Security

- Your API key is stored in Home Assistant's config entry storage
- The API key is exchanged for a short-lived JWT — the raw key is only sent to `/v1/auth`
- All API communication is over HTTPS
- Only entities you explicitly expose to voice assistants can be controlled
- No data is stored locally by this integration beyond configuration

## License

MIT License — see [LICENSE](LICENSE) for details.
