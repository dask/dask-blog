---
layout: post
title: Single-GPU CuPy Benchmarks
author: Peter Andreas Entschev
tags: [CuPy, SVD]
theme: twitter
---
{% include JB/setup %}


Summary
-------

Array operations with GPUs can provide considerable speedups over CPU computing,
but the amount of speedup varies greatly depending on the operation. The intent
of this blog post is to benchmark CuPy performance for various different
operations. We can definitely plug Dask in to enable multi-GPU performance gains,
as discussed
[in this post from March](https://blog.dask.org/2019/03/18/dask-nep18), but here
we will only look at individual performance for single-GPU CuPy.


Hardware and Software Setup
---------------------------

Before going any further, assume the following hardware and software is
utilized for all performance results described in this post:

* System: NVIDIA DGX-1
* CPU: 2x Intel Xeon E5-2698 v4 @ 2.20GHz
* Main memory: 1 TB
* GPU: NVIDIA Tesla V100 32 GB
* Python 3.7.3
* NumPy 1.16.4
* Intel MKL 2019.4.243
* CuPy 6.1.0
* CUDA Toolkit 9.2


General Performance
-------------------

I have generated a greph comprising various operations. Most of them perform
well on a GPU using CuPy out of the box. See the graph below:

<img src="/images/single-gpu-cupy-benchmarks.png">

I have recently started working on a
[simple benchmark suite](https://github.com/pentschev/pybench) to help me
benchmark things quickly and reliably, as well as to automate some plotting,
it's still incomplete and lacks documentation, which I intend to improve during
the next days, and it is what I used to generate the plot above. If you're
interested in figuring out exactly how synthetic data was generated and the
exact compute operation benchmarked, you can look at
[this file](https://github.com/pentschev/pybench/blob/master/pybench/benchmarks/benchmark_array.py).
I won't go into too much details of how this benchmark suite works right now,
but I also intend to write something about it in the near future, when it's a
bit more mature and easier to use.

As seen on the graph, we can get 270x speedup for elementwise operations. Not
too bad for not having to write any parallel code by hand. However, the speedup
is immensely affected by nature of each operation. I am not going to get too
deep in why each operation performs differently in this post, but I will
continue that on a future post.

Let me briefly describe each of the operations from the graph above:

* Elementwise: scalar operation on all elements of the array
* Sum: Compute sum of entire array, reducing it to a single scalar
* Sum With CUB: same as previous, but using [CUB](https://nvlabs.github.io/cub/),
    still [under development](https://github.com/cupy/cupy/pull/2090)
* Standard deviation: Compute standard deviation of entire array, reducing
    it to a single scalar
* Array Slicing: select every third element of first dimension
* Matrix Multiplication: Multiplication of two square matrices
* FFT: Fast Fourier Transform of matrix
* SVD: Singular Value Decomposition of matrix (tall-and-skinny for larger
    array)
* Stencil (*Not a CuPy operation!*):
    [uniform filtering with Numba](https://blog.dask.org/2019/04/09/numba-stencil)

It's important to note that there are two array sizes, 800 MB and 8 MB, the
first means 10000x10000 arrays and the latter 1000x1000, double-precision
floating-point (8 bytes) in both cases. SVD array size is an exception, where
the large size is actually a tall-and-skinny of size 10000x1000, or 80MB.


Future Work
-----------

For better understanding of the speedups (or slowdowns) seen in this post,
we definitely need a careful analysis of what happens in those cases.

It's also important to have standard benchmarks, the benchmark suite should
be improved, made more general-purpose and be properly documented as well.
