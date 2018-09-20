---
layout: post
title: Dask Scaling Limits
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Anaconda Inc.](http://anaconda.com)*


## History

For the first year of Dask's life it focused exclusively on single node
parallelism.  We felt then that efficiently supporting 100+GB datasets on
personal laptops or 1TB datasets on large workstations was a sweet spot for
productivity, especially when avoiding the pain of deploying and configuring
distributed systems.  We still believe in the efficiency of single-node
parallelism, but in the years since, Dask has extended itself to support larger
distributed systems.

After that first year, Dask focused equally on both single-node and distributed
parallelism.  We maintain [two entirely separate
schedulers](http://dask.pydata.org/en/latest/scheduling.html), one optimized for
each case.  This allows Dask to be very simple to use on single machines, but
also scale up to thousand-node clusters and 100+TB datasets when needed with
the same API.

Dask's distributed system has a single central scheduler and many distributed
workers.  This is a common architecture today that scales out to a few thousand
nodes.  Roughly speaking Dask scales about the same as a system like Apache
Spark, but less well than a high-performance system like MPI.


## An Example

Most Dask examples in blogposts or talks are on modestly sized datasets,
usually in the 10-50GB range.  This, combined with Dask's history with
medium-data on single-nodes may have given people a more humble impression of
Dask than is appropriate.

As a small nudge, here is an example using Dask to interact with 50 36-core
nodes on an artificial terabyte dataset.

<iframe width="700"
        height="394"
        src="https://www.youtube.com/embed/nH_AQo8WdKw"
        frameborder="0"
        allow="autoplay; encrypted-media"
        allowfullscreen></iframe>

This is a common size for a typical modestly sized Dask cluster.  We usually
see Dask deployment sizes either in the tens of machines (usually with Hadoop
style or ad-hoc enterprise clusters), or in the few-thousand range (usually
with high performance computers or cloud deployments).  We're showing the
modest case here just due to lack of resources.  Everything in that example
should work fine scaling out a couple extra orders of magnitude.


## Challenges to Scaling Out

For the rest of the article we'll talk about common causes that we see today
that get in the way of scaling out.  These are collected from experience
working both with people in the open source community, as well as private
contracts.

### Simple Map-Reduce style

If you're doing simple map-reduce style parallelism then things will be pretty
smooth out to a large number of nodes.  However, there are still some
limitations to keep in mind:

1.  The scheduler will have at least one, and possibly a few connections open
    to each worker.  You'll want to ensure that your machines can have many
    open file handles at once.  Some Linux distributions cap this at 1024 by
    default, but it is easy to change.

2.  The scheduler has an overhead of around 200 microseconds per task.
    So if each task takes one second then your scheduler can saturate 5000
    cores, but if each task takes only 100ms then your scheduler can only
    saturate around 500 cores, and so on.  Task duration imposes an inversely
    proportional constraint on scaling.

    If you want to scale larger than this then your tasks will need to
    start doing more work in each task to avoid overhead.  Often this involves
    moving inner for loops within tasks rather than spreading them out to many
    tasks.

### More complex algorithms

If you're doing more complex algorithms (which is common among Dask users) then
many more things can break along the way.  High performance computing isn't
about doing any one thing well, it's about doing *nothing badly*.  This section
lists a few issues that arise for larger deployments:

1.  Dask collection algorithms may be suboptimal.

    The parallel algorithms in Dask-array/bag/dataframe/ml are *pretty* good,
    but as Dask scales out to larger clusters and its algorithms are used by
    more domains we invariably find that small corners of the API fail beyond a
    certain point.  Luckily these are usually pretty easy to fix after they are
    reported.

2.  The graph size may grow too large for the scheduler

    The metadata describing your computation has to all fit on a single
    machine, the Dask scheduler.  This metadata, the task graph, can grow big
    if you're not careful.  It's nice to have a scheduler process with at least
    a few gigabytes of memory if you're going to be processing million-node
    task graphs.  A task takes up around 1kB of memory *if* you're careful to
    avoid closing over any unnecessary local data.

3.  The graph serialization time may become annoying for interactive use

    Again, if you have million node task graphs you're going to be serializaing
    them up and passing them from the client to the scheduler.  This is *fine*,
    assuming they fit at both ends, but can take up some time and limit
    interactivity.  If you press `compute` and nothing shows up on the
    dashboard for a minute or two, this is what's happening.

4.  The interactive dashboard plots stop being as useful

    Those beautiful plots on the dashboard were mostly designed for deployments
    with 1-100 nodes, but not 1000s.  Seeing the start and stop time of every
    task of a million-task computation just isn't something that our brains can
    fully understand.

    This is something that we would like to improve.  If anyone out there is
    interested in scalable performance diagnostics, please get involved.

5.  Other components that you rely on, like distributed storage, may also start
    to break

    Dask provides users more power than they're accustomed to.
    It's easy for them to accidentally clobber some other component of their
    systems, like distributed storage, a local database, the network, and so
    on, with too many requests.

    Many of these systems provide abstractions that are very well tested and
    stable for normal single-machine use, but that quickly become brittle when
    you have a thousand machines acting on them with the full creativity of a
    novice user.  Dask provies some primitives like distributed locks and
    queues to help control access to these resources, but it's on the user to
    use them well and not break things.


## Conclusion

Dask scales happily out to tens of nodes, like in the example above, or to
thousands of nodes, which I'm not showing here simply due to lack of resources.

Dask provides this scalability while still maintaining the flexibility and
freedom to build custom systems that has defined the project since it began.
However, the combination of scalability and freedom makes it hard for Dask to
fully protect users from breaking things.  It's much easier to protect users
when you can constrain what they can do.  When users stick to standard
workflows like Dask dataframe or Dask array they'll probably be ok, but when
operating with full creativity at the thousand-node scale some expertise will
invariably be necessary.  We try hard to provide the diagnostics and tools
necessary to investigate issues and control operation.  The project is getting
better at this every day, in large part due to some expert users out there.


## A Call for Examples

Do you use Dask on more than one machine to do interesting work?
We'd love to hear about it either in the comments below, or in this [online
form](https://goo.gl/forms/ueIMoGl6ZPl529203).
