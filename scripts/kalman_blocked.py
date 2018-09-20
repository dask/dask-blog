from kalman import inputs, outputs, Sigma, H, R, mu, data, n, k

from sympy import blockcut, block_collapse
blocksizes = {
        Sigma: [(n/2, n/2), (n/2, n/2)],
        H:     [(k/2, k/2), (n/2, n/2)],
        R:     [(k/2, k/2), (k/2, k/2)],
        mu:    [(n/2, n/2), (1,)],
        data:  [(k/2, k/2), (1,)]
        }
blockinputs = [blockcut(i, *blocksizes[i]) for i in inputs]
blockoutputs = [o.subs(dict(zip(inputs, blockinputs))) for o in outputs]
collapsed_outputs = map(block_collapse, blockoutputs)

from sympy.printing.theanocode import theano_function

dtype = 'float64'
dtypes = dict(zip(inputs, [dtype]*len(inputs)))
f = theano_function(inputs, outputs, dtypes=dtypes)
fblocked = theano_function(inputs, collapsed_outputs, dtypes=dtypes)

import numpy
ninputs = [numpy.random.rand(*i.shape).astype(dtype) for i in inputs]
