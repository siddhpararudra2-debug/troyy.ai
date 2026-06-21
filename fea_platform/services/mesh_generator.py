import numpy as np
from typing import List, Tuple, Dict
from fea_platform.schemas.fea_models import MeshResult

class MeshGenerator:
    """Generates FEA meshes from geometry descriptions.
    In production, wraps Gmsh or similar meshing library."""
    
    def generate_structured_hex_mesh(self, length: float, width: float, height: float,
                                     nx: int, ny: int, nz: int) -> MeshResult:
        """Generate a structured hexahedral mesh for a box geometry."""
        nodes = []
        elements = []
        
        # Generate nodes
        for k in range(nz + 1):
            for j in range(ny + 1):
                for i in range(nx + 1):
                    x = i * length / nx
                    y = j * width / ny
                    z = k * height / nz
                    node_id = k * (ny + 1) * (nx + 1) + j * (nx + 1) + i + 1
                    nodes.append((node_id, x, y, z))
                    
        # Generate hex8 elements
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    n1 = k * (ny + 1) * (nx + 1) + j * (nx + 1) + i + 1
                    n2 = n1 + 1
                    n3 = n1 + (nx + 1) + 1
                    n4 = n1 + (nx + 1)
                    n5 = n1 + (ny + 1) * (nx + 1)
                    n6 = n5 + 1
                    n7 = n5 + (nx + 1) + 1
                    n8 = n5 + (nx + 1)
                    elem_id = k * ny * nx + j * nx + i + 1
                    elements.append((elem_id, n1, n2, n3, n4, n5, n6, n7, n8))
                    
        # Compute mesh quality
        quality = self._assess_quality(nodes, elements)
        
        return MeshResult(
            node_count=len(nodes),
            element_count=len(elements),
            nodes=nodes,
            elements=elements,
            quality_metrics=quality
        )
        
    def _assess_quality(self, nodes: List, elements: List) -> Dict:
        """Compute mesh quality metrics."""
        if not elements:
            return {"min_aspect_ratio": 0.0, "max_aspect_ratio": 0.0, "avg_aspect_ratio": 0.0}
            
        # Simplified aspect ratio calculation
        aspects = []
        for elem in elements:
            # For hex8, compute edge lengths
            node_coords = {n[0]: (n[1], n[2], n[3]) for n in nodes}
            edges = []
            for i in range(4):
                n_a = node_coords[elem[i + 1]]
                n_b = node_coords[elem[(i + 1) % 4 + 1]]
                edges.append(np.linalg.norm(np.array(n_a) - np.array(n_b)))
            min_edge = min(edges)
            max_edge = max(edges)
            aspect = max_edge / min_edge if min_edge > 0 else float('inf')
            aspects.append(aspect)
            
        return {
            "min_aspect_ratio": float(min(aspects)),
            "max_aspect_ratio": float(max(aspects)),
            "avg_aspect_ratio": float(np.mean(aspects)),
            "elements_over_limit": float(sum(1 for a in aspects if a > 5.0))
        }
