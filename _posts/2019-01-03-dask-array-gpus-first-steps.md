---
layout: post
title: GPU Dask Arrays, first steps
tagline: throwing Dask and CuPy together
author: Matthew Rocklin
tags: [GPU, array, cupy]
theme: twitter
---

{% include JB/setup %}

The following code creates and manipulates 2 TB of randomly generated data.

```python
import dask.array as da

rs = da.random.RandomState()
x = rs.normal(10, 1, size=(500000, 500000), chunks=(10000, 10000))
(x + 1)[::2, ::2].sum().compute(scheduler='threads')
```

On a single CPU, this computation takes two hours.

On an eight-GPU single-node system this computation takes nineteen seconds.

## Combine Dask Array with CuPy

Actually this computation isn't that impressive.
It's a simple workload,
for which most of the time is spent creating and destroying random data.
The computation and communication patterns are simple,
reflecting the simplicity commonly found in data processing workloads.

What _is_ impressive is that we were able to create a distributed parallel GPU
array quickly by composing these four existing libraries:

1.  [CuPy](https://cupy.chainer.org/) provides a partial implementation of
    Numpy on the GPU.

2.  [Dask Array](https://docs.dask.org/en/latest/array.html) provides chunked
    algorithms on top of Numpy-like libraries like Numpy and CuPy.

    This enables us to operate on more data than we could fit in memory
    by operating on that data in chunks.

3.  The [Dask distributed](https://distributed.dask.org) task scheduler runs
    those algorithms in parallel, easily coordinating work across many CPU
    cores.

4.  The [Dask CUDA](https://github.com/rapidsai/dask-cuda) to extend Dask
    distributed with GPU support.

These tools already exist. We had to connect them together with a small amount
of glue code and minor modifications. By mashing these tools together we can
quickly build and switch between different architectures to explore what is
best for our application.

For this example we relied on the following changes upstream:

- [cupy/cupy #1689: Support Numpy arrays as seeds in RandomState](https://github.com/cupy/cupy/pull/1689)
- [dask/dask #4041 Make da.RandomState accessible to other modules](https://github.com/dask/dask/pull/4041)
- [dask/distributed #2432: Add LocalCUDACluster](https://github.com/dask/distributed/pull/2432)

## Comparison among single/multi CPU/GPU

We can now easily run some experiments on different architectures. This is
easy because ...

- We can switch between CPU and GPU by switching between Numpy and CuPy.
- We can switch between single/multi-CPU-core and single/multi-GPU
  by switching between Dask's different task schedulers.

These libraries allow us to quickly judge the costs of this computation for
the following hardware choices:

1.  Single-threaded CPU
2.  Multi-threaded CPU with 40 cores (80 H/T)
3.  Single-GPU
4.  Multi-GPU on a single machine with 8 GPUs

We present code for these four choices below,
but first,
we present a table of results.

### Results

<table border="1" class="dataframe">
  <thead>
  <tr>
    <th>Architecture</th>
    <th>Time</th>
  </tr>
  </thead>
  <tbody>
    <tr>
      <th> Single CPU Core </th>
      <td> 2hr 39min </td>
    </tr>
    <tr>
      <th> Forty CPU Cores </th>
      <td> 11min 30s </td>
    </tr>
    <tr>
      <th> One GPU </th>
      <td> 1 min 37s </td>
    </tr>
    <tr>
      <th> Eight GPUs </th>
      <td> 19s </td>
    </tr>
  </tbody>
</table>

### Setup

```python
import cupy
import dask.array as da

# generate chunked dask arrays of mamy numpy random arrays
rs = da.random.RandomState()
x = rs.normal(10, 1, size=(500000, 500000), chunks=(10000, 10000))

print(x.nbytes / 1e9)  # 2 TB
# 2000.0
```

### CPU timing

```python
(x + 1)[::2, ::2].sum().compute(scheduler='single-threaded')
(x + 1)[::2, ::2].sum().compute(scheduler='threads')
```

### Single GPU timing

We switch from CPU to GPU by changing our data source to generate CuPy arrays
rather than NumPy arrays. Everything else should more or less work the same
without special handling for CuPy.

_(This actually isn't true yet, many things in dask.array will break for
non-NumPy arrays, but we're working on it actively both within Dask, within
NumPy, and within the GPU array libraries. Regardless, everything in this
example works fine.)_

```python
# generate chunked dask arrays of mamy cupy random arrays
rs = da.random.RandomState(RandomState=cupy.random.RandomState)  # <-- we specify cupy here
x = rs.normal(10, 1, size=(500000, 500000), chunks=(10000, 10000))
```

```python
(x + 1)[::2, ::2].sum().compute(scheduler='single-threaded')
```

### Multi GPU timing

```python
from dask_cuda import LocalCUDACluster
from dask.distributed import Client

cluster = LocalCUDACluster()
client = Client(cluster)

(x + 1)[::2, ::2].sum().compute()
```

And again, here are the results:

<table border="1" class="dataframe">
  <thead>
  <tr>
    <th>Architecture</th>
    <th>Time</th>
  </tr>
  </thead>
  <tbody>
    <tr>
      <th> Single CPU Core </th>
      <td> 2hr 39min </td>
    </tr>
    <tr>
      <th> Forty CPU Cores </th>
      <td> 11min 30s </td>
    </tr>
    <tr>
      <th> One GPU </th>
      <td> 1 min 37s </td>
    </tr>
    <tr>
      <th> Eight GPUs </th>
      <td> 19s </td>
    </tr>
  </tbody>
</table>

First, this is my first time playing with an 40-core system. I was surprised
to see that many cores. I was also pleased to see that Dask's normal threaded
scheduler happily saturates many cores.

<img src="https://matthewrocklin.com/blog/images/python-gil-8000-percent.png" width="100%">

Although later on it did dive down to around 5000-6000%, and if you do the math
you'll see that we're not getting a 40x speedup. My _guess_ is that
performance would improve if we were to play with some mixture of threads and
processes, like having ten processes with eight threads each.

The jump from the biggest multi-core CPU to a single GPU is still an order of
magnitude though. The jump to multi-GPU is another order of magnitude, and
brings the computation down to 19s, which is short enough that I'm willing to
wait for it to finish before walking away from my computer.

Actually, it's quite fun to watch on the dashboard (especially after you've
been waiting for three hours for the sequential solution to run):

<blockquote class="imgur-embed-pub"
            lang="en"
            data-id="a/6hkPPwA">
<a href="//imgur.com/6hkPPwA"></a>
</blockquote>
<script async src="//s.imgur.com/min/embed.js" charset="utf-8"></script>

## Conclusion

This computation was simple, but the range in architecture just explored was
extensive. We swapped out the underlying architecture from CPU to GPU (which
had an entirely different codebase) and tried both multi-core CPU parallelism
as well as multi-GPU many-core parallelism.

We did this in less than twenty lines of code, making this experiment something
that an undergraduate student or other novice could perform at home.
We're approaching a point where experimenting with multi-GPU systems is
approachable to non-experts (at least for array computing).

[Here is a notebook for the experiment above](https://gist.github.com/mrocklin/57be0ca4143974e6015732d0baacc1cb)

## Room for improvement

We can work to expand the computation above in a variety of directions.
There is a ton of work we still have to do to make this reliable.

1.  **Use more complex array computing workloads**

    The Dask Array algorithms were designed first around Numpy. We've only
    recently started making them more generic to other kinds of arrays (like
    GPU arrays, sparse arrays, and so on). As a result there are still many
    bugs when exploring these non-Numpy workloads.

    For example if you were to switch `sum` for `mean` in the computation above
    you would get an error because our `mean` computation contains an easy to
    fix error that assumes Numpy arrays exactly.

2.  **Use Pandas and cuDF instead of Numpy and CuPy**

    The cuDF library aims to reimplement the Pandas API on the GPU,
    much like how CuPy reimplements the NumPy API.
    Using Dask DataFrame with cuDF will require some work on both sides,
    but is quite doable.

    I believe that there is plenty of low-hanging fruit here.

3.  **Improve and move LocalCUDACluster**

    The `LocalCUDAClutster` class used above is an experimental `Cluster` type
    that creates as many workers locally as you have GPUs, and assigns each
    worker to prefer a different GPU. This makes it easy for people to load
    balance across GPUs on a single-node system without thinking too much about
    it. This appears to be a common pain-point in the ecosystem today.

    However, the LocalCUDACluster probably shouldn't live in the
    `dask/distributed` repository (it seems too CUDA specific) so will probably
    move to some dask-cuda repository. Additionally there are still many
    questions about how to handle concurrency on top of GPUs, balancing between
    CPU cores and GPU cores, and so on.

4.  **Multi-node computation**

    There's no reason that we couldn't accelerate computations like these
    further by using multiple multi-GPU nodes. This is doable today with
    manual setup, but we should also improve the existing deployment solutions
    [dask-kubernetes](https://kubernetes.dask.org),
    [dask-yarn](https://yarn.dask.org), and
    [dask-jobqueue](https://jobqueue.dask.org), to make this easier for
    non-experts who want to use a cluster of multi-GPU resources.

5.  **Expense**

    The machine I ran this on is expensive. Well, it's nowhere close to as
    expensive to own and operate as a traditional cluster that you would need
    for these kinds of results, but it's still well beyond the price point of a
    hobbyist or student.

    It would be useful to run this on a more budget system to get a sense of
    the tradeoffs on more reasonably priced systems. I should probably also
    learn more about provisioning GPUs on the cloud.

### Come help!

If the work above sounds interesting to you then come help!
There is a lot of low-hanging and high impact work to do.

If you're interested in being paid to focus more on these topics, then consider
applying for a job. The NVIDIA corporation is hiring around the use of Dask
with GPUs.

- [Senior Library Software Engineer - RAPIDS](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-TX-Austin/Senior-Library-Software-Engineer---RAPIDS_JR1919608-1)

That's a fairly generic posting. If you're interested the posting doesn't seem
to fit then please apply anyway and we'll tweak things.
