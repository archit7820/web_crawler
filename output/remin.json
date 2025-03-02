import time
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def fetch_links_with_selenium(url: str) -> set:
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless (no UI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Block unnecessary content for performance.
    # Note: javascript is set to 1 (enabled) since many pages require it.
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2,
        "profile.managed_default_content_settings.javascript": 1,
        "profile.managed_default_content_settings.media_stream": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(55)
        driver.set_script_timeout(55)
    except WebDriverException as e:
        print(f"[DEBUG] Error initializing WebDriver: {e}")
        return set()
    
    try:
        driver.get(url)
    except Exception as e:
        print(f"[DEBUG] Exception during get(url) for {url}: {e}")
    
    try:
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
    
    # Scroll the page to load lazy-loaded content.
    scroll_page(driver)
    
    try:
        anchor_elements = driver.find_elements(By.TAG_NAME, "a")
        raw_urls = {anchor.get_attribute("href") for anchor in anchor_elements if anchor.get_attribute("href")}
    except Exception as e:
        print(f"[DEBUG] Error extracting links for {url}: {e}")
        raw_urls = set()
    
    driver.quit()
    
    # Filter URLs: skip paths and file extensions that are not required.
    skip_paths = {'/contact', '/about', '/cart', '/checkout', '/login', '/signup', '/account', '/admin', '/privacy', '/terms', '/faq', '/help'}
    skip_ext = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.xls', '.xlsx', '.zip'}
    filtered_urls = set()
    
    for link in raw_urls:
        try:
            parsed = urlparse(link)
            path_lower = parsed.path.lower()
            # Skip if any unwanted path is found in the URL's path.
            if any(skip in path_lower for skip in skip_paths):
                continue
            # Skip if URL ends with any unwanted file extension.
            if any(path_lower.endswith(ext) for ext in skip_ext):
                continue
            filtered_urls.add(link)
        except Exception as e:
            # In case parsing fails, skip this URL.
            continue

    return filtered_urls

def scroll_page(driver, scroll_pause_time=2, max_attempts=5):
    """
    Scrolls the page until no new content loads to reveal lazy-loaded elements.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0
    while attempts < max_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            attempts += 1
        else:
            attempts = 0
        last_height = new_height
