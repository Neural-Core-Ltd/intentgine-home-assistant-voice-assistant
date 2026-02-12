# Complete Installation Guide - Intentgine for Home Assistant

**Version**: 1.0.0  
**Last Updated**: February 12, 2026  
**Estimated Time**: 15-20 minutes

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: Get Your Intentgine API Key](#part-1-get-your-intentgine-api-key)
3. [Part 2: Install the Integration](#part-2-install-the-integration)
4. [Part 3: Configure the Integration](#part-3-configure-the-integration)
5. [Part 4: Expose Entities](#part-4-expose-entities)
6. [Part 5: Add Dashboard Card](#part-5-add-dashboard-card)
7. [Part 6: Test Your Setup](#part-6-test-your-setup)
8. [Part 7: Enable Voice Assistant (Optional)](#part-7-enable-voice-assistant-optional)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Home Assistant** version 2024.1 or newer
  - Check: Settings → System → Repairs → Three dots → System Information
- ✅ **Internet connection** (required for Intentgine API)
- ✅ **Admin access** to your Home Assistant instance
- ✅ **At least one smart device** configured in Home Assistant (light, switch, etc.)

---

## Part 1: Get Your Intentgine API Key

**Time**: 3-5 minutes

### Step 1.1: Create Intentgine Account

1. Open your web browser
2. Go to **[https://intentgine.dev](https://intentgine.dev)**
3. Click **Sign Up** (top right)
4. Enter your email and create a password
5. Verify your email address (check your inbox)
6. Log in to your new account

### Step 1.2: Create an App

1. Once logged in, you'll see the **Dashboard**
2. Click **Apps** in the left sidebar
3. Click **Create New App** button
4. Fill in the form:
   - **App Name**: `Home Assistant` (or any name you prefer)
   - **Description**: `Voice control for my smart home` (optional)
5. Click **Create App**

### Step 1.3: Copy Your API Key

1. Your new app will appear in the list
2. Click on the app name to open it
3. You'll see your **API Key** displayed
4. Click the **Copy** button next to the API key
5. **IMPORTANT**: Save this key somewhere safe! You won't be able to see it again.
   - The key starts with `sk_live_`
   - Example: `sk_live_abc123def456...`

> ⚠️ **Security Note**: Never share your API key publicly or commit it to version control.

### Step 1.4: Check Your Plan

1. Still on the app page, note your plan details:
   - **Free Tier**: 1,000 requests/month (great for testing)
   - **Starter**: 10,000 requests/month
   - **Pro**: 100,000 requests/month
2. Each command typically uses 1-2 requests
3. You can upgrade later if needed

✅ **Checkpoint**: You should now have your API key copied and ready to use.

---

## Part 2: Install the Integration

**Time**: 5-7 minutes

Choose **ONE** of the following installation methods:

### Method A: HACS Installation (Recommended)

**Prerequisites**: HACS must be installed. If you don't have HACS, use Method B.

#### Step 2A.1: Add Custom Repository

1. Open Home Assistant
2. Click **HACS** in the left sidebar
3. Click **Integrations**
4. Click the **three dots menu** (⋮) in the top right corner
5. Select **Custom repositories**
6. In the dialog that appears:
   - **Repository**: `https://github.com/intentgine/ha-integration`
   - **Category**: Select `Integration`
7. Click **Add**

#### Step 2A.2: Install the Integration

1. Still in HACS → Integrations
2. Click **Explore & Download Repositories** (bottom right)
3. Search for `Intentgine`
4. Click on **Intentgine Voice Control**
5. Click **Download** (bottom right)
6. In the dialog:
   - Select the latest version
   - Click **Download**
7. Wait for the download to complete

#### Step 2A.3: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart** (top right)
3. Click **Restart Home Assistant**
4. Wait 1-2 minutes for Home Assistant to restart
5. Refresh your browser page

✅ **Checkpoint**: Integration is now installed via HACS.

---

### Method B: Manual Installation

**Use this if you don't have HACS installed.**

#### Step 2B.1: Download the Integration

1. Go to **[https://github.com/intentgine/ha-integration/releases](https://github.com/intentgine/ha-integration/releases)**
2. Find the latest release (v1.0.0 or newer)
3. Download the **Source code (zip)** file
4. Extract the ZIP file on your computer

#### Step 2B.2: Locate Your Home Assistant Config Directory

Your config directory location depends on your installation type:

- **Home Assistant OS**: Use the **File Editor** add-on or **Samba Share**
- **Home Assistant Container**: `/path/to/your/config` (where you mounted the volume)
- **Home Assistant Core**: Usually `~/.homeassistant/` or `/home/homeassistant/.homeassistant/`

#### Step 2B.3: Copy Files

1. In your config directory, create a folder called `custom_components` if it doesn't exist
2. Inside `custom_components`, create a folder called `intentgine`
3. Copy all files from the extracted ZIP's `custom_components/intentgine/` folder to your `config/custom_components/intentgine/` folder

Your directory structure should look like this:

```
config/
└── custom_components/
    └── intentgine/
        ├── __init__.py
        ├── api_client.py
        ├── command_handler.py
        ├── config_flow.py
        ├── const.py
        ├── conversation.py
        ├── manifest.json
        ├── services.yaml
        ├── strings.json
        ├── toolset_manager.py
        ├── translations/
        │   └── en.json
        └── www/
            ├── intentgine-command-card.js
            └── intentgine-chat-card.js
```

#### Step 2B.4: Verify File Permissions

If using Home Assistant OS or Container, ensure files are readable:

```bash
chmod -R 755 config/custom_components/intentgine/
```

#### Step 2B.5: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart** (top right)
3. Click **Restart Home Assistant**
4. Wait 1-2 minutes for restart
5. Refresh your browser

✅ **Checkpoint**: Integration files are now in place.

---

## Part 3: Configure the Integration

**Time**: 2-3 minutes

### Step 3.1: Add the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right corner)
3. In the search box, type `Intentgine`
4. Click on **Intentgine Voice Control** when it appears

> 💡 **Tip**: If you don't see it, try refreshing your browser or clearing cache (Ctrl+Shift+R)

### Step 3.2: Enter Your API Key

1. A configuration dialog will appear
2. **API Key**: Paste the API key you copied in Part 1
   - Should start with `sk_live_`
3. **API Endpoint** (optional): Leave as default `https://api.intentgine.dev`
   - Only change this if you're using a self-hosted Intentgine instance
4. Click **Submit**

### Step 3.3: Wait for Validation

1. The integration will test your API connection
2. This takes 5-10 seconds
3. If successful, you'll see a success message

### Step 3.4: Verify Installation

1. You should now see **Intentgine Voice Control** in your integrations list
2. It will show as "1 device" (the integration itself)
3. Click on it to see details

✅ **Checkpoint**: Integration is configured and connected to Intentgine API.

---

## Part 4: Expose Entities

**Time**: 3-5 minutes

The integration can only control entities that are "exposed to voice assistants". Let's expose some devices.

### Step 4.1: Navigate to Voice Assistants

1. Go to **Settings** → **Voice Assistants**
2. Click on the **Expose** tab at the top

### Step 4.2: Expose Your Devices

You'll see a list of all your entities. For each device you want to control with Intentgine:

1. Find the entity in the list
2. Toggle the switch to **ON** (blue)

**Recommended entities to expose**:

- ✅ **Lights** you use frequently
  - Example: `light.living_room_main`, `light.bedroom_lamp`
- ✅ **Switches** for appliances
  - Example: `switch.coffee_maker`, `switch.fan`
- ✅ **Climate controls** (thermostats)
  - Example: `climate.bedroom`, `climate.living_room`
- ✅ **Covers** (blinds, garage doors)
  - Example: `cover.garage_door`, `cover.bedroom_blinds`
- ✅ **Scenes** you use often
  - Example: `scene.movie_time`, `scene.good_morning`

**Be cautious with**:

- ⚠️ **Locks** and **alarms** (security devices)
- ⚠️ **Rarely used devices** (to keep toolsets manageable)

### Step 4.3: Organize by Area (Recommended)

For best results, assign entities to areas:

1. Go to **Settings** → **Areas & Zones**
2. Create areas if you haven't already:
   - Living Room
   - Bedroom
   - Kitchen
   - etc.
3. Go back to **Settings** → **Devices & Services**
4. For each device, click on it and assign it to an area

### Step 4.4: Trigger Initial Sync

The integration will automatically sync your exposed entities, but you can trigger it manually:

1. Go to **Developer Tools** → **Services**
2. Select service: `intentgine.sync_toolsets`
3. Click **Call Service**
4. Wait 10-30 seconds for sync to complete

### Step 4.5: Verify Sync

1. Go to your [Intentgine Dashboard](https://intentgine.dev/dashboard)
2. Click on your **Home Assistant** app
3. Click on **Toolsets** in the left menu
4. You should see toolsets like:
   - `ha-living-room-v1`
   - `ha-bedroom-v1`
   - `ha-global-v1`
5. Click on a toolset to see the tools (actions) available

✅ **Checkpoint**: Your devices are exposed and synced to Intentgine.

---

## Part 5: Add Dashboard Card

**Time**: 2-3 minutes

Now let's add a card to your dashboard so you can send commands.

### Step 5.1: Edit Your Dashboard

1. Go to your Home Assistant dashboard (Overview)
2. Click the **three dots menu** (⋮) in the top right
3. Click **Edit Dashboard**

### Step 5.2: Add the Card

1. Click **+ Add Card** (bottom right)
2. Scroll down to find **Custom: Intentgine Command Card**
   - If you don't see it, try refreshing your browser (Ctrl+Shift+R)
3. Click on it

### Step 5.3: Configure the Card

A configuration dialog will appear. You can use the visual editor or YAML:

**Visual Editor**:
- **Title**: `Voice Command` (or any title you like)
- **Placeholder**: `What would you like to do?`
- **Show History**: Toggle ON if you want to see recent commands

**Or use YAML**:

```yaml
type: custom:intentgine-command-card
title: Voice Command
placeholder: "What would you like to do?"
show_history: true
```

### Step 5.4: Save the Card

1. Click **Save** on the card configuration
2. Click **Done** to exit edit mode

### Step 5.5: Position the Card (Optional)

1. Enter edit mode again
2. Drag the card to your preferred position
3. Click **Done**

✅ **Checkpoint**: Command card is now on your dashboard.

---

## Part 6: Test Your Setup

**Time**: 2-3 minutes

Let's make sure everything works!

### Test 1: Simple Light Command

1. Find your Intentgine Command card on the dashboard
2. In the text input, type: `Turn on the living room lights`
   - Replace "living room" with an area you have
3. Click **Run** or press Enter
4. You should see:
   - A loading indicator
   - Then a green success message: "✓ Command executed successfully"
   - Your lights should turn on!

### Test 2: Parameter Command

Try a command with parameters:

```
Set bedroom lights to 50%
```

or

```
Set bedroom temperature to 72
```

### Test 3: Different Actions

Try various commands:

```
Turn off the kitchen lights
Open the garage door
Activate movie time scene
```

### Test 4: Check Command History

If you enabled "Show History" on your card:

1. Look below the input field
2. You should see your recent commands listed
3. ✓ indicates success, ✗ indicates failure

### Troubleshooting Test Failures

**If commands don't work**:

1. **Check entity is exposed**:
   - Settings → Voice Assistants → Expose
   - Make sure the entity is toggled ON

2. **Check entity name**:
   - Be specific: "Turn on the living room lights" not just "Turn on lights"
   - Use the area name in your command

3. **Check entity is available**:
   - Go to Developer Tools → States
   - Find your entity
   - Make sure it's not "unavailable" or "unknown"

4. **Check logs**:
   - Settings → System → Logs
   - Look for errors from `custom_components.intentgine`

5. **Try manual sync**:
   - Developer Tools → Services
   - Service: `intentgine.sync_toolsets`
   - Call Service

✅ **Checkpoint**: Commands are working and controlling your devices!

---

## Part 7: Enable Voice Assistant (Optional)

**Time**: 2-3 minutes

Want to use voice commands? Let's set up the conversation agent.

### Step 7.1: Select Intentgine as Conversation Agent

1. Go to **Settings** → **Voice Assistants**
2. Click on your voice assistant (usually "Home Assistant")
3. Under **Conversation Agent**, select **Intentgine**
4. Click **Save**

### Step 7.2: Test with Voice

**If using Home Assistant Assist**:

1. Click the microphone icon in the top right of Home Assistant
2. Say: "Turn on the living room lights"
3. The command should execute

**If using Google Home**:

1. Say: "Hey Google, ask Home Assistant to turn on the living room lights"

**If using Alexa**:

1. Say: "Alexa, tell Home Assistant to turn on the living room lights"

### Step 7.3: Verify It's Working

1. Try a few voice commands
2. Check that devices respond
3. Check the Intentgine card history to see commands

✅ **Checkpoint**: Voice control is working!

---

## Troubleshooting

### Issue: Integration doesn't appear in Add Integration

**Solution**:
1. Verify files are in `config/custom_components/intentgine/`
2. Check file permissions (should be readable)
3. Restart Home Assistant
4. Clear browser cache (Ctrl+Shift+R)
5. Check logs for errors: Settings → System → Logs

### Issue: "Cannot connect to Intentgine API"

**Solution**:
1. Verify your API key is correct (starts with `sk_live_`)
2. Check internet connectivity
3. Try the default endpoint: `https://api.intentgine.dev`
4. Check Intentgine service status
5. Verify API key in Intentgine dashboard (not revoked)

### Issue: "No toolsets available"

**Solution**:
1. Expose entities: Settings → Voice Assistants → Expose
2. Manually sync: Developer Tools → Services → `intentgine.sync_toolsets`
3. Wait 30 seconds and try again
4. Check logs for sync errors

### Issue: Commands don't work

**Solution**:
1. Be more specific (include room name)
2. Check entity is exposed
3. Check entity is available (not offline)
4. Try the command in Developer Tools first:
   ```yaml
   service: light.turn_on
   target:
     entity_id: light.living_room_main
   ```
5. If manual service call works, issue is with Intentgine resolution

### Issue: Card doesn't appear

**Solution**:
1. Verify file exists: `config/custom_components/intentgine/www/intentgine-command-card.js`
2. Clear browser cache (Ctrl+Shift+R)
3. Try a different browser
4. Check browser console for JavaScript errors (F12)
5. Restart Home Assistant

### Issue: Slow responses

**Solution**:
1. First command after sync is slower (cache miss)
2. Subsequent similar commands should be faster
3. Check internet speed
4. Reduce number of exposed entities
5. Check Intentgine dashboard for API status

### Issue: "Insufficient requests remaining"

**Solution**:
1. Check usage in Intentgine dashboard
2. Wait for monthly reset
3. Upgrade your Intentgine plan
4. Reduce command frequency

---

## Next Steps

### Explore More Features

1. **Add Chat Interface**:
   ```yaml
   type: custom:intentgine-chat-card
   title: Home Assistant Chat
   persona: friendly
   ```

2. **Create Automations**:
   ```yaml
   automation:
     - alias: "Goodnight Routine"
       trigger:
         - platform: event
           event_type: intentgine_command_executed
       action:
         - service: scene.turn_on
           target:
             entity_id: scene.goodnight
   ```

3. **Set Up Scheduled Sync**:
   ```yaml
   automation:
     - alias: "Sync Intentgine Daily"
       trigger:
         - platform: time
           at: "03:00:00"
       action:
         - service: intentgine.sync_toolsets
   ```

### Learn More

- **Usage Guide**: See `docs/usage.md` for command examples
- **Examples**: See `EXAMPLES.md` for dashboard configs
- **Troubleshooting**: See `docs/troubleshooting.md` for detailed help
- **API Reference**: See `API-REFERENCE.md` for technical details

### Get Help

- **GitHub Issues**: Report bugs
- **Home Assistant Community**: Ask questions
- **Discord**: Chat with other users
- **Intentgine Support**: API-related issues

---

## Summary Checklist

After completing this guide, you should have:

- [x] Intentgine account created
- [x] API key obtained
- [x] Integration installed (HACS or manual)
- [x] Integration configured with API key
- [x] Entities exposed to voice assistants
- [x] Toolsets synced to Intentgine
- [x] Dashboard card added
- [x] Commands tested and working
- [x] (Optional) Voice assistant enabled

---

## Quick Reference

### Useful Services

```yaml
# Execute a command
service: intentgine.execute_command
data:
  query: "Turn on the living room lights"

# Sync toolsets
service: intentgine.sync_toolsets
```

### Useful Locations

- **Integration Settings**: Settings → Devices & Services → Intentgine
- **Expose Entities**: Settings → Voice Assistants → Expose
- **Logs**: Settings → System → Logs
- **Services**: Developer Tools → Services
- **Intentgine Dashboard**: https://intentgine.dev/dashboard

### Example Commands

```
Turn on the living room lights
Turn off all bedroom lights
Set kitchen lights to 50%
Set bedroom temperature to 72
Open the garage door
Close all blinds
Activate movie time scene
Dim the lights
Make it warmer
```

---

**Congratulations!** 🎉

You've successfully installed and configured Intentgine for Home Assistant. Enjoy controlling your smart home with natural language!

**Version**: 1.0.0  
**Last Updated**: February 12, 2026
