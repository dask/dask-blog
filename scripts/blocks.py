from sympy import MatrixSymbol, BlockMatrix, block_collapse, latex
from sympy.abc import n

A, B, C, D, E, F, G, H = [MatrixSymbol(a, n, n) for a in 'ABCDEFGH']
X = BlockMatrix([[A, B],
                 [C, D]])
Y = BlockMatrix([[E, F],
                 [G, H]])

print latex(X*Y)
print latex(block_collapse(X*Y))

print latex(block_collapse(X.I))
