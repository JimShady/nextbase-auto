from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import os
from extract_from_image import analyze_dashcam_image


def setup_driver(headless=True):
    """Setup Chrome driver with options"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    print("Setting up ChromeDriver...")
    driver_path = ChromeDriverManager().install()
    driver_dir = os.path.dirname(driver_path)
    actual_driver = os.path.join(driver_dir, 'chromedriver')
    
    if os.path.exists(actual_driver):
        driver_path = actual_driver
        os.chmod(driver_path, 0o755)
    
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def load_form_data(file_path='form_data.txt'):
    """Load form data from text file"""
    data = {}
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                data[key.strip()] = value.strip()
    
    return data


def fill_form(driver, form_data, incident_data=None):
    """Fill the Nextbase form with provided data"""
    url = "https://secureform.nextbase.co.uk/?location=SouthYorkshire"
    
    print(f"Loading form: {url}")
    driver.get(url)
    
    # Wait for page to load
    time.sleep(3)
    
    # Handle the welcome modal - "I am willing to attend court if required to do so"
    try:
        print("Looking for welcome modal...")
        modal = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "welcome-modal"))
        )
        print("  Modal found, clicking 'I am willing to attend court' button...")
        close_button = driver.find_element(By.ID, "modal-close")
        close_button.click()
        time.sleep(1)
        print("  ✓ Modal closed")
    except Exception as e:
        print(f"  No modal found or already closed: {e}")
    
    # Auto-fill today's date in YYYY-MM-DD format (for HTML5 date input)
    if form_data.get('date_today') == '[AUTO]':
        form_data['date_today'] = datetime.now().strftime('%Y-%m-%d')
        print(f"  ✓ Set today's date to: {form_data['date_today']}")
    
    # Convert date_of_birth from dd/mm/yyyy to YYYY-MM-DD for HTML5 date input
    if form_data.get('date_of_birth'):
        dob = form_data.get('date_of_birth')
        if '/' in dob:  # If in dd/mm/yyyy format, convert to YYYY-MM-DD
            try:
                dt = datetime.strptime(dob, '%d/%m/%Y')
                form_data['date_of_birth'] = dt.strftime('%Y-%m-%d')
                print(f"  ✓ Converted date_of_birth to: {form_data['date_of_birth']}")
            except:
                print(f"  ⚠️  Could not convert date_of_birth format: {dob}")
    
    # Merge incident data from image if available (for date/time extraction)
    if incident_data:
        if form_data.get('incident_date') == '[EXTRACT_FROM_IMAGE]':
            # HTML5 date input expects YYYY-MM-DD format
            form_data['incident_date'] = incident_data.get('date', '')
            print(f"  ✓ Extracted incident date: {form_data['incident_date']}")
        if form_data.get('incident_day') == '[EXTRACT_FROM_IMAGE]':
            form_data['incident_day'] = incident_data.get('day_of_week', '')
            print(f"  ✓ Extracted incident day: {form_data['incident_day']}")
        if form_data.get('incident_time') == '[EXTRACT_FROM_IMAGE]':
            form_data['incident_time'] = incident_data.get('time', '')
            print(f"  ✓ Extracted incident time: {form_data['incident_time']}")
        # Registration and colour already set from prompts/auto-detection above
    
    print("\nFilling form fields...")
    
    # Map form_data keys to field IDs
    field_mapping = {
        'signature': 'signature',
        'date_today': 'frm-date-today',
        'first_name': 'first-name',
        'last_name': 'last-name',
        'email': 'email',
        'phone': 'phone',
        'address1': 'address1',
        'address2': 'address2',
        'address_county': 'addresscounty',
        'address_postcode': 'addresspc',
        'occupation': 'occupation',
        'date_of_birth': 'frm-date-of-birth',
        'place_of_birth': 'place-of-birth',
        'former_name': 'former-name',
        'gender': 'gender',
        'incident_location': 'incident-location',
        'incident_location_exact': 'incident-location-exact',
        'travelling_location': 'travelling-location',
        'incident_date': 'frm-incident-date',
        'incident_day': 'incident-day',
        'incident_time': 'incident-time',
        'incident_car_registration': 'incident-carreg',
        'incident_car_colour': 'incident-carcolour',
        'incident_car_make': 'incident-carmake',
        'incident_car_model': 'incident-carmodel',
    }
    
    # Fill each field
    for data_key, field_id in field_mapping.items():
        value = form_data.get(data_key, '')
        
        if value and value not in ['[AUTO]', '[EXTRACT_FROM_IMAGE]']:
            try:
                field = driver.find_element(By.ID, field_id)
                
                # For date fields, use JavaScript to set the value directly
                # to avoid issues with send_keys and date validation
                if 'date' in data_key.lower() and field.get_attribute('type') == 'date':
                    driver.execute_script("arguments[0].value = arguments[1];", field, value)
                    # Trigger change event to update any listeners
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", field)
                    print(f"  ✓ Filled {data_key}: {value}")
                else:
                    field.clear()
                    field.send_keys(value)
                    print(f"  ✓ Filled {data_key}: {value}")
            except Exception as e:
                print(f"  ✗ Could not fill {data_key}: {e}")
    
    # Handle incident description textarea
    if form_data.get('incident_description'):
        try:
            desc_field = driver.find_element(By.ID, "incident-description")
            desc_field.clear()
            desc_field.send_keys(form_data['incident_description'])
            print(f"  ✓ Filled incident description")
        except Exception as e:
            print(f"  ✗ Could not fill incident description: {e}")
    
    # Always select "Email" for preferred contact method
    try:
        # Look for the preferred contact dropdown/select element
        # Try different possible selectors
        preferred_contact = None
        try:
            preferred_contact = Select(driver.find_element(By.ID, "preferredContact"))
        except:
            pass
        
        if not preferred_contact:
            try:
                preferred_contact = Select(driver.find_element(By.NAME, "preferredContact"))
            except:
                pass
        
        if preferred_contact:
            preferred_contact.select_by_visible_text("Email")
            print(f"  ✓ Selected preferred contact: Email")
    except Exception as e:
        print(f"  ✗ Could not set preferred contact: {e}")
    
    # Always select "18 or over" for age
    try:
        age_dropdown = None
        try:
            age_dropdown = Select(driver.find_element(By.ID, "age"))
        except:
            pass
        
        if not age_dropdown:
            try:
                age_dropdown = Select(driver.find_element(By.NAME, "age"))
            except:
                pass
        
        if age_dropdown:
            # Try to select by visible text first, fallback to index if that fails
            try:
                age_dropdown.select_by_visible_text("18 or over")
            except:
                age_dropdown.select_by_index(3)  # Try 4th option (index 3) if text match fails
            print(f"  ✓ Selected age: 18 or over")
    except Exception as e:
        print(f"  ✗ Could not set age: {e}")
    
    # Always fill "Not applicable" for unavailable dates
    try:
        dates_field = driver.find_element(By.ID, "dates-unavailiable")
        dates_field.clear()
        dates_field.send_keys("Not applicable")
        print(f"  ✓ Filled unavailable dates: Not applicable")
    except Exception as e:
        print(f"  ✗ Could not fill unavailable dates: {e}")
    
    # Upload files if provided
    upload_files = form_data.get('upload_files', '')
    if upload_files:
        file_paths = [f.strip() for f in upload_files.split(',') if f.strip()]
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    # Find the file input element - it's usually hidden
                    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                    file_input.send_keys(os.path.abspath(file_path))
                    print(f"  ✓ Uploaded file: {os.path.basename(file_path)}")
                    time.sleep(2)  # Wait for upload to process
                except Exception as e:
                    print(f"  ✗ Could not upload {file_path}: {e}")
            else:
                print(f"  ✗ File not found: {file_path}")
    
    print("\nForm filling complete!")
    print("\nNOTE: reCAPTCHA must be completed manually")
    print("The browser will remain open for you to:")
    print("  1. Verify uploaded files")
    print("  2. Complete reCAPTCHA")
    print("  3. Review and submit the form")
    
    # Keep browser open
    input("\nPress Enter when you're done to close the browser...")


def load_incident_templates(file_path='incident_templates.txt'):
    """Load incident description templates from text file"""
    templates = {}
    current_key = None
    current_value = []
    
    with open(file_path, 'r') as f:
        for line in f:
            # Skip comments and empty lines at the start
            if not line.strip() or line.strip().startswith('#'):
                if current_key:  # If we're in a multi-line value, preserve the blank line
                    current_value.append('')
                continue
            
            # Check if this is a new key=value line
            if '=' in line and not current_key:
                key, value = line.split('=', 1)
                current_key = key.strip()
                # Remove leading/trailing quotes and whitespace
                value = value.strip().strip('"\'')
                current_value = [value]
            elif current_key:
                # Continue multi-line value
                value = line.strip().strip('"\'')
                if value:  # Only add non-empty lines to avoid trailing spaces
                    current_value.append(value)
                else:
                    current_value.append('')  # Preserve paragraph breaks
                
                # Check if this line ends the value (ends with closing quote)
                if line.rstrip().endswith('"') or line.rstrip().endswith("'"):
                    # Join all lines with newlines and save
                    templates[current_key] = '\n'.join(current_value).strip('"\'')
                    current_key = None
                    current_value = []
    
    # Handle case where file doesn't end with closing quote
    if current_key:
        templates[current_key] = '\n'.join(current_value).strip('"\'')
    
    return templates


def main():
    import sys
    
    # Parse command line arguments
    if len(sys.argv) < 5:
        print("Usage: python fill_form.py <street_name> <incident_type> <registration> <colour> <image_path> [additional_images...]")
        print("       python fill_form.py <street_name> auto auto auto <image_path> [additional_images...]")
        print("")
        print("Examples:")
        print("  python fill_form.py 'Hunter House Road' 'corner' 'AB12XYZ' 'silver' photo.jpg")
        print("  python fill_form.py 'Hunter House Road' 'corner' 'auto' 'auto' photo.jpg  # Extract registration & colour")
        print("  python fill_form.py 'Hunter House Road' 'auto' 'auto' 'auto' photo.jpg  # Auto-detect everything")
        print("")
        print("Available incident types: corner, pavement, or 'auto' to detect from image")
        print("Use 'auto' for incident_type, registration and/or colour to extract from the image using OpenAI Vision (requires API key in form_data.txt)")
        sys.exit(1)
    
    street_name = sys.argv[1]
    incident_type = sys.argv[2].lower()
    registration = sys.argv[3].upper() if sys.argv[3].lower() != 'auto' else 'auto'
    colour = sys.argv[4] if len(sys.argv) > 4 else 'auto'  # Default to auto if not provided
    image_paths = sys.argv[5:] if len(sys.argv) > 5 else []
    
    # If colour is provided but no images, treat colour as first image path
    if not image_paths and colour and colour.lower() != 'auto':
        # Check if colour looks like a file path
        if '/' in colour or '.' in colour:
            image_paths = [colour]
            colour = 'auto'
    
    # Validate all images exist
    for image_path in image_paths:
        if not os.path.exists(image_path):
            print(f"Error: Image file not found: {image_path}")
            sys.exit(1)
    
    # Load form data first to check for API key (needed for auto-detection)
    print("Loading form data from form_data.txt...")
    form_data = load_form_data('form_data.txt')
    
    # If incident_type is 'auto', we need to analyze the image first
    incident_data = None
    if incident_type == 'auto' or registration == 'auto' or colour.lower() == 'auto':
        dashcam_image = image_paths[0] if image_paths else ''
        openai_key = form_data.get('openai_api_key', '')
        
        if not openai_key:
            print("\nError: Auto-detection requires OpenAI API key in form_data.txt")
            sys.exit(1)
        
        if dashcam_image and os.path.exists(dashcam_image):
            print(f"\nAnalyzing image for auto-detection: {dashcam_image}")
            from extract_from_image import analyze_dashcam_image
            incident_data = analyze_dashcam_image(dashcam_image, openai_key)
            
            # Use extracted incident_type if set to auto
            if incident_type == 'auto':
                if incident_data and incident_data.get('incident_type'):
                    incident_type = incident_data['incident_type']
                    print(f"\n✓ Auto-detected incident type: {incident_type}")
                else:
                    print("\n⚠️  Could not auto-detect incident type from image")
                    print("Please specify the incident type:")
                    print("  1. corner - parking near junction/corner")
                    print("  2. pavement - parking on pavement/footway")
                    choice = input("Enter 1 or 2: ").strip()
                    if choice == '1':
                        incident_type = 'corner'
                    elif choice == '2':
                        incident_type = 'pavement'
                    else:
                        print("Invalid choice")
                        sys.exit(1)
                    print(f"✓ Incident type set to: {incident_type}")
            
            # Check registration if set to auto
            if registration == 'auto':
                if incident_data and incident_data.get('registration'):
                    registration = incident_data['registration'].upper()
                    print(f"✓ Auto-detected registration: {registration}")
                else:
                    print("\n⚠️  Could not auto-detect registration from image")
                    registration = input("Enter vehicle registration: ").strip().upper()
                    if registration:
                        print(f"✓ Registration set to: {registration}")
                    else:
                        print("Error: Registration is required")
                        sys.exit(1)
            
            # Check colour if set to auto
            if colour.lower() == 'auto':
                if incident_data and incident_data.get('colour'):
                    colour = incident_data['colour'].lower()
                    print(f"✓ Auto-detected colour: {colour}")
                else:
                    print("\n⚠️  Could not auto-detect colour from image")
                    colour = input("Enter vehicle colour: ").strip().lower()
                    if colour:
                        print(f"✓ Colour set to: {colour}")
                    else:
                        print("Error: Colour is required")
                        sys.exit(1)
    
    # Validate incident type
    print(f"\nLoading incident templates...")
    templates = load_incident_templates('incident_templates.txt')
    
    if incident_type not in templates:
        print(f"Error: Unknown incident type '{incident_type}'")
        print(f"Available types: {', '.join(templates.keys())}")
        sys.exit(1)
    
    # Override with command line parameters
    form_data['incident_location'] = street_name
    form_data['incident_location_exact'] = street_name
    form_data['travelling_location'] = street_name  # Where you were travelling towards
    form_data['incident_description'] = templates[incident_type]
    form_data['incident_car_registration'] = registration
    form_data['incident_car_colour'] = colour
    
    form_data['upload_files'] = ','.join(image_paths)  # All images for upload
    form_data['dashcam_image_path'] = image_paths[0] if image_paths else ''    # First image for EXIF extraction
    
    print(f"\n✓ Incident location set to: {street_name}")
    print(f"✓ Travelling towards: {street_name}")
    print(f"✓ Incident type: {incident_type}")
    print(f"✓ Vehicle registration: {registration}")
    print(f"✓ Vehicle colour: {colour}")
    print(f"✓ Images to upload: {len(image_paths)}")
    for idx, img in enumerate(image_paths, 1):
        print(f"    {idx}. {img}")
    if image_paths:
        print(f"✓ Using first image for EXIF data extraction: {image_paths[0]}")
    
    # Display image and confirm details before proceeding
    print("\n" + "="*50)
    print("VERIFICATION")
    print("="*50)
    
    # Open image for verification
    if image_paths:
        print(f"\nOpening image for verification: {image_paths[0]}")
        import subprocess
        import platform
        
        try:
            # Open image with default viewer
            img_path = os.path.abspath(image_paths[0])
            if platform.system() == 'Darwin':  # macOS
                image_process = subprocess.Popen(['open', img_path])
            elif platform.system() == 'Windows':
                image_process = subprocess.Popen(['start', img_path], shell=True)
            else:  # Linux
                image_process = subprocess.Popen(['xdg-open', img_path])
            
            print("✓ Image opened in viewer")
        except Exception as e:
            print(f"⚠️  Could not open image automatically: {e}")
            print(f"   Please manually view: {img_path}")
    
    # Interactive confirmation
    print("\nPlease verify the following details while viewing the image:")
    print(f"\n1. Incident type: {incident_type}")
    confirm = input("   Is this correct? (y/n or press Enter to confirm): ").strip().lower()
    if confirm == 'n':
        print("   Please select the correct incident type:")
        print("     1. corner - parking near junction/corner")
        print("     2. pavement - parking on pavement/footway")
        choice = input("   Enter 1 or 2: ").strip()
        if choice == '1':
            incident_type = 'corner'
        elif choice == '2':
            incident_type = 'pavement'
        print(f"   ✓ Updated to: {incident_type}")
    
    print(f"\n2. Vehicle registration: {registration}")
    confirm = input("   Is this correct? (y/n or press Enter to confirm): ").strip().lower()
    if confirm == 'n':
        new_reg = input("   Enter correct registration: ").strip().upper()
        if new_reg:
            registration = new_reg
            print(f"   ✓ Updated to: {registration}")
    
    print(f"\n3. Vehicle colour: {colour}")
    confirm = input("   Is this correct? (y/n or press Enter to confirm): ").strip().lower()
    if confirm == 'n':
        new_colour = input("   Enter correct colour: ").strip().lower()
        if new_colour:
            colour = new_colour
            print(f"   ✓ Updated to: {colour}")
    
    # Close the image viewer
    if image_paths:
        try:
            if platform.system() != 'Windows':
                image_process.terminate()
            print("\n✓ Image viewer closed")
        except:
            print("\n⚠️  Please close the image viewer manually")
    
    print("\n" + "="*50)
    print("PROCEEDING WITH FORM FILLING")
    print("="*50)
    
    # Update form_data with verified/corrected values
    form_data['incident_car_registration'] = registration
    form_data['incident_car_colour'] = colour
    # Reload templates in case incident_type was changed
    templates = load_incident_templates('incident_templates.txt')
    form_data['incident_description'] = templates[incident_type]
    
    print(f"\n✓ Final values to be filled:")
    print(f"  Incident type: {incident_type}")
    print(f"  Registration: {registration}")
    print(f"  Colour: {colour}")
    
    # If we haven't analyzed the image yet (because nothing was set to 'auto'), do it now
    if incident_data is None and image_paths:
        dashcam_image = image_paths[0]
        openai_key = form_data.get('openai_api_key', '')
        
        if dashcam_image and os.path.exists(dashcam_image):
            print(f"\nAnalyzing dashcam image for date/time: {dashcam_image}")
            from extract_from_image import analyze_dashcam_image
            incident_data = analyze_dashcam_image(
                dashcam_image,
                openai_key if openai_key else None
            )
    
    # Setup browser
    driver = setup_driver(headless=False)  # Use headless=False to keep browser visible
    
    try:
        fill_form(driver, form_data, incident_data)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
