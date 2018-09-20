---
layout: post
title: Towards Out-of-core ND-Arrays -- Slicing and Stacking
category : work
tags : [scipy, Python, Programming, Blaze, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr** Dask.arrays can slice and stack.  This is useful for weather data.


Introduction
------------

This is the sixth in a sequence of posts constructing an out-of-core nd-array
using NumPy, and dask.  You can view these posts here:

1. [Simple task scheduling](http://matthewrocklin.com/blog/work/2014/12/27/Towards-OOC/),
2. [Frontend usability](http://matthewrocklin.com/blog/work/2014/12/30/Towards-OOC-Frontend/)
3. [A multi-threaded scheduler](http://matthewrocklin.com/blog/work/2015/01/06/Towards-OOC-Scheduling/)
4. [Matrix Multiply Benchmark](http://matthewrocklin.com/blog/work/2015/01/14/Towards-OOC-MatMul/)
5. [Spilling to disk](http://matthewrocklin.com/blog/work/2015/01/16/Towards-OOC-SpillToDisk/)

Now we talk about slicing and stacking.  We use meteorological data as an
example use case.


Slicing
-------

Dask.array now supports most of the NumPy slicing syntax.  In particular it
supports the following:

*  Slicing by integers and slices ``x[0, :5]``
*  Slicing by a `list`/`np.ndarray` of integers  ``x[[1, 2, 4]]``
*  Slicing by a `list`/`np.ndarray` of booleans ``x[[False, True, True, False, True]]``

It does not currently support the following:

*  Slicing one ``dask.array`` with another ``x[x > 0]``
*  Slicing with lists in multiple axes  ``x[[1, 2, 3], [3, 2, 1]]``


Stack and Concatenate
---------------------

We often store large arrays on disk in many different files.  We
want to stack or concatenate these arrays together into one logical array.
Dask solves this problem with the `stack` and `concatenate` functions, which
stitch many arrays together into a single array, either creating a new
dimension with `stack` or along an existing dimension with `concatenate`.

### Stack

We stack many existing dask arrays into a new array, creating a new dimension
as we go.

{% highlight Python %}
>>> import dask.array as da
>>> arrays = [from_array(np.ones((4, 4)), blockshape=(2, 2))
...            for i in range(3)]  # A small stack of dask arrays

>>> da.stack(arrays, axis=0).shape
(3, 4, 4)

>>> da.stack(arrays, axis=1).shape
(4, 3, 4)

>>> da.stack(arrays, axis=2).shape
(4, 4, 3)
{% endhighlight %}

This creates a new dimension with length equal to the number of slices

### Concatenate

We concatenate existing arrays into a new array, extending them along an
existing dimension

{% highlight Python %}
>>> import dask.array as da
>>> arrays = [from_array(np.ones((4, 4)), blockshape=(2, 2))
...            for i in range(3)]  # small stack of dask arrays

>>> da.concatenate(arrays, axis=0).shape
(12, 4)

>>> da.concatenate(arrays, axis=1).shape
(4, 12)
{% endhighlight %}


Case Study with Meteorological Data
-----------------------------------

To test this new functionality we download [meteorological
data](http://www.ecmwf.int/en/research/climate-reanalysis/era-interim) from the
[European Centre for Medium-Range Weather
Forecasts](http://www.ecmwf.int/#main-menu).  In particular we have the
temperature for the Earth every six hours for all of 2014 with spatial
resolution of a quarter degree.  We download this data using [this
script](https://gist.github.com/mrocklin/26d8323f9a8a6a75fce0) (please don't
hammer their servers unnecessarily) (Thanks due to [Stephan
Hoyer](http://stephanhoyer.com/) for pointing me to this dataset).

As a result, I now have a bunch of netCDF files!

    $ ls
    2014-01-01.nc3  2014-03-18.nc3  2014-06-02.nc3  2014-08-17.nc3  2014-11-01.nc3
    2014-01-02.nc3  2014-03-19.nc3  2014-06-03.nc3  2014-08-18.nc3  2014-11-02.nc3
    2014-01-03.nc3  2014-03-20.nc3  2014-06-04.nc3  2014-08-19.nc3  2014-11-03.nc3
    2014-01-04.nc3  2014-03-21.nc3  2014-06-05.nc3  2014-08-20.nc3  2014-11-04.nc3
    ...             ...             ...             ...             ...

{% highlight Python %}
>>> import netCDF4
>>> t = netCDF4.Dataset('2014-01-01.nc3').variables['t2m']
>>> t.shape
(4, 721, 1440)
{% endhighlight %}

The shape corresponds to four measurements per day (24h / 6h), 720 measurements
North/South (180 / 0.25) and 1440 measurements East/West (360/0.25).  There are
365 files.

Great!  We collect these under one logical dask array, concatenating along
the time axis.

{% highlight Python %}
>>> from glob import glob
>>> filenames = sorted(glob('2014-*.nc3'))
>>> temps = [netCDF4.Dataset(fn).variables['t2m'] for fn in filenames]

>>> import dask.array as da
>>> arrays = [da.from_array(t, blockshape=(4, 200, 200)) for t in temps]
>>> x = da.concatenate(arrays, axis=0)

>>> x.shape
(1464, 721, 1440)
{% endhighlight %}

Now we can play with `x` as though it were a NumPy array.

{% highlight Python %}
avg = x.mean(axis=0)
diff = x[1000] - avg
{% endhighlight %}

If we want to actually compute these results we have a few options

{% highlight Python %}
>>> diff.compute()  # compute result, return as array, float, int, whatever is appropriate
>>> np.array(diff)  # compute result and turn into `np.ndarray`
>>> diff.store(anything_that_supports_setitem)  # For out-of-core storage
{% endhighlight %}

Alternatively, because many scientific Python libraries call `np.array` on
inputs, we can just feed our `da.Array` objects directly in to matplotlib
(hooray for the `__array__` protocol!):

{% highlight Python %}
>>> from matplotlib import imshow
>>> imshow(x.mean(axis=0), cmap='bone')
>>> imshow(x[1000] - x.mean(axis=0), cmap='RdBu_r')
{% endhighlight %}

<table>
<tr>
<td><a href="{{ BASE_PATH }}/images/avg.png">
        <img src="{{ BASE_PATH }}/images/avg.png" width="100%"></a></td>
<td><a href="{{ BASE_PATH }}/images/diff.png">
        <img src="{{ BASE_PATH }}/images/diff.png" width="100%"></a></td>
</tr>
</table>

I suspect that the temperature scale is in Kelvin.  It looks like the random
day is taken during Northern Summer.  Another fun one, lets look at the
difference between the temperatures at 00:00 and at 12:00

{% highlight Python %}
>>> imshow(x[::4].mean(axis=0) - x[2::4].mean(axis=0), cmap='RdBu_r')
{% endhighlight %}

<a href="{{ BASE_PATH }}/images/day-vs-night.png">
    <img src="{{ BASE_PATH }}/images/day-vs-night.png" width="100%"></a>

Even though this looks and feels like NumPy we're actually operating off of
disk using blocked algorithms.  We execute these operations using only a small
amount of memory.  If these operations were computationally intense (they
aren't) then we also would also benefit from multiple cores.


What just happened
------------------

To be totally clear the following steps just occurred:

1.  Open up a bunch of netCDF files and located a temperature variable
    within each file.  This is cheap.
2.  For each of those temperature variables create a `da.Array` object,
    specifying how we want to block up that variable.  This is also cheap.
3.  Make a new `da.Array` by concatenating all of our `da.Array`s for each
    day.  This, like the other steps, is just book-keeping.  We haven't loaded
    data or computed anything yet.
4.  Write numpy-style code `x[::2].mean(axis=0) - x[2::2].mean(axis=0)`.
    This creates yet another `da.Array` with a more complex task graph.  It
    takes a few hundred milliseconds to create this dictionary.
5.  Call``imshow`` on our `da.Array` object
6.  `imshow` calls `np.array` on its input, this starts the multi-core task
    scheduler
7.  A flurry of chunks fly out of all the netCDF files.  These chunks meet
    various NumPy functions and create new chunks.  Well organized magic occurs
    and an `np.ndarray` emerges.
8.  Matplotlib makes a pretty graph


Problems that Popped Up
-----------------------

The threaded scheduler is introducing significant overhead in its planning.
For this workflow the single-threaded naive scheduler is actually significantly
faster.  We'll have to find better solutions to reduce scheduling overhead.


Conclusion
----------

I hope that this shows off how `dask.array` can be useful when dealing with
collections of on-disk arrays.  As always I'm very happy to hear how we can
make this project more useful for your work.  If you have large n-dimensional
datasets I'd love to hear about what you do and how `dask.array` can help.  I
can be reached either in the comments below or at `blaze-dev@continuum.io`.


Acknowledgements
----------------

First, other projects can already do this.  In particular if this seemed useful
for your work then you should probably also know about
[Biggus](https://github.com/SciTools/biggus),
produced by the UK Met office, which has been around for much longer than
`dask.array` and is used in production.

Second, this post shows off work from the following people:

1.  [Erik Welch](https://github.com/eriknw) ([Continuum](http://continuum.io))
    wrote optimization passes to clean up dask graphs before execution.
2.  [Wesley Emeneker](https://github.com/nevermindewe) ([Continuum](http://continuum.io)) wrote a good deal of the slicing code
3.  [Stephan Hoyer](http://stephanhoyer.com/) ([Climate Corp](http://climate.com/))
    talked me through the application and pointed me to the data.  If you'd
    like to see dask integrated with
    [`xray`](http://xray.readthedocs.org/en/stable/)
    then you should definitely bug Stephan :)
