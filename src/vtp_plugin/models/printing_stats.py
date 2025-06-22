"""
Printing statistics and calculations for the VTP plugin.
"""

import math
import re
from typing import List, Tuple, Optional
from pathlib import Path

import numpy as np
from sympy import symbols, sympify

from ..core.exceptions import FileNotFoundError, ConfigurationError
from ..utils.math_utils import (
    calculate_distance, calculate_midpoint, calculate_circle_area,
    evaluate_equations, validate_positive
)


class PrintingStats:
    """Manages printing statistics and calculations for variable thickness printing."""
    
    PI = math.pi  # Use proper mathematical constant
    
    def __init__(self, parameters, equation_path: Path):
        """Initialize printing statistics.
        
        Args:
            parameters: PrintingParameters instance
            equation_path: Path to the equation file
            
        Raises:
            ConfigurationError: If parameters are invalid
            FileNotFoundError: If equation file doesn't exist
        """
        self.params = parameters
        self._validate_parameters()
        self._load_equations(equation_path)
        self._calculate_areas()
    
    def _validate_parameters(self) -> None:
        """Validate printing parameters.
        
        Raises:
            ConfigurationError: If parameters are invalid
        """
        try:
            validate_positive(self.params.alpha, "alpha")
            validate_positive(self.params.nozzle_dia, "nozzle_dia")
            validate_positive(self.params.fil_dia, "fil_dia")
            validate_positive(self.params.e_dot, "e_dot")
            validate_positive(self.params.layer_height, "layer_height")
        except ValueError as e:
            raise ConfigurationError(str(e))
    
    def _calculate_areas(self) -> None:
        """Calculate filament and thread areas once during initialization."""
        self.fil_area = calculate_circle_area(self.params.fil_dia)
        self.thread_area = calculate_circle_area(self.params.alpha * self.params.nozzle_dia)
    
    def _load_equations(self, path: Path) -> None:
        """Load and validate equation files.
        
        Args:
            path: Path to the equation file
            
        Raises:
            FileNotFoundError: If equation file doesn't exist
            ConfigurationError: If equation file is invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"Equation file not found: {path}")
        
        self.V_star_functions = []
        self.H_star_functions = []
        
        try:
            with open(path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue  # Skip empty lines and comments
                    
                    try:
                        parts = line.split(";")
                        if len(parts) != 2:
                            raise ValueError(f"Invalid format at line {line_num}")
                        
                        self.V_star_functions.append(sympify(parts[0].strip()))
                        self.H_star_functions.append(sympify(parts[1].strip()))
                        
                    except Exception as e:
                        raise ValueError(f"Error parsing line {line_num}: {e}")
            
            if not self.V_star_functions or not self.H_star_functions:
                raise ValueError("No valid equations found in file")
                
        except Exception as e:
            raise ConfigurationError(f"Failed to load equation file: {e}")
    
    def evaluate_vars(self, x_start: float, x_end: float, y_start: float, 
                     y_end: float, z_end: float, mesh_number: int) -> Tuple[float, float, float]:
        """Calculate new Z, E, and F values for a line segment.
        
        Args:
            x_start: Starting X coordinate
            x_end: Ending X coordinate
            y_start: Starting Y coordinate
            y_end: Ending Y coordinate
            z_end: Current Z coordinate
            mesh_number: Mesh ID for equation selection
            
        Returns:
            Tuple of (z_new, e_new, f_new)
            
        Raises:
            IndexError: If mesh_number is out of range
            ValueError: If calculation fails
        """
        try:
            length = calculate_distance((x_start, y_start), (x_end, y_end))
            x_mid, y_mid = calculate_midpoint((x_start, y_start), (x_end, y_end))
            
            V_star, H_star = self._evaluate_functions(x_mid, y_mid, z_end, mesh_number)
            
            H_new = H_star * self.params.alpha * self.params.nozzle_dia
            f_new = self.params.e_dot * V_star * self.fil_area / self.thread_area
            e_new = length * self.params.e_dot / f_new
            z_new = z_end + H_new - self.params.layer_height + self.params.z_offset
            
            return z_new, e_new, f_new
            
        except Exception as e:
            raise ValueError(f"Failed to evaluate variables: {e}")
    
    def evaluate_z_at_point(self, x: float, y: float, z: float, mesh_number: int) -> float:
        """Calculate new Z value at a specific point.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Current Z coordinate
            mesh_number: Mesh ID for equation selection
            
        Returns:
            New Z coordinate
            
        Raises:
            IndexError: If mesh_number is out of range
            ValueError: If calculation fails
        """
        try:
            _, H_star = self._evaluate_functions(x, y, z, mesh_number)
            H_new = H_star * self.params.alpha * self.params.nozzle_dia
            z_new = z + H_new - self.params.layer_height + self.params.z_offset
            return z_new
            
        except Exception as e:
            raise ValueError(f"Failed to evaluate Z at point ({x}, {y}, {z}): {e}")
    
    def _evaluate_functions(self, x: float, y: float, z: float, mesh_number: int) -> Tuple[float, float]:
        """Evaluate V* and H* functions at a given point.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            mesh_number: Mesh ID for equation selection
            
        Returns:
            Tuple of (V_star_value, H_star_value)
            
        Raises:
            IndexError: If mesh_number is out of range
            ValueError: If evaluation fails
        """
        if mesh_number < 0 or mesh_number >= len(self.V_star_functions):
            raise IndexError(f"Mesh number {mesh_number} out of range (0-{len(self.V_star_functions)-1})")
        
        try:
            # Create symbols for variables
            x_sym, y_sym, z_sym = symbols('x y z')
            
            # Evaluate V* function
            V_star_value = float(self.V_star_functions[mesh_number].evalf(subs={x_sym: x, y_sym: y, z_sym: z}))
            
            # Evaluate H* function
            H_star_value = float(self.H_star_functions[mesh_number].evalf(subs={x_sym: x, y_sym: y, z_sym: z}))
            
            return V_star_value, H_star_value
            
        except Exception as e:
            raise ValueError(f"Failed to evaluate functions at point ({x}, {y}, {z}): {e}")
    
    def debug_vars(self, x_start: float, x_end: float, y_start: float, 
                  y_end: float, z_end: float, mesh_number: int) -> Tuple[float, float, float, float, float, float, float]:
        """Debug version of evaluate_vars that returns all intermediate values.
        
        Args:
            x_start: Starting X coordinate
            x_end: Ending X coordinate
            y_start: Starting Y coordinate
            y_end: Ending Y coordinate
            z_end: Current Z coordinate
            mesh_number: Mesh ID for equation selection
            
        Returns:
            Tuple of (V_star, H_star, e_dot, H_new, f_new, e_new, z_new)
        """
        length = calculate_distance((x_start, y_start), (x_end, y_end))
        x_mid, y_mid = calculate_midpoint((x_start, y_start), (x_end, y_end))
        
        V_star, H_star = self._evaluate_functions(x_mid, y_mid, z_end, mesh_number)
        
        H_new = H_star * self.params.alpha * self.params.nozzle_dia
        f_new = self.params.e_dot * V_star * self.fil_area / self.thread_area
        e_new = length * self.params.e_dot / f_new
        z_new = z_end + H_new - self.params.layer_height + self.params.z_offset
        
        return V_star, H_star, self.params.e_dot, H_new, f_new, e_new, z_new
    
    def get_equation_count(self) -> int:
        """Get the number of loaded equations.
        
        Returns:
            Number of equation pairs
        """
        return len(self.V_star_functions)
    
    def __repr__(self) -> str:
        """String representation of the printing stats."""
        return (f"PrintingStats(equations={len(self.V_star_functions)}, "
                f"alpha={self.params.alpha}, nozzle_dia={self.params.nozzle_dia})") 