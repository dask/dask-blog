from kalman import new_mu, new_Sigma, assumptions, mu, Sigma, R, H, data, I

from sympy.computations.matrices.compile import make_rule, patterns
from sympy.computations.core import Identity

ident = Identity(new_mu, new_Sigma)
rule = make_rule(patterns, assumptions)
mathcomp = next(rule(ident))

assert set(mathcomp.inputs) == set((mu, Sigma, H, R, data, I))
assert set(mathcomp.outputs).issuperset(set((new_mu, new_Sigma)))

mathcomp.show()
