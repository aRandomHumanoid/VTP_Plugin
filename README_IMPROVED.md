# VTP Plugin - Variable Thickness Printing

A Python-based G-code post-processor for implementing Variable Thickness Printing (VTP) techniques in 3D printing.

## Features

- **Variable Thickness Printing**: Modify G-code to create variable layer thickness based on mathematical equations
- **Mesh-based Classification**: Use 3D meshes to classify points and apply different equations
- **Flexible Configuration**: Customize printing parameters, file paths, and processing options
- **Robust Error Handling**: Comprehensive error handling and logging
- **Modern Python**: Built with modern Python practices, type hints, and proper packaging

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/romantenger/VTP_Plugin.git
   cd VTP_Plugin
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv vtp-env
   
   # On Windows:
   vtp-env\Scripts\activate
   
   # On macOS/Linux:
   source vtp-env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the plugin** (optional, for development):
   ```bash
   pip install -e .
   ```

## Usage

### Basic Usage

1. **Prepare your files**:
   - Export your build plate as `test_mesh.3mf` from PrusaSlicer
   - Export your sliced G-code as `test_mesh.gcode`
   - Create an `equations.txt` file with your V* and H* equations

2. **Run the plugin**:
   ```bash
   python main_new.py
   ```

3. **Check the output**:
   - The processed G-code will be saved as `outputtest.gcode`
   - Logs will be written to `vtp_plugin.txt`

### Advanced Usage

The plugin supports various command-line options:

```bash
# Custom printing parameters
python main_new.py -alpha 1.2 -nozzle_dia 0.6 -fil_dia 1.75

# Custom file paths
python main_new.py -input_gcode my_model.gcode -output_gcode processed.gcode

# Custom evaluation increment
python main_new.py -eval_increment 0.5 -e_dot 300

# Verbose output
python main_new.py -v

# Dry run (process without writing output)
python main_new.py --dry-run
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-alpha` | Alpha parameter for thread area calculation | 1.0 |
| `-nozzle_dia` | Nozzle diameter in mm | 0.4 |
| `-fil_dia` | Filament diameter in mm | 1.75 |
| `-eval_increment` | Evaluation increment for line splitting | 1.0 |
| `-e_dot` | E_dot parameter for extrusion calculation | 250.0 |
| `-input_gcode` | Input G-code file path | test_mesh.gcode |
| `-output_gcode` | Output G-code file path | outputtest.gcode |
| `-mesh_file` | Mesh file path | test_mesh.3mf |
| `-equation_file` | Equation file path | equations.txt |
| `-log_file` | Log file path | vtp_plugin.txt |
| `-travel_speed` | Travel speed in mm/min | 15000.0 |
| `--keep-nozzle-check` | Keep nozzle check lines | False |
| `-v, --verbose` | Enable verbose output | False |
| `--dry-run` | Process without writing output | False |

## File Formats

### Equation File (`equations.txt`)

The equation file contains V* and H* equations for each mesh, separated by semicolons:

```
# Format: V*_equation; H*_equation
# One equation pair per line
0.1 + 0.003*(x-100) + 0.003*(y-100) + 0.003*z; 6
0.2 + 0.002*x + 0.002*y + 0.001*z; 8
```

### Mesh File

Supported formats:
- `.3mf` (3D Manufacturing Format) - Recommended
- `.stl` (Stereolithography)
- `.obj` (Wavefront OBJ)
- Other formats supported by trimesh

### G-code File

Standard G-code format with PrusaSlicer-style comments:
- `; layer_height = 0.2` - Layer height information
- `; infill` - Infill lines
- `; travel` - Travel moves
- `; support` - Support material

## Project Structure

```
VTP_Plugin/
├── src/vtp_plugin/           # Main package
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration management
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── processor.py      # Main processor
│   ├── models/               # Data models
│   │   ├── gcode.py          # G-code parsing
│   │   ├── mesh.py           # Mesh management
│   │   └── printing_stats.py # Printing calculations
│   ├── utils/                # Utility functions
│   │   ├── file_utils.py     # File operations
│   │   └── math_utils.py     # Mathematical utilities
│   └── cli.py                # Command-line interface
├── tests/                    # Test suite
├── main_new.py               # New entry point
├── main.py                   # Original entry point
├── pyproject.toml            # Project configuration
└── requirements.txt          # Dependencies
```

## Development

### Setting up Development Environment

1. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run tests**:
   ```bash
   pytest
   ```

3. **Run type checking**:
   ```bash
   mypy src/vtp_plugin
   ```

4. **Format code**:
   ```bash
   black src/vtp_plugin tests
   isort src/vtp_plugin tests
   ```

5. **Lint code**:
   ```bash
   flake8 src/vtp_plugin tests
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/vtp_plugin

# Run specific test file
pytest tests/test_gcode.py

# Run with verbose output
pytest -v
```

## Configuration

### PrusaSlicer Integration

1. **Install printer configuration**:
   - Copy files from the `slicer/` folder to your PrusaSlicer configuration directory
   - Restart PrusaSlicer

2. **Export workflow**:
   - Export build plate as `.3mf` file
   - Export sliced G-code as `.gcode` file
   - Run the VTP plugin
   - Use the processed G-code for printing

## Troubleshooting

### Common Issues

1. **File not found errors**:
   - Ensure all required files exist in the correct locations
   - Check file permissions
   - Verify file paths in command-line arguments

2. **Equation parsing errors**:
   - Check equation file format (V*; H*)
   - Ensure equations use valid mathematical syntax
   - Verify variable names (x, y, z)

3. **Mesh loading errors**:
   - Ensure mesh file is valid and not corrupted
   - Check mesh file format compatibility
   - Verify mesh contains valid geometry

4. **G-code processing errors**:
   - Check G-code file format
   - Ensure G-code contains required comments
   - Verify coordinate system compatibility

### Debug Mode

Enable verbose output for detailed debugging:

```bash
python main_new.py -v
```

Check the log file (`vtp_plugin.txt`) for detailed error messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Acknowledgments

- Original implementation by Roman Tenger
- Built with modern Python development practices
- Uses trimesh for 3D mesh processing
- Uses sympy for mathematical equation evaluation

## Support

For issues and questions:
- Check the troubleshooting section
- Review the log files for error details
- Open an issue on GitHub with detailed information 