"""
Progress tracker for saving and resuming crawl progress.
"""
import json
from pathlib import Path
from typing import Dict, Optional
import threading


class ProgressTracker:
    """Track crawling progress to enable resume functionality."""
    
    def __init__(self, progress_file: str = "data/crawl_progress.json"):
        """
        Initialize progress tracker.
        
        Args:
            progress_file: Path to progress file
        """
        self.progress_file = Path(progress_file)
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.progress_data = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load progress from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load progress file: {e}")
                return {}
        return {}
    
    def _save_progress(self):
        """Save progress to file."""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save progress: {e}")
    
    def get_last_page(self, source: str, brand: str = None) -> int:
        """
        Get the last crawled page for a source/brand.
        
        Args:
            source: Source website (bonbanh/chotot)
            brand: Brand name (for bonbanh only)
            
        Returns:
            Last page number (0 if starting fresh)
        """
        key = f"{source}_{brand}" if brand else source
        return self.progress_data.get(key, {}).get('last_page', 0)
    
    def update_page(self, source: str, page: int, brand: str = None):
        """
        Update the last crawled page.
        
        Args:
            source: Source website (bonbanh/chotot)
            page: Current page number
            brand: Brand name (for bonbanh only)
        """
        with self.lock:
            key = f"{source}_{brand}" if brand else source
            if key not in self.progress_data:
                self.progress_data[key] = {}
            
            self.progress_data[key]['last_page'] = page
            self.progress_data[key]['source'] = source
            if brand:
                self.progress_data[key]['brand'] = brand
            
            self._save_progress()
    
    def mark_completed(self, source: str, brand: str = None):
        """
        Mark a crawl as completed.
        
        Args:
            source: Source website (bonbanh/chotot)
            brand: Brand name (for bonbanh only)
        """
        with self.lock:
            key = f"{source}_{brand}" if brand else source
            if key in self.progress_data:
                self.progress_data[key]['completed'] = True
                self._save_progress()
    
    def is_completed(self, source: str, brand: str = None) -> bool:
        """
        Check if a crawl is already completed.
        
        Args:
            source: Source website (bonbanh/chotot)
            brand: Brand name (for bonbanh only)
            
        Returns:
            True if completed, False otherwise
        """
        key = f"{source}_{brand}" if brand else source
        return self.progress_data.get(key, {}).get('completed', False)
    
    def reset(self, source: str = None, brand: str = None):
        """
        Reset progress for a specific source/brand or all.
        
        Args:
            source: Source website (None to reset all)
            brand: Brand name (None to reset all brands for source)
        """
        with self.lock:
            if source is None:
                self.progress_data = {}
                print("✓ All progress reset")
            else:
                key = f"{source}_{brand}" if brand else source
                if key in self.progress_data:
                    del self.progress_data[key]
                    print(f"✓ Progress reset for {key}")
            
            self._save_progress()
    
    def show_progress(self):
        """Display current progress."""
        if not self.progress_data:
            print("No progress data available")
            return
        
        print("\n" + "="*60)
        print("CRAWL PROGRESS")
        print("="*60)
        
        for key, data in self.progress_data.items():
            status = "✓ COMPLETED" if data.get('completed') else f"Last page: {data.get('last_page', 0)}"
            print(f"{key:30} - {status}")
        
        print("="*60 + "\n")
