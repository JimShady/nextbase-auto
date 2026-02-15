# Nextbase Auto

Automated form filling tool for Nextbase dashcam incident reporting to South Yorkshire Police. Uses Python, Selenium, and OpenAI Vision to automatically fill incident report forms with data extracted from dashcam images.

## Features

- 🚗 **Automated Form Filling** - Fills all personal and incident details automatically
- 📸 **Image Analysis** - Extracts date, time, vehicle registration, and colour from dashcam images
- 🤖 **OpenAI Vision Integration** - Uses GPT-4o Vision to intelligently analyze images
- 📋 **Template System** - Pre-written incident descriptions referencing Highway Code rules
- 🔄 **Multi-Image Upload** - Support for uploading multiple images per incident
- ⚡ **EXIF Extraction** - Reads date/time metadata from image files
- 🎯 **Command-Line Interface** - Simple, scriptable interface for quick submissions

## Quick Start

```bash
# 1. Install dependencies (Linux/Ubuntu)
./install.sh

# Or install manually
pip install -r requirements.txt

# 2. Configure your details
cp form_data.txt.example form_data.txt
# Edit form_data.txt with your personal information

# 3. Submit an incident (auto-detect everything from image)
python fill_form.py 'Hunter House Road' auto auto auto photo.jpg
```

## Setup

### 1. Install Dependencies

**Linux/Ubuntu (Recommended):**
```bash
./install.sh
```
This installs both system dependencies (Tesseract OCR) and Python packages.

**Manual installation:**
```bash
# Install Tesseract OCR (Linux)
sudo apt install tesseract-ocr

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Personal Information

Copy the example file and add your details:
```bash
cp form_data.txt.example form_data.txt
```

Edit `form_data.txt` with your personal details:
- Name, email, phone, address
- Date of birth, occupation, etc.
- OpenAI API key (optional, for automatic extraction)

**Important:** `form_data.txt` is in `.gitignore` and will not be committed to version control. Keep it secure and never share it publicly.

## Usage

### Basic Command Structure

```bash
python fill_form.py <street_name> <incident_type> <registration> <colour> <image_path> [additional_images...]
```

### Parameters

1. **street_name** - Location where incident occurred (e.g., 'Hunter House Road')
2. **incident_type** - Type of incident: `corner`, `pavement`, or `auto` to detect from image
3. **registration** - Vehicle registration number, or `auto` to extract from image
4. **colour** - Vehicle colour, or `auto` to extract from image
5. **image_path(s)** - One or more image files to upload

All parameters except street_name support `auto` for automatic detection using OpenAI Vision.

### Examples

**Manual entry with all details:**
```bash
python fill_form.py 'Hunter House Road' 'corner' 'AB12XYZ' 'silver' photo.jpg
```

**Auto-extract registration and colour:**
```bash
python fill_form.py 'Hunter House Road' 'corner' 'auto' 'auto' photo.jpg
```

**Full auto-detection (everything except location):**
```bash
python fill_form.py 'Hunter House Road' 'auto' 'auto' 'auto' photo.jpg
```

**Upload multiple images:**
```bash
python fill_form.py 'Hunter House Road' 'pavement' 'CD34EFG' 'blue' photo1.jpg photo2.jpg photo3.jpg
```

**Note:** If auto-detection fails for any field, the script will prompt you to enter the information manually.

### What Happens When You Run It

1. ✅ Loads your personal information from `form_data.txt`
2. ✅ Loads the appropriate incident description template
3. ✅ Analyzes the first image to extract date, time, registration, colour, and incident type (if set to `auto`)
4. ✅ **Opens the image for verification** - The image displays in your default viewer
5. ✅ **Interactive verification** - Confirms incident type, registration, and colour with you:
   - Press Enter or 'y' to accept each value
   - Type 'n' to correct any value that's wrong
6. ✅ Closes the image viewer automatically
7. ✅ Opens Chrome browser and navigates to the Nextbase form
8. ✅ Accepts the court declaration pop-up
9. ✅ Fills all form fields automatically with verified data
10. ✅ Uploads all specified images
11. ⏸️ **Keeps browser open for you to:**
   - Verify all filled data is correct
   - Complete the reCAPTCHA manually
   - Submit the form
12. ✅ Press Enter in terminal to close browser

## Automatic Extraction Features

### EXIF Data Extraction
The script automatically reads date and time from image metadata (EXIF data) or filename timestamps.

### OpenAI Vision Extraction
When you use `auto` for incident_type, registration, or colour, the script uses OpenAI's GPT-4o Vision model to analyze the image and extract:
- **Incident type** - Determines if vehicle is parked near junction/corner or on pavement
- **Vehicle registration number**
- **Vehicle colour**
- Date and time (if not in EXIF)

**Requirements for auto-extraction:**
- Add your OpenAI API key to `form_data.txt`: `openai_api_key=sk-...`
- Image must clearly show the vehicle and parking context

**Fallback behavior:**
If auto-detection fails for any field, the script will interactively prompt you to enter the information manually:
- Incident type: Choose from numbered menu (1=corner, 2=pavement)
- Registration: Enter manually
- Colour: Enter manually

**Verification step:**
After extraction (whether automatic or manual), the script will:
1. Open the image in your default image viewer
2. Display the detected/entered values
3. Ask you to confirm each value (incident type, registration, colour)
4. Allow you to correct any mistakes before filling the form

This ensures complete accuracy before the form is submitted to authorities.

## File Structure

```
nextbase-auto/
├── fill_form.py              # Main script - run this to submit incidents
├── extract_from_image.py     # Image analysis and EXIF extraction module
├── incident_templates.txt    # Pre-written Highway Code compliant descriptions
├── inspect_form.py          # Development tool - inspects web form structure
├── form_data.txt.example    # Template for personal information
├── requirements.txt         # Python dependencies
├── install.sh              # Installation script (Linux/Ubuntu)
└── README.md              # This file
```

**Note:** `form_data.txt` (your actual personal data) is gitignored and not committed to the repository.

## Incident Types

### Corner
Used for vehicles that:
- Park within 10m of junctions
- Obscure visibility at junctions
- Park on dropped kerbs at junctions

### Pavement
Used for vehicles that:
- Park partly or wholly on pavements/footways
- Block wheelchair users and pedestrians
- Create unnecessary obstructions

Both templates include references to relevant Highway Code rules (Rules 145, 242, 243, 244) and offence code RT88508.

## Troubleshooting

**Browser doesn't open:**
- Check ChromeDriver is properly installed
- Try running: `python inspect_form.py` to test browser setup

**Images not uploading:**
- Verify image file paths are correct and files exist
- Check file permissions
- Supported formats: JPG, PNG, TIFF, PDF, MOV, MP4, AVI

**Auto-extraction not working:**
- Verify OpenAI API key is set in `form_data.txt`
- Check you have API credits available
- Ensure image shows registration plate clearly

**Form fields not filling:**
- Review console output for specific error messages
- Check `form_data.txt` has all required fields filled in
- Verify internet connection is stable

## Requirements

- **Python 3.7+** (tested with Python 3.8-3.11)
- **Chrome browser** (latest version recommended)
- **ChromeDriver** (auto-managed by webdriver-manager)
- **Tesseract OCR** (for image text extraction)
- **OpenAI API key** (optional, required for auto-detection features)

## Development Tools

### Inspect Form Fields
```bash
python inspect_form.py
```
Opens the Nextbase form, analyzes all fields, and saves page source to `page_source.html`. Useful for debugging or if the form structure changes.

### Test Image Extraction
```bash
python extract_from_image.py <image_path> [openai_api_key]
```
Tests extraction without filling the form. Shows what data can be extracted from your dashcam image.

## Security Notes

- **Never commit `form_data.txt`** with your personal information (it's already in `.gitignore`)
- Keep your OpenAI API key secure
- The script keeps the browser open so you can verify all data before submission
- Always review extracted data for accuracy before submitting to authorities
- Test images and personal photos are also excluded from git via `.gitignore`

## Known Limitations

- reCAPTCHA must be completed manually
- Only supports South Yorkshire Police Nextbase portal
- Requires Chrome browser
- Auto-detection quality depends on image clarity and dashcam overlay visibility

## License

This tool is for personal use to assist in reporting traffic incidents. Always verify the accuracy of automatically extracted information before submitting reports to authorities.
