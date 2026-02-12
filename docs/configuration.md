# Configuration Guide

## Getting Your API Key

1. Go to [intentgine.dev](https://intentgine.dev)
2. Sign up or log in
3. Navigate to **Dashboard** → **Apps**
4. Click **Create New App**
5. Give your app a name (e.g., "Home Assistant")
6. Copy the API key (starts with `sk_live_`)
7. Keep this key secure!

## Adding the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "Intentgine"
4. Click on "Intentgine Voice Control"
5. Enter your API key
6. (Optional) Enter a custom API endpoint if using self-hosted Intentgine
7. Click **Submit**

The integration will:
- Test your API connection
- Create a config entry
- Start syncing your entities

## Exposing Entities

By default, only entities already exposed to voice assistants can be controlled.

### To expose entities:

1. Go to **Settings** → **Voice Assistants**
2. Click on **Expose** tab
3. Select entities you want to control via Intentgine
4. The integration will automatically sync within a few minutes

### Recommended entities to expose:

- ✅ Lights you control frequently
- ✅ Switches for appliances
- ✅ Climate controls (thermostats)
- ✅ Covers (blinds, garage doors)
- ✅ Scenes you use often
- ❌ Sensitive devices (locks, alarms) - be cautious
- ❌ Rarely used entities

## Manual Sync

If you add/remove entities and want to sync immediately:

1. Go to **Developer Tools** → **Services**
2. Select service: `intentgine.sync_toolsets`
3. Click **Call Service**

Or use the service in an automation:

```yaml
service: intentgine.sync_toolsets
```

## Configuration Options

To change options after setup:

1. Go to **Settings** → **Devices & Services**
2. Find "Intentgine Voice Control"
3. Click **Configure**

### Available Options:

- **Enable Area-Based Toolsets**: Organize tools by room (recommended: ON)

## Verifying Setup

### Check Toolsets

1. Go to your [Intentgine Dashboard](https://intentgine.dev/dashboard)
2. Navigate to your app
3. Check the **Toolsets** section
4. You should see toolsets like:
   - `ha-living-room-v1`
   - `ha-bedroom-v1`
   - `ha-global-v1`

### Test a Command

1. Go to **Developer Tools** → **Services**
2. Select service: `intentgine.execute_command`
3. Enter service data:
   ```yaml
   query: "Turn on the living room lights"
   ```
4. Click **Call Service**
5. Check if the lights turned on

## Troubleshooting

### "Cannot connect to Intentgine API"

- Verify your API key is correct
- Check your internet connection
- Try the default endpoint: `https://api.intentgine.dev`
- Check Intentgine service status

### "No toolsets available"

- Make sure you've exposed entities to voice assistants
- Manually trigger sync: `intentgine.sync_toolsets`
- Check logs for sync errors

### Entities not syncing

- Verify entities are exposed in Voice Assistants settings
- Check entity is in a supported domain (light, switch, climate, etc.)
- Manually trigger sync
- Check integration logs

## Next Steps

Continue to the [Usage Guide](usage.md) to learn how to use the integration.
