"""PDF file validation module"""

from pathlib import Path
from typing import Tuple
from pdf2image import pdfinfo_from_path
from .exceptions import FileValidationError


class PDFValidator:
    """Validator for PDF files"""
    
    @staticmethod
    def validate_file(file_path: Path) -> Tuple[bool, str]:
        """Validate file existence and format
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check if file exists
        if not file_path.exists():
            return False, f"File does not exist: {file_path}"
        
        # Check if it's a file (not a directory)
        if not file_path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        # Check file extension
        if file_path.suffix.lower() != '.pdf':
            return False, f"Invalid file format: expected .pdf, got {file_path.suffix}"
        
        # Try to read PDF info to verify it's a valid PDF
        try:
            pdfinfo_from_path(file_path)
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"
        
        return True, ""
    
    @staticmethod
    def check_file_size(file_path: Path, max_size_mb: int = 100) -> Tuple[bool, str]:
        """Check file size against maximum limit
        
        Args:
            file_path: Path to the PDF file
            max_size_mb: Maximum file size in megabytes
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        file_size_bytes = file_path.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum limit of {max_size_mb} MB"
        
        return True, ""
    
    @staticmethod
    def get_page_count(file_path: Path) -> int:
        """Get the number of pages in the PDF
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            int: Number of pages in the PDF
            
        Raises:
            FileValidationError: If unable to read PDF info
        """
        try:
            info = pdfinfo_from_path(file_path)
            return info.get("Pages", 0)
        except Exception as e:
            raise FileValidationError(f"Unable to get page count: {str(e)}")
