from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def fetch_links_with_selenium(url: str) -> set:
    chrome_options = Options()
    chrome_options.add_argument("--headless")            # Run headless (no UI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Disable images, stylesheets, and fonts to speed up page loading
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(55)  # Increase timeouts as needed
        driver.set_script_timeout(55)
    except WebDriverException as e:
        print(f"[DEBUG] Error initializing WebDriver: {e}")
        return set()
    
    try:
        driver.get(url)
    except Exception as e:
        print(f"[DEBUG] Exception during get(url) for {url}: {e}")
    
    try:
        # Instead of waiting for the entire body, wait for a specific element if available.
        # For example, if you know a product container's ID or class, wait for that.
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException as te:
        print(f"[DEBUG] Timeout waiting for page to load in Selenium for {url}: {te}")
        driver.quit()
        return set()
    except Exception as e:
        print(f"[DEBUG] Exception waiting for page load for {url}: {e}")
        driver.quit()
        return set()
    
    try:
        anchor_elements = driver.find_elements(By.TAG_NAME, "a")
        urls = {anchor.get_attribute("href") for anchor in anchor_elements if anchor.get_attribute("href")}
    except Exception as e:
        print(f"[DEBUG] Error extracting links for {url}: {e}")
        urls = set()
    
    driver.quit()
    return urls
