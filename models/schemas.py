from pydantic import BaseModel
from typing import List

class CrawlRequest(BaseModel):
    urls: List[str]
    max_depth: int = 2   #max_depth controls how deep the crawler goes in following links, allowing you to limit the scope of the crawl.
    concurrency: int = 10  #concurrency controls how many requests can be made simultaneously, affecting the speed of the crawling process.
    output_filename: str = "products.json"