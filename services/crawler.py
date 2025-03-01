import asyncio
from typing import List
import aiohttp
from urllib.parse import urlparse
from services.fetcher import fetch_url
from services.parser import extract_links, is_product_url
from utils.file_handler import save_to_json
from config.settings import get_settings

settings = get_settings()

async def crawl_domain(session, start_url: str, max_depth: int, concurrency: int, output_file: str):
    visited = set()          # Track visited URLs
    product_urls = set()     # Track unique product URLs
    base_domain = urlparse(start_url).netloc

    # Remove robots.txt logic
    # robots_txt = await fetch_robots_txt(start_url)
    # rules = parse_robots_txt(robots_txt) if robots_txt else {}
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"

    semaphore = asyncio.Semaphore(concurrency)
    current_level = {start_url}
    
    for depth in range(max_depth + 1):
        tasks = []
        for url in current_level:
            if url not in visited:  # Removed robots.txt check
                visited.add(url)  # Mark URL as visited
                tasks.append(fetch_and_process(session, url, semaphore, base_domain))
        
        results = await asyncio.gather(*tasks)
        current_level = set()
        
        for links, products in results:
            current_level.update(links)  # Add new links for the next level
            product_urls.update(products)  # Add found product URLs
        
        if products:
            await save_to_json(output_file, list(products))  # Save found products

    return list(product_urls)

async def fetch_and_process(session, url, semaphore, base_domain):
    async with semaphore:
        print(f"[DEBUG] Fetching URL: {url}")  # Debugging statement
        html = await fetch_url(session, url)
        if not html:
            print(f"[DEBUG] No HTML content retrieved from: {url}")  # Debugging statement
            return (set(), set())
        
        links = extract_links(html, url)
        print(f"[DEBUG] Extracted links: {links}")  # Debugging statement
        products = set()
        new_links = set()
        
        for link in links:
            if is_product_url(link):
                products.add(link)  # Add product URL
                print(f"[DEBUG] Found product URL: {link}")  # Debugging statement
            elif urlparse(link).netloc == base_domain:
                new_links.add(link)  # Add internal link for further crawling
        
        return (new_links, products)

async def crawl_urls(urls: List[str], max_depth: int, concurrency: int, output_file: str):
    # Ensure all URLs have the scheme
    for i in range(len(urls)):
        if not urls[i].startswith(('http://', 'https://')):
            urls[i] = 'https://' + urls[i]  # Default to https if no scheme is provided

    async with aiohttp.ClientSession() as session:
        tasks = [crawl_domain(session, url, max_depth, concurrency, output_file) for url in urls]
        results = await asyncio.gather(*tasks)
        return [url for sublist in results for url in sublist]

