"""Configuration management for PDF to Long Screenshot Converter"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ConversionConfig:
    """Configuration for PDF conversion"""
    input_path: Path
    output_path: Optional[Path] = None
    dpi: int = 150
    format: str = "png"
    quality: int = 85
    spacing: int = 0
    confirm_overwrite: bool = True
    auto_width: bool = True
    auto_crop: bool = True
    crop_margin: int = 10
    
    def validate(self) -> tuple[bool, str]:
        """Validate configuration parameters
        
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Validate DPI range
        if not 72 <= self.dpi <= 300:
            return False, f"DPI must be between 72 and 300, got {self.dpi}"
        
        # Validate format
        if self.format.lower() not in ["png", "jpeg", "jpg"]:
            return False, f"Format must be 'png' or 'jpeg', got {self.format}"
        
        # Validate quality for JPEG
        if self.format.lower() in ["jpeg", "jpg"]:
            if not 1 <= self.quality <= 100:
                return False, f"JPEG quality must be between 1 and 100, got {self.quality}"
        
        # Validate spacing
        if self.spacing < 0:
            return False, f"Spacing must be non-negative, got {self.spacing}"
        
        return True, ""
    
    def get_output_path(self) -> Path:
        """Get the final output path
        
        If output_path is not specified, generates a default path
        in the same directory as the input file with suffix '_long_screenshot'
        
        Returns:
            Path: The output file path
        """
        if self.output_path:
            return self.output_path
        
        # Generate default output path
        input_stem = self.input_path.stem
        input_dir = self.input_path.parent
        
        # Normalize format
        ext = "jpg" if self.format.lower() == "jpeg" else self.format.lower()
        
        return input_dir / f"{input_stem}_long_screenshot.{ext}"
