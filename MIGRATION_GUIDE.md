# Migration Guide: Old to New VTP Plugin Structure

This guide helps you transition from the old VTP plugin structure to the new improved version.

## What's Changed

### 1. **Project Structure**
- **Old**: Monolithic files (`main.py`, `printing_stats.py`, `mesh_stuff.py`, `move_gcode_line.py`)
- **New**: Modular package structure with proper separation of concerns

### 2. **Code Organization**
- **Old**: Global variables and functions scattered across files
- **New**: Object-oriented design with proper encapsulation

### 3. **Error Handling**
- **Old**: Basic error handling with print statements
- **New**: Comprehensive exception hierarchy and logging

### 4. **Configuration**
- **Old**: Hardcoded values and command-line arguments
- **New**: Structured configuration management

## Migration Steps

### Step 1: Update Your Workflow

**Old way**:
```bash
python main.py
```

**New way**:
```bash
python main_new.py
```

### Step 2: Update Command Line Arguments

**Old way**:
```bash
python main.py -alpha 1.2 -nozzle_dia 0.6
```

**New way**:
```bash
python main_new.py -alpha 1.2 -nozzle_dia 0.6
```

*Note: The command-line interface is backward compatible!*

### Step 3: File Locations

The new structure expects the same files in the same locations:
- `test_mesh.3mf` - Mesh file
- `test_mesh.gcode` - Input G-code
- `equations.txt` - Equation file
- `outputtest.gcode` - Output G-code (generated)

### Step 4: Custom File Paths

**Old way**: Modify code to change file paths

**New way**: Use command-line arguments:
```bash
python main_new.py -input_gcode my_file.gcode -output_gcode my_output.gcode
```

## New Features

### 1. **Better Error Messages**
The new version provides more detailed error messages and logging:

```bash
python main_new.py -v
```

### 2. **Dry Run Mode**
Test your configuration without generating output:
```bash
python main_new.py --dry-run
```

### 3. **Verbose Output**
Get detailed information about the processing:
```bash
python main_new.py -v
```

### 4. **Custom Travel Speed**
Set custom travel speed:
```bash
python main_new.py -travel_speed 12000
```

### 5. **Keep Nozzle Check Lines**
Optionally keep nozzle check lines:
```bash
python main_new.py --keep-nozzle-check
```

## Backward Compatibility

### What Still Works
- ✅ All original command-line arguments
- ✅ Same file formats and locations
- ✅ Same processing logic
- ✅ Same output format

### What's Improved
- 🔧 Better error handling
- 🔧 More detailed logging
- 🔧 Structured configuration
- 🔧 Modular code organization
- 🔧 Type hints and validation
- 🔧 Comprehensive testing

## Troubleshooting Migration

### Issue: "Module not found" errors
**Solution**: Make sure you're using `main_new.py` instead of the old `main.py`

### Issue: Different output behavior
**Solution**: The core processing logic is the same, but check the log file (`vtp_plugin.txt`) for any warnings or errors

### Issue: Missing dependencies
**Solution**: Install the updated requirements:
```bash
pip install -r requirements.txt
```

### Issue: Configuration errors
**Solution**: Use the verbose flag to see detailed configuration:
```bash
python main_new.py -v
```

## Development Migration

### If You Were Modifying the Code

**Old way** - Modify `main.py`:
```python
# Global variables
global stats
global meshes

# Modify processing logic
def process_gcode(lines):
    # Your custom logic
    pass
```

**New way** - Extend the processor:
```python
from vtp_plugin.core.processor import VTPProcessor
from vtp_plugin.core.config import VTPConfig

class CustomProcessor(VTPProcessor):
    def _process_gcode_lines(self, lines):
        # Your custom logic
        return super()._process_gcode_lines(lines)

# Usage
config = VTPConfig.from_args(args)
processor = CustomProcessor(config)
result = processor.process_file()
```

### If You Were Adding New Features

**Old way** - Add functions to existing files

**New way** - Create new modules:
```python
# src/vtp_plugin/utils/my_feature.py
def my_new_feature():
    pass

# src/vtp_plugin/models/my_model.py
class MyNewModel:
    pass
```

## Testing the Migration

1. **Backup your files**:
   ```bash
   cp test_mesh.gcode test_mesh_backup.gcode
   ```

2. **Run the new version**:
   ```bash
   python main_new.py -v
   ```

3. **Compare outputs**:
   ```bash
   diff outputtest.gcode outputtest_backup.gcode
   ```

4. **Check logs**:
   ```bash
   cat vtp_plugin.txt
   ```

## Getting Help

If you encounter issues during migration:

1. **Check the logs**: Look at `vtp_plugin.txt` for detailed error messages
2. **Use verbose mode**: Run with `-v` flag for more information
3. **Try dry run**: Use `--dry-run` to test without generating output
4. **Review this guide**: Make sure you've followed all migration steps
5. **Open an issue**: If problems persist, open an issue with detailed information

## Future Development

The new structure makes it easier to:

- Add new features
- Write tests
- Maintain code
- Collaborate with others
- Deploy as a package

Consider contributing to the project or creating your own extensions using the new modular architecture! 