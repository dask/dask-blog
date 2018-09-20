---
layout: post
title: Towards Out-of-core ND-Arrays -- Frontend
category : work
tags : [scipy, Python, Programming, Blaze, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr** Blaze adds usability to our last post on out-of-core ND-Arrays

*Disclaimer: This post is on experimental buggy code.  This is not ready for public
use.*

Setup
-----

This follows my [last
post](http://matthewrocklin.com/blog/work/2014/12/27/Towards-OOC/) designing a simple
task scheduler for use with out-of-core (or distributed) nd-arrays.  We
encoded tasks-with-data-dependencies as simple dictionaries.  We then
built functions to create dictionaries that describe blocked array operations.
We found that this was an effective-but-unfriendly way to solve some
important-but-cumbersome problems.

This post sugars the programming experience with `blaze` and `into` to give a
numpy-like experience out-of-core.


## Old low-level code

Here is the code we wrote for an
out-of-core transpose/dot-product (actually a symmetric rank-k update).

### Create random array on disk

{% highlight Python %}
import bcolz
import numpy as np
b = bcolz.carray(np.empty(shape=(0, 1000), dtype='f8'),
                 rootdir='A.bcolz', chunklen=1000)
for i in range(1000):
    b.append(np.random.rand(1000, 1000))
b.flush()
{% endhighlight %}

### Define computation `A.T * A`

{% highlight Python %}
d = {'A': b}
d.update(getem('A', blocksize=(1000, 1000), shape=b.shape))

# Add A.T into the mix
d.update(top(np.transpose, 'At', 'ij', 'A', 'ji', numblocks={'A': (1000, 1)}))

# Dot product A.T * A
d.update(top(dotmany, 'AtA', 'ik', 'At', 'ij', 'A', 'jk',
         numblocks={'A': (1000, 1), 'At': (1, 1000)}))
{% endhighlight %}

## New pleasant feeling code with Blaze

### Targetting users

The last section "Define computation" is written in a style that is great for
library writers and automated systems but is challenging to users
accustomed to Matlab/NumPy or R/Pandas style.

We wrap this process with Blaze, an extensible front-end for analytic
computations


### Redefine computation `A.T * A` with Blaze

{% highlight Python %}
from dask.obj import Array  # a proxy object holding on to a dask dict
from blaze import *

# Load data into dask dictionaries
dA = into(Array, 'A.bcolz', blockshape=(1000, 1000))
A = Data(dA)  # Wrap with blaze.Data

# Describe computation in friendly numpy style
expr = A.T.dot(A)

# Compute results
>>> %time compute(expr)
CPU times: user 2min 57s, sys: 6.4 s, total: 3min 3s
Wall time: 2min 50s
array([[ 334071.93541158,  250297.16968262,  250404.87729587, ...,
         250436.85274716,  250330.64262904,  250590.98832611],
       [ 250297.16968262,  333451.72293343,  249978.2751824 , ...,
         250103.20601281,  250014.96660956,  250251.0146828 ],
       [ 250404.87729587,  249978.2751824 ,  333279.76376277, ...,
         249961.44796719,  250061.8068036 ,  250125.80971858],
       ...,
       [ 250436.85274716,  250103.20601281,  249961.44796719, ...,
         333444.797894  ,  250021.78528189,  250147.12015207],
       [ 250330.64262904,  250014.96660956,  250061.8068036 , ...,
         250021.78528189,  333240.10323875,  250307.86236815],
       [ 250590.98832611,  250251.0146828 ,  250125.80971858, ...,
         250147.12015207,  250307.86236815,  333467.87105673]])
{% endhighlight %}


### Under the hood

Under the hood, Blaze creates the same dask dicts we created by hand last time.
I've doctored the result rendered here to include suggestive names.

{% highlight Python %}
>>> compute(expr, post_compute=False).dask
{('A': carray((10000000, 1000), float64), ...
 ...
 ('A', 0, 0): (ndget, 'A', (1000, 1000), 0, 0),
 ('A', 1, 0): (ndget, 'A', (1000, 1000), 1, 0),
 ...
 ('At', 0, 0): (np.transpose, ('A', 0, 0)),
 ('At', 0, 1): (np.transpose, ('A', 1, 0)),
 ...
 ('AtA', 0, 0): (dotmany, [('At', 0, 0), ('At', 0, 1), ('At', 0, 2), ...],
                          [('A', 0, 0),  ('A', 1, 0),  ('A', 2, 0), ...])
}
{% endhighlight %}

We then compute this sequentially on a single core.  However we could have
passed this on to a distributed system.  This result contains all necessary
information to go from on-disk arrays to computed result in whatever manner you
choose.


Separating Backend from Frontend
--------------------------------

Recall that Blaze is an extensible front-end to data analytics technologies.
It lets us wrap messy computational APIs with a pleasant and familiar
user-centric API.  Extending Blaze to dask dicts was the straightforward work
of an afternoon.  This separation allows us to continue to build out
dask-oriented solutions without worrying about user-interface.  By separating
backend work from frontend work we allow both sides to be cleaner and to
progress more swiftly.


Future work
-----------

I'm on vacation right now.  Work for recent posts has been done in evenings
while watching TV with the family.  It isn't particularly robust.  Still, it's
exciting how effective this approach has been with relatively little effort.

Perhaps now would be a good time to mention that Continuum has ample grant
funding.  We're looking for people who want to create usable large-scale data
analytics tools.  For what it's worth, I quit my academic postdoc to work on
this and couldn't be happier with the switch.


Source
------

This code is experimental and buggy.  I don't expect it to stay around for
forever in it's current form (it'll improve).  Still, if you're reading this
when it comes out then you might want to check out the following:

1.  [master branch on dask](https://github.com/mrocklin/dask)
2.  [array-expr branch on my blaze fork](https://github.com/mrocklin/blaze/tree/array-expr)
