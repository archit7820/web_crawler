# Async E-commerce Product URL Crawler

An asynchronous crawler designed to discover and extract "product" URLs from various e-commerce websites. This project leverages `asyncio` and `aiohttp` for concurrent HTTP requests and includes a Selenium fallback for JavaScript-rendered pages.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Workflow](#workflow)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview

The Async E-commerce Product URL Crawler is built to efficiently discover product pages across multiple e-commerce sites. It crawls websites using a breadth-first search (BFS) strategy, extracting links and filtering them with pre-defined patterns to identify product URLs. In cases where pages rely on JavaScript for rendering content, the system falls back to a Selenium-based approach.

---

## Features

- **Asynchronous Crawling:** Utilizes `asyncio` and `aiohttp` for high-performance concurrent requests.
- **Breadth-First Search:** Explores websites level by level, ensuring thorough link discovery.
- **Product URL Detection:** Uses regex-based patterns to identify product pages.
- **Selenium Fallback:** Handles JavaScript-heavy pages with Selenium.
- **Real-Time Data Storage:** Saves unique product URLs to a JSON file in real time.
- **API Integration:** Can be integrated with FastAPI for RESTful crawling operations.

---

## Architecture

### Core Components

- **Web Crawler:**  
  The `AsyncCrawler` class orchestrates the crawling process, handling URL fetching, link extraction, and data storage.

- **Parser & URL Extraction:**  
  The `extract_links` function parses HTML content to extract all `<a>` tags and resolves relative URLs to absolute paths.

- **Product URL Detection:**  
  The `is_product_url` function checks URLs against specific patterns to determine if they represent product pages.

- **Selenium Integration:**  
  The `ProductCrawler` class serves as a fallback to process pages that require JavaScript execution.

- **Data Storage:**  
  Unique product URLs are stored in a JSON file with real-time updates. A Python set ensures deduplication, and an `asyncio.Lock` is used to prevent concurrent write issues.

- **API Interface:**  
  A FastAPI endpoint can be configured to trigger the crawling process and return the results as JSON.

---

## Installation

### Prerequisites

- Python 3.7+
- [aiohttp](https://docs.aiohttp.org/)
- [asyncio](https://docs.python.org/3/library/asyncio.html)
- [Selenium](https://www.selenium.dev/) and a WebDriver (e.g., ChromeDriver)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) (if used in your parser)
- Other dependencies as specified in `requirements.txt`

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/archit7820/web_crawler.git
   cd web_crawler
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**

   Update the configuration in `config/settings.py` to set parameters such as:
   - `USER_AGENT`
   - `REQUEST_TIMEOUT`
   - `OUTPUT_DIR`
   - Other relevant settings

---

## Usage

### Running the Crawler Directly

You can execute the crawler using the top-level API function `crawl_urls`. For example:

```python
import asyncio
from services.crawler import crawl_urls  # Adjust the import based on your project structure

urls = [
    "https://wwww.myntra.com",
    "https://www.nykaafashion.com/"
]
max_depth = 3

concurrency = 50

async def main():
    product_urls = await crawl_urls(urls, max_depth, concurrency)
    print("Total product URLs found:", len(product_urls))

asyncio.run(main())
```

### API Integration with FastAPI

A sample FastAPI integration:

```python
from fastapi import FastAPI, HTTPException
import asyncio
from services.crawler import crawl_urls

app = FastAPI()

@app.post("/crawl/")
async def start_crawl(urls: list[str], max_depth: int = 3, concurrency: int = 50):
    product_urls = await crawl_urls(urls, max_depth, concurrency)
    if not product_urls:
        raise HTTPException(status_code=404, detail="No product URLs found.")
    return {"product_urls": product_urls}

# Run the API using:
# uvicorn main:app --reload
```

---

## Workflow

1. **User Input:**  
   The user provides a list of URLs, along with settings for maximum depth and concurrency.

2. **Crawling Process:**
   - **URL Normalization:** Ensures each URL includes the proper scheme (`http://` or `https://`).
   - **Fetching & Parsing:** Uses aiohttp to fetch HTML content, then parses it for links.
   - **Product URL Detection:** Filters extracted links to identify product pages.
   - **Selenium Fallback:** Uses Selenium if the standard fetch fails (e.g., due to JavaScript rendering).
   - **Real-Time Storage:** Updates a JSON file with new, unique product URLs in real time.

3. **Output:**  
   The final set of unique product URLs is saved to a JSON file and returned via the API or script.

---

## Example 


**Input** 

```python
{
  "urls": [
     "https://wwww.myntra.com",
  ],
  "max_depth": 2,
  "concurrency": 50,
  "output_filename": "products.json"
}
```

**Output**

---

## Output

After running the crawler, all discovered product URLs are saved in a JSON file named **`final_products.json`** located in the Fast API Section . You can download the file using the link below:

[Download final_products.json](./Testing%20result.json)

---





