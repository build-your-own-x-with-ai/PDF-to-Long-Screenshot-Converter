"""Custom exceptions for PDF to Long Screenshot Converter"""


class PDFConverterError(Exception):
    """Base exception class for PDF converter errors"""
    pass


class FileValidationError(PDFConverterError):
    """Exception raised for file validation errors"""
    pass


class RenderingError(PDFConverterError):
    """Exception raised during PDF rendering"""
    pass


class CompositionError(PDFConverterError):
    """Exception raised during image composition"""
    pass


class OutputError(PDFConverterError):
    """Exception raised during output generation"""
    pass
