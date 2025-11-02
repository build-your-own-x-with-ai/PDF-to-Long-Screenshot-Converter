"""Image composition module"""

from typing import Tuple
from PIL import Image
from .exceptions import CompositionError


class ImageCompositor:
    """Compositor for vertically concatenating images"""
    
    def __init__(self, spacing: int = 0, auto_width: bool = True):
        """Initialize the image compositor
        
        Args:
            spacing: Spacing between images in pixels
            auto_width: If True, use each page's actual width instead of max width
        """
        if spacing < 0:
            raise ValueError(f"Spacing must be non-negative, got {spacing}")
        self.spacing = spacing
        self.auto_width = auto_width
    
    def compose(self, images: list[Image.Image]) -> Image.Image:
        """Compose multiple images into a single long screenshot
        
        Args:
            images: List of PIL Image objects to concatenate
            
        Returns:
            Composed PIL Image object
            
        Raises:
            CompositionError: If composition fails
        """
        if not images:
            raise CompositionError("Cannot compose empty image list")
        
        try:
            if self.auto_width:
                # Stack images directly without padding to max width
                return self._compose_auto_width(images)
            else:
                # Use max width and center align (original behavior)
                return self._compose_fixed_width(images)
            
        except Exception as e:
            raise CompositionError(f"Failed to compose images: {str(e)}")
    
    def _compose_auto_width(self, images: list[Image.Image]) -> Image.Image:
        """Compose images using each page's actual width
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            Composed image with variable width per page
        """
        # Calculate total height
        total_height = sum(img.height for img in images)
        if len(images) > 1:
            total_height += self.spacing * (len(images) - 1)
        
        # Find max width for canvas
        max_width = max(img.width for img in images)
        
        # Create canvas
        canvas = Image.new('RGB', (max_width, total_height), (255, 255, 255))
        
        # Paste images
        y_offset = 0
        for image in images:
            # Paste at left edge (x=0) instead of centering
            canvas.paste(image, (0, y_offset))
            y_offset += image.height + self.spacing
        
        # Crop to actual content width if all images have same width
        # or find the rightmost non-white pixel
        actual_width = self._find_actual_width(canvas)
        if actual_width < max_width:
            canvas = canvas.crop((0, 0, actual_width, total_height))
        
        return canvas
    
    def _compose_fixed_width(self, images: list[Image.Image]) -> Image.Image:
        """Compose images using max width and center alignment
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            Composed image with fixed width
        """
        # Calculate canvas size
        canvas_width, canvas_height = self._calculate_canvas_size(images)
        
        # Create white canvas
        canvas = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
        
        # Paste images onto canvas
        y_offset = 0
        for image in images:
            self._paste_centered(canvas, image, y_offset)
            y_offset += image.height + self.spacing
        
        return canvas
    
    def _find_actual_width(self, image: Image.Image) -> int:
        """Find the actual content width by detecting rightmost non-white pixels
        
        Args:
            image: PIL Image object
            
        Returns:
            Actual content width in pixels
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get image data
        pixels = image.load()
        width, height = image.size
        
        # Scan from right to left to find non-white content
        for x in range(width - 1, -1, -1):
            for y in range(height):
                pixel = pixels[x, y]
                # Check if pixel is not white (with small tolerance)
                if not (pixel[0] > 250 and pixel[1] > 250 and pixel[2] > 250):
                    return x + 1  # Return width (x + 1)
        
        # If all white, return minimum width
        return 1
    
    def _calculate_canvas_size(self, images: list[Image.Image]) -> Tuple[int, int]:
        """Calculate the size of the canvas needed for all images
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            Tuple of (width, height) in pixels
        """
        # Find maximum width
        max_width = max(img.width for img in images)
        
        # Calculate total height (sum of all heights + spacing between them)
        total_height = sum(img.height for img in images)
        if len(images) > 1:
            total_height += self.spacing * (len(images) - 1)
        
        return max_width, total_height
    
    def _paste_centered(
        self,
        canvas: Image.Image,
        image: Image.Image,
        y_offset: int
    ) -> None:
        """Paste an image centered horizontally on the canvas
        
        Args:
            canvas: Target canvas image
            image: Source image to paste
            y_offset: Vertical offset for pasting
        """
        # Calculate horizontal centering position
        x_offset = (canvas.width - image.width) // 2
        
        # Paste image onto canvas
        canvas.paste(image, (x_offset, y_offset))
