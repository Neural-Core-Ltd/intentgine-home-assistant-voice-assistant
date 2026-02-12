# Installation Guide

## Prerequisites

- Home Assistant 2024.1 or newer
- Active Intentgine subscription ([sign up here](https://intentgine.dev))
- Intentgine API key

## Method 1: HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu (⋮) in the top right
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/intentgine/ha-integration`
6. Select category: "Integration"
7. Click "Add"
8. Find "Intentgine Voice Control" in the list
9. Click "Download"
10. Restart Home Assistant

## Method 2: Manual Installation

1. Download the latest release from GitHub
2. Extract the `intentgine` folder from the zip file
3. Copy the `intentgine` folder to your Home Assistant `config/custom_components/` directory
4. Your directory structure should look like:
   ```
   config/
   └── custom_components/
       └── intentgine/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           └── ...
   ```
5. Restart Home Assistant

## Verify Installation

1. Go to **Settings** → **System** → **Logs**
2. Look for any errors related to `intentgine`
3. If no errors, the integration is installed correctly

## Next Steps

Continue to the [Configuration Guide](configuration.md) to set up the integration.
