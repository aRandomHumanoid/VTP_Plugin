"""
Mathematical utilities for the VTP plugin.
"""

import math
from typing import Tuple, List
import numpy as np
from sympy import symbols, sympify


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two 2D points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Distance between the points
    """
    return math.dist(point1, point2)


def calculate_midpoint(point1: Tuple[float, float], point2: Tuple[float, float]) -> Tuple[float, float]:
    """Calculate the midpoint between two 2D points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Midpoint coordinates
    """
    return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)


def split_line_segment(x_start: float, x_end: float, y_start: float, y_end: float, 
                      increment_length: float) -> List[Tuple[float, float]]:
    """Split a line segment into smaller segments of specified length.
    
    Args:
        x_start: Starting X coordinate
        x_end: Ending X coordinate
        y_start: Starting Y coordinate
        y_end: Ending Y coordinate
        increment_length: Length of each segment
        
    Returns:
        List of points along the line segment
    """
    total_length = calculate_distance((x_start, y_start), (x_end, y_end))
    num_segments = math.ceil(total_length / increment_length)
    
    if num_segments <= 1:
        return [(x_end, y_end)]
    
    delta_x = (x_end - x_start) / num_segments
    delta_y = (y_end - y_start) / num_segments
    
    points = []
    for i in range(1, num_segments + 1):
        x = x_start + delta_x * i
        y = y_start + delta_y * i
        points.append((x, y))
    
    return points


def calculate_circle_area(diameter: float) -> float:
    """Calculate the area of a circle given its diameter.
    
    Args:
        diameter: Circle diameter
        
    Returns:
        Circle area
    """
    radius = diameter / 2
    return math.pi * radius ** 2


def evaluate_equations(V_star_func: str, H_star_func: str, x: float, y: float, z: float) -> Tuple[float, float]:
    """Evaluate V* and H* equations at a given point.
    
    Args:
        V_star_func: V* equation as string
        H_star_func: H* equation as string
        x: X coordinate
        y: Y coordinate
        z: Z coordinate
        
    Returns:
        Tuple of (V_star_value, H_star_value)
        
    Raises:
        ValueError: If equation evaluation fails
    """
    try:
        # Create symbols for variables
        x_sym, y_sym, z_sym = symbols('x y z')
        
        # Parse and evaluate V* function
        V_star_expr = sympify(V_star_func)
        V_star_value = float(V_star_expr.evalf(subs={x_sym: x, y_sym: y, z_sym: z}))
        
        # Parse and evaluate H* function
        H_star_expr = sympify(H_star_func)
        H_star_value = float(H_star_expr.evalf(subs={x_sym: x, y_sym: y, z_sym: z}))
        
        return V_star_value, H_star_value
        
    except Exception as e:
        raise ValueError(f"Failed to evaluate equations at point ({x}, {y}, {z}): {e}")


def validate_positive(value: float, name: str) -> None:
    """Validate that a value is positive.
    
    Args:
        value: Value to validate
        name: Name of the parameter for error messages
        
    Raises:
        ValueError: If value is not positive
    """
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


def validate_range(value: float, min_val: float, max_val: float, name: str) -> None:
    """Validate that a value is within a specified range.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Name of the parameter for error messages
        
    Raises:
        ValueError: If value is outside the range
    """
    if not (min_val <= value <= max_val):
        raise ValueError(f"{name} must be between {min_val} and {max_val}, got {value}") 