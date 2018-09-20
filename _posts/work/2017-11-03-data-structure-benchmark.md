---
layout: post
title: Optimizing Data Structure Access in Python
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---

{% include JB/setup %}

*This work is supported by [Anaconda Inc](http://anaconda.com) and the Data
Driven Discovery Initiative from the [Moore Foundation](https://www.moore.org/)*

Last week at [PyCon DE](https://de.pycon.org/) I had the good fortune to meet
[Stefan Behnel](http://www.behnel.de/), one of the core developers of Cython.
Together we worked to optimize a small benchmark that is representative of
Dask's central task scheduler, a pure-Python application that is primarily data
structure bound.

Our benchmark is a toy problem that creates three data structures that index
each other with dictionaries, lists, and sets, and then does some simple
arithmetic. (You don't need to understand this benchmark deeply to read this
article.)

```python
import random
import time

nA = 100
nB = 100
nC = 100

A = {'A-%d' % i: ['B-%d' % random.randint(0, nB - 1)
                  for i in range(random.randint(0, 5))]
     for i in range(nA)}

B = {'B-%d' % i: {'C-%d' % random.randint(0, nC - 1)
                  for i in range(random.randint(1, 3))}
     for i in range(nB)}

C = {'C-%d' % i: i for i in range(nC)}

data = ['A-%d' % i for i in range(nA)]


def f(A, B, C, data):
    for a_key in data:
        b_keys = A[a_key]
        for b_key in b_keys:
            for c_key in B[b_key]:
                C[c_key] += 1


start = time.time()

for i in range(10000):
    f(A, B, C, data)

end = time.time()

print("Duration: %0.3f seconds" % (end - start))
```

```
$ python benchmark.py
Duration: 1.12 seconds
```

This is an atypical problem Python optimization because it is primarily bound
by data structure access (dicts, lists, sets), rather than numerical operations
commonly optimized by Cython (nested for loops over floating point arithmetic).
Python is already decently fast here, typically within a factor of 2-5x of
compiled languages like Java or C++, but still we'd like to improve this when
possible.

In this post we combine two different methods to optimize data-structure bound
workloads:

1.  Compiling Python code with Cython with no other annotations
2.  Interning strings for more rapid dict lookups

Finally at the end of the post we also run the benchmark under PyPy to compare
performance.


Cython
------

First we compile our Python code with Cython.  Normally when using Cython we
annotate our variables with types, giving the compiler enough information
to avoid using Python altogether.  However in our case we don't have many
numeric operations and we're going to be using Python data structures
regardless, so this won't help much.  We compile our original Python code
without alteration.

    cythonize -i benchmark.py

And run

    $ python -c "import benchmark"
    Duration: 0.73 seconds

This gives us a decent speedup from 1.1 seconds to 0.73 seconds.  This isn't
huge relative to typical Cython speedups (which are often 10-100x) but would be
a *very welcome* change for our scheduler, where we've been chasing 5%
optimizations for a while now.


Interning Strings
-----------------

Our second trick is to intern strings.  This means that we try to always have
only one copy of every string.  This improves performance when doing dictionary
lookups because of the following:

1.  Python computes the hash of the string only once (strings cache their hash
    value once computed)
2.  Python checks for object identity (fast) before moving on to value equality
    (slow)

Or, anecdotally, `text is text` is faster in Python than `text == text`.  If
you ensure that there is only one copy of every string then you only need to do
identity comparisons like `text is text`.

So, if any time we see a string `"abc"` it is exactly the same object as all
other `"abc"` strings in our program, then string-dict lookups will only
require a pointer/integer equality check, rather than having to do a full
string comparison.

Adding string interning to our benchmark looks like the following:

```python
inter = {}

def intern(x):
    try:
        return inter[x]
    except KeyError:
        inter[x] = x
        return x

A = {intern('A-%d' % i): [intern('B-%d' % random.randint(0, nB - 1))
                  for i in range(random.randint(0, 5))]
     for i in range(nA)}

B = {intern('B-%d' % i): {intern('C-%d' % random.randint(0, nC - 1))
                  for i in range(random.randint(1, 3))}
     for i in range(nB)}

C = {intern('C-%d' % i): i for i in range(nC)}

data = [intern('A-%d' % i) for i in range(nA)]

# The rest of the benchmark is as before
```

This brings our duration from 1.1s down to 0.75s.  Note that this is without
the separate Cython improvements described just above.


Cython + Interning
------------------

We can combine both optimizations.  This brings us to around 0.45s, a 2-3x
improvement over our original time.

    cythonize -i benchmark2.py

    $ python -c "import benchmark2"
    Duration: 0.46 seconds

PyPy
----

Alternatively, we can just run everything in PyPy.

    $ pypy3 benchmark1.py  # original
    Duration: 0.25 seconds

    $ pypy3 benchmark2.py  # includes interning
    Duraiton: 0.20 seconds

So PyPy can be quite a bit faster than Cython on this sort of code (which is
not a big surprise).  Interning helps a bit, but not quite as much.

This is fairly encouraging.  The Dask scheduler can run under PyPy even while
Dask clients and workers run under normal CPython (for use with the full PyData
stack).

Preliminary Results on Dask Benchmark
-------------------------------------

We started this experiment with the assumption that our toy benchmark somehow
represented the Dask's scheduler in terms of performance characteristics.  This
assumption, of course, is false.  The Dask scheduler is significantly more
complex and it is difficult to build a single toy example to represent its
performance.

When we try these tricks on a [slightly more complex
benchmark](https://gist.github.com/88b3c29e645ba2eae2d079a1de25d266) that
actually uses the Dask scheduler we find the following results:

-  **Cython**: almost no effect
-  **String Interning**: almost no effect
-  **PyPy**: almost no effect

However I have only spent a brief amount of time on this (twenty minutes?) and
so I hope that the lack of a performance gain here is due to lack of effort.

If anyone is interested in this I hope that this blogpost contains enough
information to get anyone started if they want to investigate further.
