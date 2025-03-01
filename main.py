from fastapi import FastAPI
from routes.crawler import router as crawler_router
from config.settings import get_settings

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)
app.include_router(crawler_router, prefix="/api/v1/crawler", tags=["crawler"])