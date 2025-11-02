"""Unit tests for OutputGenerator"""

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from PIL import Image
from src.output import OutputGenerator
from src.exceptions import OutputError


class TestOutputGenerator(unittest.TestCase):
    """Test cases for OutputGenerator class"""
    
    def test_init_valid_png(self):
        """Test initialization with PNG format"""
        generator = OutputGenerator(format='png')
        self.assertEqual(generator.format, 'png')
        self.assertEqual(generator.quality, 85)
    
    def test_init_valid_jpeg(self):
        """Test initialization with JPEG format"""
        generator = OutputGenerator(format='jpeg', quality=90)
        self.assertEqual(generator.format, 'jpeg')
        self.assertEqual(generator.quality, 90)
        
        # Test jpg alias
        generator = OutputGenerator(format='jpg', quality=80)
        self.assertEqual(generator.format, 'jpeg')
        self.assertEqual(generator.quality, 80)
    
    def test_init_invalid_format(self):
        """Test initialization with invalid format"""
        with self.assertRaises(ValueError):
            OutputGenerator(format='bmp')
    
    def test_init_invalid_quality(self):
        """Test initialization with invalid quality"""
        with self.assertRaises(ValueError):
            OutputGenerator(format='jpeg', quality=0)
        
        with self.assertRaises(ValueError):
            OutputGenerator(format='jpeg', quality=101)
    
    @patch('src.output.Path.exists')
    @patch('src.output.Path.mkdir')
    def test_save_png_success(self, mock_mkdir, mock_exists):
        """Test successful PNG save"""
        mock_exists.return_value = False
        
        generator = OutputGenerator(format='png')
        image = Image.new('RGB', (100, 100), (255, 0, 0))
        output_path = Path('test_output.png')
        
        with patch.object(Image.Image, 'save') as mock_save:
            result = generator.save(image, output_path, confirm_overwrite=False)
            
            self.assertTrue(result)
            mock_save.assert_called_once_with(output_path, format='PNG', optimize=True)
    
    @patch('src.output.Path.exists')
    @patch('src.output.Path.mkdir')
    def test_save_jpeg_success(self, mock_mkdir, mock_exists):
        """Test successful JPEG save"""
        mock_exists.return_value = False
        
        generator = OutputGenerator(format='jpeg', quality=90)
        image = Image.new('RGB', (100, 100), (255, 0, 0))
        output_path = Path('test_output.jpg')
        
        with patch.object(Image.Image, 'save') as mock_save:
            result = generator.save(image, output_path, confirm_overwrite=False)
            
            self.assertTrue(result)
            mock_save.assert_called_once_with(output_path, format='JPEG', quality=90, optimize=True)
    
    @patch('src.output.Path.exists')
    @patch('src.output.Path.mkdir')
    def test_save_jpeg_converts_rgba(self, mock_mkdir, mock_exists):
        """Test JPEG save converts RGBA to RGB"""
        mock_exists.return_value = False
        
        generator = OutputGenerator(format='jpeg', quality=85)
        image = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
        output_path = Path('test_output.jpg')
        
        with patch.object(Image.Image, 'save') as mock_save:
            with patch.object(Image.Image, 'convert', return_value=image) as mock_convert:
                result = generator.save(image, output_path, confirm_overwrite=False)
                
                self.assertTrue(result)
                mock_convert.assert_called_once_with('RGB')
    
    @patch('src.output.Path.exists')
    @patch('builtins.input')
    def test_save_with_overwrite_confirmation_yes(self, mock_input, mock_exists):
        """Test save with overwrite confirmation (yes)"""
        mock_exists.return_value = True
        mock_input.return_value = 'y'
        
        generator = OutputGenerator(format='png')
        image = Image.new('RGB', (100, 100))
        output_path = Path('existing.png')
        
        with patch.object(Image.Image, 'save'):
            with patch('src.output.Path.mkdir'):
                result = generator.save(image, output_path, confirm_overwrite=True)
                
                self.assertTrue(result)
                mock_input.assert_called_once()
    
    @patch('src.output.Path.exists')
    @patch('builtins.input')
    def test_save_with_overwrite_confirmation_no(self, mock_input, mock_exists):
        """Test save with overwrite confirmation (no)"""
        mock_exists.return_value = True
        mock_input.return_value = 'n'
        
        generator = OutputGenerator(format='png')
        image = Image.new('RGB', (100, 100))
        output_path = Path('existing.png')
        
        result = generator.save(image, output_path, confirm_overwrite=True)
        
        self.assertFalse(result)
        mock_input.assert_called_once()
    
    @patch('src.output.Path.exists')
    @patch('src.output.Path.mkdir')
    def test_save_failure(self, mock_mkdir, mock_exists):
        """Test save failure"""
        mock_exists.return_value = False
        
        generator = OutputGenerator(format='png')
        image = Image.new('RGB', (100, 100))
        output_path = Path('test.png')
        
        with patch.object(Image.Image, 'save', side_effect=Exception("Save failed")):
            with self.assertRaises(OutputError):
                generator.save(image, output_path, confirm_overwrite=False)
    
    def test_generate_default_output_path_png(self):
        """Test default output path generation for PNG"""
        generator = OutputGenerator(format='png')
        input_path = Path('/path/to/document.pdf')
        
        output_path = generator._generate_default_output_path(input_path)
        
        self.assertEqual(output_path, Path('/path/to/document_long_screenshot.png'))
    
    def test_generate_default_output_path_jpeg(self):
        """Test default output path generation for JPEG"""
        generator = OutputGenerator(format='jpeg')
        input_path = Path('/path/to/document.pdf')
        
        output_path = generator._generate_default_output_path(input_path)
        
        self.assertEqual(output_path, Path('/path/to/document_long_screenshot.jpg'))
    
    @patch('builtins.input')
    def test_confirm_overwrite_yes(self, mock_input):
        """Test overwrite confirmation with yes"""
        mock_input.return_value = 'y'
        
        generator = OutputGenerator()
        result = generator._confirm_overwrite(Path('test.png'))
        
        self.assertTrue(result)
    
    @patch('builtins.input')
    def test_confirm_overwrite_no(self, mock_input):
        """Test overwrite confirmation with no"""
        mock_input.return_value = 'n'
        
        generator = OutputGenerator()
        result = generator._confirm_overwrite(Path('test.png'))
        
        self.assertFalse(result)
    
    @patch('builtins.input')
    def test_confirm_overwrite_yes_variations(self, mock_input):
        """Test overwrite confirmation with various yes responses"""
        generator = OutputGenerator()
        
        for response in ['y', 'Y', 'yes', 'YES', 'Yes']:
            mock_input.return_value = response
            result = generator._confirm_overwrite(Path('test.png'))
            self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
