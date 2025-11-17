# Car Scraping Module

A comprehensive web scraping module for collecting car listing data from Vietnamese websites (Bonbanh.com and Chotot.com).

## Features

- **Two Website Crawlers**:
  - `BonbanhCrawler`: Scrapes car data from bonbanh.com
  - `ChototCrawler`: Scrapes car data from chotot.com (xe.chotot.com)

- **Flexible Crawling Control**:
  - Limit by number of cars (`max_cars`)
  - Limit by number of pages (`max_pages`)
  - Configurable delay between requests

- **Clean Architecture**:
  - `crawler.py`: Main crawling logic
  - `parser.py`: HTML parsing functions
  - `utils.py`: Utility functions and constants
  - `main.py`: CLI interface

## Installation

Install required dependencies:

```bash
pip install requests beautifulsoup4 lxml pandas
```

## Usage

### Command Line Interface

The easiest way to use the scraper:

```bash
# List available car brands
python src/scraping/main.py --list-brands

# Crawl 20 BMW cars from Bonbanh
python src/scraping/main.py --source bonbanh --brand bmw --max-cars 20

# Crawl 10 cars from Chotot
python src/scraping/main.py --source chotot --max-cars 10

# Crawl first 3 pages of Toyota from Bonbanh
python src/scraping/main.py --source bonbanh --brand toyota --max-pages 3

# Crawl both sites (specify brand for Bonbanh)
python src/scraping/main.py --source both --brand honda --max-cars 15

# Crawl ALL brands from Bonbanh (10 cars per brand)
python src/scraping/main.py --all-brands --cars-per-brand 10

# Crawl ALL brands (5 cars each, no combined CSV)
python src/scraping/main.py --all-brands --cars-per-brand 5 --no-combined
```

### Python API

Use the crawlers directly in your Python code:

#### Bonbanh Crawler

```python
from src.scraping import BonbanhCrawler

# Initialize crawler (delay in seconds between requests)
crawler = BonbanhCrawler(delay=1.0)

# Crawl 10 BMW cars
cars = crawler.crawl_brand(brand='bmw', max_cars=10)

# Crawl first 2 pages of Toyota
cars = crawler.crawl_brand(brand='toyota', max_pages=2)

# Crawl all Honda cars (no limits)
cars = crawler.crawl_brand(brand='honda')

# Crawl ALL brands (10 cars per brand)
all_data = crawler.crawl_all_brands(cars_per_brand=10)
# Returns: {'toyota': [...], 'honda': [...], 'bmw': [...], ...}
```

#### Chotot Crawler

```python
from src.scraping import ChototCrawler

# Initialize crawler
crawler = ChototCrawler(delay=0.5)

# Crawl 20 cars
cars = crawler.crawl_listings(max_cars=20)

# Crawl first 5 pages
cars = crawler.crawl_listings(max_pages=5)
```

### Advanced Usage

#### Crawl All Brands (Automated)

The easiest way to crawl all brands:

```python
from src.scraping import BonbanhCrawler

crawler = BonbanhCrawler(delay=1.0)

# Crawl 5 cars from each brand (113+ brands)
all_data = crawler.crawl_all_brands(
    cars_per_brand=5,      # 5 cars per brand
    save_to_csv=True,      # Save individual CSV for each brand
    output_dir="data",     # Output directory
    save_combined=True     # Also save combined CSV with all cars
)

# Results in:
# - data/bonbanh_toyota_*.csv
# - data/bonbanh_honda_*.csv
# - ... (one CSV per brand)
# - data/bonbanh_all_brands_*.csv (combined file)
```

#### Crawl Multiple Brands (Manual)

```python
from src.scraping import BonbanhCrawler

brands = ['bmw', 'toyota', 'honda', 'mercedes_benz']
crawler = BonbanhCrawler(delay=1.0)

all_cars = []
for brand in brands:
    cars = crawler.crawl_brand(brand=brand, max_cars=10)
    all_cars.extend(cars)

print(f"Total cars crawled: {len(all_cars)}")
```

#### Save Results

```python
import json
import pandas as pd
from src.scraping import BonbanhCrawler

crawler = BonbanhCrawler()
cars = crawler.crawl_brand(brand='bmw', max_cars=50)

# Save as JSON
with open('bmw_cars.json', 'w', encoding='utf-8') as f:
    json.dump(cars, f, ensure_ascii=False, indent=2)

# Save as CSV
df = pd.DataFrame(cars)
df.to_csv('bmw_cars.csv', index=False, encoding='utf-8-sig')
```

## Module Structure

```
src/scraping/
├── __init__.py          # Module exports
├── crawler.py           # BonbanhCrawler, ChototCrawler classes
├── parser.py            # HTML parsing functions
├── utils.py             # Utility functions, constants
└── main.py              # CLI interface
```

## Available Car Brands (Bonbanh)

The module includes 113 pre-configured car brands. Some popular ones:

- toyota, honda, mazda, mitsubishi
- bmw, mercedes_benz, audi, lexus
- ford, chevrolet, hyundai, kia
- vinfast, tesla, and many more

Use `--list-brands` to see all available brands.

## Data Output Format

Each crawled car is returned as a dictionary with the following structure:

### Bonbanh.com
```python
{
    'title': 'BMW 320i 2019',
    'Năm sản xuất': '2019',
    'Số Km đã đi': '45000',
    'Màu ngoại thất': 'Trắng',
    'Màu nội thất': 'Đen',
    # ... other fields
    'source': 'bonbanh',
    'url': 'https://bonbanh.com/...'
}
```

### Chotot.com
```python
{
    'Hãng xe': 'Toyota',
    'Dòng xe': 'Camry',
    'Năm sản xuất': '2020',
    # ... other fields
    'source': 'chotot',
    'url': 'https://xe.chotot.com/...'
}
```

## Rate Limiting

The crawlers include built-in rate limiting to avoid overwhelming the servers:
- Bonbanh: 1.0 second delay (default)
- Chotot: 0.5 second delay (default)

You can adjust these when initializing the crawler:

```python
crawler = BonbanhCrawler(delay=2.0)  # 2 seconds between requests
```

## Examples

See `examples/crawl_examples.py` for more usage examples:

```bash
python examples/crawl_examples.py
```

## Error Handling

The crawlers include comprehensive error handling:
- Failed requests are logged but don't stop the crawler
- HTML parsing errors are caught and reported
- Network issues are handled gracefully

## Best Practices

1. **Use rate limiting**: Don't set delay too low to respect server resources
2. **Limit your requests**: Use `max_cars` or `max_pages` for testing
3. **Save incrementally**: For large crawls, consider saving results periodically
4. **Check robots.txt**: Be respectful of website crawling policies
5. **Monitor your crawls**: Watch the console output for errors

## Command Line Arguments

```
--source            Which website to crawl: bonbanh, chotot, or both
--brand             Car brand to crawl (required for bonbanh unless using --all-brands)
--all-brands        Crawl all brands from Bonbanh (uses --cars-per-brand)
--cars-per-brand    Number of cars per brand when using --all-brands (default: 10)
--no-combined       Do not save combined CSV when using --all-brands
--max-cars          Maximum number of cars to crawl (single brand mode)
--max-pages         Maximum number of pages to crawl (single brand mode)
--output-dir        Directory to save output files (default: data)
--list-brands       List all available car brands
```

## Troubleshooting

**Issue**: "Request failed" errors
- Solution: Check your internet connection, increase delay between requests

**Issue**: No data returned
- Solution: The website structure may have changed; check parser functions

**Issue**: Brand not found
- Solution: Use `--list-brands` to see valid brand names

## License

This module is part of the DS_Predictor project. Use responsibly and respect website terms of service.
