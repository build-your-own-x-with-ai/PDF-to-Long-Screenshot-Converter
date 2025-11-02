"""Output generation module"""

from pathlib import Path
from typing import Optional
from PIL import Image
from .exceptions import OutputError


class OutputGenerator:
    """Generator for saving images to files"""
    
    def __init__(self, format: str = "png", quality: int = 85):
        """Initialize the output generator
        
        Args:
            format: Output format ('png' or 'jpeg')
            quality: JPEG quality (1-100), only used for JPEG format
        """
        format = format.lower()
        if format not in ['png', 'jpeg', 'jpg']:
            raise ValueError(f"Format must be 'png' or 'jpeg', got '{format}'")
        
        if not 1 <= quality <= 100:
            raise ValueError(f"Quality must be between 1 and 100, got {quality}")
        
        # Normalize jpeg/jpg to jpeg
        self.format = 'jpeg' if format in ['jpeg', 'jpg'] else format
        self.quality = quality
    
    def save(
        self,
        image: Image.Image,
        output_path: Path,
        confirm_overwrite: bool = True
    ) -> bool:
        """Save image to file
        
        Args:
            image: PIL Image object to save
            output_path: Path where to save the image
            confirm_overwrite: Whether to confirm before overwriting existing files
            
        Returns:
            True if saved successfully
            
        Raises:
            OutputError: If saving fails
        """
        try:
            # Check if file exists and confirm overwrite
            if output_path.exists() and confirm_overwrite:
                if not self._confirm_overwrite(output_path):
                    return False
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save based on format
            if self.format == 'png':
                image.save(output_path, format='PNG', optimize=True)
            elif self.format == 'jpeg':
                # Ensure image is in RGB mode for JPEG
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(output_path, format='JPEG', quality=self.quality, optimize=True)
            
            return True
            
        except Exception as e:
            raise OutputError(f"Failed to save image: {str(e)}")
    
    def _generate_default_output_path(self, input_path: Path) -> Path:
        """Generate default output path based on input path
        
        Args:
            input_path: Input PDF file path
            
        Returns:
            Default output path
        """
        # Get the directory and stem of input file
        directory = input_path.parent
        stem = input_path.stem
        
        # Create output filename with suffix
        extension = 'png' if self.format == 'png' else 'jpg'
        output_filename = f"{stem}_long_screenshot.{extension}"
        
        return directory / output_filename
    
    def _confirm_overwrite(self, path: Path) -> bool:
        """Confirm whether to overwrite existing file
        
        Args:
            path: Path to the existing file
            
        Returns:
            True if user confirms overwrite, False otherwise
        """
        response = input(f"File '{path}' already exists. Overwrite? (y/n): ").strip().lower()
        return response in ['y', 'yes']
