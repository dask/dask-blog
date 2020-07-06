---
layout: post
title: Reduce Scheduling Overhead
tagline:
author: Matthew Rocklin (Coiled)
tags: []
theme: twitter
---
{% include JB/setup %}

Summary
-------

This post discusses Dask overhead costs for task scheduling,
and then lays out a rough plan for acceleration.

This post is written for other maintainers, and often refers to internal
details.  It is not intended for broad readability.

How does this present?
----------------------

When we submit large graphs there is a bit of a delay between us calling
`.compute()` and work actually starting on the workers.  In some cases, that
delay can affect usability and performance.

Additionally, in far fewer cases, the gaps in between tasks can be an issue,
especially if those tasks are very short and for some reason can not be made
longer.

Who cares?
----------

First, this is a problem that affects about 1% of Dask users.  These are people
who want to process millions of tasks relatively quickly.  Let's list a few use
cases:

1.  Xarray/Pangeo workloads on the 100TB scale
2.  NVIDIA benchmarking (GPUs make computing fast, so other costs become
    relatively larger)
3.  Some mystery use cases inside of some hedge funds

It does not affect the everyday user, who processes 100GB to a few TB of data,
and doesn't mind waiting 10s for things to start running.


Coarse breakdown of costs
-------------------------

When you call `x.sum().compute()` a few things happen:

1.  **Graph generation:** Some Python code in a Dask collection library, like
    dask array, calls the sum function, which generates a task graph on the
    client side.
2.  **Graph Optimization:** We then optimize that graph, also on the client
    side, in order to remove unnecessary work, fuse tasks, apply important high
    level optimizations, and more.
3.  **Graph Serializtion:** We now pack up that graph in a form that can be
    sent over to the scheduler.
4.  **Graph Communication:** We fire those bytes across a wire over to the
    scheduler
5.  **Scheduler.update\_graph:** The scheduler receives these bytes, unpacks
    them, and then updates its own internal data structures
6.  **Scheduling:** The scheduler then assigns ready tasks to workers
7.  **Communicate to workers:** The scheduler sends out lots of smaller
    messages to each of the workers with the tasks that they can perform
8.  **Workers work:** The workers then perform this work, and start
    communicating back and forth with the scheduler to receive new instructions

Generally most people today are concerned with steps 1-6.  Once things get out
to the workers and progress bars start moving people tend to care a bit less
(but not zero).


What do other people do?
------------------------

Let's look at a few things that other projects do, and see if there are things
that we can learn.  These are commonly suggested, but there are challenges with
most of them.

1.  Rewrite the scheduler it in C++/Rust/C/Cython

    Proposal: Python is slow.  Want to make it faster?  Don't use Python.  See
    academic projects.

    Challenge: This makes sense for some parts of the pipeline above, but not
    for others.  It also makes it harder to attract maintainers.

    What we should consider: Some parts of the scheduler and optimization
    algorithms could be written in a lower level language, maybe Cython.  We'll
    need to be careful about maintainability.

2.  Distributed scheduling

    Proposal: The scheduler is slow, maybe have many schedulers?  See Ray.

    Challenge: It's actually really hard to make the kinds of decisions that
    Dask has to make if scheduling state is spread on many computers.
    Distributed scheduling works better when the workload is very either
    uniform or highly decoupled.
    Distributed scheduling is really attractive to people who like solving
    interesting/hard problems.

    What we should consider: We can move some simple logic down to the workers.
    We've already done this with the easy stuff though.
    It's not clear how much additional benefit there is here.

3.  Build specialty scheduling around collections

    Proposal: If Dask were to become just a dataframe library or just an array
    computing library then it could special-case things more effectively.  See
    Spark, Mars, and others.

    Challenge: Yes, but Dask is not a dataframe library or an array library.
    The three use cases we mention above are all very different.

    What we should consider: modules like dask array and dask dataframe should
    develop high level query blocks, and we should endeavor to
    communicate these subgraphs over the wire directly so that they are more
    compact.


What should we actually do?
---------------------------

Because our pipeline has many stages, each of which can be slow for different
reasons, we'll have to do many things.  Additionally, this is a hard problem
because changing one piece of the project at this level has repurcussions for
many other pieces.  The rest of this post tries to lay out a consistent set of
changes.  Let's start with a summary:

1.  For Dask array/dataframe let's use high level graphs more aggressively so
    that we can communicate only abstract representations between the client
    and scheduler.
2.  But this breaks low level graph optimizations, fuse, cull, and slice fusion
    in particular.  So we'll need to make high level graphs considerably
    smarter to make these unnecessary.
3.  Then, once all of the graph manipulation happens on the scheduler, let's
    try to accelerate it, hopefully in a language that the current dev
    community can understand, like Cython
4.  At the same time in parallel, let's take a look at our network stack

We'll go into these in more depth below


Graph Generation
----------------

### High Level Graph History

A year or two ago we moved graph generation costs from user-code-typing time to
graph-optimization-time with high level graphs

```python
y = x + 1                 # graph generation used to happen here
(y,) = dask.optimize(y,)  # now it happens here
```

This really improved usability, and also let us do some high level
optimizations which sometimes allowed us to skip some lower-level optimization
costs.

### Can we push this further?

The first four stages of our pipeline happen on the client:

1.  **Graph generation:** Some Python code in a Dask collection library, like
    dask array, calls the sum function, which generates a task graph on the
    client side.
2.  **Graph Optimization:** We then optimize that graph, also on the client
    side, in order to remove unnecessary work, fuse tasks, apply important high
    level optimizations, and more.
3.  **Graph Serializtion:** We now pack up that graph in a form that can be
    sent over to the scheduler.
4.  **Graph Communication:** We fire those bytes across a wire over to the
    scheduler

If we're able to stay with the high level graph representation through these
stages all the way until graph communication, then we can communicate a far
more compact representation up to the scheduler.  We can drop a lot of these
costs, at least for the high level collection APIs (delayed and client.submit
would still be slow, client.map might be ok though).

This has a couple of other nice benefits:

1.  User's code won't block, and we can alert the user immediately that we're
    on the job
2.  We've centralized costs in just the scheduler,
    so there is now only one place where we might have to think about low-level code

(some conversation here: https://github.com/dask/distributed/issues/3872)


### However, low-level graph optimizations are going to be a problem

In principle changing the distributed scheduler to accept a variety of graph
layer types is a tedious but straightforward problem.  I'm not concerned.

The bigger concern is what to do with low-level graph optimizations.
Today we have three of these that really matter:

1.  Task fusion: this is what keeps your `read_parquet` task merged with your
    subsequent blockwise tasks
2.  Culling: this is what makes `df.head()` or `x[0]` fast
3.  Slice fusion: this is why `x[:100][5]` works well

In order for us to transmit abstract graph layers up to the scheduler, we need
to remove the need for these low level graph optimizations.  Our best option
here is to replace them with much more clever high level graph optimizations.

We already do this a bit with blockwise, which has its own fusion, and which
removes much of the need for fusion generally.  But other blockwise-like
operations, like `read_*` will probably have to join the Blockwise family.

Getting culling to work properly may require us to teach each of the individual
graph layers how to cull themselves.  This may get tricky.

Slicing is doable, we just need someone to go in, grok all of the current
slicing optimizations, and make high level graph layers for these
computations.


### Also, unpacking abstract graph layers on the scheduler

The scheduler will also have to know how to unpack these graphs.  This is a
little tricky because the Scheduler can't run user Python code (for security
reasons).  We'll have to register layer types (like blockwise) that the
scheduler knows about and trusts ahead of time.  We'll still always support
custom layers, and these will be at the same speed that they've always been,
but hopefully there will be far less need for these if we go all-in on high
level layers.



### Maybe we should encode graphs in something other than Python?

Today we encode graphs as dicts of tuples.  If we had a more compact
representation then we could generate them more efficiently, and communicate
them across a wire more efficiently.

Personally I think that this is less important if we can encode most large
graphs in abstract form (like Blockwise).  Then we can defer this to the
scheduler code.


Rewrite scheduler in low-level language
---------------------------------------

Once most of the finicky bits are moved to the scheduler, we'll have one place
where we can focus on low level graph state manipulation.

Dask's distributed scheduler is two things:

1.  A Tornado TCP application that receives signals from clients and workers
    and send signals out to clients and workers

    This is async-heavy networking code

2.  A complex state machine internally that responds to those state changes

    This is a complex data structure heavy Python code


### Networking

Jim has an interesting project here that shows promise: https://github.com/jcrist/ery
Reducing latency between workers and the scheduler would be good, and would
help to accelerate stages 7-8 in the pipeline listed at the top of this post.


### State machine

Rewriting the state machine in some lower level language would be fine.
Ideally this would be in a language that was easy for people to maintain,
(Cython?) but we may also consider making a more firm interface here that would
allow other groups to experiment safely.

There are some advantages to this (more experimentation by different groups)
but also some costs (splitting of core efforts and mismatches for users).
Also, I suspect that splitting out also probably means that we'll probably lose the dashboard,
unless those other groups are very careful to expose the same state to Bokeh.

There is more exploration to do here.  Regardless I think that it probaby makes
sense to try to isolate the state machine from the networking system.
Maybe this also makes it easier for people to profile in isolation.


High Level Graph Optimizations
------------------------------

Once we have everything in smarter high level graph layers,
we will also be more ripe for optimization.
