---
layout: post
title: High Performance Task Scheduling
tagline: when arrays and dataframes aren't flexible enough
category : work
draft: true
tags : [Programming, scipy, Python, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

Last week I optimized Dask's distributed task scheduler to run small tasks
quickly.  This post discusses why that is important and how we accomplished it.

Recap: What is a task?
----------------------

A task is an in-memory computation that occurs on one worker computer.  In
dask this is a Python function on Python objects.  In Spark a task would be a
Scala function operating on one partition.  In databases it's one operation
running on a shard of data from the database.

Internally most distributed systems break up large logical queries into many
small physical tasks and then schedule those tasks to run on their worker
computers.  In most high-level systems like databases or Spark you never see
the task scheduler, except occasionally in logs.  Here is an example from
Spark showing logs from a four-partition RDD.

```python
In [1]: from pyspark import SparkContext
In [2]: sc = SparkContext('local[4]')
In [3]: rdd = sc.parallelize(range(10), numSlices=4)
In [4]: rdd.map(lambda x: x + 1).collect()
...
INFO Executor: Finished task 1.0 in stage 0.0 (TID 1). 1017 bytes result sent to driver
INFO Executor: Finished task 2.0 in stage 0.0 (TID 2). 1014 bytes result sent to driver
INFO Executor: Finished task 0.0 in stage 0.0 (TID 0). 1014 bytes result sent to driver
INFO Executor: Finished task 3.0 in stage 0.0 (TID 3). 1017 bytes result sent to driver
INFO TaskSchedulerImpl: Removed TaskSet 0.0, whose tasks have all completed, from pool
...
Out[4]: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```


Motivating Applications
-----------------------

If your tasks take a long time then you don't need to schedule them
quickly.  A 10ms scheduler overhead on a 10s task is negligible.

However fast task scheduling is important in the following regimes:

1.  **Low latency:** You want to fire off a computation, and get a result back
    soon afterwards.  You want to stay in the loop at high frequency.
2.  **Fast computations:** Tasks like summing arrays and counting
    things are genuinely very fast in memory, probably near the millisecond
    level.  Scheduler overhead dominates total execution time.
3.  **Shuffles:** Shuffling data around between partitions creates many little
    pieces of data to manage and coalesce back together.  If your task
    scheduler is slow then this becomes infeasible.  Systems like Spark switch
    to a completely different mode when shuffling to avoid this issue.
4.  **Resilience to poor partitioning:** Users often partition their data into
    very small bins, resulting in many very fast tasks.  It's nice if your
    system can degrade gracefully in this situation.
5.  **Giant clusters**: If every task takes 1s and scheduler overhead is 10ms
    per task then one sequential scheduler keep at most 100 cores occupied.

Lately I've run into cases 2 (fast computations) and 3 (shuffling).  These are
important to me because of the following:

1.  Waiting more than a second for my big expensive cluster to sum an array
    seems silly.
2.  I need to shuffle data from row-major to column-major strides.

I'm curious if Dask should go the route that Spark took and create a shuffle
step that is completely separate from the low-level task scheduling system or
if we can optimize the task scheduling system enough to get by.  I'd like to
avoid a separate shuffle if possible, it's a jarring deviation from the rest
of the project.


Prior Art
---------

Very little is published about the task schedulers internal to most
distributed systems.  Technical documentation is sparse and scholarly articles
are infrequent on most databases used in industry.  There is good reason for
this.  Task schedulers change and they're not something with which most users
ever need concern themselves.

We can investigate though; I have Spark handy so lets try to measure scheduler
overhead with a simple experiment.  We create an RDD with 1000 numbers with
either a single partition or with 1000 partitions (each number in its own
partition) and call a trivial computation on each number.  Looking at the
difference in speed will show us the rough overhead per task.:

```python
In [1]: from pyspark import SparkContext
In [2]: sc = SparkContext('local[4]')
In [3]: def inc(x):
   ...:     return x + 1
   ...:

In [4]: rdd = sc.parallelize(range(1000), numSlices=1)
In [5]: %time rdd.map(inc).sum()
CPU times: user 15.6 ms, sys: 1.87 ms, total: 17.5 ms
Wall time: 1.5 s
Out[5]: 500500

In [6]: %time rdd.map(inc).sum()
Wall time: 71.8 ms
Out[6]: 500500

In [7]: rdd = sc.parallelize(range(1000), numSlices=1000)
In [8]: %time rdd.map(inc).sum()
CPU times: user 165 ms, sys: 41.9 ms, total: 207 ms
Wall time: 7.72 s
Out[8]: 500500
```

Observations from this experiment:

1.  It takes around 1-2 seconds to start the first job.  This is
    probably setting up workers.  Subsequent computations don't suffer
    this cost.
2.  A trivial computation with a single partition/task takes about 70ms
3.  One thousand trivial computations with one thousand partitions/tasks takes
    around 7-8s

Conclusions on general costs:

1.  There is a 1-2s one-time cost
2.  There is a 7-8ms cost per task
3.  There is a 60ms overhead per job (or maybe stage?)

*Disclaimers*:

*   I'm running this on an older laptop.  I expect a newer laptop
    would run these in about half the time.
*   Calling `sc.parallellize(range(1000), numSlices=1000)` is a misuse of
    Spark which was designed to be used with longer-running tasks.
    This is like judging an apple for not tasting like an orange.
*   Running the above experiment in Scala Spark I get around a 1.5ms overhead
    per task, which is much much nicer.
    [gist](https://gist.github.com/mrocklin/985398124663ffe2ed257c1ad89243c8)


Fast Scheduling
---------------

For general data processing the numbers above are sufficient and there is no
reason to work to improve them.  Tasks should take several seconds, making the
7-8 ms overhead negligible.

However, many Dask users perform fast numeric computations on data such that
task durations are only milliseconds rather than seconds.  They want to
perform many of these at the same time and they're using interactive systems
like the Jupyter notebook, so they're actively waiting for the result.  We
need to drive the scheduler and the client code much much faster than 7ms per
task, ideally we'd like to land somewhere below the millisecond boundary.

We'll achieve this through the following tricks:

1.  Giving workers far more tasks than they have cores
2.  Batching frequent communications together
3.  General profiling and code optimization


Saturating workers
------------------

Naively a scheduler might send a task to a worker, wait for it to finish, and
then send another.

*  Scheduler: "Please compute `inc(1)`
*  Worker: "Got it, computing `inc(1)`
*  Worker: "OK, I've computed `inc(1)` and am storing the result"
*  Scheduler: "Great, now please compute `inc(2)`"
*  ...

This is nice because the scheduler can allocate the right tasks to the right
workers with full knowledge of what is complete and incomplete everywhere in
the cluster.  However, when computation time is significantly less than
communication latency our workers end up spending most of their time idle,
waiting for a new task.

So instead, we try to send many more tasks to a worker than it can finish by
the time our next message arrives.

*  Scheduler: "Please compute `inc(1)`
*  Worker: "Got it, computing `inc(1)`
*  Worker: "OK, I've computed `inc(1)`; it took 0.0001s"
*  Scheduler: "Wow, that was fast"
*  Scheduler: "Please compute `inc(2)`"
*  Scheduler: "Please compute `inc(3)`"
*  Scheduler: "Please compute `inc(4)`"
*  Scheduler: "Please compute `inc(5)`"
*  Worker: "OK, I've computed `inc(2)`; it took 0.0001s"
*  Worker: "OK, I've computed `inc(3)`; it took 0.0001s"
*  Worker: "OK, I've computed `inc(4)`; it took 0.0001s"
*  Scheduler: "Please compute `inc(6)`"
*  Scheduler: "Please compute `inc(7)`"
*  Scheduler: "Please compute `inc(8)`"
*  Worker: "OK, I've computed `inc(5)`; it took 0.0001s"
*  Worker: "OK, I've computed `inc(6)`; it took 0.0001s"
*  Worker: "OK, I've computed `inc(7)`; it took 0.0001s"

In this way we have a buffer of tasks on the worker and on the wire between
the worker and scheduler.  We scale the size of this buffer by the duration of
recent tasks to keep the worker occupied without giving it so many tasks that
we can't schedule intelligently with other workers.

This approach can go wrong if give the worker too many tasks.  This can
happen when the task duration suddenly changes.  We need to react well to
these situations and make accurate guesses about how long tasks are likely to
take.  Failure to do this results in sub-optimal scheduling.

There are some tricks around this.  Generally we use an exponential moving
average to keep track of recent task durations per worker.  We also completely
forget the average if we experience a delay of greater than the network
latency time and greater than current duration.  This helps the system to
adapt quickly between different user-submissions and when we switch to
long-running tasks.


Batch Communications
--------------------

If we batch several communications together we can improve network efficiency,
both on the physical hardware and for our process of encoding messages down to
bytes.  High-volume communication channels within the dask scheduler will
refuse to send two messages within a fixed interval of time (currently 2ms).
Instead, if messages come along very soon after a previous transmission
they'll hold onto them and transmit many as a batch after a suitable waiting
period.  Currently high-volume channels batch with a two millisecond time
window.  Our previous string of communications now looks like the following:

*  Scheduler: "Please compute `inc(1)`
*  Worker: "Got it, computing `inc(1)`
*  Worker: "OK, I've computed `inc(1)`; it took 0.0001s"
*  Scheduler: "Wow, that was fast"
*  Scheduler: "Please compute [`inc(2)`, `inc(3)`, `inc(4)`, `inc(5)`]"
*  Worker: "OK, I've computed [`inc(2)`; it took 0.0001s,
                               `inc(3)`; it took 0.0001s,
                               `inc(4)`; it took 0.0001s],"
*  Scheduler: "Please compute [`inc(6)`, `inc(7)`, `inc(8)`]"
*  Worker: "OK, I've computed [`inc(5)`; it took 0.0001s,
                               `inc(6)`; it took 0.0001s,
                               `inc(7)`; it took 0.0001s],"


General Optimization
--------------------

As with any system where you start to push performance boundaries it's not
about doing one thing well, it's about doing nothing poorly.  As we improved
batching within the scheduler several other bottlenecks rose to the top.  I'm
not going to get into them here in depth but I do want to point out a few of
the tools I found useful while profiling:

1.  [Snakeviz](https://jiffyclub.github.io/snakeviz/) is a great Python
    profile visualization tool that integrates well with the `cProfile`
    module and the IPython projects.
    Thanks due to [Matt Davis](https://github.com/jiffyclub) for snakeviz.
2.  The [Dask Web UI](http://distributed.readthedocs.io/en/latest/web.html)
    was really helpful here
    (thanks [Bokeh developers](http://bokeh.pydata.org/en/latest/docs/user_guide/server.html))!)
    It's really useful to be able to explore what all of the workers are doing
    down to the microsecond in real time.
3.  The Tornado event loop allows us to put the entire distributed system into
    a single local thread.  This is *really* handy when profiling.  The `tc`
    command line tool was great to simulate network latency.


Same experiment with dask
-------------------------

So lets do our little increment experiment again with Dask futures.

```python
In [1]: from distributed import Executor, progress
In [2]: e = Executor('localhost:8786')

In [3]: def inc(x):
   ...:    return x + 1
   ...:

In [4]: def mapinc(x):
   ...:     return [inc(i) for i in x]
   ...:

In [5]: [future] = e.scatter([list(range(1000))])  # one partition of data

In [6]: %time x = e.submit(mapinc, future); e.submit(sum, x).result()
CPU times: user 8.52 ms, sys: 1.54 ms, total: 10.1 ms
Wall time: 27.5 ms

In [7]: futures = e.scatter(list(range(1000)))  # one thousand pieces

In [8]: futures[:3]
Out[8]:
[<Future: status: finished, key: f1b37646b1331806c57001fca979724e>,
 <Future: status: finished, key: 8068024105615db5ba4cbd263d42a6db>,
 <Future: status: finished, key: d1d6feb3b70239a6081e64b7272d18c8>]

In [9]: %time L = e.map(inc, futures); total = e.submit(sum, L).result()
CPU times: user 101 ms, sys: 4.6 ms, total: 106 ms
Wall time: 412 ms
```

So we see a total overhead of around 27ms and a per-task overhead of 412
microseconds.  As a reminder, this is on a fairly old and low-powered laptop.
I can run the dask scheduler up to about 5000 Hz (200us) on a nicer machine.

<table>
  <thead>
    <tr>
      <th>System</th>
      <th>Startup</th>
      <th>Per-task</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>PySpark</td>
      <td>60ms</td>
      <td>7ms</td>
    </tr>
    <tr>
      <td>ScalaSpark</td>
      <td>400ms</td>
      <td>1.5ms</td>
    </tr>
    <tr>
      <td>Dask</td>
      <td>25ms</td>
      <td>415us</td>
    </tr>
  </tbody>
</table>

Also nice is the fact that we don't have to `map` the same function over and
over again.  Dask can do arbitrary function calls.  This would have happened
with the same performance even with 1000 different functions on each our
different pieces of data rather than just a simple embarrassingly parallel map
call.


What's next
-----------

In an upcoming post I'll use Dask's fast task scheduling to achieve a
distributed shuffle of nd-array data, such as you might find when managing
spatial timeseries or performing 2D FFTs.


Future Work
-----------


It's still unclear whether or not Dask.distributed can become fast enough to
get by without an explicit shuffle.


What didn't work
----------------

As always, I'll have a section that says honestly what doesn't work well or
what I would change with more time.

In this particular post optimizing existing code there isn't really anything
inaccurate or missing.  I haven't done a perfect job though and I suspect that
there is still 2-5x improvement to be had for Dask's distributed scheduler.
I'm aiming for 10kHz (100us) scheduling.  This is likely to be accomplished by
continuing to profile and optimize existing code and eventually by rewriting a
select few functions in Cython.
