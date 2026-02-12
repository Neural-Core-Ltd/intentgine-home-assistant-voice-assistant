# Changelog

All notable changes to this project will be documented in this file.

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
