# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-15

### Added
- **Telegram Bot** - Mobile-friendly incident reporting via Telegram
  - Interactive conversation flow with 19 questions
  - Photo upload support
  - Manual data entry (no AI/OpenAI required)
  - Mobile-optimized copy-paste output format
  - Privacy notice for personal data collection
  - Split output into 4 easy-to-copy messages
  - Keyboard buttons for incident type and gender selection
  - Automatic day-of-week calculation from date
  - `/start`, `/help`, `/cancel` commands
- Documentation: `TELEGRAM_BOT.md` setup guide
- Privacy notice in bot conversation flow
- Error handling in bot functions

### Changed
- Updated README.md to highlight both Telegram bot and CLI tool options
- Version bumped to 1.1.0
- Clarified language: "bad parking" instead of "traffic incidents" 
- Removed "dashcam" references, updated to "photos from mobile phone"
- Added `python-telegram-bot` to requirements.txt
- Updated `.env.example` with `TELEGRAM_BOT_TOKEN` field

## [1.0.0] - 2026-02-15

### Added
- Initial release of Nextbase Auto form filling tool
- Automated form filling for South Yorkshire Police Nextbase portal
- OpenAI GPT-4o Vision integration for intelligent vehicle detection
- Auto-detection of vehicle registration numbers from dashcam images
- Auto-detection of vehicle colours from dashcam images
- Auto-detection of incident type (corner vs pavement parking)
- EXIF metadata extraction for date/time from dashcam images
- Filename timestamp parsing as fallback for date/time extraction
- Multi-image upload support
- Interactive verification workflow with image preview
- Highway Code compliant incident templates
  - Corner parking template (Rule 243, RT88508)
  - Pavement parking template (Rules 145, 244, RT88508)
- Command-line interface with flexible parameters
- Support for 'auto' keyword to enable AI extraction
- Manual fallback prompts when auto-detection fails
- Chrome browser automation with Selenium
- Form field auto-population from configuration file
- Installation script for Linux/Ubuntu (install.sh)
- Development tools:
  - `inspect_form.py` - Web form structure inspector
  - `extract_from_image.py` - Standalone image analysis tool

### Security
- Personal data stored in gitignored `form_data.txt`
- OpenAI API key securely stored in configuration file
- Browser remains open for manual reCAPTCHA verification
- User verification step before form submission

## [Unreleased]

### Planned
- Cloud deployment guide for 24/7 bot availability
- Support for additional police forces/Nextbase portals
- Video file support (extract frames automatically)
- Batch processing for multiple incidents
- Configuration file validation
- More incident templates (other Highway Code violations)
- Bot conversation state persistence
- Multi-language support

---

## Version History

- **1.1.0** (2026-02-15) - Telegram bot for mobile reporting
- **1.0.0** (2026-02-15) - Initial release with CLI tool
