"""
Tests for G-code parsing and manipulation.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from vtp_plugin.models.gcode import MoveGcodeLine, GCodeParameters


class TestMoveGcodeLine:
    """Test G-code line parsing and manipulation."""
    
    def test_from_line_basic(self):
        """Test basic G-code line parsing."""
        line = "G1 X100.5 Y200.3 Z10.2 E5.1 F1500"
        gcode = MoveGcodeLine.from_line(line)
        
        assert gcode.x == 100.5
        assert gcode.y == 200.3
        assert gcode.z == 10.2
        assert gcode.e == 5.1
        assert gcode.f == 1500
    
    def test_from_line_partial(self):
        """Test parsing G-code line with partial parameters."""
        line = "G1 X100.5 Y200.3"
        gcode = MoveGcodeLine.from_line(line)
        
        assert gcode.x == 100.5
        assert gcode.y == 200.3
        assert gcode.z is None
        assert gcode.e is None
        assert gcode.f is None
    
    def test_from_line_empty(self):
        """Test parsing empty line."""
        with pytest.raises(ValueError, match="Empty or invalid G-code line"):
            MoveGcodeLine.from_line("")
    
    def test_from_line_invalid_coordinate(self):
        """Test parsing line with invalid coordinate."""
        line = "G1 Xinvalid Y200.3"
        with pytest.raises(ValueError, match="Invalid X coordinate"):
            MoveGcodeLine.from_line(line)
    
    def test_to_gcode_basic(self):
        """Test converting parameters back to G-code."""
        gcode = MoveGcodeLine(x=100.5, y=200.3, z=10.2, e=5.1, f=1500)
        result = gcode.to_gcode("test comment")
        
        expected = "G1 X100.500 Y200.300 Z10.200 E5.100 F1500.000 ; test comment\n"
        assert result == expected
    
    def test_to_gcode_partial(self):
        """Test converting partial parameters to G-code."""
        gcode = MoveGcodeLine(x=100.5, y=200.3)
        result = gcode.to_gcode()
        
        expected = "G1 X100.500 Y200.300 ; modified line\n"
        assert result == expected
    
    def test_get_stats(self):
        """Test getting parameter statistics."""
        gcode = MoveGcodeLine(x=100.5, y=200.3, z=10.2, e=5.1, f=1500)
        stats = gcode.get_stats()
        
        expected = "X: 100.5, Y: 200.3, Z: 10.2, E: 5.1, F: 1500"
        assert stats == expected
    
    def test_equality(self):
        """Test G-code line equality."""
        gcode1 = MoveGcodeLine(x=100.5, y=200.3, z=10.2)
        gcode2 = MoveGcodeLine(x=100.5, y=200.3, z=10.2)
        gcode3 = MoveGcodeLine(x=100.5, y=200.3, z=10.3)
        
        assert gcode1 == gcode2
        assert gcode1 != gcode3
        assert gcode1 != "not a gcode line"
    
    def test_repr(self):
        """Test string representation."""
        gcode = MoveGcodeLine(x=100.5, y=200.3, z=10.2)
        repr_str = repr(gcode)
        
        assert "MoveGcodeLine" in repr_str
        assert "x=100.5" in repr_str
        assert "y=200.3" in repr_str
        assert "z=10.2" in repr_str


class TestGCodeParameters:
    """Test G-code parameters dataclass."""
    
    def test_default_values(self):
        """Test default parameter values."""
        params = GCodeParameters()
        
        assert params.x is None
        assert params.y is None
        assert params.z is None
        assert params.e is None
        assert params.f is None
    
    def test_custom_values(self):
        """Test custom parameter values."""
        params = GCodeParameters(x=100.5, y=200.3, z=10.2)
        
        assert params.x == 100.5
        assert params.y == 200.3
        assert params.z == 10.2
        assert params.e is None
        assert params.f is None 