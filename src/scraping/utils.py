"""
Utility functions for web scraping.
"""
import time
from typing import Optional

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

CAR_BRANDS = [
    "toyota", "kia", "ford", "hyundai", "chevrolet", "daewoo", "mercedes_benz",
    "mazda", "honda", "mitsubishi", "lexus", "bmw", "audi", "landrover", "mg",
    "nissan", "peugeot", "porsche", "subaru", "suzuki", "vinfast", "volkswagen",
    "bentley", "byd", "isuzu", "jaguar", "jeep", "mini", "rolls_royce", "volvo",
    "acura", "aion", "alfa_romeo", "asia", "aston_martin", "baic", "bestune",
    "brilliance", "buick", "cadillac", "changan", "chenglong", "chery", "chrysler",
    "citroen", "daihatsu", "datsun", "dodge", "dongben", "dongfeng", "eagle",
    "ferrari", "fiat", "gac", "gaz", "geely", "genesis", "geo", "gmc", "haima",
    "haval", "hino", "hongqi", "hummer", "infiniti", "iveco", "jaecoo", "jrd",
    "lada", "lamborghini", "lancia", "lifan", "lincoln", "lotus", "luxgen",
    "lynk_co", "maserati", "maybach", "mclaren", "mekong", "mercury", "morgan",
    "oldsmobile", "omoda", "opel", "plymouth", "pontiac", "proton", "ram",
    "renault", "rover", "saab", "samsung", "santana", "saturn", "scion", "seat",
    "skoda", "smart", "ssangyong", "sym", "tank", "teraco", "tesla", "thaco",
    "tobe", "tq", "wuling", "uaz", "vinaxuki", "xiaomi", "zeekr", "zotye"
]


def rate_limit(delay: float = 1.0):
    """
    Add delay between requests to avoid overwhelming the server.
    
    Args:
        delay: Time to sleep in seconds (default: 1.0)
    """
    time.sleep(delay)


def get_headers() -> dict:
    """
    Get HTTP headers for requests.
    
    Returns:
        Dictionary containing HTTP headers
    """
    return HEADERS.copy()
