"""
Web crawler for car listing websites.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
import concurrent.futures
import threading

from .utils import get_headers, rate_limit, CAR_BRANDS
from .parser import (
    parse_bonbanh_car_details,
    parse_bonbanh_listing,
    parse_chotot_car_details,
    parse_chotot_listing
)
from .progress_tracker import ProgressTracker


class BonbanhCrawler:
    """Crawler for Bonbanh.com car listings."""
    
    BASE_URL = "https://bonbanh.com/oto/"
    
    def __init__(self, delay: float = 0.1):
        """
        Initialize the Bonbanh crawler.
        
        Args:
            delay: Delay between requests in seconds (default: 1.0)
        """
        self.headers = get_headers()
        self.delay = delay
        self.current_brand = None
        self.csv_lock = threading.Lock()
        self.progress = ProgressTracker()
    
    def crawl_car_details(self, link: str, brand: str = None) -> Optional[Dict[str, str]]:
        """
        Crawl details of a single car.
        
        Args:
            link: URL of the car detail page
            brand: Brand code for proper parsing
            
        Returns:
            Dictionary containing car details or None if failed
        """
        try:
            response = requests.get(link, headers=self.headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                car_data = parse_bonbanh_car_details(soup, brand=brand or self.current_brand)
                car_data['url'] = link
                return car_data
            else:
                print(f"Failed to fetch {link}, status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error crawling car details from {link}: {e}")
            return None
    
    def crawl_brand(self, brand: str, max_cars: Optional[int] = None, 
                    max_pages: Optional[int] = None, save_to_csv: bool = True,
                    output_dir: str = "data") -> List[Dict[str, str]]:
        """
        Crawl cars of a specific brand.
        
        Args:
            brand: Brand name (must be in CAR_BRANDS list)
            max_cars: Maximum number of cars to crawl (None for all)
            max_pages: Maximum number of pages to crawl (None for all)
            save_to_csv: Whether to save results to CSV file (default: True)
            output_dir: Directory to save CSV file (default: "data")
            
        Returns:
            List of dictionaries containing car data
        """
        if brand not in CAR_BRANDS:
            print(f"Warning: '{brand}' is not in the predefined brands list")
        
        # Set current brand for parsing
        self.current_brand = brand
        
        all_cars = []
        cars_crawled = 0
        skipped_count = 0
        
        # Check if already completed
        if self.progress.is_completed('bonbanh', brand):
            print(f"⚠ Brand '{brand}' was already completed. Use --reset-progress to start over.")
            return all_cars
        
        # Get last crawled page
        page = self.progress.get_last_page('bonbanh', brand)
        if page > 0:
            print(f"📍 Resuming from page {page + 1} (last completed: page {page})")
        
        # Setup CSV file path if saving
        csv_filepath = None
        if save_to_csv:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            csv_filepath = output_path / "bonbanh.csv"
        
        print(f"\n{'='*60}")
        print(f"Starting crawl for brand: {brand}")
        print(f"Max cars: {max_cars if max_cars else 'unlimited'}")
        print(f"Max pages: {max_pages if max_pages else 'unlimited'}")
        print(f"{'='*60}\n")
        
        while True:
            # Check if we've reached max pages
            if max_pages and page >= max_pages:
                print(f"\nReached maximum pages limit: {max_pages}")
                break
            
            # Check if we've reached max cars
            if max_cars and cars_crawled >= max_cars:
                print(f"\nReached maximum cars limit: {max_cars}")
                break
            
            try:
                url = f'{self.BASE_URL}{brand}/page,{page}'
                print(f"Fetching page {page + 1} from: {url}")
                
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')
                    car_links = parse_bonbanh_listing(soup)
                    
                    if not car_links:
                        print(f"No more cars found on page {page + 1}")
                        break
                    
                    print(f"Found {len(car_links)} cars on page {page + 1}")
                    
                    # Crawl each car on this page
                    for idx, link in enumerate(car_links, 1):
                        if max_cars and cars_crawled >= max_cars:
                            break
                        
                        print(f"  [{cars_crawled + 1}] Crawling: {link}")
                        car_data = self.crawl_car_details(link, brand=brand)
                        
                        if car_data:
                            all_cars.append(car_data)
                            
                            # Write to CSV
                            if save_to_csv and csv_filepath:
                                self._append_single_car_to_csv(car_data, csv_filepath)
                            
                            cars_crawled += 1
                            print(f"  ✓ Successfully crawled: {car_data.get('model', 'Unknown')}")
                        
                        rate_limit(self.delay)
                    
                    # Save progress after completing this page
                    self.progress.update_page('bonbanh', page, brand)
                    
                    page += 1
                    
                else:
                    print(f"Failed to fetch page {page + 1}, status code: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"Error on page {page + 1}: {e}")
                break
        
        print(f"\n{'='*60}")
        print(f"Crawl completed for brand: {brand}")
        print(f"Total cars crawled: {cars_crawled}")
        if save_to_csv and csv_filepath and csv_filepath.exists():
            try:
                # Count lines instead of reading entire CSV to avoid column mismatch errors
                with open(csv_filepath, 'r', encoding='utf-8-sig') as f:
                    total_in_file = sum(1 for line in f) - 1  # Subtract header
                print(f"Total cars in bonbanh.csv: {total_in_file}")
            except Exception as e:
                print(f"Could not count total cars: {e}")
        print(f"{'='*60}\n")
        
        # Mark as completed if we finished naturally (not due to max limits)
        if not ((max_cars and cars_crawled >= max_cars) or (max_pages and page >= max_pages)):
            self.progress.mark_completed('bonbanh', brand)
        
        return all_cars
    
    def _append_single_car_to_csv(self, car_data: Dict[str, str], filepath: Path):
        """
        Append a single car to CSV file immediately.
        
        Args:
            car_data: Dictionary containing car data
            filepath: Path to the CSV file
        """
        try:
            # Remove unwanted fields
            car_data.pop('crawl_timestamp', None)
            car_data.pop('title', None)
            
            # Convert to DataFrame
            df = pd.DataFrame([car_data])
            
            with self.csv_lock:
                # Append to existing file or create new one
                if filepath.exists():
                    df.to_csv(filepath, mode='a', header=False, index=False, encoding='utf-8-sig')
                else:
                    df.to_csv(filepath, mode='w', header=True, index=False, encoding='utf-8-sig')
            
        except Exception as e:
            print(f"  ✗ Error writing to CSV: {e}")
    
    def crawl_all_brands(self, cars_per_brand: int = 10, save_to_csv: bool = True,
                         output_dir: str = "data", save_combined: bool = True, workers: int = 1) -> Dict[str, List[Dict[str, str]]]:
        """
        Crawl cars from all available brands.
        
        Args:
            cars_per_brand: Number of cars to crawl per brand
            save_to_csv: Whether to save results to CSV files (default: True)
            output_dir: Directory to save CSV files (default: "data")
            save_combined: Whether to save a combined CSV of all brands (default: True)
            workers: Number of worker threads for parallel crawling (default: 1)
            
        Returns:
            Dictionary with brand names as keys and lists of car data as values
        """
        all_brands_data = {}
        total_cars = 0
        successful_brands = 0
        failed_brands = []
        
        print(f"\n{'#'*60}")
        print(f"CRAWLING ALL BRANDS FROM BONBANH.COM")
        print(f"{'#'*60}")
        print(f"Total brands: {len(CAR_BRANDS)}")
        print(f"Cars per brand: {cars_per_brand}")
        print(f"Workers: {workers}")
        print(f"{'#'*60}\n")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_brand = {
                executor.submit(
                    self.crawl_brand, 
                    brand=brand, 
                    max_cars=cars_per_brand, 
                    save_to_csv=save_to_csv, 
                    output_dir=output_dir
                ): brand for brand in CAR_BRANDS
            }
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_brand), 1):
                brand = future_to_brand[future]
                try:
                    cars = future.result()
                    if cars:
                        all_brands_data[brand] = cars
                        total_cars += len(cars)
                        successful_brands += 1
                    else:
                        failed_brands.append(brand)
                except Exception as e:
                    failed_brands.append(brand)
                    print(f"✗ Brand '{brand}': Error - {e}")
                
                print(f"Progress: [{i}/{len(CAR_BRANDS)}] brands completed")
        
        # Print summary
        print(f"\n{'#'*60}")
        print("CRAWL ALL BRANDS - SUMMARY")
        print(f"{'#'*60}")
        print(f"Total brands processed: {len(CAR_BRANDS)}")
        print(f"Successful brands: {successful_brands}")
        print(f"Failed brands: {len(failed_brands)}")
        print(f"Total cars crawled: {total_cars}")
        if failed_brands:
            print(f"\nFailed brands list: {', '.join(failed_brands[:10])}")
            if len(failed_brands) > 10:
                print(f"... and {len(failed_brands) - 10} more")
        print(f"{'#'*60}\n")
        
        return all_brands_data


class ChototCrawler:
    """Crawler for Chotot.com car listings."""
    
    BASE_URL = "https://xe.chotot.com/mua-ban-oto"
    
    def __init__(self, delay: float = 0.1):
        """
        Initialize the Chotot crawler.
        
        Args:
            delay: Delay between requests in seconds (default: 0.5)
        """
        self.headers = get_headers()
        self.delay = delay
        self.progress = ProgressTracker()
    
    def crawl_car_details(self, link: str) -> Optional[Dict[str, str]]:
        """
        Crawl details of a single car.
        
        Args:
            link: URL of the car detail page
            
        Returns:
            Dictionary containing car details or None if failed
        """
        try:
            response = requests.get(link, headers=self.headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                car_data = parse_chotot_car_details(soup)
                car_data['url'] = link
                return car_data
            else:
                print(f"Failed to fetch {link}, status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error crawling car details from {link}: {e}")
            return None
    
    def crawl_listings(self, max_cars: Optional[int] = None, 
                       max_pages: Optional[int] = None, save_to_csv: bool = True,
                       output_dir: str = "data") -> List[Dict[str, str]]:
        """
        Crawl car listings from Chotot.
        
        Args:
            max_cars: Maximum number of cars to crawl (None for all)
            max_pages: Maximum number of pages to crawl (None for all)
            save_to_csv: Whether to save results to CSV file (default: True)
            output_dir: Directory to save CSV file (default: "data")
            
        Returns:
            List of dictionaries containing car data
        """
        all_cars = []
        cars_crawled = 0
        skipped_count = 0
        
        # Check if already completed
        if self.progress.is_completed('chotot'):
            print(f"⚠ Chotot was already completed. Use --reset-progress to start over.")
            return all_cars
        
        # Get last crawled page
        page = self.progress.get_last_page('chotot')
        if page > 0:
            page += 1  # Start from next page
            print(f"📍 Resuming from page {page} (last completed: page {page - 1})")
        else:
            page = 1
        
        # Setup CSV file path if saving
        csv_filepath = None
        if save_to_csv:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            csv_filepath = output_path / "chotot.csv"
        
        print(f"\n{'='*60}")
        print(f"Starting crawl for Chotot.com")
        print(f"Max cars: {max_cars if max_cars else 'unlimited'}")
        print(f"Max pages: {max_pages if max_pages else 'unlimited'}")
        print(f"{'='*60}\n")
        
        while True:
            # Check if we've reached max pages
            if max_pages and page > max_pages:
                print(f"\nReached maximum pages limit: {max_pages}")
                break
            
            # Check if we've reached max cars
            if max_cars and cars_crawled >= max_cars:
                print(f"\nReached maximum cars limit: {max_cars}")
                break
            
            try:
                url = f'{self.BASE_URL}?page={page}'
                print(f"Fetching page {page} from: {url}")
                
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'lxml')
                    car_links = parse_chotot_listing(soup)
                    
                    if not car_links:
                        print(f"No more cars found on page {page}")
                        break
                    
                    print(f"Found {len(car_links)} cars on page {page}")
                    
                    # Crawl each car on this page
                    for idx, link in enumerate(car_links, 1):
                        if max_cars and cars_crawled >= max_cars:
                            break
                        
                        print(f"  [{cars_crawled + 1}] Crawling: {link}")
                        car_data = self.crawl_car_details(link)
                        
                        if car_data:
                            all_cars.append(car_data)
                            
                            # Write to CSV
                            if save_to_csv and csv_filepath:
                                self._append_single_car_to_csv(car_data, csv_filepath)
                            
                            cars_crawled += 1
                            print(f"  ✓ Successfully crawled")
                        
                        rate_limit(self.delay)
                    
                    # Save progress after completing this page
                    self.progress.update_page('chotot', page)
                    
                    page += 1
                    
                else:
                    print(f"Failed to fetch page {page}, status code: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
        
        print(f"\n{'='*60}")
        print(f"Crawl completed for Chotot.com")
        print(f"Total cars crawled: {cars_crawled}")
        if save_to_csv and csv_filepath and csv_filepath.exists():
            try:
                # Count lines instead of reading entire CSV to avoid column mismatch errors
                with open(csv_filepath, 'r', encoding='utf-8-sig') as f:
                    total_in_file = sum(1 for line in f) - 1  # Subtract header
                print(f"Total cars in chotot.csv: {total_in_file}")
            except Exception as e:
                print(f"Could not count total cars: {e}")
        print(f"{'='*60}\n")
        
        # Mark as completed if we finished naturally (not due to max limits)
        if not ((max_cars and cars_crawled >= max_cars) or (max_pages and page > max_pages)):
            self.progress.mark_completed('chotot')
        
        return all_cars
    
    def _append_single_car_to_csv(self, car_data: Dict[str, str], filepath: Path):
        """
        Append a single car to CSV file immediately.
        
        Args:
            car_data: Dictionary containing car data
            filepath: Path to the CSV file
        """
        try:
            # Remove unwanted fields
            car_data.pop('crawl_timestamp', None)
            car_data.pop('title', None)
            
            # Convert to DataFrame
            df = pd.DataFrame([car_data])
            
            # Append to existing file or create new one
            if filepath.exists():
                df.to_csv(filepath, mode='a', header=False, index=False, encoding='utf-8-sig')
            else:
                df.to_csv(filepath, mode='w', header=True, index=False, encoding='utf-8-sig')
            
        except Exception as e:
            print(f"  ✗ Error writing to CSV: {e}")
