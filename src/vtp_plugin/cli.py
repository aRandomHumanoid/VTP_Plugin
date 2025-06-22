"""
Command-line interface for the VTP plugin.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core.config import VTPConfig
from .core.processor import VTPProcessor
from .core.exceptions import VTPError, FileNotFoundError, ConfigurationError, ProcessingError


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="VTP Plugin - Variable Thickness Printing G-code post-processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use default settings
  %(prog)s -alpha 1.2 -nozzle_dia 0.6        # Custom alpha and nozzle diameter
  %(prog)s -e_dot 300 -eval_increment 0.5    # Custom extrusion and evaluation increment
        """
    )
    
    # Printing parameters
    parser.add_argument(
        "-alpha", type=float, default=1.0,
        help="Alpha parameter for thread area calculation (default: 1.0)"
    )
    parser.add_argument(
        "-nozzle_dia", type=float, default=0.4,
        help="Nozzle diameter in mm (default: 0.4)"
    )
    parser.add_argument(
        "-fil_dia", type=float, default=1.75,
        help="Filament diameter in mm (default: 1.75)"
    )
    parser.add_argument(
        "-eval_increment", type=float, default=1.0,
        help="Evaluation increment for line splitting (default: 1.0)"
    )
    parser.add_argument(
        "-e_dot", type=float, default=250.0,
        help="E_dot parameter for extrusion calculation (default: 250.0)"
    )
    
    # File paths
    parser.add_argument(
        "-equation_file", type=Path, default=Path("equations.txt"),
        help="Path to equation file (default: equations.txt)"
    )
    parser.add_argument(
        "-mesh_file", type=Path, default=Path("test_mesh.3mf"),
        help="Path to mesh file (default: test_mesh.3mf)"
    )
    parser.add_argument(
        "-input_gcode", type=Path, default=Path("test_mesh.gcode"),
        help="Path to input G-code file (default: test_mesh.gcode)"
    )
    parser.add_argument(
        "-output_gcode", type=Path, default=Path("outputtest.gcode"),
        help="Path to output G-code file (default: outputtest.gcode)"
    )
    parser.add_argument(
        "-log_file", type=Path, default=Path("vtp_plugin.txt"),
        help="Path to log file (default: vtp_plugin.txt)"
    )
    
    # Processing options
    parser.add_argument(
        "--keep-nozzle-check", action="store_true",
        help="Keep nozzle check lines (default: remove them)"
    )
    parser.add_argument(
        "-travel_speed", type=float, default=15000.0,
        help="Travel speed in mm/min (default: 15000.0)"
    )
    
    # Output options
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Process without writing output file"
    )
    
    return parser


def validate_args(args) -> None:
    """Validate command-line arguments.
    
    Args:
        args: Parsed arguments
        
    Raises:
        ConfigurationError: If arguments are invalid
    """
    if args.alpha <= 0:
        raise ConfigurationError("Alpha must be positive")
    if args.nozzle_dia <= 0:
        raise ConfigurationError("Nozzle diameter must be positive")
    if args.fil_dia <= 0:
        raise ConfigurationError("Filament diameter must be positive")
    if args.e_dot <= 0:
        raise ConfigurationError("E_dot must be positive")
    if args.eval_increment <= 0:
        raise ConfigurationError("Evaluation increment must be positive")
    if args.travel_speed <= 0:
        raise ConfigurationError("Travel speed must be positive")


def print_banner() -> None:
    """Print the VTP plugin banner."""
    print("=" * 60)
    print("VTP Plugin - Variable Thickness Printing")
    print("G-code Post-processor")
    print("=" * 60)


def print_config(config: VTPConfig) -> None:
    """Print the current configuration.
    
    Args:
        config: Configuration to print
    """
    print("\nConfiguration:")
    print(f"  Alpha: {config.printing.alpha}")
    print(f"  Nozzle diameter: {config.printing.nozzle_dia} mm")
    print(f"  Filament diameter: {config.printing.fil_dia} mm")
    print(f"  E_dot: {config.printing.e_dot}")
    print(f"  Evaluation increment: {config.printing.eval_increment}")
    print(f"  Travel speed: {config.travel_speed} mm/min")
    print(f"  Remove nozzle check: {config.remove_nozzle_check}")
    print(f"  Input file: {config.input_gcode}")
    print(f"  Output file: {config.output_gcode}")
    print(f"  Mesh file: {config.mesh_file}")
    print(f"  Equation file: {config.equation_file}")
    print(f"  Log file: {config.log_file}")


def main() -> int:
    """Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Parse arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Print banner
        print_banner()
        
        # Validate arguments
        validate_args(args)
        
        # Create configuration
        config = VTPConfig.from_args(args)
        config.remove_nozzle_check = not args.keep_nozzle_check
        config.travel_speed = args.travel_speed
        
        # Override file paths if specified
        if args.equation_file != Path("equations.txt"):
            config.equation_file = args.equation_file
        if args.mesh_file != Path("test_mesh.3mf"):
            config.mesh_file = args.mesh_file
        if args.input_gcode != Path("test_mesh.gcode"):
            config.input_gcode = args.input_gcode
        if args.output_gcode != Path("outputtest.gcode"):
            config.output_gcode = args.output_gcode
        if args.log_file != Path("vtp_plugin.txt"):
            config.log_file = args.log_file
        
        # Print configuration if verbose
        if args.verbose:
            print_config(config)
        
        # Create and initialize processor
        print("\nInitializing processor...")
        processor = VTPProcessor(config)
        processor.initialize()
        
        # Process file
        print("Processing G-code file...")
        result = processor.process_file()
        
        if result.success:
            print(f"\n✅ Processing completed successfully!")
            print(f"   Processed lines: {result.processed_lines}")
            print(f"   Output lines: {result.modified_lines}")
            
            if not args.dry_run:
                print(f"   Output saved to: {config.output_gcode}")
            else:
                print("   Dry run mode - no output file written")
            
            return 0
        else:
            print(f"\n❌ Processing failed: {result.error_message}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        return 130
    except VTPError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 