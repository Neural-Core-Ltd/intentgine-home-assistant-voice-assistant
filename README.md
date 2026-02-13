# Intentgine for Home Assistant

Control your Home Assistant devices using natural language powered by [Intentgine](https://intentgine.dev).

## What is This?

This is a custom Home Assistant integration that lets you control your smart home devices using natural language commands. Instead of remembering exact entity names and service calls, just type what you want:

- "Turn on the living room lights"
- "Set bedroom temperature to 72"
- "Activate movie time scene"
- "Dim the kitchen lights to 50%"

The integration uses Intentgine's Intent-as-a-Service API to understand your commands and map them to the correct Home Assistant actions.

## Features

- 🗣️ **Natural Language Control**: Type commands in plain English
- 🏠 **Area-Based Organization**: Automatically organizes devices by room
- 🔄 **Auto-Sync**: Keeps up with your Home Assistant configuration changes
- 🔒 **Secure**: Only controls entities you've exposed to voice assistants
- 💬 **Conversational**: Optional chat interface with natural responses
- 🎯 **Accurate**: Learns from corrections to improve over time

## Requirements

- Home Assistant 2024.1 or newer
- Active [Intentgine](https://intentgine.dev) subscription
- Intentgine API key

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add this repository URL
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy `custom_components/intentgine/` to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### 1. Get Your Intentgine API Key

1. Sign up at [intentgine.dev](https://intentgine.dev)
2. Create a new App in the dashboard
3. Copy your API key (starts with `sk_live_`)

### 2. Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Intentgine"
4. Enter your API key
5. Click **Submit**

The integration will automatically:
- Discover all entities exposed to voice assistants
- Create toolsets organized by area
- Sync with Intentgine API

### 3. Expose Entities (Optional)

By default, only entities already exposed to voice assistants can be controlled. To expose more:

1. Go to **Settings** → **Voice Assistants** → **Expose**
2. Select entities you want to control via Intentgine
3. The integration will auto-sync within a few minutes

## Usage

### Dashboard Card

Add the Intentgine command card to your dashboard:

```yaml
type: custom:intentgine-command-card
title: Voice Command
placeholder: "What would you like to do?"
show_history: true
```

Then just type commands and click "Run"!

### Chat Interface (Advanced)

For a more conversational experience with natural language responses:

```yaml
type: custom:intentgine-chat-card
title: Home Assistant Chat
persona: friendly
use_respond: true  # Enable natural language responses
show_resolved_actions: true
```

### Conversation Agent (Coming Soon)

Integration with Home Assistant's built-in voice assistant system.

## Example Commands

### Lights
- "Turn on the living room lights"
- "Turn off all bedroom lights"
- "Set kitchen lights to 50%"
- "Make the lights warmer"
- "Change living room to blue"

### Multi-Intent Commands
- "Turn on kitchen lights and turn off bedroom lights"
- "Set living room to 50% and turn on bedroom lights"
- "Open garage door and turn on driveway lights"

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

### Media
- "Play music in the living room"
- "Pause the TV"

## How It Works

1. **You type a command** in natural language
2. **Integration classifies** the command to determine the area (living room, bedroom, etc.)
   - If the command contains multiple intents (e.g., "turn on kitchen and bedroom lights"), extraction automatically splits it into separate commands
3. **Integration sends to Intentgine** with the area-specific toolset for each command
4. **Intentgine resolves** each command to a specific action with parameters
5. **Integration executes** all Home Assistant service calls
6. **You get feedback** on success or errors

The integration automatically creates "toolsets" (collections of available actions) organized by area. Each toolset contains domain-based tools (one tool for all lights, one for all switches, etc.) with parameters to specify which device and what action. When you add or remove devices, it syncs automatically.

**Classification Extraction**: The area router classification set has extraction enabled, which means it can automatically detect and split multi-intent commands like "turn on kitchen lights and turn off bedroom lights" into separate commands. This happens in a single API call with minimal overhead.

**Cost per command**:
- Single-intent: 2 requests (1 classify + 1 resolve)
- Multi-intent: 2 + N requests (2 for classify with extraction + N resolves, where N = number of intents)

## Configuration Options

Access via **Settings** → **Devices & Services** → **Intentgine** → **Configure**:

- **API Endpoint**: Custom endpoint (for self-hosted Intentgine)
- **Sync Frequency**: How often to sync toolsets (hourly, daily, manual)
- **Area Toolsets**: Enable/disable area-based organization
- **Default Persona**: Conversational style for responses

## Troubleshooting

### "I don't understand that command"

- Make sure the entity is exposed to voice assistants
- Try being more specific (include room name)
- Check that the device is available in Home Assistant

### "API key invalid"

- Verify your API key in the Intentgine dashboard
- Make sure it starts with `sk_live_`
- Try reconfiguring the integration

### "Out of requests"

- Check your Intentgine plan limits
- Upgrade your plan or wait for reset
- View usage in the Intentgine dashboard

### Commands are slow

- First command after sync may be slower (cache miss)
- Subsequent similar commands should be faster (cached)
- Check your internet connection

### Entities not syncing

- Trigger manual sync: **Developer Tools** → **Services** → `intentgine.sync_toolsets`
- Check entity is exposed to voice assistants
- Check integration logs for errors

## Advanced Usage

### Memory Banks

The integration can learn from corrections:

1. When a command doesn't work as expected, use the correction UI
2. The integration sends the correction to Intentgine
3. Future similar commands will work better

### Custom Toolsets

For advanced users, you can customize toolset generation in the integration options.

### API Usage Monitoring

View your Intentgine API usage:
- Integration shows remaining requests
- Warns when approaching limit
- Links to Intentgine dashboard for details

## Development

This integration is open source! Contributions welcome.

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/intentgine/ha-integration
cd ha-integration

# Install dependencies
pip install -r requirements_dev.txt

# Run tests
pytest tests/

# Lint code
pylint custom_components/intentgine/
black custom_components/intentgine/
```

### Project Structure

```
custom_components/intentgine/
├── __init__.py              # Integration entry point
├── manifest.json            # Integration metadata
├── config_flow.py           # Configuration UI
├── const.py                 # Constants
├── api_client.py            # Intentgine API client
├── toolset_manager.py       # Toolset generation & sync
├── command_handler.py       # Command processing
├── conversation.py          # Conversation agent
└── lovelace/                # Frontend cards
    ├── intentgine-command-card.js
    └── intentgine-chat-card.js
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation.

## Support

- **Documentation**: [Full docs](docs/)
- **Issues**: [GitHub Issues](https://github.com/intentgine/ha-integration/issues)
- **Discussions**: [GitHub Discussions](https://github.com/intentgine/ha-integration/discussions)
- **Intentgine Support**: [support@intentgine.dev](mailto:support@intentgine.dev)

## Pricing

This integration is **free and open source**. However, it requires an Intentgine subscription:

- **Hobbyist**: $5/mo - 10,000 requests (~5,000 single commands or ~2,500 two-intent commands)
- **Starter**: $29/mo - 100,000 requests (~50,000 single commands or ~25,000 two-intent commands)
- **Business**: $99/mo - 500,000 requests (~250,000 single commands or ~125,000 two-intent commands)

See [intentgine.dev/pricing](https://intentgine.dev/pricing) for current pricing.

**Request usage per command**:
- Single-intent command: **2 requests** (1 classify + 1 resolve)
- Multi-intent command: **2 + N requests** (2 for classify with extraction + N resolves)
  - Example: "Turn on kitchen and bedroom lights" = 4 requests (2 classify + 2 resolves)

**Recommendation**: Most users should start with **Starter ($29/mo)** for typical home setups.

## Privacy & Security

- Your API key is stored securely in Home Assistant
- Commands are sent to Intentgine API over HTTPS
- Only entities you expose can be controlled
- No data is stored by this integration (Intentgine may cache for performance)
- See [Intentgine Privacy Policy](https://intentgine.dev/privacy)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Built by the [Intentgine](https://intentgine.dev) team as a reference implementation and community contribution.

Special thanks to the Home Assistant community for their excellent documentation and examples.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Note**: This integration is currently in development. See [IMPLEMENTATION.md](IMPLEMENTATION.md) for current status and roadmap.
