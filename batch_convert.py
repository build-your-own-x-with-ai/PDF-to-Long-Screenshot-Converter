#!/usr/bin/env python3
"""Batch convert PDFs to long screenshots"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple
import time

from src.validator import PDFValidator
from src.renderer import PDFRenderer
from src.compositor import ImageCompositor
from src.output import OutputGenerator
from src.config import ConversionConfig
from src.exceptions import PDFConverterError


def find_pdf_files(input_dir: Path, recursive: bool = True) -> List[Path]:
    """Find all PDF files in directory
    
    Args:
        input_dir: Directory to search
        recursive: If True, search subdirectories recursively
        
    Returns:
        List of PDF file paths
    """
    if recursive:
        pdf_files = list(input_dir.rglob("*.pdf"))
    else:
        pdf_files = list(input_dir.glob("*.pdf"))
    
    return sorted(pdf_files)


def generate_output_path(pdf_path: Path, input_dir: Path, output_dir: Path, format: str) -> Path:
    """Generate output path maintaining directory structure
    
    Args:
        pdf_path: Path to PDF file
        input_dir: Input directory root
        output_dir: Output directory root
        format: Output format (png/jpeg)
        
    Returns:
        Output file path
    """
    # Get relative path from input_dir
    try:
        relative_path = pdf_path.relative_to(input_dir)
    except ValueError:
        # If not relative, just use filename
        relative_path = pdf_path.name
    
    # Change extension
    ext = "jpg" if format.lower() == "jpeg" else format.lower()
    output_filename = relative_path.stem + "_long_screenshot." + ext
    
    # Maintain directory structure
    output_path = output_dir / relative_path.parent / output_filename
    
    return output_path


def convert_single_pdf(
    pdf_path: Path,
    output_path: Path,
    config: ConversionConfig,
    verbose: bool = True
) -> Tuple[bool, str]:
    """Convert a single PDF file
    
    Args:
        pdf_path: Path to PDF file
        output_path: Path for output image
        config: Conversion configuration
        verbose: Print progress messages
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Validate PDF
        is_valid, error_msg = PDFValidator.validate_file(pdf_path)
        if not is_valid:
            return False, f"Validation failed: {error_msg}"
        
        # Check file size
        is_valid, error_msg = PDFValidator.check_file_size(pdf_path)
        if not is_valid:
            return False, f"File too large: {error_msg}"
        
        # Get page count
        page_count = PDFValidator.get_page_count(pdf_path)
        
        if verbose:
            print(f"  Converting {page_count} page(s)...")
        
        # Render pages
        renderer = PDFRenderer(
            dpi=config.dpi,
            auto_crop=config.auto_crop,
            crop_margin=config.crop_margin
        )
        images = renderer.render_pages(pdf_path)
        
        # Compose images
        compositor = ImageCompositor(
            spacing=config.spacing,
            auto_width=config.auto_width
        )
        long_screenshot = compositor.compose(images)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save output
        output_generator = OutputGenerator(
            format=config.format,
            quality=config.quality
        )
        output_generator.save(
            long_screenshot,
            output_path,
            confirm_overwrite=False  # No confirmation in batch mode
        )
        
        return True, f"Saved to {output_path}"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


def batch_convert(
    input_dir: Path,
    output_dir: Path,
    config: ConversionConfig,
    recursive: bool = True,
    skip_existing: bool = False,
    verbose: bool = True
) -> Tuple[int, int, int]:
    """Batch convert PDFs in directory
    
    Args:
        input_dir: Input directory containing PDFs
        output_dir: Output directory for images
        config: Conversion configuration
        recursive: Search subdirectories recursively
        skip_existing: Skip files that already have output
        verbose: Print progress messages
        
    Returns:
        Tuple of (total, successful, failed)
    """
    # Find all PDF files
    pdf_files = find_pdf_files(input_dir, recursive=recursive)
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return 0, 0, 0
    
    print(f"Found {len(pdf_files)} PDF file(s) in {input_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    successful = 0
    failed = 0
    skipped = 0
    
    start_time = time.time()
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        # Generate output path
        output_path = generate_output_path(pdf_path, input_dir, output_dir, config.format)
        
        # Check if output already exists
        if skip_existing and output_path.exists():
            if verbose:
                print(f"[{idx}/{len(pdf_files)}] Skipping (exists): {pdf_path.name}")
            skipped += 1
            continue
        
        if verbose:
            print(f"[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
        
        # Convert PDF
        success, message = convert_single_pdf(pdf_path, output_path, config, verbose=verbose)
        
        if success:
            successful += 1
            if verbose:
                print(f"  ✓ {message}")
        else:
            failed += 1
            if verbose:
                print(f"  ✗ {message}")
        
        if verbose:
            print()
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("=" * 60)
    print("Batch Conversion Summary")
    print("=" * 60)
    print(f"Total files:      {len(pdf_files)}")
    print(f"Successful:       {successful}")
    print(f"Failed:           {failed}")
    if skip_existing:
        print(f"Skipped:          {skipped}")
    print(f"Processing time:  {elapsed_time:.2f} seconds")
    print("=" * 60)
    
    return len(pdf_files), successful, failed


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Batch convert PDFs to long screenshots',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Convert pdfs/ to images/
  %(prog)s -i my_pdfs -o my_images     # Custom directories
  %(prog)s --no-recursive               # Only top-level files
  %(prog)s --skip-existing              # Skip already converted files
  %(prog)s --dpi 200 -f jpeg            # Custom conversion settings
        """
    )
    
    # Directory arguments
    parser.add_argument(
        '-i', '--input-dir',
        type=str,
        default='pdfs',
        help='Input directory containing PDF files (default: pdfs)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='images',
        help='Output directory for images (default: images)'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories recursively'
    )
    
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip PDFs that already have output images'
    )
    
    # Conversion settings
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
        help='JPEG quality (1-100, default: 85)'
    )
    
    parser.add_argument(
        '-s', '--spacing',
        type=int,
        default=0,
        help='Spacing between pages in pixels (default: 0)'
    )
    
    parser.add_argument(
        '--fixed-width',
        action='store_true',
        help='Use fixed width for all pages'
    )
    
    parser.add_argument(
        '--no-crop',
        action='store_true',
        help='Disable automatic cropping of whitespace'
    )
    
    parser.add_argument(
        '--crop-margin',
        type=int,
        default=10,
        help='Margin to keep when cropping (pixels, default: 10)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not 72 <= args.dpi <= 300:
        print(f"Error: DPI must be between 72 and 300, got {args.dpi}")
        return 1
    
    if not 1 <= args.quality <= 100:
        print(f"Error: Quality must be between 1 and 100, got {args.quality}")
        return 1
    
    # Setup paths
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        return 1
    
    if not input_dir.is_dir():
        print(f"Error: Input path is not a directory: {input_dir}")
        return 1
    
    # Create configuration
    config = ConversionConfig(
        input_path=input_dir,  # Placeholder
        output_path=None,
        dpi=args.dpi,
        format=args.format,
        quality=args.quality,
        spacing=args.spacing,
        confirm_overwrite=False,
        auto_width=not args.fixed_width,
        auto_crop=not args.no_crop,
        crop_margin=args.crop_margin
    )
    
    # Run batch conversion
    try:
        total, successful, failed = batch_convert(
            input_dir=input_dir,
            output_dir=output_dir,
            config=config,
            recursive=not args.no_recursive,
            skip_existing=args.skip_existing,
            verbose=not args.quiet
        )
        
        # Return exit code based on results
        if failed > 0:
            return 2  # Some failures
        elif successful == 0:
            return 1  # No files processed
        else:
            return 0  # All successful
            
    except KeyboardInterrupt:
        print("\n\nBatch conversion cancelled by user.")
        return 130
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return 255


if __name__ == '__main__':
    sys.exit(main())
