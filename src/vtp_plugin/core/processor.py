"""
Main VTP processor for G-code post-processing.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

from ..core.config import VTPConfig
from ..core.exceptions import ProcessingError, FileNotFoundError
from ..models.gcode import MoveGcodeLine
from ..models.mesh import MeshManager
from ..models.printing_stats import PrintingStats
from ..utils.file_utils import (
    read_gcode_file, write_gcode_file, extract_layer_info,
    remove_nozzle_check_lines, setup_logging
)
from ..utils.math_utils import split_line_segment


@dataclass
class ProcessingResult:
    """Result of G-code processing."""
    success: bool
    output_lines: List[str]
    error_message: Optional[str] = None
    processed_lines: int = 0
    modified_lines: int = 0


class VTPProcessor:
    """Main processor for Variable Thickness Printing G-code modification."""
    
    def __init__(self, config: VTPConfig):
        """Initialize the VTP processor.
        
        Args:
            config: Configuration for the processor
        """
        self.config = config
        self.logger = setup_logging(config.log_file)
        self.mesh_manager: Optional[MeshManager] = None
        self.printing_stats: Optional[PrintingStats] = None
        
        # Processing state
        self.prev_x = 0.0
        self.prev_y = 0.0
        self.current_z = 0.0
    
    def initialize(self) -> None:
        """Initialize mesh manager and printing stats.
        
        Raises:
            FileNotFoundError: If required files are missing
            ProcessingError: If initialization fails
        """
        try:
            self.logger.info("Initializing VTP processor")
            
            # Initialize mesh manager
            self.mesh_manager = MeshManager(self.config.mesh_file)
            self.logger.info(f"Loaded {self.mesh_manager.get_mesh_count()} meshes")
            
            # Read G-code to extract layer information
            gcode_lines = read_gcode_file(self.config.input_gcode)
            layer_height, layer_width = extract_layer_info(gcode_lines)
            
            # Update printing parameters with layer info
            self.config.printing.layer_height = layer_height
            self.config.printing.layer_width = layer_width
            
            # Initialize printing stats
            self.printing_stats = PrintingStats(
                self.config.printing, 
                self.config.equation_file
            )
            self.logger.info(f"Loaded {self.printing_stats.get_equation_count()} equations")
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise ProcessingError(f"Failed to initialize processor: {e}")
    
    def process_file(self) -> ProcessingResult:
        """Process the input G-code file.
        
        Returns:
            ProcessingResult with success status and output lines
        """
        try:
            self.logger.info("Starting G-code processing")
            
            # Read input file
            input_lines = read_gcode_file(self.config.input_gcode)
            self.logger.info(f"Read {len(input_lines)} lines from input file")
            
            # Remove nozzle check lines if configured
            if self.config.remove_nozzle_check:
                input_lines = remove_nozzle_check_lines(input_lines, self.config.printing.nozzle_dia)
                self.logger.info("Removed nozzle check lines")
            
            # Process G-code lines
            output_lines = self._process_gcode_lines(input_lines)
            
            # Write output file
            write_gcode_file(self.config.output_gcode, output_lines)
            
            self.logger.info("G-code processing completed successfully")
            return ProcessingResult(
                success=True,
                output_lines=output_lines,
                processed_lines=len(input_lines),
                modified_lines=len(output_lines)
            )
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return ProcessingResult(
                success=False,
                output_lines=[],
                error_message=str(e)
            )
    
    def _process_gcode_lines(self, lines: List[str]) -> List[str]:
        """Process G-code lines and apply VTP modifications.
        
        Args:
            lines: Input G-code lines
            
        Returns:
            Modified G-code lines
        """
        result_lines = []
        
        for i, line in enumerate(lines):
            try:
                params = MoveGcodeLine.from_line(line)
                
                # Handle different line types
                if "; support" in line:
                    new_line = self._handle_support_line(params)
                    result_lines.append(new_line)
                    continue
                
                if ";Z:" in line:
                    self._update_current_z(line)
                    result_lines.append(line)
                    continue
                
                if self._is_travel_move_with_z(line) and "Z" in line:
                    new_lines = self._handle_travel_move_with_z(lines, i, params)
                    result_lines.extend(new_lines)
                    continue
                
                if " ; travel" in line or " ; move" in line:
                    self._update_previous_position(params)
                    result_lines.append(line)
                    continue
                
                if " ; infill" in line:
                    new_lines = self._handle_infill_line(params)
                    result_lines.extend(new_lines)
                    self._update_previous_position(params)
                    continue
                
                if "G1 Z" in line:
                    self.logger.warning(f"Skipping unexpected Z move: {line.strip()}")
                    continue
                
                # Default: keep line unchanged
                result_lines.append(line)
                
            except Exception as e:
                self.logger.warning(f"Error processing line {i+1}: {e}")
                result_lines.append(line)  # Keep original line on error
        
        return result_lines
    
    def _handle_support_line(self, params: MoveGcodeLine) -> str:
        """Handle support material lines.
        
        Args:
            params: Parsed G-code parameters
            
        Returns:
            Modified G-code line
        """
        new_line = MoveGcodeLine(
            x=params.x, y=params.y, z=self.current_z, 
            e=params.e, f=params.f
        )
        return new_line.to_gcode("new support")
    
    def _update_current_z(self, line: str) -> None:
        """Update current Z position from G-code line.
        
        Args:
            line: G-code line containing Z information
        """
        import re
        z_match = re.search(r'Z:(\d+(?:\.\d+)?)', line)
        if z_match:
            self.current_z = float(z_match.group(1))
    
    def _is_travel_move_with_z(self, line: str) -> bool:
        """Check if line is a travel move with Z movement.
        
        Args:
            line: G-code line to check
            
        Returns:
            True if it's a travel move with Z
        """
        return (" ; travel" in line and "Z" in line) or (" ; move" in line and "Z" in line)
    
    def _handle_travel_move_with_z(self, lines: List[str], current_index: int, params: MoveGcodeLine) -> List[str]:
        """Handle travel moves that include Z movement.
        
        Args:
            lines: All G-code lines
            current_index: Current line index
            params: Parsed G-code parameters
            
        Returns:
            List of modified G-code lines
        """
        # Find next infill line
        next_infill_index = self._find_next_infill_line(lines, current_index)
        if next_infill_index >= len(lines):
            return [lines[current_index]]  # Keep original line
        
        next_line = MoveGcodeLine.from_line(lines[next_infill_index])
        new_x, new_y = next_line.x, next_line.y
        
        if new_x is None or new_y is None:
            return [lines[current_index]]
        
        # Classify point and calculate new Z
        mesh_number = self.mesh_manager.classify_point([new_x, new_y, self.current_z])
        new_z = self.printing_stats.evaluate_z_at_point(new_x, new_y, self.current_z, mesh_number)
        
        # Create new Z move
        new_line = MoveGcodeLine(z=new_z, f=self.config.travel_speed)
        return [new_line.to_gcode("NEW Z MOVE")]
    
    def _find_next_infill_line(self, lines: List[str], start_index: int) -> int:
        """Find the next infill line after the given index.
        
        Args:
            lines: All G-code lines
            start_index: Starting index to search from
            
        Returns:
            Index of next infill line, or len(lines) if not found
        """
        for i in range(start_index + 1, len(lines)):
            if " ; infill" in lines[i]:
                return i
        return len(lines)
    
    def _update_previous_position(self, params: MoveGcodeLine) -> None:
        """Update previous X,Y position.
        
        Args:
            params: Parsed G-code parameters
        """
        if params.x is not None:
            self.prev_x = params.x
        if params.y is not None:
            self.prev_y = params.y
    
    def _handle_infill_line(self, params: MoveGcodeLine) -> List[str]:
        """Handle infill lines by splitting into segments.
        
        Args:
            params: Parsed G-code parameters
            
        Returns:
            List of modified G-code lines
        """
        if params.x is None or params.y is None:
            return [params.original_line or ""]
        
        # Split line into segments
        points = split_line_segment(
            self.prev_x, params.x, self.prev_y, params.y,
            self.config.printing.eval_increment
        )
        
        result_lines = []
        x_prev, y_prev = self.prev_x, self.prev_y
        
        for x_current, y_current in points:
            # Classify point and calculate new parameters
            mesh_number = self.mesh_manager.classify_point([x_current, y_current, self.current_z])
            z_new, e_new, f_new = self.printing_stats.evaluate_vars(
                x_prev, x_current, y_prev, y_current, self.current_z, mesh_number
            )
            
            # Create new G-code line
            new_line = MoveGcodeLine(x_current, y_current, z_new, e_new, f_new)
            result_lines.append(new_line.to_gcode("created lines"))
            
            x_prev, y_prev = x_current, y_current
        
        return result_lines
    
    def __repr__(self) -> str:
        """String representation of the processor."""
        return f"VTPProcessor(meshes={self.mesh_manager.get_mesh_count() if self.mesh_manager else 0}, equations={self.printing_stats.get_equation_count() if self.printing_stats else 0})" 