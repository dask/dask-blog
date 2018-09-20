from sympy.printing.theanocode import *
from sympy.physics.hydrogen import R_nl
import theano
from sympy import Derivative, simplify, Symbol, pprint, latex, count_ops

n, l, Z = 6, 2, 6

x = Symbol('x')
expr = R_nl(n, l, x, Z)


for e in (expr, expr.diff(x), simplify(expr.diff(x))):
    print latex(e)
    print "Operations: ", count_ops(e)
    print

print latex(Derivative(expr, x))

print '\n\n\n'

# Theano simplification functions
def fgraph_of(*exprs):
    """ Transform SymPy expressions into Theano Computation """
    outs = map(theano_code, exprs)
    ins = theano.gof.graph.inputs(outs)

    ins, outs = theano.gof.graph.clone(ins, outs)
    return theano.gof.FunctionGraph(ins, outs)

def theano_simplify(fgraph):
    """ Simplify a Theano Computation """
    mode = theano.compile.get_default_mode().excluding("fusion")
    fgraph = fgraph.clone()
    mode.optimizer.optimize(fgraph)
    return fgraph

def theano_count_ops(fgraph):
    """ Count the number of Scalar operations in a Theano Computation """
    return len(filter(lambda n: isinstance(n.op, theano.tensor.Elemwise),
                      fgraph.apply_nodes))


exprs = Derivative(expr, x), simplify(expr.diff(x))

for expr in exprs:
    fgraph = fgraph_of(expr)
    simp_fgraph = theano_simplify(fgraph)
    print latex(expr)
    print "Operations:                             ", theano_count_ops(fgraph)
    print "Operations after Theano Simplification: ", theano_count_ops(simp_fgraph)
    print


print '\n\n\n'
print "Simultaneous Computation"
# Simultaneous computation
orig_expr = R_nl(n, l, x, Z)
for expr in exprs:
    fgraph = fgraph_of(expr, orig_expr)
    simp_fgraph = theano_simplify(fgraph)
    print latex((expr, orig_expr))
    print "Operations:                             ", len(fgraph.apply_nodes)
    print "Operations after Theano Simplification: ", len(simp_fgraph.apply_nodes)
    print
