"""PDF rendering module"""

from pathlib import Path
from typing import Optional, Callable
from PIL import Image
from pdf2image import convert_from_path
from .exceptions import RenderingError


class PDFRenderer:
    """Renderer for converting PDF pages to images"""
    
    def __init__(self, dpi: int = 150, auto_crop: bool = True, crop_margin: int = 10):
        """Initialize the PDF renderer
        
        Args:
            dpi: Resolution in dots per inch (72-300)
            auto_crop: If True, automatically crop whitespace from each page
            crop_margin: Margin to keep around content in pixels (default: 10)
        """
        if not 72 <= dpi <= 300:
            raise ValueError(f"DPI must be between 72 and 300, got {dpi}")
        if crop_margin < 0:
            raise ValueError(f"Crop margin must be non-negative, got {crop_margin}")
        self.dpi = dpi
        self.auto_crop = auto_crop
        self.crop_margin = crop_margin
    
    def render_pages(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> list[Image.Image]:
        """Render all PDF pages as images
        
        Args:
            pdf_path: Path to the PDF file
            progress_callback: Optional callback function (current_page, total_pages)
            
        Returns:
            List of PIL Image objects
            
        Raises:
            RenderingError: If rendering fails
        """
        try:
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                fmt='png',
                thread_count=4
            )
            
            # Process each image
            processed_images = []
            total_pages = len(images)
            
            for idx, image in enumerate(images, start=1):
                # Ensure white background for transparent images
                processed_image = self._ensure_white_background(image)
                
                # Auto-crop whitespace if enabled
                if self.auto_crop:
                    processed_image = self._crop_whitespace(processed_image)
                
                processed_images.append(processed_image)
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(idx, total_pages)
            
            return processed_images
            
        except Exception as e:
            raise RenderingError(f"Failed to render PDF pages: {str(e)}")
    
    def _ensure_white_background(self, image: Image.Image) -> Image.Image:
        """Convert RGBA images to RGB with white background
        
        Args:
            image: PIL Image object
            
        Returns:
            PIL Image object with white background
        """
        if image.mode == 'RGBA':
            # Create white background
            white_bg = Image.new('RGB', image.size, (255, 255, 255))
            # Paste image on white background using alpha channel as mask
            white_bg.paste(image, mask=image.split()[3])
            return white_bg
        elif image.mode != 'RGB':
            # Convert other modes to RGB
            return image.convert('RGB')
        
        return image
    
    def _crop_whitespace(self, image: Image.Image) -> Image.Image:
        """Crop whitespace from all edges of the image
        
        Args:
            image: PIL Image object
            
        Returns:
            Cropped PIL Image object
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get image data
        pixels = image.load()
        width, height = image.size
        
        # Find content boundaries
        left = self._find_left_boundary(pixels, width, height)
        right = self._find_right_boundary(pixels, width, height)
        top = self._find_top_boundary(pixels, width, height)
        bottom = self._find_bottom_boundary(pixels, width, height)
        
        # Add margin but ensure we don't go outside image bounds
        left = max(0, left - self.crop_margin)
        right = min(width, right + self.crop_margin)
        top = max(0, top - self.crop_margin)
        bottom = min(height, bottom + self.crop_margin)
        
        # Crop the image
        if left < right and top < bottom:
            return image.crop((left, top, right, bottom))
        
        # If no content found, return original
        return image
    
    def _is_white_pixel(self, pixel: tuple, threshold: int = 250) -> bool:
        """Check if a pixel is white (or near-white)
        
        Args:
            pixel: RGB tuple
            threshold: Threshold for considering a pixel white (0-255)
            
        Returns:
            True if pixel is white
        """
        return pixel[0] > threshold and pixel[1] > threshold and pixel[2] > threshold
    
    def _find_left_boundary(self, pixels, width: int, height: int) -> int:
        """Find leftmost non-white column"""
        for x in range(width):
            for y in range(height):
                if not self._is_white_pixel(pixels[x, y]):
                    return x
        return 0
    
    def _find_right_boundary(self, pixels, width: int, height: int) -> int:
        """Find rightmost non-white column"""
        for x in range(width - 1, -1, -1):
            for y in range(height):
                if not self._is_white_pixel(pixels[x, y]):
                    return x + 1
        return width
    
    def _find_top_boundary(self, pixels, width: int, height: int) -> int:
        """Find topmost non-white row"""
        for y in range(height):
            for x in range(width):
                if not self._is_white_pixel(pixels[x, y]):
                    return y
        return 0
    
    def _find_bottom_boundary(self, pixels, width: int, height: int) -> int:
        """Find bottommost non-white row"""
        for y in range(height - 1, -1, -1):
            for x in range(width):
                if not self._is_white_pixel(pixels[x, y]):
                    return y + 1
        return height
