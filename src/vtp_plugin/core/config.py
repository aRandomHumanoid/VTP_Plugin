"""
Configuration management for the VTP plugin.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PrintingParameters:
    """Parameters for the printing process."""
    alpha: float = 1.0
    nozzle_dia: float = 0.4
    fil_dia: float = 1.75
    eval_increment: float = 1.0
    e_dot: float = 250.0
    layer_height: float = 0.0
    layer_width: float = 0.0
    z_offset: float = -0.5


@dataclass
class VTPConfig:
    """Main configuration for the VTP plugin."""
    # Printing parameters
    printing: PrintingParameters
    
    # File paths
    equation_file: Path = Path("equations.txt")
    mesh_file: Path = Path("test_mesh.3mf")
    input_gcode: Path = Path("test_mesh.gcode")
    output_gcode: Path = Path("outputtest.gcode")
    log_file: Path = Path("vtp_plugin.txt")
    
    # Processing options
    remove_nozzle_check: bool = True
    travel_speed: float = 15000.0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.printing.alpha <= 0:
            raise ValueError("Alpha must be positive")
        if self.printing.nozzle_dia <= 0:
            raise ValueError("Nozzle diameter must be positive")
        if self.printing.fil_dia <= 0:
            raise ValueError("Filament diameter must be positive")
        if self.printing.e_dot <= 0:
            raise ValueError("E_dot must be positive")
    
    @classmethod
    def from_args(cls, args) -> 'VTPConfig':
        """Create configuration from command line arguments."""
        printing = PrintingParameters(
            alpha=args.alpha,
            nozzle_dia=args.nozzle_dia,
            fil_dia=args.fil_dia,
            eval_increment=args.eval_increment,
            e_dot=args.e_dot
        )
        return cls(printing=printing) 