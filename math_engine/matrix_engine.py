"""
Matrix and linear algebra engine for Engineering OS.
Provides matrix operations, eigenvalue analysis, and linear transformations.
"""
import logging
from typing import Optional
from sympy import (
    Matrix, eye, zeros, ones, diag, transpose, det, trace,
    GramSchmidt, latex, simplify,
    Symbol, symbols, factor, expand,
)

from math_engine.symbolic_math import Step, DerivationResult

logger = logging.getLogger(__name__)


class MatrixEngine:
    """
    Linear algebra and matrix operations engine.
    Provides step-by-step matrix computations for engineering applications.
    """

    @staticmethod
    def create_matrix(rows: int, cols: int, values: list[list]) -> Matrix:
        """Create a SymPy Matrix from values."""
        return Matrix(values)

    def determinant(self, matrix_data: list[list]) -> DerivationResult:
        """Compute the determinant of a matrix."""
        M = self.create_matrix(len(matrix_data), len(matrix_data[0]), matrix_data)
        n = M.rows
        
        steps = [
            Step(f"Matrix A ({n}×{n})", str(M), latex(M)),
        ]
        
        if n <= 3:
            # Show formula for small matrices
            if n == 2:
                steps.append(Step(
                    "det(A) = ad - bc",
                    f"({M[0,0]})({M[1,1]}) - ({M[0,1]})({M[1,0]})",
                    latex(M[0,0]*M[1,1] - M[0,1]*M[1,0]),
                ))
            elif n == 3:
                steps.append(Step(
                    "Using Sarrus rule for 3×3 determinant",
                    str(det(M)),
                    latex(det(M)),
                ))
        
        result = det(M)
        steps.append(Step(
            "Determinant result",
            str(result),
            latex(result),
        ))
        
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )

    def inverse(self, matrix_data: list[list]) -> DerivationResult:
        """Compute the inverse of a matrix."""
        M = self.create_matrix(len(matrix_data), len(matrix_data[0]), matrix_data)
        
        steps = [
            Step("Original matrix A", str(M), latex(M)),
        ]
        
        d = det(M)
        steps.append(Step(
            f"det(A) = {d}",
            str(d),
            latex(d),
        ))
        
        if d == 0:
            steps.append(Step(
                "Matrix is singular, inverse does not exist",
                "No inverse",
                "\\text{No inverse}",
            ))
            return DerivationResult(
                result="Singular matrix - no inverse",
                steps=steps,
                latex_result="\\text{Singular}",
            )
        
        result = M.inv()
        steps.append(Step(
            "Inverse matrix A⁻¹",
            str(result),
            latex(result),
        ))
        
        # Verify: A * A⁻¹ = I
        verify = M * result
        steps.append(Step(
            "Verification: A × A⁻¹ = I",
            str(simplify(verify)),
            latex(simplify(verify)),
        ))
        
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )

    def eigenvalues(self, matrix_data: list[list]) -> DerivationResult:
        """Compute eigenvalues of a matrix."""
        M = self.create_matrix(len(matrix_data), len(matrix_data[0]), matrix_data)
        
        steps = [
            Step("Original matrix A", str(M), latex(M)),
        ]
        
        # Characteristic equation
        n = M.rows
        char_poly = M.charpoly()
        steps.append(Step(
            f"Characteristic polynomial",
            str(char_poly.as_expr()),
            latex(char_poly.as_expr()),
        ))
        
        vals = M.eigenvals()
        steps.append(Step(
            "Eigenvalues",
            str(vals),
            latex(vals),
        ))
        
        return DerivationResult(
            result=str(vals),
            steps=steps,
            latex_result=latex(vals),
        )

    def eigenvectors(self, matrix_data: list[list]) -> DerivationResult:
        """Compute eigenvalues and eigenvectors."""
        M = self.create_matrix(len(matrix_data), len(matrix_data[0]), matrix_data)
        
        steps = [
            Step("Original matrix A", str(M), latex(M)),
        ]
        
        char_poly = M.charpoly()
        steps.append(Step(
            "Characteristic polynomial",
            str(char_poly.as_expr()),
            latex(char_poly.as_expr()),
        ))
        
        vecs = M.eigenvects()
        result_str = ""
        for val, mult, evecs in vecs:
            for v in evecs:
                result_str += f"λ={val}: {v}\n"
                steps.append(Step(
                    f"Eigenvector for λ={val}",
                    str(v),
                    latex(v),
                ))
        
        return DerivationResult(
            result=result_str.strip(),
            steps=steps,
            latex_result=latex(result_str.strip()),
        )

    def matrix_multiply(self, A_data: list[list], B_data: list[list]) -> DerivationResult:
        """Multiply two matrices."""
        A = self.create_matrix(len(A_data), len(A_data[0]), A_data)
        B = self.create_matrix(len(B_data), len(B_data[0]), B_data)
        
        steps = [
            Step("Matrix A", str(A), latex(A)),
            Step("Matrix B", str(B), latex(B)),
        ]
        
        if A.cols != B.rows:
            steps.append(Step(
                f"Dimension mismatch: A is {A.rows}×{A.cols}, B is {B.rows}×{B.cols}",
                "Cannot multiply",
                "\\text{Cannot multiply}",
            ))
            return DerivationResult(
                result="Dimension mismatch",
                steps=steps,
            )
        
        result = A * B
        steps.append(Step(
            "Product A × B",
            str(result),
            latex(result),
        ))
        
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )

    def transpose(self, matrix_data: list[list]) -> DerivationResult:
        """Compute the transpose of a matrix."""
        M = self.create_matrix(len(matrix_data), len(matrix_data[0]), matrix_data)
        result = M.T
        
        steps = [
            Step("Original matrix A", str(M), latex(M)),
            Step("Transpose Aᵀ", str(result), latex(result)),
        ]
        
        return DerivationResult(
            result=str(result),
            steps=steps,
            latex_result=latex(result),
        )

    def solve_linear_system(self, A_data: list[list], b_data: list) -> DerivationResult:
        """Solve Ax = b linear system."""
        A = self.create_matrix(len(A_data), len(A_data[0]), A_data)
        b = Matrix(b_data)
        
        steps = [
            Step("Coefficient matrix A", str(A), latex(A)),
            Step("Right-hand side b", str(b), latex(b)),
        ]
        
        d = det(A)
        steps.append(Step(
            f"det(A) = {d}",
            str(d),
            latex(d),
        ))
        
        if d == 0:
            return DerivationResult(
                result="System has no unique solution (singular matrix)",
                steps=steps,
            )
        
        x = A.LUsolve(b)
        steps.append(Step(
            "Solution x = A⁻¹b",
            str(x),
            latex(x),
        ))
        
        return DerivationResult(
            result=str(x),
            steps=steps,
            latex_result=latex(x),
        )

    def gram_schmidt(self, vectors: list[list]) -> DerivationResult:
        """Apply Gram-Schmidt orthonormalization."""
        vec_matrices = [Matrix(v) for v in vectors]
        
        steps = [
            Step("Original vectors", str(vec_matrices), latex(vec_matrices)),
        ]
        
        orthonormal = GramSchmidt(vec_matrices, orthonormal=True)
        steps.append(Step(
            "Orthonormal basis",
            str(orthonormal),
            latex(orthonormal),
        ))
        
        return DerivationResult(
            result=str(orthonormal),
            steps=steps,
            latex_result=latex(orthonormal),
        )