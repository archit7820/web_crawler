import aiohttp
from config.settings import get_settings

settings = get_settings()

async def fetch_url(session, url: str):
       try:
           async with session.get(
               url,
               headers={"User-Agent": settings.USER_AGENT},
               timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
           ) as response:
               if response.status == 200:
                   return await response.text()
               else:
                   print(f"[DEBUG] Failed to fetch {url}: Status {response.status}")  # Log status
                   return None
       except Exception as e:
           print(f"[DEBUG] Error fetching {url}: {e}")  # Log error
           return None