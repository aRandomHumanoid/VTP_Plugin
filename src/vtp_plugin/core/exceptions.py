"""
Custom exceptions for the VTP plugin.
"""


class VTPError(Exception):
    """Base exception for VTP plugin errors."""
    pass


class FileNotFoundError(VTPError):
    """Raised when required files are missing."""
    pass


class InvalidGCodeError(VTPError):
    """Raised when G-code parsing fails."""
    pass


class InvalidMeshError(VTPError):
    """Raised when mesh processing fails."""
    pass


class ConfigurationError(VTPError):
    """Raised when configuration is invalid."""
    pass


class ProcessingError(VTPError):
    """Raised when G-code processing fails."""
    pass 