# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Support for additional police forces/Nextbase portals
- Video file support (extract frames automatically)
- Batch processing for multiple incidents
- Configuration file validation
- More incident templates (other Highway Code violations)

---

## Version History

- **1.0.0** (2026-02-15) - Initial release
