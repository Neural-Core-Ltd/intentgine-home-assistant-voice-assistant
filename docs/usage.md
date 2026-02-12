# Usage Guide

## Dashboard Card

### Adding the Command Card

1. Edit your dashboard
2. Click **+ Add Card**
3. Scroll down to **Custom: Intentgine Command Card**
4. Configure the card (see options below)
5. Click **Save**

### Card Configuration

```yaml
type: custom:intentgine-command-card
title: Voice Command
placeholder: "What would you like to do?"
show_history: true
```

**Options**:
- `title`: Card title (default: "Intentgine Command")
- `placeholder`: Input placeholder text
- `show_history`: Show recent commands (default: false)

### Using the Card

1. Type a command in natural language
2. Click **Run** or press Enter
3. Wait for the command to execute
4. See success/error feedback

## Chat Interface

### Adding the Chat Card

```yaml
type: custom:intentgine-chat-card
title: Home Assistant Chat
persona: friendly
```

**Options**:
- `title`: Card title
- `persona`: Response style (friendly, concise, helpful)

### Using Chat

1. Type a message
2. Press Enter or click Send
3. See the assistant's response
4. Command executes automatically

## Voice Assistant Integration

The integration registers as a conversation agent in Home Assistant.

### Setup

1. Go to **Settings** → **Voice Assistants**
2. Select your voice assistant (e.g., "Home Assistant")
3. Under **Conversation Agent**, select "Intentgine"
4. Click **Save**

### Using with Voice

Now you can use voice commands:
- "Hey Google, ask Home Assistant to turn on the living room lights"
- "Alexa, tell Home Assistant to set bedroom temperature to 72"

Or use Home Assistant's built-in Assist:
- Press the microphone button
- Say your command
- Intentgine processes it

## Service Calls

### Execute Command Service

Use in automations or scripts:

```yaml
service: intentgine.execute_command
data:
  query: "Turn on the living room lights"
```

### Sync Toolsets Service

Manually sync entities:

```yaml
service: intentgine.sync_toolsets
```

## Example Commands

### Lights

```
Turn on the living room lights
Turn off all bedroom lights
Set kitchen lights to 50%
Dim the lights
Make the lights brighter
Change living room to blue
Turn on the lamp
```

### Climate

```
Set bedroom temperature to 72
Turn on the AC
Set thermostat to heat mode
Make it warmer
Cool down the house
```

### Switches

```
Turn on the coffee maker
Turn off the fan
Toggle the kitchen switch
```

### Covers

```
Open the garage door
Close the bedroom blinds
Open all blinds
Stop the garage door
```

### Scenes

```
Activate movie time
Turn on good morning scene
Set the mood for dinner
```

### Complex Commands

```
Turn on living room lights at 50% brightness
Set bedroom to 68 degrees in heat mode
Open the blinds and turn on the lights
```

## Tips for Better Results

### Be Specific

❌ "Turn on the lights"  
✅ "Turn on the living room lights"

### Include the Room

❌ "Set temperature to 72"  
✅ "Set bedroom temperature to 72"

### Use Natural Language

✅ "Make it warmer"  
✅ "Dim the lights"  
✅ "Turn everything off"

### Entity Names Matter

The integration uses your entity's friendly names. Make sure they're clear:

❌ `light.light_1` → "Light 1"  
✅ `light.living_room_main` → "Living Room Main Light"

## Automations

### Voice-Triggered Automation

```yaml
automation:
  - alias: "Goodnight Routine"
    trigger:
      - platform: event
        event_type: intentgine_command_executed
        event_data:
          query: "goodnight"
    action:
      - service: scene.turn_on
        target:
          entity_id: scene.goodnight
```

### Scheduled Sync

```yaml
automation:
  - alias: "Sync Intentgine Daily"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: intentgine.sync_toolsets
```

## Advanced Usage

### Custom Personas

Define personas in your Intentgine dashboard for different response styles:

- **concise**: Brief, direct responses
- **friendly**: Warm, conversational
- **technical**: Detailed, precise

### Memory Banks

The integration can learn from corrections (future feature):

1. When a command doesn't work as expected
2. Use the correction UI
3. Future similar commands improve

### Multiple Areas

The integration automatically organizes by area:

- Commands about "living room" use `ha-living-room-v1` toolset
- Commands about "bedroom" use `ha-bedroom-v1` toolset
- Better context = better accuracy

## Monitoring Usage

### Check Remaining Requests

View in Intentgine dashboard:
1. Go to [intentgine.dev/dashboard](https://intentgine.dev/dashboard)
2. Select your app
3. View usage statistics

### Integration Logs

Check Home Assistant logs:
1. **Settings** → **System** → **Logs**
2. Filter by `intentgine`
3. See command executions and errors

## Best Practices

1. **Expose only what you need** - Fewer entities = faster sync
2. **Use clear entity names** - Helps with command recognition
3. **Organize by area** - Improves accuracy
4. **Test commands** - Use the card to test before automations
5. **Monitor usage** - Stay within your plan limits

## Next Steps

- Check [Troubleshooting](troubleshooting.md) if you encounter issues
- Join the community for tips and examples
- Share your favorite commands!
