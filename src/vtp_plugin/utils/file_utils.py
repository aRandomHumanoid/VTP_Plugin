"""
File utility functions for the VTP plugin.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple
import logging

from ..core.exceptions import FileNotFoundError, InvalidGCodeError


def read_gcode_file(file_path: Path) -> List[str]:
    """Read G-code file and return lines.
    
    Args:
        file_path: Path to the G-code file
        
    Returns:
        List of lines from the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
        InvalidGCodeError: If file cannot be read
    """
    if not file_path.exists():
        raise FileNotFoundError(f"G-code file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        raise InvalidGCodeError(f"Failed to read G-code file: {e}")


def write_gcode_file(file_path: Path, lines: List[str]) -> None:
    """Write G-code lines to a file.
    
    Args:
        file_path: Path to the output file
        lines: List of G-code lines to write
        
    Raises:
        InvalidGCodeError: If file cannot be written
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    except Exception as e:
        raise InvalidGCodeError(f"Failed to write G-code file: {e}")


def extract_gcode_parameters(line: str) -> Tuple[Optional[float], Optional[float], Optional[float], 
                                                Optional[float], Optional[float]]:
    """Extract G-code parameters from a line.
    
    Args:
        line: G-code line to parse
        
    Returns:
        Tuple of (x, y, z, e, f) values, None if not present
    """
    def extract_value(pattern: str, prefix: str) -> Optional[float]:
        match = re.search(pattern, line)
        if match:
            try:
                return float(match.group().removeprefix(prefix))
            except ValueError:
                return None
        return None
    
    x = extract_value(r'X(?:\d*\.\d+|\d+(?:\.\d+)?)', 'X')
    y = extract_value(r'Y(?:\d*\.\d+|\d+(?:\.\d+)?)', 'Y')
    z = extract_value(r'Z(?:\d*\.\d+|\d+(?:\.\d+)?)', 'Z')
    e = extract_value(r'E(?:\d*\.\d+|\d+(?:\.\d+)?)', 'E')
    f = extract_value(r'F(?:\d*\.\d+|\d+(?:\.\d+)?)', 'F')
    
    return x, y, z, e, f


def extract_layer_info(lines: List[str]) -> Tuple[float, float]:
    """Extract layer height and width from G-code comments.
    
    Args:
        lines: List of G-code lines
        
    Returns:
        Tuple of (layer_height, layer_width)
    """
    layer_height = 0.0
    layer_width = 0.0
    
    for line in lines:
        if "; layer_height = " in line:
            match = re.search(r'\d+(?:\.\d+)?', line)
            if match:
                layer_height = float(match.group())
        elif ";layer_height = " in line:
            match = re.search(r'\d+(?:\.\d+)?', line)
            if match:
                layer_width = float(match.group())
    
    return layer_height, layer_width


def remove_nozzle_check_lines(lines: List[str], nozzle_dia: float) -> List[str]:
    """Remove nozzle check lines from G-code.
    
    Args:
        lines: List of G-code lines
        nozzle_dia: Nozzle diameter (unused but kept for compatibility)
        
    Returns:
        Filtered list of G-code lines
    """
    return [line for line in lines if "; nozzle check" not in line]


def setup_logging(log_file: Path, level: int = logging.INFO) -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        log_file: Path to the log file
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    return logging.getLogger(__name__)


def validate_file_path(file_path: Path, file_type: str = "file") -> None:
    """Validate that a file path exists and is accessible.
    
    Args:
        file_path: Path to validate
        file_type: Type of file for error messages
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"{file_type.capitalize()} not found: {file_path}")
    
    if not file_path.is_file():
        raise FileNotFoundError(f"Path is not a file: {file_path}")


def get_file_extension(file_path: Path) -> str:
    """Get the file extension of a path.
    
    Args:
        file_path: Path to get extension from
        
    Returns:
        File extension (lowercase, without dot)
    """
    return file_path.suffix.lower().lstrip('.')


def is_gcode_file(file_path: Path) -> bool:
    """Check if a file is a G-code file.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file has .gcode extension
    """
    return get_file_extension(file_path) == 'gcode' 