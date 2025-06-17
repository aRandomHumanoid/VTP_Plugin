import trimesh
import numpy as np


class MeshStuff:
    meshes = None

    def __init__(self, path):
        scene = trimesh.load(path, force='scene')
        unnamed_meshes = scene.to_geometry().split()
        self.meshes = {i: v for i, v in enumerate(unnamed_meshes)}  # autogenerates meshes names 1, 2 3...

    # todo make GUI for assigning names for meshes

    def assign_mesh_numbers(self, V_star_eq, H_star_eq):
        return

    def check_point(self, point):
        if(point[1] is None):
            print()
        assert(point[0] is not None)
        assert(point[1] is not None)
        assert(point[2] is not None)

    def classify_point(self, point):
        self.check_point(point)
        for name, mesh in self.meshes.items():
            if mesh.contains([point]):
                return name
        return self.closest_mesh(point)  # if not within a mesh, returns the closest mesh

    def closest_mesh(self, point):
        closest_name = None
        closest_distance = np.inf

        for name, mesh in self.meshes.items():
            # Compute distance from the point to the mesh surface
            distance = mesh.nearest.signed_distance([point])[0]
            abs_distance = abs(distance)
            if abs_distance < closest_distance:
                closest_distance = abs_distance
                closest_name = name

        return closest_name
