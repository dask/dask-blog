from sympy.matrices.expressions.gen import top_down, rr_from_blas
from sympy.matrices.expressions import MatrixSymbol
from sympy.rules.branch import multiplex
from sympy.matrices.expressions.blas import GEMM, SYMM, TRMM, TRSV
from sympy.matrices.expressions.lapack import POSV, GESV
from sympy import Symbol, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)
Z = MatrixSymbol('Z', n, n)
target = (4*X*X.T + 2*Z).I*X
assumptions = Q.invertible(X) & Q.positive_definite(Z) & Q.symmetric(Z)

routines = (TRSV, POSV, GESV, GEMM, SYMM, TRMM)
rules = [rr_from_blas(r, assumptions) for r in routines]
rule = top_down(multiplex(*rules))
computations = list(rule(target))

print computations[0].print_Fortran(str, assumptions)
f = computations[0].build(str, assumptions)
