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

BRAND_MAPPING = {
    "toyota": "Toyota", "kia": "Kia", "ford": "Ford", "hyundai": "Hyundai",
    "chevrolet": "Chevrolet", "daewoo": "Daewoo", "mercedes_benz": "Mercedes Benz",
    "mazda": "Mazda", "honda": "Honda", "mitsubishi": "Mitsubishi", "lexus": "Lexus",
    "bmw": "BMW", "audi": "Audi", "landrover": "Land Rover", "mg": "MG",
    "nissan": "Nissan", "peugeot": "Peugeot", "porsche": "Porsche", "subaru": "Subaru",
    "suzuki": "Suzuki", "vinfast": "VinFast", "volkswagen": "Volkswagen",
    "bentley": "Bentley", "byd": "BYD", "isuzu": "Isuzu", "jaguar": "Jaguar",
    "jeep": "Jeep", "mini": "MINI", "rolls_royce": "Rolls Royce", "volvo": "Volvo",
    "acura": "Acura", "aion": "Aion", "alfa_romeo": "Alfa Romeo", "asia": "Asia",
    "aston_martin": "Aston Martin", "baic": "BAIC", "bestune": "Bestune",
    "brilliance": "Brilliance", "buick": "Buick", "cadillac": "Cadillac",
    "changan": "Changan", "chenglong": "Chenglong", "chery": "Chery",
    "chrysler": "Chrysler", "citroen": "Citroen", "daihatsu": "Daihatsu",
    "datsun": "Datsun", "dodge": "Dodge", "dongben": "Dongben", "dongfeng": "Dongfeng",
    "eagle": "Eagle", "ferrari": "Ferrari", "fiat": "Fiat", "gac": "GAC",
    "gaz": "GAZ", "geely": "Geely", "genesis": "Genesis", "geo": "Geo",
    "gmc": "GMC", "haima": "Haima", "haval": "Haval", "hino": "Hino",
    "hongqi": "Hongqi", "hummer": "Hummer", "infiniti": "Infiniti", "iveco": "Iveco",
    "jaecoo": "Jaecoo", "jrd": "JRD", "lada": "Lada", "lamborghini": "Lamborghini",
    "lancia": "Lancia", "lifan": "Lifan", "lincoln": "Lincoln", "lotus": "Lotus",
    "luxgen": "Luxgen", "lynk_co": "Lynk & Co", "maserati": "Maserati",
    "maybach": "Maybach", "mclaren": "McLaren", "mekong": "Mekong",
    "mercury": "Mercury", "morgan": "Morgan", "oldsmobile": "Oldsmobile",
    "omoda": "Omoda", "opel": "Opel", "plymouth": "Plymouth", "pontiac": "Pontiac",
    "proton": "Proton", "ram": "Ram", "renault": "Renault", "rover": "Rover",
    "saab": "Saab", "samsung": "Samsung", "santana": "Santana", "saturn": "Saturn",
    "scion": "Scion", "seat": "SEAT", "skoda": "Skoda", "smart": "Smart",
    "ssangyong": "Ssangyong", "sym": "SYM", "tank": "Tank", "teraco": "Teraco",
    "tesla": "Tesla", "thaco": "Thaco", "tobe": "Tobe", "tq": "TQ",
    "wuling": "Wuling", "uaz": "UAZ", "vinaxuki": "Vinaxuki", "xiaomi": "Xiaomi",
    "zeekr": "Zeekr", "zotye": "Zotye"
}


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
