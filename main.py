from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
from dotenv import load_dotenv

load_dotenv()

def setup_driver(headless=True):
    """Setup Chrome driver with options"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fill_form(driver, url):
    """Navigate to URL and fill form"""
    driver.get(url)
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "form"))
    )
    
    # TODO: Add form filling logic here
    # Example:
    # name_field = driver.find_element(By.ID, "name")
    # name_field.send_keys("Your Name")
    
    print("Form filled successfully")

def main():
    url = os.getenv("WEBSITE_URL", "")
    
    if not url:
        print("Please set WEBSITE_URL in .env file")
        return
    
    driver = setup_driver(headless=True)
    
    try:
        fill_form(driver, url)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
