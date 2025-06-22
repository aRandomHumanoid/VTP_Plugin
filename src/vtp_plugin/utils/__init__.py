"""
Utility functions for the VTP plugin.
"""

from .math_utils import (
    calculate_distance,
    calculate_midpoint,
    split_line_segment,
    calculate_circle_area,
    evaluate_equations,
    validate_positive,
    validate_range
)
from .file_utils import (
    read_gcode_file,
    write_gcode_file,
    extract_gcode_parameters,
    extract_layer_info,
    remove_nozzle_check_lines,
    setup_logging,
    validate_file_path,
    get_file_extension,
    is_gcode_file
)

__all__ = [
    # Math utilities
    'calculate_distance',
    'calculate_midpoint',
    'split_line_segment',
    'calculate_circle_area',
    'evaluate_equations',
    'validate_positive',
    'validate_range',
    
    # File utilities
    'read_gcode_file',
    'write_gcode_file',
    'extract_gcode_parameters',
    'extract_layer_info',
    'remove_nozzle_check_lines',
    'setup_logging',
    'validate_file_path',
    'get_file_extension',
    'is_gcode_file'
] 