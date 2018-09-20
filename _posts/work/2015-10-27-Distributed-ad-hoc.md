---
layout: post
title: Ad-hoc Distributed Computation
category : work
draft: true
theme: twitter
tags : [scipy, Python, Programming, dask, blaze]
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr: We enable ad-hoc distributed computations with a concurrent.futures
interface.**


Distributed
-----------

The `distributed` project prototype provides distributed computing on a cluster
in pure Python.

*  [docs](http://distributed.readthedocs.org/en/latest/),
   [source](http://github.com/mrocklin/distributed/),
   [chat](https://gitter.im/mrocklin/distributed)

concurrent.futures interface
------------------------------

The `distributed.Executor` interface mimics the `concurrent.futures` stdlib package.

{% highlight Python %}
from distributed import Executor
executor = Executor('192.168.1.124:8787')  # address of center-node in cluster

def inc(x):
    return x + 1

>>> x = executor.submit(inc, 1)
>>> x
<Future: status: waiting, key: inc-8bca9db48807c7d8bf613135d01b875f>
{% endhighlight %}

The submit call executes `inc(1)` on a remote machine.  The returned future
serves as a proxy to the remote result.  We can collect this result back to the
local process with the `.result()` method:

{% highlight Python %}
>>> x.result()  # transfers data from remote to local process
2
{% endhighlight %}


Data Locality
-------------

However we don't want to move data with the `.result` method if we can avoid it.

By default the result of the computation (`2`) stays on the remote computer
where the computation occurred.  Data transfer often becomes the bottleneck so
we avoid calling `.result()` whenever possible.

We avoid data transfer by allowing `submit` calls to directly accept futures as
arguments:

{% highlight Python %}
>>> y = executor.submit(inc, x)  # no need to call x.result()
{% endhighlight %}

This deviates from the `concurrent.futures` API where we would wait on `x`
before submiting `y`.  We no longer have to do the following:

{% highlight Python %}
>>> y = executor.submit(inc, x.result())  # old concurrent.futures API
{% endhighlight %}

This is useful for two reasons:

1.  **Avoids moving data to the local process**:  We keep data on the
distributed network.  This avoids unnecessary data transfer.
2.  **Fire and forget**: We don't have to reason about which jobs finish before
which others.  The scheduler takes care of this for us.


Ad hoc computations
-------------------

For ad-hoc computations we often want the fine-grained control that a simple
`.submit(func, *args)` function provides.  Ad-hoc computations often have
various function calls that depend on each other in various strange ways; they
don't fit a particular model or framework.

We don't need this fine-grained control if we're just parsing JSON and loading
it into a database.  In this case bulk operations like `map` and `reduce`
provided by MapReduce or Spark are often sufficient.

However when our computations aren't straightforward and they don't fit nicely
into a framework then we're stuck performing `groupby` and `join` gymnastics
over strange key naming schemes to coerce our problem into the MapReduce or
Spark programming model.  If we're not operating at the peta-byte scale then
these programming models might be overkill.

The `.submit` function has an overhead of about a millisecond per call (not
counting network latency).  This might be crippling at the petabyte scale, but
it's quite convenient and freeing at the medium-data scale.  It lets us use a
cluster of machines without strongly mangling our code or our conceptual model
of what's going on.


Example: Binary Tree Reduction
------------------------------

As an example we perform a binary tree reduction on a sequence of random
arrays.

This is the kind of algorithm you would find hard-coded into a library like
[Spark](http://spark.apache.org/) or
[dask.array](http://dask.pydata.org/en/latest/array.html)/[dataframe](http://dask.pydata.org/en/latest/dataframe.html)
but that we can accomplish by hand with some for loops while still using
parallel distributed computing.  The difference here is that we're not limited
to the algorithms chosen for us and can screw around more freely.

    finish           total             single array output
        ^          /        \
        |        z1          z2
        |       /  \        /  \
        |     y1    y2    y3    y4     neighbors merge
        ^    / \   / \   / \   / \
    start   x1 x2 x3 x4 x5 x6 x7 x8    many array inputs

*  Make sixteen, million element random arrays on the cluster:

{% highlight Python %}
import numpy as np
xs = executor.map(np.random.random, [1000000] * 16, pure=False)
{% endhighlight %}

*  Add neighbors until there is only one left:

{% highlight Python %}
while len(xs) > 1:
    xs = [executor.submit(add, xs[i], xs[i + 1])
          for i in range(0, len(xs), 2)]
{% endhighlight %}

*  Fetch final result:

{% highlight Python %}
>>> xs[0].result()
array([  2.069694  ,   9.01727599,   5.42682524, ...,   0.42372487,
         1.50364966,  13.48674896])
{% endhighlight %}

This entire computation, from writing the code to receiving the answer takes
well under a second on a small cluster.  This isn't surprising, it's a very
small computation.  What's notable though is the very small startup and
overhead time.  It's rare to find distributed computing systems that can spin
up and finish small computations this quickly.

Notes
-----

Various other Python frameworks provide distributed function evaluation.  A few
are listed [here](http://distributed.readthedocs.org/en/latest/related-work.html)
.  Notably we're stepping on the toes of
[SCOOP](http://scoop.readthedocs.org/en/0.7/), which also provides a
distributed `concurrent.futures` interface.

The `distributed` project could use a more distinct name.  Any suggestions?

For more information see the following links:

*   [Documentation](http://distributed.readthedocs.org/en/latest/)
*   [Source on Github](http://github.com/mrocklin/distributed/)
*   [Gitter chat](https://gitter.im/mrocklin/distributed)
