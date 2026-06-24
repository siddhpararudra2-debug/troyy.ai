"""
Matrix Engine — linear algebra operations
Determinants, inverses, eigenvalues, linear systems
"""
import sympy as sp
import numpy as np
from typing import Any, Dict, List


class MatrixEngine:
    """Engine for matrix operations"""

    def __init__(self):
        pass

    def determinant(self, matrix: Any) -> Dict[str, Any]:
        """Compute determinant of matrix (sympy or numpy)"""
        if isinstance(matrix, sp.Matrix):
            det = matrix.det()
            return {"determinant": det, "latex": sp.latex(det)}
        else:
            m_np = np.array(matrix, dtype=float)
            det = np.linalg.det(m_np)
            return {"determinant": float(det)}

    def inverse(self, matrix: Any) -> Dict[str, Any]:
        """Compute matrix inverse"""
        if isinstance(matrix, sp.Matrix):
            inv = matrix.inv()
            return {"inverse": inv, "latex": sp.latex(inv)}
        else:
            m_np = np.array(matrix, dtype=float)
            inv = np.linalg.inv(m_np)
            return {"inverse": inv.tolist()}

    def eigenvalues(self, matrix: Any) -> Dict[str, Any]:
        """Compute eigenvalues and eigenvectors"""
        if isinstance(matrix, sp.Matrix):
            eig = matrix.eigenvals()
            eigvec = matrix.eigenvects()
            return {
                "eigenvalues": eig,
                "eigenvectors": eigvec,
                "latex": sp.latex(matrix.eigenvals()),
            }
        else:
            m_np = np.array(matrix, dtype=float)
            w, v = np.linalg.eig(m_np)
            return {
                "eigenvalues": w.tolist(),
                "eigenvectors": v.tolist(),
            }

    def solve_linear_system(
        self,
        a_matrix: Any,
        b_vector: Any,
    ) -> Dict[str, Any]:
        """Solve Ax = b linear system"""
        if isinstance(a_matrix, sp.Matrix) and isinstance(b_vector, sp.Matrix):
            sol = a_matrix.gauss_jordan_solve(b_vector)[0]
            return {"solution": sol, "latex": sp.latex(sol)}
        else:
            a_np = np.array(a_matrix, dtype=float)
            b_np = np.array(b_vector, dtype=float)
            sol = np.linalg.solve(a_np, b_np)
            return {"solution": sol.tolist()}

    def gram_schmidt(self, vectors: List[Any]) -> Dict[str, Any]:
        """Gram-Schmidt orthogonalization"""
        if all(isinstance(v, sp.Matrix) for v in vectors):
            orth = []
            for v in vectors:
                u = v
                for w in orth:
                    u = u - (v.dot(w) / w.dot(w)) * w
                orth.append(u)
            orthonormal = [u / u.norm() for u in orth if u.norm() != 0]
            return {
                "orthogonal": orth,
                "orthonormal": orthonormal,
            }
        else:
            # Numpy
            arr = np.column_stack([np.array(v, dtype=float) for v in vectors])
            q, r = np.linalg.qr(arr)
            return {
                "orthonormal": q.tolist(),
            }
