# Troubleshooting Guide

## Common Issues

### Integration Won't Load

**Symptoms**: Integration doesn't appear in the list, or shows errors on load

**Solutions**:
1. Check Home Assistant version (need 2024.1+)
2. Verify files are in correct location: `config/custom_components/intentgine/`
3. Check logs: **Settings** → **System** → **Logs**
4. Restart Home Assistant
5. Clear browser cache

### "Cannot connect to Intentgine API"

**Symptoms**: Error during setup or when executing commands

**Solutions**:
1. Verify API key is correct (starts with `sk_live_`)
2. Check internet connectivity
3. Try default endpoint: `https://api.intentgine.dev`
4. Check Intentgine service status at [status.intentgine.dev](https://status.intentgine.dev)
5. Verify API key in Intentgine dashboard

### "Invalid API key"

**Symptoms**: 401 error in logs

**Solutions**:
1. Copy API key again from Intentgine dashboard
2. Make sure no extra spaces in the key
3. Verify key hasn't been revoked
4. Try creating a new API key
5. Reconfigure integration with new key

### "Insufficient requests remaining"

**Symptoms**: 402 error, commands stop working

**Solutions**:
1. Check usage in Intentgine dashboard
2. Wait for monthly reset
3. Upgrade your Intentgine plan
4. Reduce command frequency
5. Use caching effectively (similar commands are cached)

### No Toolsets Available

**Symptoms**: "No toolsets available" error when executing commands

**Solutions**:
1. Expose entities: **Settings** → **Voice Assistants** → **Expose**
2. Manually sync: `intentgine.sync_toolsets` service
3. Check logs for sync errors
4. Verify entities are in supported domains
5. Wait a few minutes after exposing entities

### Commands Not Working

**Symptoms**: Commands execute but nothing happens

**Solutions**:
1. Verify entity is exposed to voice assistants
2. Check entity is available (not unavailable/unknown)
3. Try more specific commands (include room name)
4. Check entity name matches what you're saying
5. Test with Developer Tools first

### Entities Not Syncing

**Symptoms**: New entities don't appear in toolsets

**Solutions**:
1. Expose the entity in Voice Assistants settings
2. Manually trigger sync: `intentgine.sync_toolsets`
3. Wait 5 minutes for automatic sync
4. Check entity domain is supported
5. Restart integration

### Card Not Appearing

**Symptoms**: Custom card doesn't show in card picker

**Solutions**:
1. Verify file exists: `config/custom_components/intentgine/www/intentgine-command-card.js`
2. Clear browser cache (Ctrl+Shift+R)
3. Check browser console for JavaScript errors
4. Try different browser
5. Restart Home Assistant

### Conversation Agent Not Working

**Symptoms**: Voice commands don't use Intentgine

**Solutions**:
1. Verify conversation agent is selected in Voice Assistants settings
2. Check integration loaded successfully
3. Test with text input first
4. Check logs for conversation errors
5. Try re-selecting the conversation agent

### Slow Response Times

**Symptoms**: Commands take >5 seconds to execute

**Solutions**:
1. First command after sync is slower (cache miss)
2. Subsequent similar commands should be faster
3. Check internet speed
4. Reduce number of toolsets (fewer exposed entities)
5. Use area-based organization

### Wrong Device Controlled

**Symptoms**: Command controls different device than intended

**Solutions**:
1. Be more specific (include room name)
2. Check entity friendly names are clear
3. Avoid duplicate names across rooms
4. Use full entity names in commands
5. Check toolset organization in dashboard

## Error Messages

### "I don't understand that command"

**Meaning**: Intentgine couldn't match command to any tool

**Solutions**:
- Be more specific
- Include room/area name
- Check entity is exposed
- Try different phrasing
- Verify toolsets are synced

### "That device is currently unavailable"

**Meaning**: Entity exists but is unavailable in Home Assistant

**Solutions**:
- Check device is online
- Restart device
- Check device integration
- Wait for device to reconnect

### "Command failed"

**Meaning**: Service call to Home Assistant failed

**Solutions**:
- Check entity supports the action
- Verify parameters are valid
- Check Home Assistant logs
- Test service call manually in Developer Tools

## Debugging

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.intentgine: debug
```

Restart Home Assistant and check logs.

### Test API Connection

Use Developer Tools → Services:

```yaml
service: intentgine.execute_command
data:
  query: "Turn on the living room lights"
```

Check response and logs.

### Verify Toolsets

1. Go to Intentgine dashboard
2. Check your app's toolsets
3. Verify tools exist for your entities
4. Check tool names match entity IDs

### Check Entity Exposure

Developer Tools → States:
1. Find your entity
2. Check attributes
3. Look for `conversation.should_expose: true`

### Manual Service Call

Test without Intentgine:

```yaml
service: light.turn_on
target:
  entity_id: light.living_room_main
```

If this fails, issue is with Home Assistant, not Intentgine.

## Performance Issues

### High Memory Usage

**Solutions**:
- Reduce number of exposed entities
- Disable history for integration
- Restart Home Assistant periodically

### Slow Sync

**Solutions**:
- Reduce number of entities
- Check internet speed
- Sync during off-peak hours
- Disable automatic sync, use manual

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Search existing GitHub issues
3. Check Home Assistant logs
4. Check Intentgine dashboard for errors
5. Try with a simple test command

### Information to Provide

When reporting issues, include:

- Home Assistant version
- Integration version
- Error messages from logs
- Steps to reproduce
- Example command that fails
- Number of exposed entities
- Intentgine plan type

### Where to Get Help

- **GitHub Issues**: [github.com/intentgine/ha-integration/issues](https://github.com/intentgine/ha-integration/issues)
- **Home Assistant Community**: [community.home-assistant.io](https://community.home-assistant.io)
- **Intentgine Support**: [support@intentgine.dev](mailto:support@intentgine.dev)
- **Discord**: [discord.gg/intentgine](https://discord.gg/intentgine)

## Known Limitations

1. **Internet Required**: Integration needs internet connectivity
2. **API Costs**: Each command uses Intentgine requests
3. **Exposed Entities Only**: Can only control exposed entities
4. **Supported Domains**: Limited to specific entity domains
5. **English Only**: Currently only supports English commands

## FAQ

**Q: Can I use this offline?**  
A: No, Intentgine is a cloud service requiring internet.

**Q: How many requests does each command use?**  
A: Typically 1 request. Chat interface uses 2 requests.

**Q: Can I control locks and alarms?**  
A: Yes, but be cautious about exposing security devices.

**Q: Does it work with Google Home/Alexa?**  
A: Yes, via Home Assistant's voice assistant integration.

**Q: Can I customize the responses?**  
A: Yes, use personas in the Intentgine dashboard.

**Q: Is my data private?**  
A: Commands are sent to Intentgine API. See [privacy policy](https://intentgine.dev/privacy).

**Q: Can I self-host Intentgine?**  
A: Not currently, but you can use a custom endpoint if available.

## Still Having Issues?

If you've tried everything and still have problems:

1. Create a GitHub issue with full details
2. Include logs and configuration
3. Describe expected vs actual behavior
4. Provide steps to reproduce

We're here to help! 🚀
