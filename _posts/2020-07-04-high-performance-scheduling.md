---
layout: post
title: High Performance Scheduling
tagline:
author: Matthew Rocklin (Coiled)
tags: []
theme: twitter
---
{% include JB/setup %}

Summary
-------

This post discusses all of the current costs around task scheduling in Dask,
and then lays out a plan to accelerate things.

This post is written for other maintainers, and often refers to internal
details.  It is not intended for broad readability.

How does this present?
----------------------

When we submit large graphs there is a bit of a delay between us calling
`.compute()` and work actually starting on the workers.  In some cases, that
delay can be considerable.

Additionally, in far fewer cases, the gaps in between tasks can be an issue,
especially if those tasks are very short and for some reason can not be made
longer.

Who cares?
----------

First, this is a problem that affects about 1% of Dask users.  These are people
who want to process millions of tasks relatively quickly.  Let's list a few use
cases:

1.  Pangeo workloads on the 100TB scale
2.  NVIDIA benchmarking (GPUs make computing fast, so other costs become
    proportionally larger)
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
that we can learn.

1.  Rewrite the scheduler it in C++/Rust/C/Cython

    Proposal: Python is slow.  Want to make it faster?  Don't use Python.  See
    academic projects

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

    What we should consider: We can move some simple logic down to the workers.
    We've already done this with the easy stuff though.
    It's not clear how much additional benefit there is here.

3.  Build specialty scheduling around collections

    Proposal: If Dask were to become just a dataframe library or just an array
    computing library then it could special-case things more effectively.  See
    Spark, Mars, and others.

    Challenge: Yes, but Dask is not a dataframe library or an array library.
    The three use cases we mention above are all very different

    What we should consider: modules like dask array and dask dataframe should
    develop high level query blocks, and we should endeavor to
    communicate these subgraphs over the wire directly so that they are more
    compact.


What should we actually do?
---------------------------

I don't know.  We're going to find out.  This is a hard problem because
changing one piece of the project at this level has repurcussions for many
other pieces.  The rest of this post tries to lay out a consistent set of
changes.


Graph Generation
----------------

A year or two ago we moved graph generation costs from user-code-typing time to
graph-optimization-time with high level graphs

```python
y = x + 1                 # graph generation used to happen here
(y,) = dask.optimize(y,)  # now it happens here
```

This really improved usability, and also let us do some high level
optimizations which sometimes allowed us to skip some lower-level optimization
costs.  We can extend this approach, but only if we make high level graphs much
better.


### Send abstract graph layers to the scheduler

If we don't lower all the way on the client side then we can send these more
compact graph representations up to the scheduler rather than sending the whole
thing as a bunch of Python dicts.

The scheduler will then have to know how to unpack these graphs.  This is a
little tricky because the Scheduler can't run user Python code (for security
reasons) but we can special-case a few common cases.

(some conversation here: https://github.com/dask/distributed/issues/3872)


### Encode graphs in something other than Python

Today we encode graphs as dicts of tuples.  If we had a more compact
representation then we could generate them more efficiently, and communicate
them across a wire more efficiently.

Personally I think that this is less important if we can encode most large
graphs in abstract form (like Blockwise).  Then we can defer this to the
scheduler code.


### Challenge: low level graph optimizations

Many important optimizations like culling, fusion, and slice optimization require the low
level graph.  This currently happens on the Client side.  How do we handle those?

There are many cases where not culling on the client side will mean that we'll
send very large graphs to the scheduler needlessly (consider `df.head()`)

In array computing we also require the low level graph for efficient slicing
optimizations (which are critical for performance).


### Proposal

I would like to see a world where the Client sends a sequence of graph layers
up to the Scheduler.  This will allow more compact abstract graphs, and
possibly also graphs encoded in a lower level langauge.  There is a nice
opportunity for creativity there if we can encode graphs in different ways.

However, in order to keep the high level graph structure we need to resolve
some critical issues around optimization in the Dask collections, particularly
array and dataframe.  I think that these are solvable if we ramp up high level
query optimizations considerably, so that those optimizations can take care of
things like culling and slice optimization and we never need to lower to a full
low-level task graph.

So if we want faster graph generation I think that we need much smarter high level graphs.


Rewrite scheduler in low-level language
---------------------------------------

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
(Cython?) but more likely we'll end up making a protocol here so that other
groups can experiment safely.  In doing this we'll probably lose the dashboard,
unless those other groups are very careful to expose the same state to Bokeh.

It could also be that we can tune just small parts of the scheduler and
maintain much of the same state.  I think that in an ideal world we would find
some solution with Cython/MyPy that got most of the job done.

There is more exploration to do here.  Short-term I think that separating out
the state machine from the networking makes sense.  Maybe that also makes it
easier for people to profile.
