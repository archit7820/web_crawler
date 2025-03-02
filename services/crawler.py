import asyncio
import os
from typing import List, Tuple, Set
import aiohttp
import sys
from urllib.parse import urlparse
from collections import deque
from services.fetcher import fetch_url
from services.parser import extract_links, is_product_url
from utils.file_handler import save_to_json
from config.settings import get_settings
from services.selenium_fetcher import ProductCrawler

# Set event loop policy for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

settings = get_settings()

class AsyncCrawler:
    def __init__(self, concurrency: int = 50):
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)
        self.output_file = os.path.join(settings.OUTPUT_DIR, "final_products.json")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        self.product_urls: Set[str] = set()  # Store product URLs dynamically

    async def retry_fetch(self, session: aiohttp.ClientSession, url: str, max_retries: int = 3) -> str:
        """Retries fetching a URL with exponential backoff before switching to Selenium."""
        backoff = 1.0
        for attempt in range(max_retries):
            try:
                print(f"🔍 Fetching URL: {url} (Attempt {attempt + 1})")
                html = await asyncio.shield(fetch_url(session, url))  # Prevent cancellation
                if html:
                    return html
            except Exception as e:
                print(f"⚠️ Retry {attempt + 1} failed for {url}: {e}")
                await asyncio.sleep(backoff)
                backoff *= 2  # Exponential backoff
        return None  # Return None if all retries fail

    async def process_url(self, session: aiohttp.ClientSession, url: str, base_domain: str) -> Tuple[Set[str], Set[str]]:
        """Processes a URL to extract product pages and discoverable links."""
        async with self.semaphore:
            html = await self.retry_fetch(session, url)
            if html:
                links = extract_links(html, url)
                products = {link for link in links if is_product_url(link)}
                discoverable_links = {link for link in links if urlparse(link).netloc == base_domain}

                print(f"✅ Found {len(products)} Product URLs on {url}")
                await self.save_results(products)  # Save results dynamically
                return discoverable_links, products
            
            print(f"⚡ Switching to Selenium for {url} due to failed aiohttp requests.")
            selenium_crawler = ProductCrawler(base_url=url, max_pages=50)
            selenium_products = await asyncio.to_thread(selenium_crawler.crawl)
            print(f"🕵️ Selenium Extracted {len(selenium_products)} Products from {url}")

            await self.save_results(selenium_products)
            return set(), selenium_products

    async def save_results(self, new_products: Set[str]):
        """Saves product URLs in real-time to JSON and prints them."""
        if new_products:
            self.product_urls.update(new_products)
            await save_to_json(self.output_file, list(self.product_urls))
            for product in new_products:
                print(f"📦 Product URL: {product}")

    async def crawl_domain(self, session: aiohttp.ClientSession, start_url: str, max_depth: int):
        """Crawls a domain using BFS, prioritizing product-like URLs."""
        base_domain = urlparse(start_url).netloc
        visited = set()
        queue = deque([(start_url, 0)])

        while queue:
            url, depth = queue.popleft()
            if depth > max_depth or url in visited:
                continue

            visited.add(url)
            links, products = await self.process_url(session, url, base_domain)

            # Add new links to queue, prioritizing product-like URLs
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1))

            # Sort queue every 5 iterations for better prioritization
            if len(queue) % 5 == 0:
                queue = deque(sorted(queue, key=lambda x: is_product_url(x[0]), reverse=True))

    async def crawl_urls(self, urls: List[str], max_depth: int):
        """Crawls multiple URLs concurrently and stores real-time results."""
        normalized_urls = [f'https://{url}' if not url.startswith(('http://', 'https://')) else url for url in urls]
        timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=15)

        async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(limit_per_host=10)) as session:
            tasks = [self.crawl_domain(session, url, max_depth) for url in normalized_urls]
            await asyncio.gather(*tasks)

# API Function
async def crawl_urls(urls: List[str], max_depth: int, concurrency: int, output_file: str = "final_products.json") -> List[str]:
    """Top-level function to start the AsyncCrawler."""
    crawler = AsyncCrawler(concurrency=concurrency)
    crawler.output_file = output_file
    await crawler.crawl_urls(urls, max_depth)

    print(f"🔄 Total Products Found: {len(crawler.product_urls)}")
    return list(crawler.product_urls)  # Ensure it returns a list
