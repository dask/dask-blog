---
layout: post
title: Composing Dask Array with Numba Stencils
author: Matthew Rocklin
tags: [dask, numba]
theme: twitter
---

{% include JB/setup %}

In this post we explore four array computing technologies, and how they
work together to achieve powerful results.

1.  Numba's stencil decorator to craft localized compute kernels
2.  Numba's Just-In-Time (JIT) compiler for array computing in Python
3.  Dask Array for parallelizing array computations across many chunks
4.  NumPy's Generalized Universal Functions (gufuncs) to tie everything
    together

In the end we'll show how a novice developer can write a small amount of Python
to efficiently compute localized computation on large amounts of data. In
particular we'll write a simple function to smooth images and apply that in
parallel across a large stack of images.

Here is the full code, we'll dive into it piece by piece below.

```python
import numba

@numba.stencil
def _smooth(x):
    return (x[-1, -1] + x[-1, 0] + x[-1, 1] +
            x[ 0, -1] + x[ 0, 0] + x[ 0, 1] +
            x[ 1, -1] + x[ 1, 0] + x[ 1, 1]) // 9


@numba.guvectorize(
    [(numba.int8[:, :], numba.int8[:, :])],
    '(n, m) -> (n, m)'
)
def smooth(x, out):
    out[:] = _smooth(x)


# If you want fake data
import dask.array as da
x = da.ones((1000000, 1000, 1000), chunks=('auto', -1, -1), dtype='int8')

# If you have actual data
import dask_image
x = dask_image.imread.imread('/path/to/*.png')

y = smooth(x)
# dask.array<transpose, shape=(1000000, 1000, 1000), dtype=int8, chunksize=(125, 1000, 1000)>
```

Note: the `smooth` function above is more commonly referred to as the 2D mean filter in the image processing community.

Now, lets break this down a bit

## Numba Stencils

**Docs:**: https://numba.pydata.org/numba-doc/dev/user/stencil.html

Many array computing functions operate only on a local region of the array.
This is common in image processing, signals processing, simulation, the
solution of differential equations, anomaly detection, time series analysis,
and more. Typically we write code that looks like the following:

```python
def _smooth(x):
    out = np.empty_like(x)
    for i in range(1, x.shape[0] - 1):
        for j in range(1, x.shape[1] - 1):
            out[i, j] = x[i + -1, j + -1] + x[i + -1, j + 0] + x[i + -1, j + 1] +
                        x[i +  0, j + -1] + x[i +  0, j + 0] + x[i +  0, j + 1] +
                        x[i +  1, j + -1] + x[i +  1, j + 0] + x[i +  1, j + 1]) // 9

    return out
```

Or something similar. The `numba.stencil` decorator makes this a bit easier to
write down. You just write down what happens on every element, and Numba
handles the rest.

```python
@numba.stencil
def _smooth(x):
    return (x[-1, -1] + x[-1, 0] + x[-1, 1] +
            x[ 0, -1] + x[ 0, 0] + x[ 0, 1] +
            x[ 1, -1] + x[ 1, 0] + x[ 1, 1]) // 9
```

## Numba JIT

**Docs:** http://numba.pydata.org/

When we run this function on a NumPy array, we find that it is slow, operating
at Python speeds.

```python
x = np.ones((100, 100))
timeit _smooth(x)
527 ms ± 44.1 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

But if we JIT compile this function with Numba, then it runs more quickly.

```python
@numba.njit
def smooth(x):
    return _smooth(x)

%timeit smooth(x)
70.8 µs ± 6.38 µs per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

For those counting, that's over 1000x faster!

_Note: this function already exists as `scipy.ndimage.uniform_filter`, which
operates at the same speed._

## Dask Array

**Docs:** https://docs.dask.org/en/latest/array.html

In these applications people often have many such arrays and they want to apply
this function over all of them. In principle they could do this with a for
loop.

```python
from glob import glob
import skimage.io

for fn in glob('/path/to/*.png'):
    img = skimage.io.imread(fn)
    out = smooth(img)
    skimage.io.imsave(fn.replace('.png', '.out.png'), out)
```

If they wanted to then do this in parallel they would maybe use the
multiprocessing or concurrent.futures modules. If they wanted to do this
across a cluster then they could rewrite their code with PySpark or some other
system.

Or, they could use Dask array, which will handle both the pipelining and the
parallelism (single machine or on a cluster) all while still looking mostly
like a NumPy array.

```python
import dask_image
x = dask_image.imread('/path/to/*.png')  # a large lazy array of all of our images
y = x.map_blocks(smooth, dtype='int8')
```

And then because each of the chunks of a Dask array are just NumPy arrays, we
can use the `map_blocks` function to apply this function across all of our
images, and then save them out.

This is fine, but lets go a bit further, and discuss generalized universal
functions from NumPy.

## Generalized Universal Functions

**Numba Docs:** https://numba.pydata.org/numba-doc/dev/user/vectorize.html

**NumPy Docs:** https://docs.scipy.org/doc/numpy-1.16.0/reference/c-api.generalized-ufuncs.html

A generalized universal function (gufunc) is a normal function that has been
annotated with typing and dimension information. For example we can redefine
our `smooth` function as a gufunc as follows:

```python
@numba.guvectorize(
    [(numba.int8[:, :], numba.int8[:, :])],
    '(n, m) -> (n, m)'
)
def smooth(x, out):
    out[:] = _smooth(x)
```

This function knows that it consumes a 2d array of int8's and produces a 2d
array of int8's of the same dimensions.

This sort of annotation is a small change, but it gives other systems like Dask
enough information to use it intelligently. Rather than call functions like
`map_blocks`, we can just use the function directly, as if our Dask Array was
just a very large NumPy array.

```python
# Before gufuncs
y = x.map_blocks(smooth, dtype='int8')

# After gufuncs
y = smooth(x)
```

This is nice. If you write library code with gufunc semantics then that code
just works with systems like Dask, without you having to build in explicit
support for parallel computing. This makes the lives of users much easier.

## Finished result

Lets see the full example one more time.

```python
import numba
import dask.array as da

@numba.stencil
def _smooth(x):
    return (x[-1, -1] + x[-1, 0] + x[-1, 1] +
            x[ 0, -1] + x[ 0, 0] + x[ 0, 1] +
            x[ 1, -1] + x[ 1, 0] + x[ 1, 1]) // 9


@numba.guvectorize(
    [(numba.int8[:, :], numba.int8[:, :])],
    '(n, m) -> (n, m)'
)
def smooth(x, out):
    out[:] = _smooth(x)

x = da.ones((1000000, 1000, 1000), chunks=('auto', -1, -1), dtype='int8')
smooth(x)
```

This code is decently approachable by novice users. They may not understand
the internal details of gufuncs or Dask arrays or JIT compilation, but they can
probably copy-paste-and-modify the example above to suit their needs.

The parts that they do want to change are easy to change, like the stencil
computation, and creating an array of their own data.

This workflow is efficient and scalable, using low-level compiled code and
potentially clusters of thousands of computers.

## What could be better

There are a few things that could make this workflow nicer.

1.  It would be nice not to have to specify dtypes in `guvectorize`, but
    instead specialize to types as they arrive.
    [numba/numba #2979](https://github.com/numba/numba/issues/2979)

2.  Support GPU accelerators for the stencil computations using
    [numba.cuda.jit](https://numba.pydata.org/numba-doc/dev/cuda/index.html).
    Stencil computations are obvious candidates for GPU acceleration, and this
    is a good accessible point where novice users can specify what they want in
    a way that is sufficiently constrained for automated systems to rewrite it
    as CUDA somewhat easily.
    [numba/numba 3915](https://github.com/numba/numba/issues/3915)

3.  It would have been nicer to be able to apply the `@guvectorize` decorator
    directly on top of the stencil function like this.

    ```python
    @numba.guvectorize(...)
    @numba.stencil
    def average(x):
        ...
    ```

    Rather than have two functions.
    [numba/numba #3914](https://github.com/numba/numba/issues/3914)

4.  You may have noticed that our guvectorize function had to assign its result into an
    out parameter.

    ```python
    @numba.guvectorize(
        [(numba.int8[:, :], numba.int8[:, :])],
        '(n, m) -> (n, m)'
    )
    def smooth(x, out):
        out[:] = _smooth(x)
    ```

    It would have been nicer, perhaps, to just return the output

    ```python
    def smooth(x):
        return _smooth(x)
    ```

    [numba/numba #3916](https://github.com/numba/numba/issues/3916)

5.  The dask-image library could use a `imsave` function

    [dask/dask-image #110](https://github.com/dask/dask-image/issues/110)

## Aspirational Result

With all of these, we might then be able to write the code above as follows

```python
# This is aspirational

import numba
import dask_image

@numba.guvectorize(
    [(numba.int8[:, :], numba.int8[:, :])],
    signature='(n, m) -> (n, m)',
    target='gpu'
)
@numba.stencil
def smooth(x):
    return (x[-1, -1] + x[-1, 0] + x[-1, 1] +
            x[ 0, -1] + x[ 0, 0] + x[ 0, 1] +
            x[ 1, -1] + x[ 1, 0] + x[ 1, 1]) // 9

x = dask_image.io.imread('/path/to/*.png')
y = smooth(x)
dask_image.io.imsave(y, '/path/to/out/*.png')
```

## Update: Now with GPUs!

After writing this blogpost I did a small update where I used
[numba.cuda.jit](https://numba.pydata.org/numba-doc/dev/cuda/index.html)
to implement the same smooth function on a GPU to achieve a 200x speedup with
only a modest increase to code complexity.

[That notebook is here](https://gist.github.com/mrocklin/9272bf84a8faffdbbe2cd44b4bc4ce3c).
