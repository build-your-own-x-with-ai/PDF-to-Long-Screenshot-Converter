"""Unit tests for ImageCompositor"""

import unittest
from PIL import Image
from src.compositor import ImageCompositor
from src.exceptions import CompositionError


class TestImageCompositor(unittest.TestCase):
    """Test cases for ImageCompositor class"""
    
    def test_init_valid_spacing(self):
        """Test initialization with valid spacing"""
        compositor = ImageCompositor(spacing=0)
        self.assertEqual(compositor.spacing, 0)
        
        compositor = ImageCompositor(spacing=10)
        self.assertEqual(compositor.spacing, 10)
        
        compositor = ImageCompositor(spacing=0, auto_width=False)
        self.assertEqual(compositor.auto_width, False)
    
    def test_init_invalid_spacing(self):
        """Test initialization with invalid spacing"""
        with self.assertRaises(ValueError):
            ImageCompositor(spacing=-5)
    
    def test_compose_empty_list(self):
        """Test composition with empty image list"""
        compositor = ImageCompositor()
        
        with self.assertRaises(CompositionError):
            compositor.compose([])
    
    def test_compose_single_image(self):
        """Test composition with single image"""
        compositor = ImageCompositor()
        
        image = Image.new('RGB', (100, 50), (255, 0, 0))
        result = compositor.compose([image])
        
        self.assertEqual(result.size, (100, 50))
        self.assertEqual(result.mode, 'RGB')
    
    def test_compose_same_width_images(self):
        """Test composition with images of same width"""
        compositor = ImageCompositor(spacing=0)
        
        image1 = Image.new('RGB', (100, 50), (255, 0, 0))
        image2 = Image.new('RGB', (100, 60), (0, 255, 0))
        image3 = Image.new('RGB', (100, 40), (0, 0, 255))
        
        result = compositor.compose([image1, image2, image3])
        
        self.assertEqual(result.size, (100, 150))  # 50 + 60 + 40
        self.assertEqual(result.mode, 'RGB')
    
    def test_compose_different_width_images(self):
        """Test composition with images of different widths"""
        compositor = ImageCompositor(spacing=0)
        
        image1 = Image.new('RGB', (100, 50), (255, 0, 0))
        image2 = Image.new('RGB', (150, 60), (0, 255, 0))
        image3 = Image.new('RGB', (80, 40), (0, 0, 255))
        
        result = compositor.compose([image1, image2, image3])
        
        # Width should be max width (150)
        # Height should be sum of heights (50 + 60 + 40 = 150)
        self.assertEqual(result.size, (150, 150))
        self.assertEqual(result.mode, 'RGB')
    
    def test_compose_with_spacing(self):
        """Test composition with spacing between images"""
        compositor = ImageCompositor(spacing=10)
        
        image1 = Image.new('RGB', (100, 50), (255, 0, 0))
        image2 = Image.new('RGB', (100, 60), (0, 255, 0))
        image3 = Image.new('RGB', (100, 40), (0, 0, 255))
        
        result = compositor.compose([image1, image2, image3])
        
        # Height = 50 + 60 + 40 + (2 * 10 spacing) = 170
        self.assertEqual(result.size, (100, 170))
    
    def test_calculate_canvas_size_same_width(self):
        """Test canvas size calculation with same width images"""
        compositor = ImageCompositor(spacing=0)
        
        images = [
            Image.new('RGB', (100, 50)),
            Image.new('RGB', (100, 60)),
            Image.new('RGB', (100, 40))
        ]
        
        width, height = compositor._calculate_canvas_size(images)
        
        self.assertEqual(width, 100)
        self.assertEqual(height, 150)
    
    def test_calculate_canvas_size_different_widths(self):
        """Test canvas size calculation with different width images"""
        compositor = ImageCompositor(spacing=5)
        
        images = [
            Image.new('RGB', (100, 50)),
            Image.new('RGB', (150, 60)),
            Image.new('RGB', (80, 40))
        ]
        
        width, height = compositor._calculate_canvas_size(images)
        
        self.assertEqual(width, 150)  # Max width
        self.assertEqual(height, 160)  # 50 + 60 + 40 + (2 * 5)
    
    def test_paste_centered_same_width(self):
        """Test centered pasting with same width"""
        compositor = ImageCompositor()
        
        canvas = Image.new('RGB', (100, 100), (255, 255, 255))
        image = Image.new('RGB', (100, 50), (255, 0, 0))
        
        compositor._paste_centered(canvas, image, 0)
        
        # Check that image was pasted at correct position
        pixel = canvas.getpixel((50, 25))
        self.assertEqual(pixel, (255, 0, 0))
    
    def test_paste_centered_narrower_image(self):
        """Test centered pasting with narrower image"""
        compositor = ImageCompositor()
        
        canvas = Image.new('RGB', (200, 100), (255, 255, 255))
        image = Image.new('RGB', (100, 50), (0, 255, 0))
        
        compositor._paste_centered(canvas, image, 10)
        
        # Image should be centered horizontally at x=50
        # Check left edge of pasted image
        pixel = canvas.getpixel((50, 20))
        self.assertEqual(pixel, (0, 255, 0))
        
        # Check that area before image is white
        pixel_before = canvas.getpixel((40, 20))
        self.assertEqual(pixel_before, (255, 255, 255))


if __name__ == '__main__':
    unittest.main()
