---
layout: post
title: Very Large SVDs
tagline: Dask + CuPy + Zarr + Genomics
author: Matthew Rocklin & Alistair Miles
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

In the end we compute an approximate SVD of 200GB of simulated data and using a mutli-GPU machine in 15-20 seconds.  Then we run this from a dataset stored in the cloud I/O is, predictably, a major bottleneck.


SVD - The simple case
---------------------

Dask arrays contain a relatively sophisticated SVD algorithm that works in the
tall-and-skinny or short-and-fat cases, but not so well in the roughly-square
case.  It works by taking QR decompositions of each block of the array,
combining the R matrices somehow, doing another smaller SVD on those, and then
performing some matrix multiplication to get back to the full result.  It's
numerically stable and decently fast, assuming that the intermediate R
matrices of the QR decompositions mostly fit in memory.

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


This works fine in the short and fat case too (when you have far more columns
than rows) but we're always going to assume that one of your dimensions is
unchunked, and that the other dimension has chunks that are quite a bit
longer, otherwise, things might not fit into memory.


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

Many studies are using genome sequencing to study genetic variation
between different individuals within a species.  These includes
studies of human populations, but also other species such as mice,
mosquitoes or disease-causing parasites.  These studies will, in
general, find a large number of sites in the genome sequence where
individuals differ from each other.  For example, humans have more
than 100 million variable sites in the genome, and modern studies
like the [UK BioBank](https://www.ukbiobank.ac.uk/) are working towards
sequencing the genomes of 1 million individuals or more.

In diploid species like humans, mice or mosquitoes, each individual
carries two genome sequences, one inherited from each parent.  At each
of the 100 million variable genome sites there will be two or more
"alleles" that a single genome might carry.  One way to think about
this is via the [Punnett
square](https://en.wikipedia.org/wiki/Punnett_square), which
represents the different possible genotypes that one individual might
carry at one of these variable sites:

<td>
<img src="https://upload.wikimedia.org/wikipedia/commons/9/93/Punnett_Square_Genetic_Carriers.PNG" alt="punnet square" height="40%" width="40%">
</td>

In the above there are three possible genotypes: AA, Aa, and aa.  For
computational genomics, these genotypes can be encoded as 0, 1, or 2.
In a study of a species with M genetic variants assayed in N
individual samples, we can represent these genotypes as an (N x M)
array of integers.  For a modern human genetics study, the scale of
this array might approach (100 million x 1 million).  (Although in
practice, the size of the first dimension (number of variants) can be
reduced somewhat, by at least an order of magnitude, because many
genetic variants will carry little information and/or be correlated
with each other.)

These genetic differences are not random, but carry information about
patterns of genetic similarity and shared ancestry between
individuals, because of the way they have been inherited through many
generations.  A common task is to perform a dimensionality reduction
analysis on these data, such as a [principal components
analysis](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.0020190)
(SVD), to identify genetic structure reflecting these differencies in
degree of shared ancestry.  This is an essential part of discovering
genetic variants associated with different diseases, and for learning
more about the genetic history of populations and species.

Reducing the time taken to compute an analysis such as SVD, like all
science, allows for exploring larger datasets and testing more
hypotheses in less time.  Practically, this means not simply a fast
SVD but an accelerated pipeline end-to-end, from data loading to
analysis, to understanding.

*We want to run an experiment in less time than it take to make a cup of tea*

Performant SVDs w/ Dask
-----------------------

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

I can happily perform an SVD on a 20GB array on my Macbook Pro

```python
import dask.array as da

x = da.random.random(size=(1_000_000, 20_000), chunks=(20_000, 5_000))

u, s, v = da.linalg.svd_compressed(x, k=10, compute=True)
v.compute()
```

This call is no longer entirely lazy, and it recomputes `x` a couple times, but
it works, and it works using only a few GB of RAM on my consumer laptop.

It takes around 2min 30s time to compute that on my laptop.  That's great!  But we can do better


Adding GPUs (a 15 second SVD)
-----------------------------

We can increase performance considerably by using a multi-GPU machine.
Here is almost the same code, running in significantly less same time but we make the
following changes:

1.  We increase the size of the array by a factor of **10x**
2.  We switch out NumPy for CuPy, a GPU NumPy implementation
3.  We use a sixteen-GPU DGX-2 machine with NVLink interconnects between GPUs (this will dramatically decrease transfer time between workers)

On A DGX2 we can calculate an SVD on a 200GB Dask array between 10 and15 seconds: [SVD Multi-GPU Notebook](https://gist.github.com/quasiben/98ee254920837313946f621e103d41f4)

To see this run, we recommend viewing
[the attached screencast](https://youtu.be/4X5yky2lvEw)


Read dataset from Disk
----------------------

While impressive, the computation above is mostly bound by generating random
data and then performing matrix calculations.  GPUs are good at both of these
things.

In practice though, our input array won't be randomly generated, it will be
coming from some dataset stored on disk or increasingly more common, stored in the cloud.
To make things more realistic we perform a similar calculation with data stored in a [Zarr format](https://zarr.readthedocs.io/en/stable/) (which is what Alistair, our genomics collaborator, uses) in [GCS](https://cloud.google.com/storage)

In this [Zarr SVD example](https://gist.github.com/quasiben/e52bc740ae22ae321f30987c65998078), we load a 25GB GCS backed data set onto a DGX2,

Again, on a DGX2, from data loading to SVD we are running in time less than it take to make a cup of tea.

And so we come back to a common lesson of high performance computing:

*High performance computing isn't about doing one thing exceedingly well, it's
about doing nothing poorly*.

In this case GPUs made our computation fast enough that we now need to focus on
other components of our system, notably disk bandwidth, and a direct reader for
Zarr data to GPU memory.
