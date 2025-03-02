from fastapi import APIRouter, HTTPException
from models.schemas import CrawlRequest
from services.crawler import crawl_urls
from typing import List

router = APIRouter()

@router.post("/start", response_model=List[str])
async def start_crawl(request: CrawlRequest):
    try:
        results = await crawl_urls(
            urls=request.urls,
            max_depth=request.max_depth,
            concurrency=request.concurrency,
            output_file=request.output_filename
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))