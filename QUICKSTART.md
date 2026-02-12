# Quick Start Guide

Get up and running with Intentgine in 5 minutes!

## Step 1: Get API Key (2 minutes)

1. Go to [intentgine.dev](https://intentgine.dev)
2. Sign up (free tier available)
3. Create an app
4. Copy your API key (starts with `sk_live_`)

## Step 2: Install Integration (1 minute)

### Via HACS (Recommended)
1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add: `https://github.com/intentgine/ha-integration`
4. Install "Intentgine Voice Control"
5. Restart Home Assistant

### Manual
1. Download latest release
2. Copy `intentgine` folder to `config/custom_components/`
3. Restart Home Assistant

## Step 3: Configure (1 minute)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search "Intentgine"
4. Enter your API key
5. Click Submit

✅ Integration is now set up!

## Step 4: Expose Entities (1 minute)

1. Go to **Settings** → **Voice Assistants** → **Expose**
2. Select entities you want to control:
   - ✅ Living room lights
   - ✅ Bedroom lights
   - ✅ Thermostat
   - ✅ Common switches
3. Wait 30 seconds for sync

## Step 5: Test It! (30 seconds)

### Option A: Service Call
1. **Developer Tools** → **Services**
2. Service: `intentgine.execute_command`
3. Data: `query: "Turn on the living room lights"`
4. Click **Call Service**

### Option B: Dashboard Card
1. Edit dashboard
2. Add card → Custom: Intentgine Command Card
3. Type: "Turn on the living room lights"
4. Click Run

## You're Done! 🎉

Now try these commands:
- "Turn on the bedroom lights"
- "Set temperature to 72"
- "Dim the lights to 50%"
- "Activate movie time scene"

## Next Steps

### Add Dashboard Card

```yaml
type: custom:intentgine-command-card
title: Voice Command
show_history: true
```

### Enable Voice Assistant

1. **Settings** → **Voice Assistants**
2. Select "Intentgine" as conversation agent
3. Use with Google Home, Alexa, or HA Assist

### Explore Features

- 📖 [Full Documentation](docs/)
- 💡 [Example Configurations](EXAMPLES.md)
- 🐛 [Troubleshooting](docs/troubleshooting.md)

## Common First-Time Issues

### "No toolsets available"
→ Make sure you exposed entities in Step 4

### "Cannot connect"
→ Check your API key is correct

### "Command failed"
→ Be more specific (include room name)

## Get Help

- GitHub Issues: Report bugs
- Community Forum: Ask questions
- Discord: Chat with users

**Enjoy your voice-controlled smart home!** 🏠✨
