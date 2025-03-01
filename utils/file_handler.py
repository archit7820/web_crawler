import aiofiles
import json
from pathlib import Path
from config.settings import get_settings

settings = get_settings()

async def save_to_json(filename: str, data: list):
    output_path = settings.OUTPUT_DIR / filename
    async with aiofiles.open(output_path, "a") as f:
        await f.write(json.dumps(data, indent=2) + "\n")