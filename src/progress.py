"""Progress reporting module"""

import time
from pathlib import Path


class ProgressReporter:
    """Reporter for displaying conversion progress"""
    
    def __init__(self, total_pages: int):
        """Initialize the progress reporter
        
        Args:
            total_pages: Total number of pages to process
        """
        self.total_pages = total_pages
        self.start_time = None
    
    def start(self) -> None:
        """Start the progress timer"""
        self.start_time = time.time()
        print(f"Starting conversion of {self.total_pages} page(s)...")
    
    def update(self, current_page: int, message: str = "") -> None:
        """Update progress with current page
        
        Args:
            current_page: Current page number being processed
            message: Optional additional message
        """
        progress_msg = f"Processing page {current_page}/{self.total_pages}"
        if message:
            progress_msg += f" - {message}"
        print(progress_msg)
    
    def complete(self, output_path: Path) -> None:
        """Display completion message
        
        Args:
            output_path: Path to the output file
        """
        if self.start_time is None:
            processing_time = 0
        else:
            processing_time = time.time() - self.start_time
        
        print(f"\n✓ Conversion completed successfully!")
        print(f"Output saved to: {output_path}")
        print(f"Total processing time: {processing_time:.2f} seconds")
    
    def error(self, message: str) -> None:
        """Display error message
        
        Args:
            message: Error message to display
        """
        print(f"\n✗ Error: {message}")
        
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            print(f"Failed after {elapsed_time:.2f} seconds")
