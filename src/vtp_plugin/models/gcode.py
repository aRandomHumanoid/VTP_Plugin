"""
G-code line parsing and manipulation.
"""

import re
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GCodeParameters:
    """G-code parameters with optional values."""
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    e: Optional[float] = None
    f: Optional[float] = None


class MoveGcodeLine:
    """Represents a G-code move command line."""
    
    # Compile regex patterns once for better performance
    COORDINATE_PATTERNS = {
        'x': re.compile(r'X(-?\d*\.?\d+)'),
        'y': re.compile(r'Y(-?\d*\.?\d+)'),
        'z': re.compile(r'Z(-?\d*\.?\d+)'),
        'e': re.compile(r'E(-?\d*\.?\d+)'),
        'f': re.compile(r'F(-?\d*\.?\d+)')
    }
    
    def __init__(self, **kwargs):
        """Initialize G-code line with parameters."""
        self.x = kwargs.get('x')
        self.y = kwargs.get('y')
        self.z = kwargs.get('z')
        self.e = kwargs.get('e')
        self.f = kwargs.get('f')
        self.original_line = kwargs.get('line')
    
    @classmethod
    def from_line(cls, line: str) -> 'MoveGcodeLine':
        """Parse G-code line and extract parameters.
        
        Args:
            line: The G-code line to parse
            
        Returns:
            MoveGcodeLine instance with parsed parameters
            
        Raises:
            ValueError: If line is invalid or coordinates are malformed
        """
        if not line or not line.strip():
            raise ValueError("Empty or invalid G-code line")
        
        params = {}
        for coord, pattern in cls.COORDINATE_PATTERNS.items():
            match = pattern.search(line)
            if match:
                try:
                    params[coord] = float(match.group(1))
                except ValueError:
                    raise ValueError(f"Invalid {coord.upper()} coordinate: {match.group(1)}")
        
        return cls(**params, line=line)
    
    def to_gcode(self, comment: str = "modified line") -> str:
        """Convert parameters back to G-code format.
        
        Args:
            comment: Optional comment to append to the line
            
        Returns:
            Formatted G-code string
        """
        parts = ["G1"]
        
        for coord in ['x', 'y', 'z', 'e', 'f']:
            value = getattr(self, coord)
            if value is not None:
                parts.append(f"{coord.upper()}{value:.3f}")
        
        if comment:
            parts.append(f"; {comment}")
        
        return " ".join(parts) + "\n"
    
    def get_stats(self) -> str:
        """Get human-readable parameter summary.
        
        Returns:
            String representation of all parameters
        """
        return f"X: {self.x}, Y: {self.y}, Z: {self.z}, E: {self.e}, F: {self.f}"
    
    def __repr__(self) -> str:
        """String representation of the G-code line."""
        return f"MoveGcodeLine(x={self.x}, y={self.y}, z={self.z}, e={self.e}, f={self.f})"
    
    def __eq__(self, other) -> bool:
        """Compare two G-code lines for equality."""
        if not isinstance(other, MoveGcodeLine):
            return False
        return (self.x == other.x and self.y == other.y and 
                self.z == other.z and self.e == other.e and self.f == other.f) 