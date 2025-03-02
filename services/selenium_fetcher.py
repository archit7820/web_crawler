from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib.parse import urljoin, urlparse
import re
import time
from collections import deque

class ProductCrawler:
    def __init__(self, base_url, max_pages=50):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited = set()
        self.product_urls = set()
        self.queue = deque()
        self.queue.append(base_url)
        
        # Configure Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-infobars")
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Block unnecessary content
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.managed_default_content_settings.javascript": 1,  # Keep JS enabled for SPA
            "profile.managed_default_content_settings.media_stream": 2,
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

    def is_product_url(self, url):
        """Check if URL matches common product page patterns"""
        patterns = [
            r'/product/',
            r'/p/',
            r'/prod/',
            r'\?product=',
            r'/item/',
            r'/shop/',
            r'/buy/',
            r'/detail/',
            r'/\d+/$'  # Common for product IDs
        ]
        return any(re.search(pattern, url, re.I) for pattern in patterns)

    def should_crawl(self, url):
        """Determine if a URL is worth crawling"""
        parsed = urlparse(url)
        
        # Skip if different domain
        if parsed.netloc not in self.base_url:
            return False
            
        # Skip non-http protocols
        if not parsed.scheme.startswith('http'):
            return False
            
        # Skip common non-product paths
        skip_paths = {
            '/contact', '/about', '/cart', '/checkout',
            '/login', '/signup', '/account', '/admin',
            '/privacy', '/terms', '/faq', '/help'
        }
        if any(path in parsed.path.lower() for path in skip_paths):
            return False
            
        # Skip file extensions
        skip_ext = {
            '.pdf', '.jpg', '.jpeg', '.png', '.gif',
            '.doc', '.docx', '.xls', '.xlsx', '.zip'
        }
        if any(parsed.path.lower().endswith(ext) for ext in skip_ext):
            return False
            
        return True

    def normalize_url(self, url):
        """Normalize URL to avoid duplicate visits"""
        parsed = urlparse(url)
        path = parsed.path.rstrip('/')
        return parsed.scheme + '://' + parsed.netloc + path

    def crawl(self):
        """Main crawling function"""
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(20)
        
        try:
            while self.queue and len(self.visited) < self.max_pages:
                url = self.queue.popleft()
                normalized = self.normalize_url(url)
                
                if normalized in self.visited:
                    continue
                
                self.visited.add(normalized)
                print(f"Crawling: {url}")

                try:
                    driver.get(url)
                    # Wait for core content to load
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//body'))
                    )
                except (TimeoutException, WebDriverException) as e:
                    print(f"Timeout loading {url}: {str(e)}")
                    continue

                # Check if current page is a product page
                if self.is_product_url(url):
                    self.product_urls.add(url)
                    continue  # Don't crawl links from product pages

                # Extract and process links
                try:
                    links = driver.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        href = link.get_attribute('href')
                        if not href:
                            continue

                        full_url = urljoin(url, href).split('#')[0]
                        norm_url = self.normalize_url(full_url)

                        if self.is_product_url(full_url):
                            self.product_urls.add(full_url)
                        elif self.should_crawl(full_url) and norm_url not in self.visited:
                            self.queue.append(full_url)

                except WebDriverException as e:
                    print(f"Error processing links: {str(e)}")

                # Prioritize product-like URLs by reordering the queue
                self.queue = deque(sorted(self.queue, key=lambda x: self.is_product_url(x), reverse=True))

        finally:
            driver.quit()

        return self.product_urls

