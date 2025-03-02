import asyncio
import os
from typing import List
import aiohttp
import sys
from urllib.parse import urlparse
from services.fetcher import fetch_url
from services.parser import extract_links, is_product_url
from utils.file_handler import save_to_json
from config.settings import get_settings
from services.selenium_fetcher import fetch_links_with_selenium

# Set event loop policy for Windows to avoid socket errors
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

settings = get_settings()

# Define output directory and file paths
OUTPUT_DIR = settings.OUTPUT_DIR
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "products.json")
FINAL_FILE = os.path.join(OUTPUT_DIR, "final_products.json")
EXTRACTED_FILE = os.path.join(OUTPUT_DIR, "extracted_links.json")

async def retry_fetch(session: aiohttp.ClientSession, url: str, max_retries: int = 3, initial_backoff: float = 1.0) -> str:
    """
    Attempts to fetch the URL with retries and exponential backoff.
    Returns the HTML content on success or None after max_retries.
    """
    backoff = initial_backoff
    attempt = 0
    while attempt < max_retries:
        try:
            html = await fetch_url(session, url)
            if html:
                return html
            else:
                raise Exception("Empty HTML content")
        except Exception as e:
            print(f"[DEBUG] Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
            await asyncio.sleep(backoff)
            backoff *= 2  # Exponential backoff
            attempt += 1
    return None

def fetch_links_with_htmlsession(url: str) -> set:
    """
    Uses requests_html's HTMLSession to fetch the page, render JavaScript,
    and extract links.
    """
    try:
        from requests_html import HTMLSession
        session = HTMLSession()
        response = session.get(url)
        # Render JavaScript; adjust timeout and sleep as needed.
        response.html.render(timeout=20, sleep=2)
        links = {link.attrs.get("href") for link in response.html.find("a") if link.attrs.get("href")}
        return links
    except Exception as e:
        print(f"[DEBUG] Error extracting links with HTMLSession for {url}: {e}")
        return set()

async def crawl_domain(session: aiohttp.ClientSession, start_url: str, max_depth: int, concurrency: int, output_file: str):
    visited = set()          # Track visited URLs
    product_urls = set()     # Track unique product URLs
    base_domain = urlparse(start_url).netloc

    semaphore = asyncio.Semaphore(concurrency)
    current_level = {start_url}
    
    for depth in range(max_depth + 1):
        tasks = []
        for url in current_level:
            if url not in visited:
                visited.add(url)
                tasks.append(fetch_and_process(session, url, semaphore, base_domain))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        current_level = set()
        
        for result in results:
            if isinstance(result, Exception):
                print(f"[ERROR] Error processing URL: {result}")
                continue
            links, products = result
            current_level.update(links)
            product_urls.update(products)
        
        # Save intermediate product URLs after each depth level
        await save_to_json(output_file, list(product_urls))
    
    return list(product_urls)

async def fetch_and_process(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore, base_domain: str):
    async with semaphore:
        print(f"[DEBUG] Fetching URL: {url}")
        # Use retry mechanism when fetching the URL
        html = await retry_fetch(session, url, max_retries=3, initial_backoff=1.0)
        if not html:
            print(f"[DEBUG] No HTML content retrieved from: {url}")
            return (set(), set())
        
        # First attempt: extract links using the standard parser (aiohttp HTML)
        links = extract_links(html, url)
        print(f"[DEBUG] Extracted links (aiohttp): {links}")
        
        # Fallback: if no links found, try extracting with HTMLSession
        if not links:
            print(f"[DEBUG] No links extracted via aiohttp for {url}. Falling back to HTMLSession extraction.")
            links = await asyncio.to_thread(fetch_links_with_htmlsession, url)
            print(f"[DEBUG] Extracted links (HTMLSession): {links}")
        
        # Final fallback: if still no links, use Selenium (headless)
        if not links:
            print(f"[DEBUG] No links extracted via HTMLSession for {url}. Falling back to Selenium.")
            links = await asyncio.to_thread(fetch_links_with_selenium, url)
            print(f"[DEBUG] Extracted links (Selenium): {links}")
        
        products = set()
        new_links = set()
        for link in links:
            if is_product_url(link):
                products.add(link)
                print(f"[DEBUG] Found product URL: {link}")
                await save_to_json(FINAL_FILE, list(products))  # Save current products
            elif urlparse(link).netloc == base_domain:
                new_links.add(link)
                
        return (new_links, products)

async def crawl_urls(urls: List[str], max_depth: int, concurrency: int, output_file: str):
    # Ensure each URL has a scheme (default to https if missing)
    for i in range(len(urls)):
        if not urls[i].startswith(('http://', 'https://')):
            urls[i] = 'https://' + urls[i]
    
    async with aiohttp.ClientSession() as session:
        tasks = [crawl_domain(session, url, max_depth, concurrency, output_file) for url in urls]
        try:
            results = await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            print("[INFO] Crawler cancelled by user. Saving partial results.")
            await save_to_json(output_file, [])
            raise
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}. Saving partial results.")
            await save_to_json(output_file, [])
            raise
        
        # Flatten the list of product URLs from each domain
        product_urls = [url for sublist in results for url in sublist]
        await save_to_json(output_file, product_urls)
        return product_urls
