import asyncio
import aiohttp
from config.settings import get_settings

settings = get_settings()

async def fetch_url(session, url: str):
    try:
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",  # Sometimes helps with anti-bot checks
        }
        
        async with session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT),
            ssl=False  # Try this if certificate issues arise
        ) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"[DEBUG] Failed to fetch {url}: Status {response.status}")
                return None
    except aiohttp.ClientError as e:
        print(f"[DEBUG] ClientError fetching {url}: {e}")
        return None
    except asyncio.TimeoutError:
        print(f"[DEBUG] Timeout fetching {url}")
        return None
    except Exception as e:
        print(f"[DEBUG] Unexpected error fetching {url}: {e}")
        return None