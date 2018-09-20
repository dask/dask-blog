---
layout: post
title: Dask and Celery
category: work
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}

This post compares two Python distributed task processing systems,
Dask.distributed and Celery.

*Disclaimer: technical comparisons are hard to do well.  I am biased towards
Dask and ignorant of correct Celery practices.  Please keep this in mind.
Critical feedback by Celery experts is welcome.*

[Celery](http://www.celeryproject.org/) is a distributed task queue built in
Python and heavily used by the Python community for task-based workloads.

[Dask](http://dask.pydata.org/en/latest/) is a parallel computing library
popular within the PyData community that has grown a fairly sophisticated
[distributed task scheduler](http://distributed.readthedocs.io/en/latest/).
This post explores if Dask.distributed can be useful for Celery-style problems.

Comparing technical projects is hard both because authors have bias, and also
because the scope of each project can be quite large.  This allows authors to
gravitate towards the features that show off our strengths.  Fortunately [a
Celery user asked how Dask compares on
Github](https://github.com/dask/dask/issues/1537) and they listed a few
concrete features:

1.  Handling multiple queues
2.  Canvas (celery's workflow)
3.  Rate limiting
4.  Retrying

These provide an opportunity to explore the Dask/Celery comparision from the
bias of a Celery user rather than from the bias of a Dask developer.

In this post I'll point out a couple of large differences, then go through the
Celery hello world in both projects, and then address how these requested
features are implemented or not within Dask.  This anecdotal comparison over a
few features should give us a general comparison.


Biggest difference: Worker state and communication
--------------------------------------------------

First, the biggest difference (from my perspective) is that Dask workers hold
onto intermediate results and communicate data between each other while in
Celery all results flow back to a central authority.  This difference was
critical when building out large parallel arrays and dataframes (Dask's
original purpose) where we needed to engage our worker processes' memory and
inter-worker communication bandwidths.  Computational systems like Dask do
this, more data-engineering systems like Celery/Airflow/Luigi don't.  This is
the main reason why Dask wasn't built on top of Celery/Airflow/Luigi originally.

That's not a knock against Celery/Airflow/Luigi by any means.  Typically
they're used in settings where this doesn't matter and they've focused their
energies on several features that Dask similarly doesn't care about or do well.
Tasks usually read data from some globally accessible store like a database or
S3 and either return very small results, or place larger results back in the
global store.

The question on my mind is now is *Can Dask be a useful solution in more
traditional loose task scheduling problems where projects like Celery are
typically used?  What are the benefits and drawbacks?*


Hello World
-----------

To start we do the [First steps with
Celery](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html)
walk-through both in Celery and Dask and compare the two:

### Celery

I follow the Celery quickstart, using Redis instead of RabbitMQ because it's
what I happen to have handy.

```python
# tasks.py

from celery import Celery

app = Celery('tasks', broker='redis://localhost', backend='redis')

@app.task
def add(x, y):
    return x + y
```

    $ redis-server
    $ celery -A tasks worker --loglevel=info

```python
In [1]: from tasks import add

In [2]: %time add.delay(1, 1).get()  # submit and retrieve roundtrip
CPU times: user 60 ms, sys: 8 ms, total: 68 ms
Wall time: 567 ms
Out[2]: 2

In [3]: %%time
...: futures = [add.delay(i, i) for i in range(1000)]
...: results = [f.get() for f in futures]
...:
CPU times: user 888 ms, sys: 72 ms, total: 960 ms
Wall time: 1.7 s
```


### Dask

We do the same workload with dask.distributed's concurrent.futures interface,
using the default single-machine deployment.

```python
In [1]: from distributed import Client

In [2]: c = Client()

In [3]: from operator import add

In [4]: %time c.submit(add, 1, 1).result()
CPU times: user 20 ms, sys: 0 ns, total: 20 ms
Wall time: 20.7 ms
Out[4]: 2

In [5]: %%time
...: futures = [c.submit(add, i, i) for i in range(1000)]
...: results = c.gather(futures)
...:
CPU times: user 328 ms, sys: 12 ms, total: 340 ms
Wall time: 369 ms
```

### Comparison

*  **Functions**: In Celery you register computations ahead of time on the
   server.  This is good if you know what you want to run ahead of time (such
   as is often the case in data engineering workloads) and don't want the
   security risk of allowing users to run arbitrary code on your cluster.  It's
   less pleasant on users who want to experiment.  In Dask we choose the
   functions to run on the user side, not on the server side.  This ends up
   being pretty critical in data exploration but may be a hinderance in more
   conservative/secure compute settings.
*  **Setup**: In Celery we depend on other widely deployed systems like
   RabbitMQ or Redis.  Dask depends on lower-level Torando TCP IOStreams and
   Dask's own custom routing logic.  This makes Dask trivial to set up, but
   also probably less durable.  Redis and RabbitMQ have both solved lots of
   problems that come up in the wild and leaning on them inspires confidence.
*  **Performance**:  They both operate with sub-second latencies and
   millisecond-ish overheads.  Dask is marginally lower-overhead but for data
   engineering workloads differences at this level are rarely significant.
   Dask is an order of magnitude lower-latency, which might be a big deal
   depending on your application.  For example if you're firing off tasks from
   a user clicking a button on a website 20ms is generally within interactive
   budget while 500ms feels a bit slower.


Simple Dependencies
-------------------

The question asked about
[Canvas](http://docs.celeryproject.org/en/master/userguide/canvas.html),
Celery's dependency management system.

Often tasks depend on the results of other tasks.  Both systems have ways to
help users express these dependencies.

### Celery

The `apply_async` method has a `link=` parameter that can be used to call tasks
after other tasks have run.  For example we can compute `(1 + 2) + 3` in Celery
as follows:

```python
add.apply_async((1, 2), link=add.s(3))
```

### Dask.distributed

With the Dask concurrent.futures API, futures can be used within submit calls
and dependencies are implicit.

```python
x = c.submit(add, 1, 2)
y = c.submit(add, x, 3)
```

We could also use the [dask.delayed](http://dask.pydata.org/en/latest/delayed.html) decorator to annotate arbitrary functions and then use normal-ish Python.

```python
@dask.delayed
def add(x, y):
    return x + y

x = add(1, 2)
y = add(x, 3)
y.compute()
```

### Comparison

I prefer the Dask solution, but that's subjective.


Complex Dependencies
--------------------

### Celery

Celery includes a rich vocabulary of terms to connect tasks in more complex
ways including `groups`, `chains`, `chords`, `maps`, `starmaps`, etc..  More
detail here in their docs for Canvas, the system they use to construct complex
workflows: http://docs.celeryproject.org/en/master/userguide/canvas.html

For example here we chord many adds and then follow them with a sum.

```python
In [1]: from tasks import add, tsum  # I had to add a sum method to tasks.py

In [2]: from celery import chord

In [3]: %time chord(add.s(i, i) for i in range(100))(tsum.s()).get()
CPU times: user 172 ms, sys: 12 ms, total: 184 ms
Wall time: 1.21 s
Out[3]: 9900
```

### Dask

Dask's trick of allowing futures in submit calls actually goes pretty far.
Dask doesn't really need any additional primitives.  It can do all of the
patterns expressed in Canvas fairly naturally with normal submit calls.

```python
In [4]: %%time
...: futures = [c.submit(add, i, i) for i in range(100)]
...: total = c.submit(sum, futures)
...: total.result()
...:
CPU times: user 52 ms, sys: 0 ns, total: 52 ms
Wall time: 60.8 ms
```

Or with [Dask.delayed](http://dask.pydata.org/en/latest/delayed.html)

```python
futures = [add(i, i) for i in range(100)]
total = dask.delayed(sum)(futures)
total.result()
```


Multiple Queues
---------------

In Celery there is a notion of queues to which tasks can be submitted and that
workers can subscribe.  An example use case is having "high priority" workers
that only process "high priority" tasks.  Every worker can subscribe to
the high-priority queue but certain workers will subscribe to that queue
exclusively:

```
celery -A my-project worker -Q high-priority  # only subscribe to high priority
celery -A my-project worker -Q celery,high-priority  # subscribe to both
celery -A my-project worker -Q celery,high-priority
celery -A my-project worker -Q celery,high-priority
```

This is like the TSA pre-check line or the express lane in the grocery store.

Dask has a couple of topics that are similar or could fit this need in a pinch, but nothing that is strictly analogous.

First, for the common case above, tasks have priorities.  These are typically
set by the scheduler to minimize memory use but can be overridden directly by
users to give certain tasks precedence over others.

Second, you can restrict tasks to run on subsets of workers.  This was
originally designed for data-local storage systems like the Hadoop FileSystem
(HDFS) or clusters with special hardware like GPUs but can be used in the
queues case as well.  It's not quite the same abstraction but could be used to
achieve the same results in a pinch.  For each task you can *restrict* the pool
of workers on which it can run.

The relevant docs for this are here:
[http://distributed.readthedocs.io/en/latest/locality.html#user-control](http://distributed.readthedocs.io/en/latest/locality.html#user-control)


Retrying Tasks
--------------

Celery allows tasks to retry themselves on a failure.

```python
@app.task(bind=True)
def send_twitter_status(self, oauth, tweet):
    try:
        twitter = Twitter(oauth)
        twitter.update_status(tweet)
    except (Twitter.FailWhaleError, Twitter.LoginError) as exc:
        raise self.retry(exc=exc)

# Example from http://docs.celeryproject.org/en/latest/userguide/tasks.html#retrying
```

Sadly Dask currently has no support for this (see [open
issue](https://github.com/dask/distributed/issues/391)).  All functions are
considered pure and final.  If a task errs the exception is considered to be
the true result.  This could change though; it has been requested a couple of
times now.

Until then users need to implement retry logic within the function (which isn't
a terrible idea regardless).

```python
@app.task(bind=True)
def send_twitter_status(self, oauth, tweet, n_retries=5):
    for i in range(n_retries):
        try:
            twitter = Twitter(oauth)
            twitter.update_status(tweet)
            return
        except (Twitter.FailWhaleError, Twitter.LoginError) as exc:
            pass
```


Rate Limiting
-------------

Celery lets you specify rate limits on tasks, presumably to help you avoid
getting blocked from hammering external APIs

```python
@app.task(rate_limit='1000/h')
def query_external_api(...):
    ...
```

Dask definitely has nothing built in for this, nor is it planned.  However,
this could be done externally to Dask fairly easily.  For example, Dask
supports mapping functions over arbitrary Python Queues.  If you send in a
queue then all current and future elements in that queue will be mapped over.
You could easily handle rate limiting in Pure Python on the client side by
rate limiting your input queues.  The low latency and overhead of Dask makes it
fairly easy to manage logic like this on the client-side.  It's not as
convenient, but it's still straightforward.

```python
>>> from queue import Queue

>>> q = Queue()

>>> out = c.map(query_external_api, q)
>>> type(out)
Queue
```


Final Thoughts
--------------

Based on this very shallow exploration of Celery, I'll foolishly claim that
Dask can handle Celery workloads, *if you're not diving into deep API*.
However all of that deep API is actually really important.  Celery evolved in
this domain and developed tons of features that solve problems that arise over
and over again.  This history saves users an enormous amount of time.  Dask
evolved in a very different space and has developed a very different set of
tricks.  Many of Dask's tricks are general enough that they can solve Celery
problems with a small bit of effort, but there's still that extra step.  I'm
seeing people applying that effort to problems now and I think it'll be
interesting to see what comes out of it.

Going through the Celery API was a good experience for me personally.  I think
that there are some good concepts from Celery that can inform future Dask
development.
