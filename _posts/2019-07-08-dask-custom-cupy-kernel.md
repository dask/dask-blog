---
layout: post
title: Distributing Custom CuPy Kernels with Dask
author: Peter Andreas Entschev
tags: [Dask, CuPy]
theme: twitter
---
{% include JB/setup %}


Summary
-------

Some weeks ago, Matthew Rocklin wrote a post on Numba Stencils with Dask,
demonstrating how to use it for both CPUs and GPUs. This post will show a similar
approach to writing custom code, this time with user-defined custom kernels in
CuPy. The motivation for this post comes from someone who recently asked how can
one use Dask to distribute such custom kernels, which is a question that will
surely arise again in the future.

Sample Problem
--------------

Let's get started by defining the problem we will look at in this post. The
problem here is merely for demonstration purposes, and not something very
complicated, nor particularly useful that someone would write a kernel to solve,
when you can do that directly (and quite easily) using CuPy built-in functions.

Assume you have two arrays, a 2D array `x` and a 1D array `y`, with dimensions
`MxN` and `N` respectively. We will add those arrays together, in other words,
we will add `y` to all `M` rows of `x`. As I mentioned before, the kernel we
will look at is quite simple, but the data organization is overly complicated
for this example on purpose, allowing us to demonstrate how to use `map_blocks`
for more complex situations, which are likely to happen in practice.

This example using CuPy alone would look something like the following:

```python
import cupy

x = cupy.arange(4096 * 1024, dtype=cupy.float32).reshape((4096, 1024))
y = cupy.arange(1024, dtype=cupy.float32)

res_cupy = x + y
```


Writing a custom kernel with CuPy
---------------------------------

For those familiar with CUDA kernels, this section will be easily understood. If
you're not familiar with that, feel free to skip this section, the upcoming
session entitled "Using Dask's `map_blocks`" may serve as a useful reference
for parallelizing custom code with Dask nevertheless.

To write a user-defined kernel, we will use the `cupy.RawKernel` function. This
is a very simple function, taking only three arguments: `code`, `name` and
`options`. As implied, the first two arguments are used to define the kernel
implementation and its name, the latter is used to pass optional arguments
to NVRTC (NVIDIA's RunTime Compiler), but will not talk about this last argument
during this post.

```python
add_broadcast_kernel = cupy.RawKernel(
    r'''
    extern "C" __global__
    void add_broadcast_kernel(const float* x, const float* y, float* z, const int dim0)
    {
        int idx0 = blockIdx.x * blockDim.x + threadIdx.x;
        int idx1 = blockIdx.y * blockDim.y + threadIdx.y;
        z[idx1 * dim0 + idx0] = x[idx1 * dim0 + idx0] + y[idx0];
    }
    ''',
    'add_broadcast_kernel'
)
```

We will need a dispatching function for that kernel as well. This function will
define a block size and compute the grid size based on the input sizes and the
block size defined, call the kernel we created before and finally return the
result.

```python
def dispatch_add_broadcast(x, y, z):
    block_size = (32, 32)
    grid_size = (x.shape[1] // block_size[1], x.shape[0] // block_size[0])
    add_broadcast_kernel(grid_size, block_size, (x, y, z, x.strides[0] // x.strides[1]))
    return z
```

We can now use that dispatch function and compute the sum of `x` and `y`. Note
that we have a third argument `z` in the function above, that is where the
output of the function will be stored. We could also have chosen to create that
array inside `dispatch_add_broadcast`, but for this example we chose not to,
because we will create a single Dask array to store the result later on.

```python
res_add_broadcast = dispatch_add_broadcast(x, y, cupy.empty((x.shape), dtype=cupy.float32))
```

The function above is equivalent to the previous `res_cupy = x + y`.


Using Dask's `map_blocks`
-------------------------

The `map_blocks` function in Dask is a very powerful tool, allowing developers
to write custom code and parallelize it in terms of the blocks of a Dask array.
Not only custom code can be written with `map_blocks`, existing functions from
libraries such as NumPy can be parallelized with its help too, if there's no
existing Dask implmentation for such function yet. In fact, various Dask
functions do exactly that, use `map_blocks` as a support for NumPy
parallelization.

So how do we use `map_blocks`? First, let's create Dask arrays from the CuPy
arrays `x` and `y` that we created previously, respectively calling them `dx`
and `dy`.

```python
import dask.array as da

dx = da.from_array(x, chunks=(1024, 512), asarray=False)
dy = da.from_array(y, chunks=(512), asarray=False)
```

We also create another array to store the output.

```python
z = cupy.empty((4096, 1024), dtype=cupy.float32)
dz = da.from_array(z, chunks=(1024, 512), asarray=False)
```

What is important to not here is the need match array and block sizes properly.
In this example we have `x` and `z` with sizes 4096x1024 and `y` with length
1024, so the length of `N` must match. The same is true for block sizes, here
we are creating 4 blocks on the first dimension and 2 on the second dimension of
`x`, thus we need to ensure that `y` is also split into 2 blocks. Since the
output array `z` will have the exact same shape of `x`, it must also have the
same number of blocks: 4x2.

The only thing left to do now is create a `map_blocks` task for the operation we
want execute. For this example, we will pass 5 arguments in total, our dispatch
function, the Dask arrays and the `dtype`.

```python
res = da.map_blocks(dispatch_add_broadcast, dx, dy, dz, dtype=cupy.float32)
```

If we compute the Dask array and print its output, we should see a matching
result with that of the CuPy array:


```python
res.compute()
array([[0.000000e+00, 2.000000e+00, 4.000000e+00, ..., 2.042000e+03,
        2.044000e+03, 2.046000e+03],
       [1.024000e+03, 1.026000e+03, 1.028000e+03, ..., 3.066000e+03,
        3.068000e+03, 3.070000e+03],
       [2.048000e+03, 2.050000e+03, 2.052000e+03, ..., 4.090000e+03,
        4.092000e+03, 4.094000e+03],
       ...,
       [4.191232e+06, 4.191234e+06, 4.191236e+06, ..., 4.193274e+06,
        4.193276e+06, 4.193278e+06],
       [4.192256e+06, 4.192258e+06, 4.192260e+06, ..., 4.194298e+06,
        4.194300e+06, 4.194302e+06],
       [4.193280e+06, 4.193282e+06, 4.193284e+06, ..., 4.195322e+06,
        4.195324e+06, 4.195326e+06]], dtype=float32)

res_cupy
array([[0.000000e+00, 2.000000e+00, 4.000000e+00, ..., 2.042000e+03,
        2.044000e+03, 2.046000e+03],
       [1.024000e+03, 1.026000e+03, 1.028000e+03, ..., 3.066000e+03,
        3.068000e+03, 3.070000e+03],
       [2.048000e+03, 2.050000e+03, 2.052000e+03, ..., 4.090000e+03,
        4.092000e+03, 4.094000e+03],
       ...,
       [4.191232e+06, 4.191234e+06, 4.191236e+06, ..., 4.193274e+06,
        4.193276e+06, 4.193278e+06],
       [4.192256e+06, 4.192258e+06, 4.192260e+06, ..., 4.194298e+06,
        4.194300e+06, 4.194302e+06],
       [4.193280e+06, 4.193282e+06, 4.193284e+06, ..., 4.195322e+06,
        4.195324e+06, 4.195326e+06]], dtype=float32)
```

And now we're done!


Conclusion
----------

The topic discussed in this post may seem like a lot of work, and it actually is
if we consider that we can do the same in about three lines of code. But now
consider writing a small CUDA kernel that is custom and highly optimized, the
alternative to this would probably be creating a C++ file, writing both host
code and the CUDA kernel, compiling it, exposing the API through CPython or
something similar, this is definitely much more work.

This post aimed to explain how CuPy and Dask allow extending their capabilities,
thus giving users the capabilities to write self-contained and easily
maintainable applications, even when lower-level language code, such as CUDA, is
needed to provide best performance.
