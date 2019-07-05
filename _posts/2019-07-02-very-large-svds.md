---
layout: post
title: Very Large SVDs
tagline: Dask + CuPy + Zarr + Genomics
author: Matthew Rocklin
tags: [GPU, array, cupy]
draft: true
theme: twitter
---
{% include JB/setup %}

Summary
-------

We perform Singular Value Decomposition (SVD) calculations on large datasets.

We modify the computation both by using fully precise and approximate methods,
and by using both CPUs and GPUs.

In the end we compute the approximate SVD of an 80TB dataset in a few minutes
using a mutli-GPU machine.  Then we run this from a dataset stored on disk and
found that disk I/O is, predictably, a major bottleneck.


SVD - The simple case
---------------------

Dask array contains a relatively sophisticated SVD algorithm that works in the
tall-and-skinny or short-and-fat cases, but not so well in the roughly-square
case.  It works by taking QR decompositions of each block of the array,
combining the R matrices somehow, doing another smaller SVD on those, and then
performing some matrix multiplies to get back to the full result.  It's
numerically stable and decently fast, assumming that the intermediate R
matrices of the QR decompositions mostly fit in RAM.

The memory constraints here are that if you have an `n` by `m` tall and
skinny array (`n >> m`) cut into `k` blocks then you need to have about `m**2 *
k` space.  This is true in many cases, including typical PCA machine learning
workloads, where you have tabular data with a few columns (hundreds at most)
and many rows.

It's easy to use and quite robust.

```python
import dask.array as da

x = da.random.random((10000000, 20))
x
```

<table>
<tr>
<td>
<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>
  </thead>
  <tbody>
    <tr><th> Bytes </th><td> 1.60 GB </td> <td> 100.00 MB </td></tr>
    <tr><th> Shape </th><td> (10000000, 20) </td> <td> (625000, 20) </td></tr>
    <tr><th> Count </th><td> 16 Tasks </td><td> 16 Chunks </td></tr>
    <tr><th> Type </th><td> float64 </td><td> numpy.ndarray </td></tr>
  </tbody></table>
</td>
<td>
<svg width="75" height="170" style="stroke:rgb(0,0,0);stroke-width:1" >

  <!-- Horizontal lines -->
  <line x1="0" y1="0" x2="25" y2="0" style="stroke-width:2" />
  <line x1="0" y1="7" x2="25" y2="7" />
  <line x1="0" y1="15" x2="25" y2="15" />
  <line x1="0" y1="22" x2="25" y2="22" />
  <line x1="0" y1="30" x2="25" y2="30" />
  <line x1="0" y1="37" x2="25" y2="37" />
  <line x1="0" y1="45" x2="25" y2="45" />
  <line x1="0" y1="52" x2="25" y2="52" />
  <line x1="0" y1="60" x2="25" y2="60" />
  <line x1="0" y1="67" x2="25" y2="67" />
  <line x1="0" y1="75" x2="25" y2="75" />
  <line x1="0" y1="82" x2="25" y2="82" />
  <line x1="0" y1="90" x2="25" y2="90" />
  <line x1="0" y1="97" x2="25" y2="97" />
  <line x1="0" y1="105" x2="25" y2="105" />
  <line x1="0" y1="112" x2="25" y2="112" />
  <line x1="0" y1="120" x2="25" y2="120" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="0" y1="0" x2="0" y2="120" style="stroke-width:2" />
  <line x1="25" y1="0" x2="25" y2="120" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="0.000000,0.000000 25.412617,0.000000 25.412617,120.000000 0.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Text -->
  <text x="12.706308" y="140.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" >20</text>
  <text x="45.412617" y="60.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,45.412617,60.000000)">10000000</text>
</svg>
</td>
</tr>
</table>


```python
u, s, v = da.linalg.svd(x)
```

<table>\n<tr>\n<td>\n<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>\n  </thead>\n  <tbody>\n    <tr><th> Bytes </th><td> 1.60 GB </td> <td> 100.00 MB </td></tr>\n    <tr><th> Shape </th><td> (10000000, 20) </td> <td> (625000, 20) </td></tr>\n    <tr><th> Count </th><td> 120 Tasks </td><td> 16 Chunks </td></tr>\n    <tr><th> Type </th><td> float64 </td><td> numpy.ndarray </td></tr>\n  </tbody></table>\n</td>\n<td>\n<svg width="75" height="170" style="stroke:rgb(0,0,0);stroke-width:1" >\n\n  <!-- Horizontal lines -->\n  <line x1="0" y1="0" x2="25" y2="0" style="stroke-width:2" />\n  <line x1="0" y1="7" x2="25" y2="7" />\n  <line x1="0" y1="15" x2="25" y2="15" />\n  <line x1="0" y1="22" x2="25" y2="22" />\n  <line x1="0" y1="30" x2="25" y2="30" />\n  <line x1="0" y1="37" x2="25" y2="37" />\n  <line x1="0" y1="45" x2="25" y2="45" />\n  <line x1="0" y1="52" x2="25" y2="52" />\n  <line x1="0" y1="60" x2="25" y2="60" />\n  <line x1="0" y1="67" x2="25" y2="67" />\n  <line x1="0" y1="75" x2="25" y2="75" />\n  <line x1="0" y1="82" x2="25" y2="82" />\n  <line x1="0" y1="90" x2="25" y2="90" />\n  <line x1="0" y1="97" x2="25" y2="97" />\n  <line x1="0" y1="105" x2="25" y2="105" />\n  <line x1="0" y1="112" x2="25" y2="112" />\n  <line x1="0" y1="120" x2="25" y2="120" style="stroke-width:2" />\n\n  <!-- Vertical lines -->\n  <line x1="0" y1="0" x2="0" y2="120" style="stroke-width:2" />\n  <line x1="25" y1="0" x2="25" y2="120" style="stroke-width:2" />\n\n  <!-- Colored Rectangle -->\n  <polygon points="0.000000,0.000000 25.412617,0.000000 25.412617,120.000000 0.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>\n\n  <!-- Text -->\n  <text x="12.706308" y="140.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" >20</text>\n  <text x="45.412617" y="60.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,45.412617,60.000000)">10000000</text>\n</svg>\n</td>\n</tr>\n</table>
<table>\n<tr>\n<td>\n<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>\n  </thead>\n  <tbody>\n    <tr><th> Bytes </th><td> 1.60 GB </td> <td> 100.00 MB </td></tr>\n    <tr><th> Shape </th><td> (10000000, 20) </td> <td> (625000, 20) </td></tr>\n    <tr><th> Count </th><td> 120 Tasks </td><td> 16 Chunks </td></tr>\n    <tr><th> Type </th><td> float64 </td><td> numpy.ndarray </td></tr>\n  </tbody></table>\n</td>\n<td>\n<svg width="75" height="170" style="stroke:rgb(0,0,0);stroke-width:1" >\n\n  <!-- Horizontal lines -->\n  <line x1="0" y1="0" x2="25" y2="0" style="stroke-width:2" />\n  <line x1="0" y1="7" x2="25" y2="7" />\n  <line x1="0" y1="15" x2="25" y2="15" />\n  <line x1="0" y1="22" x2="25" y2="22" />\n  <line x1="0" y1="30" x2="25" y2="30" />\n  <line x1="0" y1="37" x2="25" y2="37" />\n  <line x1="0" y1="45" x2="25" y2="45" />\n  <line x1="0" y1="52" x2="25" y2="52" />\n  <line x1="0" y1="60" x2="25" y2="60" />\n  <line x1="0" y1="67" x2="25" y2="67" />\n  <line x1="0" y1="75" x2="25" y2="75" />\n  <line x1="0" y1="82" x2="25" y2="82" />\n  <line x1="0" y1="90" x2="25" y2="90" />\n  <line x1="0" y1="97" x2="25" y2="97" />\n  <line x1="0" y1="105" x2="25" y2="105" />\n  <line x1="0" y1="112" x2="25" y2="112" />\n  <line x1="0" y1="120" x2="25" y2="120" style="stroke-width:2" />\n\n  <!-- Vertical lines -->\n  <line x1="0" y1="0" x2="0" y2="120" style="stroke-width:2" />\n  <line x1="25" y1="0" x2="25" y2="120" style="stroke-width:2" />\n\n  <!-- Colored Rectangle -->\n  <polygon points="0.000000,0.000000 25.412617,0.000000 25.412617,120.000000 0.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>\n\n  <!-- Text -->\n  <text x="12.706308" y="140.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" >20</text>\n  <text x="45.412617" y="60.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,45.412617,60.000000)">10000000</text>\n</svg>\n</td>\n</tr>\n</table>
<table>\n<tr>\n<td>\n<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>\n  </thead>\n  <tbody>\n    <tr><th> Bytes </th><td> 160 B </td> <td> 160 B </td></tr>\n    <tr><th> Shape </th><td> (20,) </td> <td> (20,) </td></tr>\n    <tr><th> Count </th><td> 120 Tasks </td><td> 1 Chunks </td></tr>\n    <tr><th> Type </th><td> float64 </td><td> numpy.ndarray </td></tr>\n  </tbody></table>\n</td>\n<td>\n<svg width="170" height="84" style="stroke:rgb(0,0,0);stroke-width:1" >\n\n  <!-- Horizontal lines -->\n  <line x1="0" y1="0" x2="120" y2="0" style="stroke-width:2" />\n  <line x1="0" y1="34" x2="120" y2="34" style="stroke-width:2" />\n\n  <!-- Vertical lines -->\n  <line x1="0" y1="0" x2="0" y2="34" style="stroke-width:2" />\n  <line x1="120" y1="0" x2="120" y2="34" style="stroke-width:2" />\n\n  <!-- Colored Rectangle -->\n  <polygon points="0.000000,0.000000 120.000000,0.000000 120.000000,34.501016 0.000000,34.501016" style="fill:#ECB172A0;stroke-width:0"/>\n\n  <!-- Text -->\n  <text x="60.000000" y="54.501016" font-size="1.0rem" font-weight="100" text-anchor="middle" >20</text>\n  <text x="140.000000" y="17.250508" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(0,140.000000,17.250508)">1</text>\n</svg>\n</td>\n</tr>\n</table>
<table>\n<tr>\n<td>\n<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>\n  </thead>\n  <tbody>\n    <tr><th> Bytes </th><td> 3.20 kB </td> <td> 3.20 kB </td></tr>\n    <tr><th> Shape </th><td> (20, 20) </td> <td> (20, 20) </td></tr>\n    <tr><th> Count </th><td> 120 Tasks </td><td> 1 Chunks </td></tr>\n    <tr><th> Type </th><td> float64 </td><td> numpy.ndarray </td></tr>\n  </tbody></table>\n</td>\n<td>\n<svg width="170" height="170" style="stroke:rgb(0,0,0);stroke-width:1" >\n\n  <!-- Horizontal lines -->\n  <line x1="0" y1="0" x2="120" y2="0" style="stroke-width:2" />\n  <line x1="0" y1="120" x2="120" y2="120" style="stroke-width:2" />\n\n  <!-- Vertical lines -->\n  <line x1="0" y1="0" x2="0" y2="120" style="stroke-width:2" />\n  <line x1="120" y1="0" x2="120" y2="120" style="stroke-width:2" />\n\n  <!-- Colored Rectangle -->\n  <polygon points="0.000000,0.000000 120.000000,0.000000 120.000000,120.000000 0.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>\n\n  <!-- Text -->\n  <text x="60.000000" y="140.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" >20</text>\n  <text x="140.000000" y="60.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(0,140.000000,60.000000)">20</text>\n</svg>\n</td>\n</tr>\n</table>


This works fine in the short and fat case too (when you have far more columns
than rows) but we're always going to assume that one of your dimensions is
unchunked, and that the other dimension has chunks that are quite a bit
longer, otherwise, things might not fit into RAM.


Approximate SVD
---------------

If your dataset is large in both dimensions then the algorithm above won't work
as is.  However, if you don't need exact results, or if you only need a few of
the components, then there are a number of excellent approximation algorithms.

Dask array has one of these approximation algorithms implemented in the
[da.linalg.svd_compressed](https://docs.dask.org/en/latest/array-api.html#dask.array.linalg.svd_compressed)
function.  And with it we can compute the approximate SVD of some very large
matrices, at least in theory.

I was recently working on a problem (explained below) and found that I was
still running out of memory when dealing with this algorithm.  There were two
challenges that I ran into:

1.  The algorithm requires multiple passes over the data, but the Dask task
    scheduler was keeping the input matrix in memory after it had been loaded once
    in order to avoid recomputation.
    Things still worked, but Dask had to move the data to disk and back
    repeatedly, which reduced performance significantly.

    We resolved this by including explicit persist/wait calls in the algorithm.

2.  Related chunks of data would be loaded at different times, and so would
    need to stick around longer than necessary to wait for their associated
    chunks.

    We resolved this by engaging task fusion as an optimization pass.

Before diving further into the technical solution
I'm going to quickly provide the use case that was motivating this work.


Application - Genomics
----------------------

Alistair Miles from XXX motivates the problem as follows:

TODO Alistair

We'll simulate the data with the following random array:


Multiple passes over the data and Fusion
----------------------------------------

To stop Dask from holding onto the data we intentionally trigger computation as
we build up the graph.  This is a bit atypical in Dask calculations (we prefer
to have as much of the computation at once before computing) but useful given
the multiple-pass nature of this problem.  This was a fairly easy change, and
is available in [dask/dask #5041](https://github.com/dask/dask/pull/5041).

Additionally, we found that it was helpful to turn on moderately wide task
fusion.

```python
import dask
dask.config.set(fuse_ave_width=5)
```

Then things work fine
---------------------

I can happily perform an SVD on a terabyte array on my Macbook Pro

```python
import dask.array as da

x = da.random.random(size=(1_000_000, 100_000), chunks=(1_000, 20_000))

u, s, v = da.linalg.svd_compressed(x, k=10, compute=True)
v.compute()
```

This call is no longer entirely lazy, and it recomputes `x` a couple times, but
it works, and it works using only a few GB of RAM on my comsumer laptop.

It takes around TODO time to compute that on my laptop.


Adding GPUs
-----------

We can increase performance considerably by using a multi-GPU machine.
Here is almost the same code, running in roughly the same time, except for the
following changes:

1.  We increase the size of the array by a factor of TODO
2.  We switch out NumPy for CuPy, a GPU NumPy implementation
3.  We use an eight-GPU DGX-1 machine

To see this run, we recommend looking at
[this point in the attached screencast](TODO)


Read dataset from Disk
----------------------

While impressive, the computation above is mostly bound by generating random
data and then performing matrix multiplies.  GPUs are good at both of these
things.

In practice though, our input array won't be randomly generated, it will be
coming from some dataset stored on disk (or some other storage system).
So to make things more realistic we generate our dataset, and then store it to
disk efficiently in the [Zarr format](https://zarr.readthedocs.io/en/stable/)
(which is what Alistair, our genomics collaborator, uses).

```python
import dask.array as da

x = da.random.randint(0, 4, size=..., chunks=...)
compressor=...
x.to_zarr(...)
```

When we rerun the computation (again on a smaller size) we find that we're
largely bound by reading from disk.


```python
x = da.from_zarr(...)
x = x.map_blocks(cupy.asarray)

u, s, v = da.linalg.svd_compressed(x, k=10, compute=True, seed=rs)
v.compute()
```

And so we come back to a common lesson of high performance computing:

*High performance computing isn't about doing one thing exceedingly well, it's
about doing nothing poorly*.

In this case GPUs made our computation fast enough that we now need to focus on
other components of our system, notably disk bandwidth, and a direct reader for
Zarr data to GPU memory.
