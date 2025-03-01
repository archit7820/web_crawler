import re

PATTERNS = {
     "wearenicerice.com": re.compile(r"/products/[\w-]+-\d+"),
    "www.myntra.com": re.compile(r"/\d+(?:/buy)?$"),
    "www2.hm.com": re.compile(r"/productpage\.\d+\.html$"),
    "www.nykaa.com": re.compile(r"/p/\d+\?productId=\d+"),
    "www.nykaafashion.com": re.compile(r"/p/\d+$"),
    "www.flipkart.com": re.compile(r"/p/itm[a-zA-Z0-9]+"),
    "www.thesouledstore.com": re.compile(r"/product/[\w-]+-\d+"),
    "coverstory.co.in": re.compile(r"/product/[\w-]+-\d+"),
    "in.urbanic.com": re.compile(r"/details/[\w-]+-\d+"),
    "www.savana.com": re.compile(r"/details/[\w-]+-\d+"),
    "www.bewakoof.com": re.compile(r"/p/[\w-]+"),
    "www.nike.com": re.compile(r"/in/t/[\w-]+-[\w\d]+/[\w\d-]+"),
    "forever21.abfrl.in": re.compile(r"/p/[\w-]+-\d+\.html"),
    "in.puma.com": re.compile(r"/pd/[\w-]+/\d+"),
    "aeo.abfrl.in": re.compile(r"/p/[\w-]+-\d+\.html"),
    "aarke.ritukumar.com": re.compile(r"/product/[\w-]+-\d+"),
    "www.jaypore.com": re.compile(r"/p/[\w-]+-\d+\.html"),
    "superdry.in": re.compile(r"/product/[\w-]+-\d+"),
    "www.fabindia.com": re.compile(r"/[\w-]+-(\d{5,})$"),  # Ensures 5+ digit product ID at the end}
 
}

def get_pattern(domain: str):
    return PATTERNS.get(domain)
