"""
Mesh management and point classification.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import trimesh
from pathlib import Path

from ..core.exceptions import FileNotFoundError, InvalidMeshError


class MeshManager:
    """Manages 3D meshes for point classification."""
    
    def __init__(self, mesh_path: Path):
        """Initialize mesh manager with mesh file.
        
        Args:
            mesh_path: Path to the mesh file (.3mf, .stl, etc.)
            
        Raises:
            FileNotFoundError: If mesh file doesn't exist
            InvalidMeshError: If mesh file is invalid or empty
        """
        self.meshes: Dict[int, trimesh.Trimesh] = {}
        self._load_meshes(mesh_path)
    
    def _load_meshes(self, path: Path) -> None:
        """Load and validate mesh files.
        
        Args:
            path: Path to the mesh file
            
        Raises:
            FileNotFoundError: If mesh file doesn't exist
            InvalidMeshError: If mesh file is invalid or empty
        """
        if not path.exists():
            raise FileNotFoundError(f"Mesh file not found: {path}")
        
        try:
            scene = trimesh.load(str(path), force='scene')
            unnamed_meshes = scene.to_geometry().split()
            self.meshes = {i: mesh for i, mesh in enumerate(unnamed_meshes)}
            
            if not self.meshes:
                raise InvalidMeshError("No valid meshes found in file")
                
        except Exception as e:
            raise InvalidMeshError(f"Failed to load mesh file: {e}")
    
    def classify_point(self, point: List[float]) -> int:
        """Classify a point to determine which mesh it belongs to.
        
        Args:
            point: 3D point coordinates [x, y, z]
            
        Returns:
            Mesh ID (integer) that the point belongs to
            
        Raises:
            ValueError: If point is invalid
        """
        self._validate_point(point)
        
        # First check if point is inside any mesh
        for mesh_id, mesh in self.meshes.items():
            if mesh.contains([point]):
                return mesh_id
        
        # If not inside any mesh, find the closest one
        return self._find_closest_mesh(point)
    
    def _validate_point(self, point: List[float]) -> None:
        """Validate point coordinates.
        
        Args:
            point: Point coordinates to validate
            
        Raises:
            ValueError: If point is invalid
        """
        if len(point) != 3:
            raise ValueError(f"Point must have 3 coordinates, got {len(point)}")
        
        if any(coord is None for coord in point):
            raise ValueError("Point coordinates cannot be None")
        
        if not all(isinstance(coord, (int, float)) for coord in point):
            raise ValueError("All point coordinates must be numbers")
    
    def _find_closest_mesh(self, point: List[float]) -> int:
        """Find the mesh closest to the given point.
        
        Args:
            point: 3D point coordinates [x, y, z]
            
        Returns:
            ID of the closest mesh
        """
        closest_id = None
        closest_distance = np.inf
        
        for mesh_id, mesh in self.meshes.items():
            try:
                distance = abs(mesh.nearest.signed_distance([point])[0])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_id = mesh_id
            except Exception as e:
                # Log warning but continue with other meshes
                print(f"Warning: Could not compute distance to mesh {mesh_id}: {e}")
                continue
        
        if closest_id is None:
            # Fallback: return first mesh if all distance calculations failed
            closest_id = list(self.meshes.keys())[0]
        
        return closest_id
    
    def get_mesh_count(self) -> int:
        """Get the number of loaded meshes.
        
        Returns:
            Number of meshes
        """
        return len(self.meshes)
    
    def get_mesh_bounds(self, mesh_id: int) -> Tuple[np.ndarray, np.ndarray]:
        """Get the bounding box of a specific mesh.
        
        Args:
            mesh_id: ID of the mesh
            
        Returns:
            Tuple of (min_bounds, max_bounds) as numpy arrays
            
        Raises:
            KeyError: If mesh_id doesn't exist
        """
        if mesh_id not in self.meshes:
            raise KeyError(f"Mesh ID {mesh_id} not found")
        
        mesh = self.meshes[mesh_id]
        return mesh.bounds
    
    def __repr__(self) -> str:
        """String representation of the mesh manager."""
        return f"MeshManager(meshes={len(self.meshes)})" 