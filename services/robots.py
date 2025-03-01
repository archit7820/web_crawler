import aiohttp
from urllib.parse import urlparse

async def fetch_robots_txt(base_url: str):
    # Debugging: Print the base URL
    print(f"[DEBUG] Base URL: {base_url}")
    
    parsed_url = urlparse(base_url)
    
    # Ensure the scheme and netloc are present
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid base URL provided. Ensure it includes the scheme and domain.")
    
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    # Debugging: Print the robots.txt URL
    print(f"[DEBUG] Fetching robots.txt from: {robots_url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(robots_url) as response:
            if response.status == 200:
                return await response.text()
            else:
                return None

def parse_robots_txt(robots_txt: str):
    rules = {}
    user_agent = None
    for line in robots_txt.splitlines():
        line = line.strip()
        if line.startswith("User-agent:"):
            user_agent = line.split(":")[1].strip()
            rules[user_agent] = []
        elif line.startswith("Disallow:") and user_agent:
            path = line.split(":")[1].strip()
            rules[user_agent].append(path)
    return rules

def is_allowed_to_crawl(rules, user_agent, url):
    if user_agent in rules:
        for disallowed in rules[user_agent]:
            if url.startswith(disallowed):
                return False
    return True
