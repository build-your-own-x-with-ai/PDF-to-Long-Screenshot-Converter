"""Unit tests for PDFRenderer"""

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from PIL import Image
from src.renderer import PDFRenderer
from src.exceptions import RenderingError


class TestPDFRenderer(unittest.TestCase):
    """Test cases for PDFRenderer class"""
    
    def test_init_valid_dpi(self):
        """Test initialization with valid DPI"""
        renderer = PDFRenderer(dpi=150)
        self.assertEqual(renderer.dpi, 150)
        
        renderer = PDFRenderer(dpi=72)
        self.assertEqual(renderer.dpi, 72)
        
        renderer = PDFRenderer(dpi=300)
        self.assertEqual(renderer.dpi, 300)
        
        renderer = PDFRenderer(dpi=150, auto_crop=False)
        self.assertFalse(renderer.auto_crop)
        
        renderer = PDFRenderer(dpi=150, crop_margin=20)
        self.assertEqual(renderer.crop_margin, 20)
    
    def test_init_invalid_dpi(self):
        """Test initialization with invalid DPI"""
        with self.assertRaises(ValueError):
            PDFRenderer(dpi=50)
        
        with self.assertRaises(ValueError):
            PDFRenderer(dpi=350)
    
    @patch('src.renderer.convert_from_path')
    def test_render_pages_success(self, mock_convert):
        """Test successful page rendering"""
        # Create mock images
        mock_image1 = MagicMock(spec=Image.Image)
        mock_image1.mode = 'RGB'
        mock_image2 = MagicMock(spec=Image.Image)
        mock_image2.mode = 'RGB'
        
        mock_convert.return_value = [mock_image1, mock_image2]
        
        renderer = PDFRenderer(dpi=150, auto_crop=False)
        file_path = Path("test.pdf")
        
        images = renderer.render_pages(file_path)
        
        self.assertEqual(len(images), 2)
        mock_convert.assert_called_once_with(
            file_path,
            dpi=150,
            fmt='png',
            thread_count=4
        )
    
    @patch('src.renderer.convert_from_path')
    def test_render_pages_with_progress_callback(self, mock_convert):
        """Test rendering with progress callback"""
        mock_image = MagicMock(spec=Image.Image)
        mock_image.mode = 'RGB'
        mock_convert.return_value = [mock_image, mock_image, mock_image]
        
        renderer = PDFRenderer(dpi=200, auto_crop=False)
        file_path = Path("test.pdf")
        
        progress_calls = []
        def progress_callback(current, total):
            progress_calls.append((current, total))
        
        images = renderer.render_pages(file_path, progress_callback=progress_callback)
        
        self.assertEqual(len(images), 3)
        self.assertEqual(progress_calls, [(1, 3), (2, 3), (3, 3)])
    
    @patch('src.renderer.convert_from_path')
    def test_render_pages_failure(self, mock_convert):
        """Test rendering failure"""
        mock_convert.side_effect = Exception("PDF conversion failed")
        
        renderer = PDFRenderer(dpi=150)
        file_path = Path("test.pdf")
        
        with self.assertRaises(RenderingError) as context:
            renderer.render_pages(file_path)
        
        self.assertIn("Failed to render PDF pages", str(context.exception))
    
    def test_ensure_white_background_rgba(self):
        """Test RGBA to RGB conversion with white background"""
        renderer = PDFRenderer()
        
        # Create a mock RGBA image
        rgba_image = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
        
        result = renderer._ensure_white_background(rgba_image)
        
        self.assertEqual(result.mode, 'RGB')
        self.assertEqual(result.size, (100, 100))
    
    def test_ensure_white_background_rgb(self):
        """Test RGB image remains unchanged"""
        renderer = PDFRenderer()
        
        rgb_image = Image.new('RGB', (100, 100), (255, 0, 0))
        
        result = renderer._ensure_white_background(rgb_image)
        
        self.assertEqual(result.mode, 'RGB')
        self.assertIs(result, rgb_image)
    
    def test_ensure_white_background_other_mode(self):
        """Test conversion of other image modes to RGB"""
        renderer = PDFRenderer()
        
        # Create a grayscale image
        gray_image = Image.new('L', (100, 100), 128)
        
        result = renderer._ensure_white_background(gray_image)
        
        self.assertEqual(result.mode, 'RGB')
        self.assertEqual(result.size, (100, 100))


if __name__ == '__main__':
    unittest.main()
