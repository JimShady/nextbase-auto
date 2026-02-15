import os
from PIL import Image
from PIL.ExifTags import TAGS
import pytesseract
from datetime import datetime
import re
from dateutil import parser as date_parser

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def extract_from_exif(image_path):
    """Extract date/time from image EXIF metadata"""
    print(f"Extracting EXIF metadata from: {image_path}")
    
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            print("  No EXIF data found")
            return None
        
        exif = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            exif[tag] = value
        
        # Look for DateTime fields
        date_fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
        
        for field in date_fields:
            if field in exif:
                date_str = exif[field]
                print(f"  Found {field}: {date_str}")
                
                try:
                    # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                    
                    data = {
                        'date': dt.strftime('%Y-%m-%d'),
                        'time': dt.strftime('%H:%M'),
                        'day_of_week': dt.strftime('%A'),
                        'source': 'EXIF'
                    }
                    
                    print(f"  ✓ Extracted from EXIF: {data['date']} {data['time']} ({data['day_of_week']})")
                    return data
                except Exception as e:
                    print(f"  Could not parse date: {e}")
        
        print("  No datetime found in EXIF")
        return None
        
    except Exception as e:
        print(f"  EXIF extraction error: {e}")
        return None


def extract_from_filename(image_path):
    """Try to extract date/time from filename"""
    filename = os.path.basename(image_path)
    print(f"Checking filename for timestamp: {filename}")
    
    # Pattern for PXL_20260203_152754898.jpg format (Pixel camera)
    match = re.search(r'(\d{8})_(\d{6})', filename)
    if match:
        date_part = match.group(1)  # YYYYMMDD
        time_part = match.group(2)  # HHMMSS
        
        try:
            dt = datetime.strptime(f"{date_part}{time_part}", "%Y%m%d%H%M%S")
            data = {
                'date': dt.strftime('%Y-%m-%d'),
                'time': dt.strftime('%H:%M'),
                'day_of_week': dt.strftime('%A'),
                'source': 'filename'
            }
            print(f"  ✓ Extracted from filename: {data['date']} {data['time']} ({data['day_of_week']})")
            return data
        except:
            pass
    
    print("  No timestamp pattern found in filename")
    return None


def extract_with_ocr(image_path):
    """Extract text from image using OCR"""
    print(f"Analyzing image with OCR: {image_path}")
    
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""


def extract_with_openai(image_path, api_key):
    """Extract incident details from image using OpenAI Vision API"""
    if not OPENAI_AVAILABLE:
        print("OpenAI library not available, falling back to OCR")
        return extract_with_ocr(image_path)
    
    print(f"Analyzing image with OpenAI Vision: {image_path}")
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Read image and encode to base64
        import base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this dashcam/street image and extract the following information:
1. Date (look for date stamp on the image)
2. Time (look for time stamp on the image)
3. Vehicle registration number (license plate)
4. Vehicle colour (the main body color of the vehicle in the image)
5. Incident type - determine if this is a:
   - "corner" incident: vehicle parked within 10m of a junction/corner, obscuring visibility at junction, or on dropped kerb near junction
   - "pavement" incident: vehicle parked partly or wholly on pavement/footway, blocking pedestrian access

Please format your response as:
DATE: [date in format YYYY-MM-DD or as shown]
TIME: [time in format HH:MM]
REGISTRATION: [vehicle registration number]
COLOUR: [vehicle colour e.g. silver, blue, white, black, red]
INCIDENT_TYPE: [corner OR pavement]
DETAILS: [brief description of what you see]

If any information is not visible or unclear, write "NOT VISIBLE" for that field."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        print("Falling back to OCR...")
        return extract_with_ocr(image_path)


def parse_extracted_data(extracted_text):
    """Parse extracted text to find incident details"""
    data = {
        'date': None,
        'time': None,
        'day_of_week': None,
        'registration': None,
        'colour': None,
        'incident_type': None
    }
    
    print("\nExtracted text:")
    print(extracted_text)
    print("\n" + "="*50)
    
    # Look for date patterns
    date_patterns = [
        r'DATE[:\s]+(\d{4}[-/]\d{2}[-/]\d{2})',
        r'DATE[:\s]+(\d{2}[-/]\d{2}[-/]\d{4})',
        r'(\d{4}[-/]\d{2}[-/]\d{2})',
        r'(\d{2}[-/]\d{2}[-/]\d{4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            try:
                parsed_date = date_parser.parse(date_str, dayfirst=True)
                data['date'] = parsed_date.strftime('%Y-%m-%d')
                data['day_of_week'] = parsed_date.strftime('%A')
                break
            except:
                pass
    
    # Look for time patterns
    time_patterns = [
        r'TIME[:\s]+(\d{1,2}:\d{2}(?::\d{2})?)',
        r'(\d{1,2}:\d{2}:\d{2})',
        r'(\d{1,2}:\d{2})',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            time_str = match.group(1)
            # Remove seconds if present and keep HH:MM format
            data['time'] = time_str[:5] if len(time_str) > 5 else time_str
            break
    
    # Look for registration patterns (UK format)
    reg_patterns = [
        r'REGISTRATION[:\s]+([A-Z]{2}\d{2}\s?[A-Z]{3})',
        r'\b([A-Z]{2}\d{2}\s?[A-Z]{3})\b',
        r'\b([A-Z]\d{1,3}\s?[A-Z]{3})\b',
    ]
    
    for pattern in reg_patterns:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            data['registration'] = match.group(1).replace(' ', '')
            break
    
    # Look for colour patterns
    colour_patterns = [
        r'COLOU?R[:\s]+([a-zA-Z\s]+?)(?:\n|$|(?=\w+:))',
    ]
    
    for pattern in colour_patterns:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            colour_text = match.group(1).strip()
            # Remove "NOT VISIBLE" if that's what was returned
            if "NOT VISIBLE" not in colour_text.upper():
                data['colour'] = colour_text.lower()
            break
    
    # Look for incident type patterns
    incident_type_patterns = [
        r'INCIDENT[_\s]TYPE[:\s]+(corner|pavement)',
    ]
    
    for pattern in incident_type_patterns:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            incident_type_text = match.group(1).strip().lower()
            # Validate it's one of our known types
            if incident_type_text in ['corner', 'pavement']:
                data['incident_type'] = incident_type_text
            break
    
    return data


def analyze_dashcam_image(image_path, openai_api_key=None):
    """Main function to analyze dashcam image and extract incident details"""
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return None
    
    incident_data = {}
    
    # Try EXIF metadata first
    print("\n" + "="*50)
    print("Method 1: Trying EXIF metadata...")
    print("="*50)
    exif_data = extract_from_exif(image_path)
    
    # Try filename extraction
    if not exif_data:
        print("\n" + "="*50)
        print("Method 2: Trying filename timestamp...")
        print("="*50)
        exif_data = extract_from_filename(image_path)
    
    # If EXIF or filename provided date/time, use it
    if exif_data:
        incident_data['date'] = exif_data['date']
        incident_data['time'] = exif_data['time']
        incident_data['day_of_week'] = exif_data['day_of_week']
        print(f"\n✓ Using {exif_data['source']} data for date/time")
    
    # Always try OCR for registration number and other details
    print("\n" + "="*50)
    print("Method 3: Using OCR/AI for registration and other details...")
    print("="*50)
    
    # Use OpenAI if API key provided, otherwise use OCR
    if openai_api_key and OPENAI_AVAILABLE:
        extracted_text = extract_with_openai(image_path, openai_api_key)
    else:
        extracted_text = extract_with_ocr(image_path)
    
    # Parse the extracted data
    ocr_data = parse_extracted_data(extracted_text)
    
    # Merge: prefer EXIF for date/time, OCR for registration
    if not incident_data.get('date'):
        incident_data['date'] = ocr_data.get('date')
    if not incident_data.get('time'):
        incident_data['time'] = ocr_data.get('time')
    if not incident_data.get('day_of_week'):
        incident_data['day_of_week'] = ocr_data.get('day_of_week')
    
    incident_data['registration'] = ocr_data.get('registration')
    incident_data['colour'] = ocr_data.get('colour')
    incident_data['incident_type'] = ocr_data.get('incident_type')
    
    print("\n" + "="*50)
    print("FINAL EXTRACTED DATA:")
    print("="*50)
    print(f"  Date: {incident_data.get('date') or 'NOT FOUND'}")
    print(f"  Time: {incident_data.get('time') or 'NOT FOUND'}")
    print(f"  Day of week: {incident_data.get('day_of_week') or 'NOT FOUND'}")
    print(f"  Registration: {incident_data.get('registration') or 'NOT FOUND'}")
    print(f"  Colour: {incident_data.get('colour') or 'NOT FOUND'}")
    print(f"  Incident type: {incident_data.get('incident_type') or 'NOT FOUND'}")
    
    return incident_data


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_from_image.py <image_path> [openai_api_key]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyze_dashcam_image(image_path, api_key)
