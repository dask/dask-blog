---
layout: post
title: Towards Out-of-core ND-Arrays -- Benchmark MatMul
category : work
tags : [scipy, Python, Programming, Blaze, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr** We benchmark dask on an out-of-core dot product.  We also compare and
motivate the use of an optimized BLAS.

**Here are the results**

<table>
  <thead>
  <tr>
    <th>Performance (GFLOPS)</th>
    <th>In-Memory</th>
    <th>On-Disk</th>
  </tr>
  </thead>
  <tbody>
    <tr>
      <th>Reference BLAS</th>
      <td>6</td>
      <td>18</td>
    </tr>
    <tr>
      <th>OpenBLAS one thread</th>
      <td>11</td>
      <td>23</td>
    </tr>
    <tr>
      <th>OpenBLAS four threads</th>
      <td>22</td>
      <td>11</td>
    </tr>
  </tbody>
</table>

*Disclaimer: This post is on experimental buggy code.  This is not ready for public use.*

Introduction
------------

This is the fourth in a sequence of posts constructing an out-of-core nd-array
using NumPy, Blaze, and dask.  You can view these posts here:

1. [Simple task scheduling](http://matthewrocklin.com/blog/work/2014/12/27/Towards-OOC/),
2. [Frontend usability](http://matthewrocklin.com/blog/work/2014/12/30/Towards-OOC-Frontend/)
3. [A multi-threaded scheduler](http://matthewrocklin.com/blog/work/2015/01/06/Towards-OOC-Scheduling/)

We now give performance numbers on out-of-core matrix-matrix multiplication.


Matrix-Matrix Multiplication
----------------------------

Dense matrix-matrix multiplication is compute-bound, not I/O bound.
We spend most of our time doing arithmetic and relatively little time shuffling
data around.  As a result we may be able to read *large* data from disk without
performance loss.

When multiplying two $n\times n$ matrices we read $n^2$ bytes but perform $n^3$
computations.  There are $n$ computations to do per byte so, relatively
speaking, I/O is cheap.

We normally measure speed for single CPUs in Giga Floating Point Operations
Per Second (GFLOPS).  Lets look at how my laptop does on single-threaded
in-memory matrix-matrix multiplication using NumPy.

{% highlight Python %}
>>> import numpy as np
>>> x = np.ones((1000, 1000), dtype='f8')
>>> %timeit x.dot(x)  # Matrix-matrix multiplication
10 loops, best of 3: 176 ms per loop

>>> 1000 ** 3 / 0.176 / 1e9  # n cubed computations / seconds / billion
>>> 5.681818181818182
{% endhighlight %}

OK, so NumPy's matrix-matrix multiplication clocks in at 6 GFLOPS more or
less.  The `np.dot` function ties in to the `GEMM` operation in the `BLAS`
library on my machine.  Currently my `numpy` just uses reference BLAS. (you can
check this with `np.show_config()`.)


Matrix-Matrix Multiply From Disk
--------------------------------

For matrices too large to fit in memory we compute the solution one part at a
time, loading blocks from disk when necessary.  We parallelize this with
multiple threads.  Our last post demonstrates how NumPy+Blaze+Dask automates
this for us.

We perform a simple numerical experiment, using HDF5 as our on-disk store.

We install stuff

{% highlight bash %}
$ conda install -c blaze blaze
$ pip install git+https://github.com/ContinuumIO/dask
{% endhighlight %}

We set up a fake dataset on disk

{% highlight Python %}
>>> import h5py
>>> f = h5py.File('myfile.hdf5')
>>> A = f.create_dataset(name='A', shape=(200000, 4000), dtype='f8',
...                                chunks=(250, 250), fillvalue=1.0)
>>> B = f.create_dataset(name='B', shape=(4000, 4000), dtype='f8',
...                                chunks=(250, 250), fillvalue=1.0)
{% endhighlight %}

We tell Dask+Blaze how to interact with that dataset

{% highlight Python %}
>>> from dask.obj import Array
>>> from blaze import Data, into

>>> a = into(Array, 'myfile.hdf5::/A', blockshape=(1000, 1000))  # dask things
>>> b = into(Array, 'myfile.hdf5::/B', blockshape=(1000, 1000))
>>> A = Data(a)  # Blaze things
>>> B = Data(b)
{% endhighlight %}

We compute our desired result, storing back onto disk

{% highlight Python %}
>>> %time into('myfile.hdf5::/result', A.dot(B))
2min 49s

>>> 200000 * 4000 * 4000 / 169 / 1e9
18.934911242
{% endhighlight %}


18.9 GFLOPS, roughly 3 times faster than the in-memory solution.  At first
glance this is confusing - shouldn't we be slower coming from disk?  Our
speedup is due to our use of four cores in parallel.  This is good, we don't
experience much slowdown coming from disk.

It's as if all of our hard drive just became memory.


OpenBLAS
--------

Reference BLAS is slow; it was written long ago.  OpenBLAS is a modern
implementation.  I installed OpenBLAS with my system installer (`apt-get`) and
then reconfigured and rebuilt numpy.  OpenBLAS supports many cores.  We'll show
timings with one and with four threads.

{% highlight bash %}
$ export OPENBLAS_NUM_THREADS=1
$ ipython
{% endhighlight %}
{% highlight Python %}
>>> import numpy as np
>>> x = np.ones((1000, 1000), dtype='f8')
>>> %timeit x.dot(x)
10 loops, best of 3: 89.8 ms per loop

>>> 1000 ** 3 / 0.0898 / 1e9  # compute GFLOPS
11.135857461024498
{% endhighlight %}


{% highlight bash %}
$ export OPENBLAS_NUM_THREADS=4
$ ipython
{% endhighlight %}
{% highlight Python %}
>>> %timeit x.dot(x)
10 loops, best of 3: 46.3 ms per loop

>>> 1000 ** 3 / 0.0463 / 1e9  # compute GFLOPS
21.598272138228943
{% endhighlight %}

This is about four times faster than reference.  If you're not already
parallelizing in some other way (like with `dask`) then you should use a modern
BLAS like OpenBLAS or MKL.


OpenBLAS + dask
---------------

Finally we run on-disk our experiment again, now with OpenBLAS.  We do this
both with OpenBLAS running with one thread and with many threads.

We'll skip the code (it's identical to what's above) and give a comprehensive
table of results below.

Sadly the out-of-core solution doesn't improve much by using OpenBLAS.
Acutally when both OpenBLAS and dask try to parallelize we *lose* performance.


Results
-------

<table>
  <thead>
  <tr>
    <th>Performance (GFLOPS)</th>
    <th>In-Memory</th>
    <th>On-Disk</th>
  </tr>
  </thead>
  <tbody>
    <tr>
      <th>Reference BLAS</th>
      <td>6</td>
      <td>18</td>
    </tr>
    <tr>
      <th>OpenBLAS one thread</th>
      <td>11</td>
      <td>23</td>
    </tr>
    <tr>
      <th>OpenBLAS four threads</th>
      <td>22</td>
      <td>11</td>
    </tr>
  </tbody>
</table>

**tl:dr** When doing compute intensive work, don't worry about using disk, just
don't use two mechisms of parallelism at the same time.


Main Take-Aways
---------------

1.  We don't lose much by operating from disk in compute-intensive tasks
2.  Actually we can improve performance when an optimized BLAS isn't avaiable.
3.  Dask doesn't benefit much from an optimized BLAS.  This is sad and surprising.  I expected performance to scale with single-core in-memory performance.  Perhaps this is indicative of some other limiting factor
4.  One shouldn't extrapolate too far with these numbers.  They're only relevant for highly compute-bound operations like matrix-matrix multiply

Also, thanks to Wesley Emeneker for finding where we were leaking memory,
making results like these possible.
