"""Unit tests for PDFValidator"""

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.validator import PDFValidator
from src.exceptions import FileValidationError


class TestPDFValidator(unittest.TestCase):
    """Test cases for PDFValidator class"""
    
    def test_validate_file_nonexistent(self):
        """Test validation with non-existent file"""
        file_path = Path("nonexistent.pdf")
        is_valid, error_msg = PDFValidator.validate_file(file_path)
        
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error_msg)
    
    def test_validate_file_wrong_extension(self):
        """Test validation with non-PDF file"""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_file', return_value=True):
                file_path = Path("document.txt")
                is_valid, error_msg = PDFValidator.validate_file(file_path)
                
                self.assertFalse(is_valid)
                self.assertIn("Invalid file format", error_msg)
    
    @patch('src.validator.pdfinfo_from_path')
    def test_validate_file_valid_pdf(self, mock_pdfinfo):
        """Test validation with valid PDF file"""
        mock_pdfinfo.return_value = {"Pages": 5}
        
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_file', return_value=True):
                file_path = Path("valid.pdf")
                is_valid, error_msg = PDFValidator.validate_file(file_path)
                
                self.assertTrue(is_valid)
                self.assertEqual(error_msg, "")
    
    @patch('src.validator.pdfinfo_from_path')
    def test_validate_file_corrupted_pdf(self, mock_pdfinfo):
        """Test validation with corrupted PDF file"""
        mock_pdfinfo.side_effect = Exception("Corrupted PDF")
        
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_file', return_value=True):
                file_path = Path("corrupted.pdf")
                is_valid, error_msg = PDFValidator.validate_file(file_path)
                
                self.assertFalse(is_valid)
                self.assertIn("Invalid PDF file", error_msg)
    
    def test_check_file_size_within_limit(self):
        """Test file size check within limit"""
        mock_stat = MagicMock()
        mock_stat.st_size = 50 * 1024 * 1024  # 50 MB
        
        with patch.object(Path, 'stat', return_value=mock_stat):
            file_path = Path("test.pdf")
            is_valid, error_msg = PDFValidator.check_file_size(file_path, max_size_mb=100)
            
            self.assertTrue(is_valid)
            self.assertEqual(error_msg, "")
    
    def test_check_file_size_exceeds_limit(self):
        """Test file size check exceeding limit"""
        mock_stat = MagicMock()
        mock_stat.st_size = 150 * 1024 * 1024  # 150 MB
        
        with patch.object(Path, 'stat', return_value=mock_stat):
            file_path = Path("large.pdf")
            is_valid, error_msg = PDFValidator.check_file_size(file_path, max_size_mb=100)
            
            self.assertFalse(is_valid)
            self.assertIn("exceeds maximum limit", error_msg)
    
    @patch('src.validator.pdfinfo_from_path')
    def test_get_page_count_success(self, mock_pdfinfo):
        """Test getting page count successfully"""
        mock_pdfinfo.return_value = {"Pages": 10}
        
        file_path = Path("test.pdf")
        page_count = PDFValidator.get_page_count(file_path)
        
        self.assertEqual(page_count, 10)
    
    @patch('src.validator.pdfinfo_from_path')
    def test_get_page_count_failure(self, mock_pdfinfo):
        """Test getting page count with error"""
        mock_pdfinfo.side_effect = Exception("Cannot read PDF")
        
        file_path = Path("test.pdf")
        
        with self.assertRaises(FileValidationError):
            PDFValidator.get_page_count(file_path)


if __name__ == '__main__':
    unittest.main()
