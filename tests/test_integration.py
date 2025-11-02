"""Integration tests for CLI"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from src.cli import main, parse_arguments, validate_arguments


class TestCLIIntegration(unittest.TestCase):
    """Integration test cases for CLI"""
    
    @patch('sys.argv', ['cli.py', '--help'])
    def test_help_flag(self):
        """Test help flag displays usage information"""
        with self.assertRaises(SystemExit) as context:
            parse_arguments()
        
        # Help should exit with code 0
        self.assertEqual(context.exception.code, 0)
    
    @patch('sys.argv', ['cli.py'])
    def test_missing_required_argument(self):
        """Test missing required input argument"""
        with self.assertRaises(SystemExit):
            parse_arguments()
    
    @patch('sys.argv', ['cli.py', 'input.pdf'])
    def test_parse_minimal_arguments(self):
        """Test parsing with minimal arguments"""
        args = parse_arguments()
        
        self.assertEqual(args.input, 'input.pdf')
        self.assertIsNone(args.output)
        self.assertEqual(args.dpi, 150)
        self.assertEqual(args.format, 'png')
        self.assertEqual(args.quality, 85)
        self.assertEqual(args.spacing, 0)
        self.assertFalse(args.no_confirm)
    
    @patch('sys.argv', ['cli.py', 'input.pdf', '-o', 'output.png', '--dpi', '200'])
    def test_parse_with_options(self):
        """Test parsing with various options"""
        args = parse_arguments()
        
        self.assertEqual(args.input, 'input.pdf')
        self.assertEqual(args.output, 'output.png')
        self.assertEqual(args.dpi, 200)
    
    @patch('sys.argv', ['cli.py', 'input.pdf', '-f', 'jpeg', '-q', '90', '-s', '10'])
    def test_parse_jpeg_options(self):
        """Test parsing JPEG-specific options"""
        args = parse_arguments()
        
        self.assertEqual(args.format, 'jpeg')
        self.assertEqual(args.quality, 90)
        self.assertEqual(args.spacing, 10)
    
    @patch('sys.argv', ['cli.py', 'input.pdf', '--no-confirm'])
    def test_parse_no_confirm_flag(self):
        """Test parsing no-confirm flag"""
        args = parse_arguments()
        
        self.assertTrue(args.no_confirm)
    
    def test_validate_arguments_valid(self):
        """Test validation with valid arguments"""
        args = MagicMock()
        args.dpi = 150
        args.quality = 85
        args.spacing = 10
        args.crop_margin = 10
        
        result = validate_arguments(args)
        self.assertTrue(result)
    
    def test_validate_arguments_invalid_dpi(self):
        """Test validation with invalid DPI"""
        args = MagicMock()
        args.dpi = 50
        args.quality = 85
        args.spacing = 0
        args.crop_margin = 10
        
        with self.assertRaises(ValueError) as context:
            validate_arguments(args)
        
        self.assertIn("DPI", str(context.exception))
    
    def test_validate_arguments_invalid_quality(self):
        """Test validation with invalid quality"""
        args = MagicMock()
        args.dpi = 150
        args.quality = 150
        args.spacing = 0
        args.crop_margin = 10
        
        with self.assertRaises(ValueError) as context:
            validate_arguments(args)
        
        self.assertIn("Quality", str(context.exception))
    
    def test_validate_arguments_invalid_spacing(self):
        """Test validation with invalid spacing"""
        args = MagicMock()
        args.dpi = 150
        args.quality = 85
        args.spacing = -5
        args.crop_margin = 10
        
        with self.assertRaises(ValueError) as context:
            validate_arguments(args)
        
        self.assertIn("Spacing", str(context.exception))
    
    @patch('sys.argv', ['cli.py', 'nonexistent.pdf'])
    @patch('builtins.print')
    def test_main_nonexistent_file(self, mock_print):
        """Test main with non-existent file"""
        exit_code = main()
        
        self.assertEqual(exit_code, 1)
        # Check that error message was printed
        self.assertTrue(any('does not exist' in str(call) for call in mock_print.call_args_list))
    
    @patch('sys.argv', ['cli.py', 'test.txt'])
    @patch('src.cli.Path.exists', return_value=True)
    @patch('src.cli.Path.is_file', return_value=True)
    @patch('builtins.print')
    def test_main_invalid_file_format(self, mock_print, mock_is_file, mock_exists):
        """Test main with invalid file format"""
        exit_code = main()
        
        self.assertEqual(exit_code, 1)
        # Check that error message was printed
        self.assertTrue(any('Invalid file format' in str(call) for call in mock_print.call_args_list))
    
    @patch('sys.argv', ['cli.py', 'test.pdf', '--dpi', '500'])
    @patch('builtins.print')
    def test_main_invalid_dpi(self, mock_print):
        """Test main with invalid DPI value"""
        exit_code = main()
        
        self.assertEqual(exit_code, 1)
        # Check that error message was printed
        self.assertTrue(any('DPI' in str(call) for call in mock_print.call_args_list))
    
    @patch('sys.argv', ['cli.py', 'test.pdf'])
    @patch('src.cli.PDFValidator.validate_file', return_value=(True, ''))
    @patch('src.cli.PDFValidator.check_file_size', return_value=(True, ''))
    @patch('src.cli.PDFValidator.get_page_count', return_value=3)
    @patch('src.cli.PDFRenderer')
    @patch('src.cli.ImageCompositor')
    @patch('src.cli.OutputGenerator')
    @patch('src.cli.Path.exists', return_value=True)
    @patch('src.cli.Path.is_file', return_value=True)
    @patch('builtins.print')
    def test_main_successful_conversion(
        self,
        mock_print,
        mock_is_file,
        mock_exists,
        mock_output_gen_class,
        mock_compositor_class,
        mock_renderer_class,
        mock_page_count,
        mock_check_size,
        mock_validate
    ):
        """Test successful end-to-end conversion"""
        # Setup mocks
        mock_renderer = MagicMock()
        mock_renderer.render_pages.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_renderer_class.return_value = mock_renderer
        
        mock_compositor = MagicMock()
        mock_compositor.compose.return_value = MagicMock()
        mock_compositor_class.return_value = mock_compositor
        
        mock_output_gen = MagicMock()
        mock_output_gen.save.return_value = True
        mock_output_gen_class.return_value = mock_output_gen
        
        exit_code = main()
        
        self.assertEqual(exit_code, 0)
        # Verify that success message was printed
        self.assertTrue(any('completed successfully' in str(call) for call in mock_print.call_args_list))
    
    @patch('sys.argv', ['cli.py', 'test.pdf'])
    @patch('src.cli.PDFValidator.validate_file', return_value=(True, ''))
    @patch('src.cli.PDFValidator.check_file_size', return_value=(True, ''))
    @patch('src.cli.PDFValidator.get_page_count', return_value=3)
    @patch('src.cli.PDFRenderer')
    @patch('src.cli.Path.exists', return_value=True)
    @patch('src.cli.Path.is_file', return_value=True)
    @patch('builtins.print')
    def test_main_rendering_error(
        self,
        mock_print,
        mock_is_file,
        mock_exists,
        mock_renderer_class,
        mock_page_count,
        mock_check_size,
        mock_validate
    ):
        """Test handling of rendering error"""
        from src.exceptions import RenderingError
        
        mock_renderer = MagicMock()
        mock_renderer.render_pages.side_effect = RenderingError("Rendering failed")
        mock_renderer_class.return_value = mock_renderer
        
        exit_code = main()
        
        self.assertEqual(exit_code, 2)
        # Verify that error message was printed
        self.assertTrue(any('Error' in str(call) for call in mock_print.call_args_list))


if __name__ == '__main__':
    unittest.main()
