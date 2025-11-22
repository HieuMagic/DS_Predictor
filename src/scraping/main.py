"""
Main script for running car crawlers.
"""
import argparse
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

from .crawler import BonbanhCrawler, ChototCrawler
from .utils import CAR_BRANDS


def save_results(data: list, output_dir: str = "data", prefix: str = "cars"):
    """
    Save crawled data to JSON and CSV files.
    
    Args:
        data: List of car dictionaries
        output_dir: Directory to save files
        prefix: Prefix for output filenames
    """
    if not data:
        print("No data to save")
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{prefix}_{timestamp}"
    
    # Save as JSON
    json_file = output_path / f"{base_filename}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved JSON to: {json_file}")
    
    # Save as CSV
    csv_file = output_path / f"{base_filename}.csv"
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"✓ Saved CSV to: {csv_file}")
    
    return json_file, csv_file


def crawl_bonbanh(brand: str, max_cars: int = 500, max_pages: int = None, 
                  output_dir: str = "data"):
    """
    Crawl cars from Bonbanh.com.
    
    Args:
        brand: Car brand to crawl
        max_cars: Maximum number of cars to crawl
        max_pages: Maximum number of pages to crawl
        output_dir: Directory to save results
    """
    crawler = BonbanhCrawler(delay=1.0)
    cars = crawler.crawl_brand(brand, max_cars=max_cars, max_pages=max_pages,
                               save_to_csv=True, output_dir=output_dir)
    
    return cars


def crawl_all_bonbanh_brands(cars_per_brand: int = 500, output_dir: str = "data",
                              save_combined: bool = True, workers: int = 1):
    """
    Crawl cars from all brands on Bonbanh.com.
    
    Args:
        cars_per_brand: Number of cars to crawl per brand
        output_dir: Directory to save results
        save_combined: Whether to save a combined CSV of all brands
        workers: Number of worker threads
    """
    crawler = BonbanhCrawler(delay=1.0)
    all_data = crawler.crawl_all_brands(
        cars_per_brand=cars_per_brand,
        save_to_csv=True,
        output_dir=output_dir,
        save_combined=save_combined,
        workers=workers
    )
    
    return all_data


def crawl_chotot(max_cars: int = 5000, max_pages: int = None, 
                 output_dir: str = "data"):
    """
    Crawl cars from Chotot.com.
    
    Args:
        max_cars: Maximum number of cars to crawl
        max_pages: Maximum number of pages to crawl
        output_dir: Directory to save results
    """
    crawler = ChototCrawler(delay=0.5)
    cars = crawler.crawl_listings(max_cars=max_cars, max_pages=max_pages,
                                  save_to_csv=True, output_dir=output_dir)
    
    return cars


def main():
    """Main entry point for the scraper."""
    from .progress_tracker import ProgressTracker
    
    parser = argparse.ArgumentParser(
        description="Crawl car listings from Vietnamese websites"
    )
    
    parser.add_argument(
        '--source',
        type=str,
        choices=['bonbanh', 'chotot', 'both'],
        default='both',
        help='Which website to crawl (default: both)'
    )
    
    parser.add_argument(
        '--brand',
        type=str,
        help='Car brand to crawl (only for Bonbanh, e.g., toyota, bmw)'
    )
    
    parser.add_argument(
        '--all-brands',
        action='store_true',
        help='Crawl all brands from Bonbanh (uses --cars-per-brand)'
    )
    
    parser.add_argument(
        '--cars-per-brand',
        type=int,
        default=500,
        help='Number of cars to crawl per brand when using --all-brands (default: 500)'
    )
    
    parser.add_argument(
        '--no-combined',
        action='store_true',
        help='Do not save combined CSV when using --all-brands'
    )
    
    parser.add_argument(
        '--max-cars',
        type=int,
        default=5000,
        help='Maximum number of cars to crawl (default: 5000 for Chotot)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        help='Maximum number of pages to crawl'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for saved files (default: data)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker threads for parallel crawling (default: 1)'
    )
    
    parser.add_argument(
        '--reset-progress',
        action='store_true',
        help='Reset crawl progress and start from beginning'
    )
    
    parser.add_argument(
        '--show-progress',
        action='store_true',
        help='Show current crawl progress and exit'
    )
    
    parser.add_argument(
        '--list-brands',
        action='store_true',
        help='List all available car brands for Bonbanh'
    )
    
    args = parser.parse_args()
    
    # Handle progress commands
    progress = ProgressTracker()
    
    if args.show_progress:
        progress.show_progress()
        return
    
    if args.reset_progress:
        progress.reset()
        print("All crawl progress has been reset.")
        return
    
    # List brands if requested
    if args.list_brands:
        print("\nAvailable car brands for Bonbanh.com:")
        print("=" * 60)
        for i, brand in enumerate(CAR_BRANDS, 1):
            print(f"{i:3d}. {brand}")
        print("=" * 60)
        print(f"Total: {len(CAR_BRANDS)} brands")
        return
    
    # Handle all-brands mode
    if args.all_brands:
        if args.source not in ['bonbanh', 'both']:
            print("Warning: --all-brands only works with Bonbanh")
            print("Setting source to 'bonbanh'")
            args.source = 'bonbanh'
        
        print(f"\n{'#'*60}")
        print("CRAWLING ALL BRANDS FROM BONBANH.COM")
        print(f"{'#'*60}")
        crawl_all_bonbanh_brands(
            cars_per_brand=args.cars_per_brand,
            output_dir=args.output_dir,
            save_combined=not args.no_combined,
            workers=args.workers
        )
        
        # Skip Chotot if source was 'both'
        if args.source == 'both':
            args.source = 'skip_bonbanh'
    else:
        # Validate brand for Bonbanh
        if args.source in ['bonbanh', 'both'] and not args.brand:
            print("Error: --brand is required when crawling Bonbanh")
            print("Use --list-brands to see available brands")
            print("Or use --all-brands to crawl all brands")
            return
        
        # Run crawlers
        if args.source in ['bonbanh', 'both']:
            print(f"\n{'#'*60}")
            print("CRAWLING BONBANH.COM")
            print(f"{'#'*60}")
            crawl_bonbanh(
                brand=args.brand,
                max_cars=args.max_cars,
                max_pages=args.max_pages,
                output_dir=args.output_dir
            )
    
    if args.source in ['chotot', 'both', 'skip_bonbanh']:
        print(f"\n{'#'*60}")
        print("CRAWLING CHOTOT.COM")
        print(f"{'#'*60}")
        crawl_chotot(
            max_cars=args.max_cars,
            max_pages=args.max_pages,
            output_dir=args.output_dir
        )
    
    print("\n" + "=" * 60)
    print("CRAWLING COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
