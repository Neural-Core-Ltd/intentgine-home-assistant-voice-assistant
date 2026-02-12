# Implementation Kickoff Checklist

**Before starting Phase 1 implementation**

## Prerequisites

### Environment Setup
- [ ] Home Assistant 2024.1+ installed (or test instance ready)
- [ ] Python 3.11+ available
- [ ] Code editor configured (VS Code recommended)
- [ ] Git repository initialized (if not already)

### Intentgine Account
- [ ] Account created at intentgine.dev
- [ ] App created in dashboard
- [ ] API key copied (starts with `sk_live_`)
- [ ] API key tested with curl/httpie
- [ ] Understand current plan limits

### Knowledge Check
- [ ] Read PROJECT-SUMMARY.md
- [ ] Read REQUIREMENTS.md (at least skim)
- [ ] Read ARCHITECTURE.md (at least skim)
- [ ] Understand tool generation strategy
- [ ] Understand sync strategy

## Phase 1 Kickoff

### Step 1: Create Directory Structure (15 min)

```bash
cd /home/jr/Code/intent-engine/example-app

# Create main structure
mkdir -p custom_components/intentgine
mkdir -p custom_components/intentgine/translations
mkdir -p custom_components/intentgine/lovelace
mkdir -p tests
mkdir -p docs

# Create empty files
touch custom_components/intentgine/__init__.py
touch custom_components/intentgine/manifest.json
touch custom_components/intentgine/config_flow.py
touch custom_components/intentgine/const.py
touch custom_components/intentgine/api_client.py
touch custom_components/intentgine/toolset_manager.py
touch custom_components/intentgine/command_handler.py
touch custom_components/intentgine/strings.json
touch custom_components/intentgine/translations/en.json

# Create test files
touch tests/__init__.py
touch tests/test_api_client.py
touch tests/test_toolset_manager.py
touch tests/test_command_handler.py
touch tests/conftest.py
```

**Verify**: Directory structure matches ARCHITECTURE.md

---

### Step 2: Create manifest.json (10 min)

Create the integration manifest with metadata.

**File**: `custom_components/intentgine/manifest.json`

**Content**:
```json
{
  "domain": "intentgine",
  "name": "Intentgine Voice Control",
  "documentation": "https://github.com/intentgine/ha-integration",
  "requirements": ["aiohttp>=3.8.0"],
  "codeowners": ["@intentgine"],
  "config_flow": true,
  "iot_class": "cloud_polling",
  "version": "0.1.0",
  "dependencies": [],
  "after_dependencies": []
}
```

**Verify**: Valid JSON, domain matches folder name

---

### Step 3: Create const.py (10 min)

Define all constants used throughout the integration.

**File**: `custom_components/intentgine/const.py`

**Content**:
```python
"""Constants for the Intentgine integration."""

DOMAIN = "intentgine"

# Config keys
CONF_API_KEY = "api_key"
CONF_ENDPOINT = "endpoint"
CONF_SYNC_FREQUENCY = "sync_frequency"
CONF_ENABLE_AREA_TOOLSETS = "enable_area_toolsets"
CONF_DEFAULT_PERSONA = "default_persona"

# Defaults
DEFAULT_ENDPOINT = "https://api.intentgine.dev"
DEFAULT_SYNC_FREQUENCY = "daily"
DEFAULT_PERSONA = "helpful"

# Sync frequencies
SYNC_FREQUENCY_MANUAL = "manual"
SYNC_FREQUENCY_HOURLY = "hourly"
SYNC_FREQUENCY_DAILY = "daily"

# Toolset naming
TOOLSET_PREFIX = "ha"
TOOLSET_VERSION = "v1"
TOOLSET_GLOBAL = f"{TOOLSET_PREFIX}-global-{TOOLSET_VERSION}"

# Service names
SERVICE_SYNC_TOOLSETS = "sync_toolsets"
SERVICE_EXECUTE_COMMAND = "execute_command"

# Attributes
ATTR_QUERY = "query"
ATTR_RESPONSE = "response"
ATTR_TOOL = "tool"
ATTR_PARAMETERS = "parameters"

# Events
EVENT_COMMAND_EXECUTED = f"{DOMAIN}_command_executed"
EVENT_SYNC_COMPLETE = f"{DOMAIN}_sync_complete"
```

**Verify**: All constants are uppercase, no typos

---

### Step 4: Create strings.json (10 min)

Define UI strings for config flow.

**File**: `custom_components/intentgine/strings.json`

**Content**:
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Set up Intentgine",
        "description": "Enter your Intentgine API credentials",
        "data": {
          "api_key": "API Key",
          "endpoint": "API Endpoint (optional)"
        }
      }
    },
    "error": {
      "invalid_auth": "Invalid API key",
      "cannot_connect": "Cannot connect to Intentgine API",
      "unknown": "Unexpected error occurred"
    },
    "abort": {
      "already_configured": "Intentgine is already configured"
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Intentgine Options",
        "data": {
          "sync_frequency": "Sync Frequency",
          "enable_area_toolsets": "Enable Area-Based Toolsets",
          "default_persona": "Default Persona"
        }
      }
    }
  }
}
```

**Verify**: Valid JSON, matches config flow steps

---

### Step 5: Create translations/en.json (5 min)

Copy strings.json to translations (HA requirement).

```bash
cp custom_components/intentgine/strings.json \
   custom_components/intentgine/translations/en.json
```

**Verify**: Files are identical

---

### Step 6: Set Up Testing (15 min)

Create pytest configuration and fixtures.

**File**: `tests/conftest.py`

**Content**:
```python
"""Pytest fixtures for Intentgine tests."""
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_hass():
    """Mock Home Assistant instance."""
    hass = Mock()
    hass.data = {}
    hass.states = Mock()
    hass.services = Mock()
    return hass

@pytest.fixture
def mock_api_client():
    """Mock Intentgine API client."""
    client = Mock()
    client.resolve = AsyncMock()
    client.respond = AsyncMock()
    client.create_toolset = AsyncMock()
    client.update_toolset = AsyncMock()
    client.get_toolset = AsyncMock()
    return client

@pytest.fixture
def sample_entities():
    """Sample Home Assistant entities for testing."""
    return [
        {
            "entity_id": "light.living_room_main",
            "name": "Living Room Main Light",
            "domain": "light",
            "area_id": "living_room",
            "exposed": True
        },
        {
            "entity_id": "switch.kitchen_coffee",
            "name": "Kitchen Coffee Maker",
            "domain": "switch",
            "area_id": "kitchen",
            "exposed": True
        }
    ]
```

**Verify**: Pytest can discover tests

```bash
cd /home/jr/Code/intent-engine/example-app
pytest tests/ --collect-only
```

---

### Step 7: Create Development Environment (10 min)

Set up a test Home Assistant configuration.

```bash
# Create test config directory
mkdir -p ha-test-config/custom_components

# Symlink integration
ln -s $(pwd)/custom_components/intentgine \
      ha-test-config/custom_components/intentgine

# Create basic configuration.yaml
cat > ha-test-config/configuration.yaml << EOF
# Test configuration for Intentgine integration
homeassistant:
  name: Test Home
  latitude: 37.7749
  longitude: -122.4194
  elevation: 0
  unit_system: metric
  time_zone: America/Los_Angeles

# Enable frontend
frontend:

# Enable config
config:

# Enable API
api:

# Enable logging
logger:
  default: info
  logs:
    custom_components.intentgine: debug
EOF
```

**Verify**: Can start HA with test config

```bash
hass -c ha-test-config/ --script check_config
```

---

## Ready to Code!

Once all checkboxes above are complete, you're ready to start implementing:

### Next: Implement API Client

**File**: `custom_components/intentgine/api_client.py`

**Tasks**:
1. Create `IntentgineAPIClient` class
2. Implement `__init__` with api_key and endpoint
3. Implement `resolve()` method
4. Implement error handling
5. Write tests in `tests/test_api_client.py`

**Reference**:
- See ARCHITECTURE.md section 3 for API client design
- See API-REFERENCE.md for endpoint details
- See `/supabase/functions/resolve/index.ts` for expected behavior

**Estimated Time**: 2-3 hours

---

## Development Workflow

### 1. Write Tests First (TDD)
```bash
# Write test
vim tests/test_api_client.py

# Run test (should fail)
pytest tests/test_api_client.py -v

# Implement feature
vim custom_components/intentgine/api_client.py

# Run test (should pass)
pytest tests/test_api_client.py -v
```

### 2. Test in Real HA
```bash
# Start HA with test config
hass -c ha-test-config/

# Open browser to http://localhost:8123
# Add integration via UI
# Test functionality
```

### 3. Check Code Quality
```bash
# Format code
black custom_components/intentgine/

# Lint code
pylint custom_components/intentgine/

# Type check
mypy custom_components/intentgine/
```

### 4. Commit Progress
```bash
git add .
git commit -m "feat: implement API client"
```

---

## Troubleshooting

### "Module not found" errors
- Check symlink is correct
- Restart Home Assistant
- Check `__init__.py` files exist

### Config flow not appearing
- Check `manifest.json` has `"config_flow": true`
- Check `strings.json` is valid JSON
- Restart Home Assistant

### Tests not running
- Install pytest: `pip install pytest pytest-asyncio`
- Check `conftest.py` exists
- Run with `-v` flag for verbose output

### API calls failing
- Verify API key is correct
- Check internet connectivity
- Test with curl first
- Check Intentgine dashboard for errors

---

## Quick Reference

### File Locations
- Integration code: `custom_components/intentgine/`
- Tests: `tests/`
- Test HA config: `ha-test-config/`
- Documentation: `docs/`

### Key Commands
```bash
# Run tests
pytest tests/ -v

# Start HA
hass -c ha-test-config/

# Check config
hass -c ha-test-config/ --script check_config

# Format code
black custom_components/intentgine/

# Lint code
pylint custom_components/intentgine/
```

### Key Files to Reference
- `ARCHITECTURE.md` - Technical design
- `API-REFERENCE.md` - API endpoints
- `PROJECT-SUMMARY.md` - Quick context
- `IMPLEMENTATION.md` - Task tracker

---

## Success Criteria for Phase 1

You'll know Phase 1 is complete when:

- [ ] Integration loads without errors
- [ ] Config flow works (can add integration via UI)
- [ ] Can enter API key and it validates
- [ ] Can execute a simple command (turn on light)
- [ ] Command resolves via Intentgine API
- [ ] Service call executes in Home Assistant
- [ ] Basic Lovelace card displays and works
- [ ] Tests pass with >70% coverage
- [ ] No critical bugs

**Estimated Total Time**: 15-20 hours

---

## Need Help?

- Review documentation in `example-app/` folder
- Check Intentgine API implementation in `../supabase/functions/`
- Look at Home Assistant developer docs
- Test API endpoints with curl/httpie first
- Start simple, add complexity incrementally

**Remember**: The goal is a working MVP, not perfection. Get it working, then make it better!

Good luck! 🚀
