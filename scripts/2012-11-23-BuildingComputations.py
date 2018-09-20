from sympy.matrices.expressions import MatrixSymbol
from sympy import Q, Symbol
from sympy.computations.inplace import inplace_compile
from sympy.computations.core import Identity
from sympy.computations.matrices.compile import make_rule, patterns

a,b,c,n = map(Symbol, 'abcn')
X = MatrixSymbol('X', n, n)
Y = MatrixSymbol('Y', n, n)
Z = MatrixSymbol('Z', n, n)
W = MatrixSymbol('W', n, n)
expr = (Y.I*Z*Y + b*Z*Y + c*W*W).I*Z*W
assumptions = Q.symmetric(Y) & Q.positive_definite(Y) & Q.symmetric(X)
identcomp = Identity(expr)

rule = make_rule(patterns, assumptions)
mathcomp = next(rule(identcomp))
mathcomp.show()
icomp = inplace_compile(mathcomp)
icomp.show()


