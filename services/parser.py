from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils.patterns import get_pattern

def extract_links(html: str, base_url: str) -> set:
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for link in soup.find_all("a", href=True):
        full_url = urljoin(base_url, link["href"])
        links.add(full_url)
    return links

def is_product_url(url: str) -> bool:
    parsed = urlparse(url)
    pattern = get_pattern(parsed.netloc)
    return bool(pattern and pattern.search(parsed.path))