---
layout: post
title: Towards Out-of-core ND-Arrays -- Spilling to Disk
category : work
tags : [scipy, Python, Programming, Blaze, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr** We implement a dictionary that spills to disk when we run out of
memory.  We connect this to our scheduler.

Introduction
------------

This is the fifth in a sequence of posts constructing an out-of-core nd-array
using NumPy, Blaze, and dask.  You can view these posts here:

1. [Simple task scheduling](http://matthewrocklin.com/blog/work/2014/12/27/Towards-OOC/),
2. [Frontend usability](http://matthewrocklin.com/blog/work/2014/12/30/Towards-OOC-Frontend/)
3. [A multi-threaded scheduler](http://matthewrocklin.com/blog/work/2015/01/06/Towards-OOC-Scheduling/)
4. [Matrix Multiply Benchmark](http://matthewrocklin.com/blog/work/2015/01/14/Towards-OOC-MatMul/)

We now present `chest` a `dict` type that spills to disk when we run out of
memory.  We show how it prevents large computations from flooding memory.


Intermediate Data
-----------------

<img src="{{ BASE_PATH }}/images/dask/fail-case.gif"
      align="right"
      width="50%"
      alt="A case where our scheduling algorithm fails to avoid intermediates">

If you read the
[post on scheduling](http://matthewrocklin.com/blog/work/2015/01/06/Towards-OOC-Scheduling/)
you may recall our goal to minimize intermediate storage during a multi-worker
computation.  The image on the right shows a trace of our scheduler as it
traverses a task dependency graph.  We want to compute the entire graph quickly
while keeping only a small amount of data in memory at once.

Sometimes we fail and our scheduler stores many large intermediate results.  In
these cases we want to spill excess intermediate data to disk rather than
flooding local memory.


Chest
-----

Chest is a dict-like object that writes data to disk once it runs out of
memory.

{% highlight Python %}
>>> from chest import Chest
>>> d = Chest(available_memory=1e9)  # Only use a GigaByte
{% endhighlight %}

It satisfies the `MutableMapping` interface so it looks and feels exactly like
a `dict`.  Below we show an example using a chest with only enough data to
store one Python integer in memory.

{% highlight Python %}
>>> d = Chest(available_memory=24)  # enough space for one Python integer

>>> d['one'] = 1
>>> d['two'] = 2
>>> d['three'] = 3
>>> d['three']
3
>>> d.keys()
['one', 'two', 'three']
{% endhighlight %}

We keep some data in memory

{% highlight Python %}
>>> d.inmem
{'three': 3}
{% endhighlight %}

While the rest lives on disk

{% highlight Python %}
>>> d.path
'/tmp/tmpb5ouAb.chest'
>>> os.listdir(d.path)
['one', 'two']
{% endhighlight %}

By default we store data with pickle but `chest` supports any protocol
with the `dump/load` interface (`pickle`, `json`, `cbor`, `joblib`, ....)

A quick point about `pickle`.  Frequent readers of my blog may know of my
sadness at how this library
[serializes functions](http://matthewrocklin.com/blog/work/2013/12/05/Parallelism-and-Serialization/)
and the crippling effect on multiprocessing.
That sadness does not extend to normal data.  Pickle is fine for data if you
use the `protocol=` keyword to `pickle.dump` correctly .  Pickle isn't a good
cross-language solution, but that doesn't matter in our application of
temporarily storing numpy arrays on disk.


Recent tweaks
-------------

In using `chest` alongside `dask` with any reasonable success I had to make the
following improvements to the original implementation:

1.  A basic LRU mechanism to write only infrequently used data
2.  A policy to avoid writing the same data to disk twice if it hasn't changed
3.  Thread safety

Now we can execute more dask workflows without risk of flooding memory

{% highlight Python %}
A = ...
B = ...
expr = A.T.dot(B) - B.mean(axis=0)

cache = Chest(available_memory=1e9)

into('myfile.hdf5::/result', expr, cache=cache)
{% endhighlight %}

Now we incur only moderate slowdown when we schedule poorly and run into large
quantities of intermediate data.


Conclusion
----------

Chest is only useful when we fail to schedule well.  We can still improve
scheduling algorithms to avoid keeping data in memory but it's nice to have
`chest` as a backup for when these algorithms fail.  Resilience is reassuring.
