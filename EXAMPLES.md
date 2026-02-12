# Example Lovelace Dashboard Configuration

## Command Card Examples

### Basic Command Card
```yaml
type: custom:intentgine-command-card
title: Voice Command
placeholder: "What would you like to do?"
```

### Command Card with History
```yaml
type: custom:intentgine-command-card
title: Home Control
placeholder: "Turn on lights, set temperature, etc."
show_history: true
```

### Multiple Command Cards by Area
```yaml
# Living Room Card
type: custom:intentgine-command-card
title: Living Room
placeholder: "Control living room devices..."

# Bedroom Card
type: custom:intentgine-command-card
title: Bedroom
placeholder: "Control bedroom devices..."
```

## Chat Interface Examples

### Basic Chat
```yaml
type: custom:intentgine-chat-card
title: Home Assistant Chat
```

### Chat with Persona
```yaml
type: custom:intentgine-chat-card
title: Friendly Assistant
persona: friendly
```

## Full Dashboard Example

```yaml
views:
  - title: Home
    cards:
      # Quick Command Card
      - type: custom:intentgine-command-card
        title: Quick Command
        placeholder: "What would you like to do?"
        show_history: true
      
      # Your other cards...
      - type: entities
        entities:
          - light.living_room
          - switch.coffee_maker

  - title: Voice Control
    cards:
      # Chat Interface
      - type: custom:intentgine-chat-card
        title: Home Assistant Chat
        persona: helpful
      
      # Command History
      - type: markdown
        content: |
          ## Recent Commands
          Check the chat above for your command history.

  - title: Settings
    cards:
      # Manual Sync Button
      - type: button
        name: Sync Intentgine
        icon: mdi:sync
        tap_action:
          action: call-service
          service: intentgine.sync_toolsets
```

## Automation Examples

### Voice-Triggered Goodnight Routine
```yaml
automation:
  - alias: "Goodnight via Voice"
    trigger:
      - platform: event
        event_type: intentgine_command_executed
        event_data:
          query: "goodnight"
    action:
      - service: scene.turn_on
        target:
          entity_id: scene.goodnight
      - service: notify.mobile_app
        data:
          message: "Goodnight routine activated"
```

### Daily Toolset Sync
```yaml
automation:
  - alias: "Sync Intentgine Daily"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: intentgine.sync_toolsets
```

### Sync After Entity Changes
```yaml
automation:
  - alias: "Sync After New Device"
    trigger:
      - platform: event
        event_type: entity_registry_updated
    action:
      - delay: "00:05:00"  # Wait 5 minutes for more changes
      - service: intentgine.sync_toolsets
```

## Script Examples

### Execute Command Script
```yaml
script:
  voice_command:
    alias: "Execute Voice Command"
    fields:
      command:
        description: "The command to execute"
        example: "Turn on the lights"
    sequence:
      - service: intentgine.execute_command
        data:
          query: "{{ command }}"
```

### Morning Routine via Voice
```yaml
script:
  morning_routine:
    alias: "Morning Routine"
    sequence:
      - service: intentgine.execute_command
        data:
          query: "Turn on bedroom lights at 50%"
      - delay: "00:00:05"
      - service: intentgine.execute_command
        data:
          query: "Set bedroom temperature to 72"
      - delay: "00:00:05"
      - service: intentgine.execute_command
        data:
          query: "Open bedroom blinds"
```

## Input Helper Examples

### Voice Command Input
```yaml
input_text:
  voice_command:
    name: Voice Command
    icon: mdi:microphone
    max: 255

automation:
  - alias: "Process Voice Command Input"
    trigger:
      - platform: state
        entity_id: input_text.voice_command
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state != '' }}"
    action:
      - service: intentgine.execute_command
        data:
          query: "{{ states('input_text.voice_command') }}"
      - service: input_text.set_value
        target:
          entity_id: input_text.voice_command
        data:
          value: ""
```

## Notification Examples

### Command Success Notification
```yaml
automation:
  - alias: "Notify on Command Success"
    trigger:
      - platform: event
        event_type: intentgine_command_executed
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.success }}"
    action:
      - service: notify.mobile_app
        data:
          message: "Executed: {{ trigger.event.data.tool }}"
```

## Advanced Examples

### Multi-Room Control
```yaml
script:
  all_lights_on:
    alias: "All Lights On"
    sequence:
      - service: intentgine.execute_command
        data:
          query: "Turn on all living room lights"
      - service: intentgine.execute_command
        data:
          query: "Turn on all bedroom lights"
      - service: intentgine.execute_command
        data:
          query: "Turn on all kitchen lights"
```

### Conditional Commands
```yaml
automation:
  - alias: "Smart Climate Control"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        above: 75
    action:
      - service: intentgine.execute_command
        data:
          query: "Set all thermostats to cool mode at 72 degrees"
```

### Voice-Activated Scenes
```yaml
automation:
  - alias: "Movie Time Voice"
    trigger:
      - platform: event
        event_type: intentgine_command_executed
    condition:
      - condition: template
        value_template: "{{ 'movie' in trigger.event.data.query.lower() }}"
    action:
      - service: scene.turn_on
        target:
          entity_id: scene.movie_time
```

## Tips

1. **Use specific room names** in commands for better accuracy
2. **Test commands** in the card before using in automations
3. **Monitor usage** to stay within API limits
4. **Sync regularly** to keep toolsets up to date
5. **Use personas** for different response styles in chat

## Resources

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Usage Guide](docs/usage.md)
- [Troubleshooting](docs/troubleshooting.md)
