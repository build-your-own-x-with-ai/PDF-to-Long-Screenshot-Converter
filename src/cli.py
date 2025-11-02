"""Command-line interface for PDF to long screenshot converter"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .validator import PDFValidator
from .renderer import PDFRenderer
from .compositor import ImageCompositor
from .output import OutputGenerator
from .progress import ProgressReporter
from .config import ConversionConfig
from .exceptions import (
    PDFConverterError,
    FileValidationError,
    RenderingError,
    CompositionError,
    OutputError
)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Convert PDF files to long screenshots',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.pdf
  %(prog)s input.pdf -o output.png
  %(prog)s input.pdf --dpi 200 --spacing 10
  %(prog)s input.pdf -f jpeg -q 90
        """
    )
    
    # Required arguments
    parser.add_argument(
        'input',
        type=str,
        help='Path to input PDF file'
    )
    
    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Path to output image file (default: <input>_long_screenshot.<format>)'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        help='Resolution in DPI (72-300, default: 150)'
    )
    
    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['png', 'jpeg', 'jpg'],
        default='png',
        help='Output image format (default: png)'
    )
    
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        help='JPEG quality (1-100, default: 85, only for JPEG format)'
    )
    
    parser.add_argument(
        '-s', '--spacing',
        type=int,
        default=0,
        help='Spacing between pages in pixels (default: 0)'
    )
    
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation when overwriting existing files'
    )
    
    parser.add_argument(
        '--fixed-width',
        action='store_true',
        help='Use fixed width (max width) for all pages instead of auto-adjusting (may create side margins)'
    )
    
    parser.add_argument(
        '--no-crop',
        action='store_true',
        help='Disable automatic cropping of whitespace from page edges'
    )
    
    parser.add_argument(
        '--crop-margin',
        type=int,
        default=10,
        help='Margin to keep around content when cropping (pixels, default: 10)'
    )
    
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> bool:
    """Validate parsed arguments
    
    Args:
        args: Parsed arguments
        
    Returns:
        True if arguments are valid
        
    Raises:
        ValueError: If arguments are invalid
    """
    # Validate DPI range
    if not 72 <= args.dpi <= 300:
        raise ValueError(f"DPI must be between 72 and 300, got {args.dpi}")
    
    # Validate quality range
    if not 1 <= args.quality <= 100:
        raise ValueError(f"Quality must be between 1 and 100, got {args.quality}")
    
    # Validate spacing
    if args.spacing < 0:
        raise ValueError(f"Spacing must be non-negative, got {args.spacing}")
    
    # Validate crop margin
    if args.crop_margin < 0:
        raise ValueError(f"Crop margin must be non-negative, got {args.crop_margin}")
    
    return True


def main() -> int:
    """Main entry point for the CLI
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse and validate arguments
        args = parse_arguments()
        validate_arguments(args)
        
        # Create configuration
        input_path = Path(args.input)
        output_path = Path(args.output) if args.output else None
        
        config = ConversionConfig(
            input_path=input_path,
            output_path=output_path,
            dpi=args.dpi,
            format=args.format,
            quality=args.quality,
            spacing=args.spacing,
            confirm_overwrite=not args.no_confirm,
            auto_width=not args.fixed_width,
            auto_crop=not args.no_crop,
            crop_margin=args.crop_margin
        )
        
        # Validate configuration
        is_valid, error_msg = config.validate()
        if not is_valid:
            print(f"Configuration error: {error_msg}")
            return 1
        
        # Validate PDF file
        is_valid, error_msg = PDFValidator.validate_file(input_path)
        if not is_valid:
            print(f"File validation error: {error_msg}")
            return 1
        
        # Check file size
        is_valid, error_msg = PDFValidator.check_file_size(input_path)
        if not is_valid:
            print(f"File size error: {error_msg}")
            return 1
        
        # Get page count
        try:
            page_count = PDFValidator.get_page_count(input_path)
        except FileValidationError as e:
            print(f"Error reading PDF: {e}")
            return 1
        
        # Initialize progress reporter
        progress = ProgressReporter(page_count)
        progress.start()
        
        # Render PDF pages
        try:
            renderer = PDFRenderer(
                dpi=config.dpi,
                auto_crop=config.auto_crop,
                crop_margin=config.crop_margin
            )
            images = renderer.render_pages(
                input_path,
                progress_callback=lambda current, total: progress.update(current, "rendering")
            )
        except RenderingError as e:
            progress.error(str(e))
            return 2
        
        # Compose images
        try:
            print("Composing images...")
            compositor = ImageCompositor(spacing=config.spacing, auto_width=config.auto_width)
            long_screenshot = compositor.compose(images)
        except CompositionError as e:
            progress.error(str(e))
            return 3
        
        # Save output
        try:
            output_generator = OutputGenerator(
                format=config.format,
                quality=config.quality
            )
            
            final_output_path = config.get_output_path()
            
            print(f"Saving to {final_output_path}...")
            saved = output_generator.save(
                long_screenshot,
                final_output_path,
                confirm_overwrite=config.confirm_overwrite
            )
            
            if not saved:
                print("Save cancelled by user.")
                return 0
            
            progress.complete(final_output_path)
            return 0
            
        except OutputError as e:
            progress.error(str(e))
            return 4
    
    except ValueError as e:
        print(f"Invalid argument: {e}")
        return 1
    
    except KeyboardInterrupt:
        print("\n\nConversion cancelled by user.")
        return 130
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 255


if __name__ == '__main__':
    sys.exit(main())
