from sympy.matrices.expressions import MatrixSymbol
from sympy import Symbol, Q

n, k    = 1000, 500 #Symbol('n'), Symbol('k')
mu      = MatrixSymbol('mu', n, 1)
Sigma   = MatrixSymbol('Sigma', n, n)
H       = MatrixSymbol('H', k, n)
R       = MatrixSymbol('R', k, k)
data    = MatrixSymbol('data', k, 1)

newmu   = mu + Sigma*H.T * (R + H*Sigma*H.T).I * (H*mu - data)
newSigma= Sigma - Sigma*H.T * (R + H*Sigma*H.T).I * H * Sigma

assumptions = (Q.positive_definite(Sigma), Q.symmetric(Sigma),
               Q.positive_definite(R), Q.symmetric(R), Q.fullrank(H))

inputs = mu, Sigma, H, R, data
outputs = newmu, newSigma
