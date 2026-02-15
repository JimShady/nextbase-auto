from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

def setup_driver(headless=False):
    """Setup Chrome driver with options"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    print("Installing ChromeDriver...")
    driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver installed at: {driver_path}")
    
    # Fix path - webdriver_manager sometimes returns wrong file
    driver_dir = os.path.dirname(driver_path)
    actual_driver = os.path.join(driver_dir, 'chromedriver')
    
    if os.path.exists(actual_driver):
        driver_path = actual_driver
        # Ensure it's executable
        os.chmod(driver_path, 0o755)
    
    print(f"Using ChromeDriver: {driver_path}")
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def inspect_form(url):
    """Inspect the form to identify all fields"""
    driver = setup_driver(headless=True)
    
    try:
        print(f"Loading {url}...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Find all forms
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"\nFound {len(forms)} form(s)\n")
        
        # Find all input fields
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Input fields found: {len(inputs)}")
        for i, inp in enumerate(inputs):
            field_type = inp.get_attribute("type")
            field_name = inp.get_attribute("name")
            field_id = inp.get_attribute("id")
            field_placeholder = inp.get_attribute("placeholder")
            print(f"  [{i}] Type: {field_type}, Name: {field_name}, ID: {field_id}, Placeholder: {field_placeholder}")
        
        # Find all textareas
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"\nTextarea fields found: {len(textareas)}")
        for i, ta in enumerate(textareas):
            field_name = ta.get_attribute("name")
            field_id = ta.get_attribute("id")
            print(f"  [{i}] Name: {field_name}, ID: {field_id}")
        
        # Find all select dropdowns
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"\nSelect dropdowns found: {len(selects)}")
        for i, sel in enumerate(selects):
            field_name = sel.get_attribute("name")
            field_id = sel.get_attribute("id")
            print(f"  [{i}] Name: {field_name}, ID: {field_id}")
        
        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nButtons found: {len(buttons)}")
        for i, btn in enumerate(buttons):
            btn_type = btn.get_attribute("type")
            btn_text = btn.text
            print(f"  [{i}] Type: {btn_type}, Text: {btn_text}")
        
        # Save page source for inspection
        with open("/home/james/dev/nextbase-auto/page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\nPage source saved to page_source.html")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://secureform.nextbase.co.uk/?location=SouthYorkshire"
    inspect_form(url)
