# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-02-13

### Added
- **Multi-Intent Command Support**: Handle commands with multiple intents in a single request
  - Example: "Turn on kitchen lights and turn off bedroom lights"
  - Uses Intentgine's classification extraction feature
  - Automatically splits compound commands and routes to appropriate areas
- **Natural Language Responses**: Optional `use_respond` parameter for human-friendly responses
  - Set `use_respond=True` to get natural language feedback
  - Uses app's configured persona
  - Works with both single and multi-intent commands
  - Example: "I've turned on the kitchen lights for you."
- Classification extraction enabled on area router classification set
- Enhanced command handler to process extracted sub-commands
- Comprehensive extraction examples documentation (EXTRACTION-EXAMPLES.md)
- Natural language responses documentation (NATURAL-LANGUAGE-RESPONSES.md)

### Changed
- API client now supports `enable_extraction` parameter for classification sets
- Command handler accepts optional `use_respond` parameter (defaults to False)
- Command handler returns structured results for multi-intent commands
- Updated cost documentation to reflect extraction overhead
- README updated with multi-intent command examples

### Technical Details
- Area router classification set now created with `enable_extraction: true`
- Single-intent commands: 2 requests (1 classify + 1 resolve/respond)
- Multi-intent commands: 2 + N requests (2 for classify with extraction + N resolve/respond)
- Extraction happens automatically when LLM detects multiple distinct intents
- Natural language responses use same request count as structured responses

## [1.0.0] - 2026-02-12

### Added
- Initial release
- Natural language command processing via Intentgine API
- Area-based toolset organization
- Automatic entity synchronization
- Config flow for easy setup
- Dashboard command card
- Chat interface card
- Conversation agent integration
- Support for lights, switches, climate, covers, and scenes
- Service calls for command execution and sync
- Comprehensive documentation

### Features
- 🗣️ Natural language control
- 🏠 Area-based organization
- 🔄 Auto-sync with entity changes
- 🔒 Respects entity exposure settings
- 💬 Conversational interface
- 🎯 High accuracy with semantic caching

### Supported Domains
- light (turn on/off, brightness)
- switch (turn on/off)
- climate (set temperature)
- cover (open/close)
- scene (activate)

### Known Issues
- First command after sync may be slower (cache miss)
- Limited to English commands
- Requires internet connectivity

## [Unreleased]

### Planned
- Memory banks for learning from corrections
- Additional entity domain support
- Multi-language support
- Local LLM option (when available)
- Advanced parameter handling
- Custom tool templates
- Parallel execution of extracted commands
