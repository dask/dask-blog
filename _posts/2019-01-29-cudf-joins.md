---
layout: post
title: Single-Node Multi-GPU Dataframe Joins
author: Matthew Rocklin
tags: [dataframe, GPU]
theme: twitter
---

{% include JB/setup %}

## Summary

We experiment with single-node multi-GPU joins using cuDF and Dask. We find
that the in-GPU computation is faster than communication. We also present
context and plans for near-future work, including improving high performance
communication in Dask with UCX.

[Here is a notebook of the experiment in this post](https://gist.github.com/mrocklin/6e2c33c33b32bc324e3965212f202f66)

## Introduction

In a recent post we showed how Dask + cuDF could accelerate reading CSV files
using multiple GPUs in parallel. That operation quickly became bound by the
speed of our disk after we added a few GPUs. Now we try a very different kind
of operation, multi-GPU joins.

This workload can be communication-heavy, especially if the column on which we
are joining is not sorted nicely, and so provides a good example on the other
extreme from parsing CSV.

## Benchmark

### Construct random data using the CPU

Here we use Dask array and Dask dataframe to construct two random tables with a
shared `id` column. We can play with the number of rows of each table and the
number of keys to make the join challenging in a variety of ways.

```python
import dask.array as da
import dask.dataframe as dd

n_rows = 1000000000
n_keys = 5000000

left = dd.concat([
    da.random.random(n_rows).to_dask_dataframe(columns='x'),
    da.random.randint(0, n_keys, size=n_rows).to_dask_dataframe(columns='id'),
], axis=1)

n_rows = 10000000

right = dd.concat([
    da.random.random(n_rows).to_dask_dataframe(columns='y'),
    da.random.randint(0, n_keys, size=n_rows).to_dask_dataframe(columns='id'),
], axis=1)
```

### Send to the GPUs

We have two Dask dataframes composed of many Pandas dataframes of our random
data. We now map the `cudf.from_pandas` function across these to make a Dask
dataframe of cuDF dataframes.

```python
import dask
import cudf

gleft = left.map_partitions(cudf.from_pandas)
gright = right.map_partitions(cudf.from_pandas)

gleft, gright = dask.persist(gleft, gright)  # persist data in device memory
```

What's nice here is that there wasn't any special
`dask_pandas_dataframe_to_dask_cudf_dataframe` function. Dask composed nicely
with cuDF. We didn't need to do anything special to support it.

We'll also persisted the data in device memory.

After this, simple operations are easy and fast and use our eight GPUs.

```python
>>> gleft.x.sum().compute()  # this takes 250ms
500004719.254711
```

### Join

We'll use standard Pandas syntax to merge the datasets, persist the result in
RAM, and then wait

```python
out = gleft.merge(gright, on=['id'])  # this is lazy
```

## Profile and analyze results

We now look at the Dask diagnostic plots for this computation.

### Task stream and communication

When we look at Dask's task stream plot we see that each of our eight threads
(each of which manages a single GPU) spent most of its time in communication
(red is communication time). The actual merge and concat tasks are quite fast
relative to the data transfer time.

<iframe src="https://matthewrocklin.com/raw-host/dask-cudf-joins.html"
        width="800"
        height="400"></iframe>

That's not too surprising. For this computation I've turned off any attempt to
communicate between devices (more on this below) so the data is being moved
from the GPU to the CPU memory, then serialized and put onto a TCP socket.
We're moving tens of GB on a single machine, so we're seeing about 1GB/s total
throughput of the system, which is typical for TCP-on-localhost in Python.

### Flamegraph of computation

We can also look more deeply at the computational costs in Dask's
flamegraph-style plot. This shows which lines of our functions were taking up
the most time (down to the Python level at least).

<iframe src="http://matthewrocklin.com/raw-host/dask-cudf-join-profile.html"
        width="800"
        height="400"></iframe>

This [Flame graph](http://www.brendangregg.com/flamegraphs.html) shows which
lines of cudf code we spent time on while computing (excluding the main
communication costs mentioned above). It may be interesting for those trying
to further optimize performance. It shows that most of our costs are in memory
allocation. Like communication, this has actually also been fixed in RAPIDS'
optional memory management pool, it just isn't default yet, so I didn't use it
here.

## Plans for efficient communication

The cuDF library actually has a decent approach to single-node multi-GPU
communication that I've intentionally turned off for this experiment. That
approach cleverly used Dask to communicate device pointer information using
Dask's normal channels (this is small and fast) and then used that information
to initiate a side-channel communication for the bulk of the data. This
approach was effective, but somewhat fragile. I'm inclined to move on for it
in favor of ...

UCX. The [UCX](http://www.openucx.org/) project provides a single API that
wraps around several transports like TCP, Infiniband, shared memory, and also
GPU-specific transports. UCX claims to find the best way to communicate data
between two points given the hardware available. If Dask were able to use this
for communication then it would provide both efficient GPU-to-GPU communication
on a single machine, and also efficient inter-machine communication when
efficient networking hardware like Infiniband was present, even outside the
context of GPUs.

There is some work we need to do here:

1.  We need to make a Python wrapper around UCX
2.  We need to make an optional [Dask Comm](https://distributed.dask.org/en/latest/communications.html)
    around this ucx-py library that allows users to specify endpoints like
    `ucx://path-to-scheduler`
3.  We need to make Python memoryview-like objects that refer to device memory
4.  ...

This work is already in progress by [Akshay
Vekatesh](https://github.com/Akshay-Venkatesh), who works on UCX, and [Tom
Augspurger](https://tomaugspurger.github.io/) a core Dask/Pandas developer. I
suspect that they'll write about it soon. I'm looking forward to seeing what
comes of it, both for Dask and for high performance Python generally.

It's worth pointing out that this effort won't just help GPU users. It should
help anyone on advanced networking hardware, including the mainstream
scientific HPC community.

## Summary

Single-node Mutli-GPU joins have a lot of promise. In fact, earlier RAPIDS
developers got this running much faster than I was able to do above through the
clever communication tricks I briefly mentioned. The main purpose of this post
is to provide a benchmark for joins that we can use in the future, and to
highlight when communication can be essential in parallel computing.

Now that GPUs have accelerated the computation time of each of our chunks of
work we increasingly find that other systems become the bottleneck. We didn't
care as much about communication before because computational costs were
comparable. Now that computation is an order of magnitude cheaper, other
aspects of our stack become much more important.

I'm looking forward to seeing where this goes.

### Come help!

If the work above sounds interesting to you then come help!
There is a lot of low-hanging and high impact work to do.

If you're interested in being paid to focus more on these topics, then consider
applying for a job. NVIDIA's RAPIDS team is looking to hire engineers for Dask
development with GPUs and other data analytics library development projects.

- [Senior Library Software Engineer - RAPIDS](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-TX-Austin/Senior-Library-Software-Engineer---RAPIDS_JR1919608-1)
