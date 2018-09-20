---
layout: post
title: Dask and Spark DataFrames
tagline: a small performance comparison
draft: true
category: work
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
the [XDATA Program](http://www.darpa.mil/program/XDATA)
and the Data Driven Discovery Initiative from the [Moore
Foundation](https://www.moore.org/).*

Summary
-------

We compare performance between Spark DataFrames and Dask DataFrames.  We begin
with strong disclaimers about how these benchmarks are limited in scope and
should not be taken too broadly.

Generally we find the following:

1.  For linear operations (arithmetic, where clauses), aggregations, and
    some groupby-aggregations ...
2.  For operations requiring all-to-all (shuffle) communication ...
3.  For operations requiring some complex computation ...

We present these benchmarks with discussion about each, highlighting technical
differences between the projects.

Introduction
------------

Dask and Spark are both libraries offering parallel and distributed computing
in Python.  Both are large projects with different objectives and capabilities.
They do overlap in functionality a bit; in particular, both projects offer a
large distributed dataframe similar to the in-memory dataframes of R or Pandas.
As a result, Dataframes provide an opportunity to benchmark both projects
together.

Spark and Dask dataframes have reached this same feature set coming from two
different approaches.  Spark started with distributed computing and built out
numeric computing (like Tungsten) while Dask comes from the numeric computing
community and built out distributed computing.  The APIs differ somewhat, Spark
dataframes borrowing more heavily from SQL while Dask dataframes copy the
Pandas user interface.


Motivation
----------

Benchmarks inform both users and developers.  They help users to decide between
different projects.  They help developers to understand where they can improve
performance.

Benchmarks are also used for marketing purposes.  To be clear I am paid by a
for-profit company to develop Dask (a liberally licensed open source project
with a good fraction of core contributors outside of the company.)  However I
hope that from the tone of this article you will come to understand that this
is not my primary goal.  I hold each project in high esteem.

My personal motivation is that people ask me "So how does Dask compare with
Spark?" a few times a week now, and some of those people are primarily
interested in Dataframes, so I'd like to have a reference to which I can point
them.  This is now that reference.

To be clear, Dask and Spark differ greatly beyond just dataframes.  I know and
work with several companies that use Dask to solve their computational problems
and maybe 10% of them focus their use on Dataframes.  Dask is foremost a
computational task scheduler, dataframes are a subcomponent.


Disclaimers
-----------

First though, some important disclaimers:

1.  I, the author of this blogpost, am highly biased towards Dask.
2.  These benchmarks focus on a very small subset of what each project can do
    and are not representative of the capabilities of either project.
    Any generalizations of results here is likely to be misleading
3.  Benchmarking is very hard to do well.  See this [recent
    blocpost](http://matthewrocklin.com/blog/work/2017/03/09/biased-benchmarks)
    about how even very honest authors can make several mistakes in the
    benchmarking process.

To address some of these failings I've done the following:

1.  To address the problem of skewed expertise and benchmark selection, I have
    collaborated with other people that I consider to be Spark experts, notably
    X and Y (TODO, check with collaborators, verify that they're comfortable
    being named).  I general trust these people as decent human beings.  They
    each have long technical records.

2.  To address the problem of focusing benchmarks towards a project's strengths
    I have done two things:
    1.  For the core benchmarks we've restricted operations to what I consider
        to be a very small core subset of functionality that more-or-less
        overlaps with the first week of someone learning SQL.
    2.  We have explicitly created sections that are biased to either side.
        The goal here is less to quantitatively compare performance
        (the differences are very large) but more to make the point that the
        projects have different objectives and strengths, and to clearly inform
        people about those strengths.  My hope is that this removes a sense of
        competition, and instead creates a sense of education.

3.  To address the problem of omitting negative results I [pre-announced my
    intent to release
    benchmarks](http://matthewrocklin.com/blog/work/2017/03/09/biased-benchmarks)
    before I ever ran anything on a cluster (though I admit that I had done a
    day or two of initial testing beforehand.)

4.  To address the problem of tuning during benchmarking, I'll admit that I
    *did* tune while running the benchmarks, but during most of the benchmarks
    listed here I'll use the latest release (pushed a few weeks before I
    started this).  I'll call out a couple of cases where newer changes made a
    difference.

That being said I am highly biased towards Dask, I am writing most of the prose
of this article, and so my biases will probably carry through regardless.


Datasets
--------

These projects process data.  We need data to perform benchmarks.  We want data
with the following properties:

1.  Representative of data we find in the wild
2.  Easy to create/load in each project
3.  Can scale up or down as we increase or decrease cluster sizes

Dask.dataframe has a convenient ``dd.demo`` submodule that has functions that
produce realistic-ish data for testing, demonstration, and benchmarking.

### Financial Time Series

```python
import dask.dataframe as dd
df = dd.demo.daily_stock('GOOG', '2010', '2011', freq='1s')

>>> df.head()
                       close     high      low     open
timestamp
2010-01-04 09:00:00  626.941  626.951  626.939  626.951
2010-01-04 09:00:01  626.957  626.957  626.947  626.953
2010-01-04 09:00:02  626.979  626.979  626.956  626.956
2010-01-04 09:00:03  626.984  626.984  626.960  626.970
2010-01-04 09:00:04  626.978  626.993  626.978  626.983
```

This function downloads daily stock data from Yahoo! finance using the
[pandas_datareader](https://github.com/pydata/pandas-datareader) project and
then interpolates within each day, creating random data that matches the
observed high/low/open/close values for the day.  We can produce arbitrarily
large datasets by increasing the sampling frequency.

Dask.dataframe is built on Pandas and Pandas probably has a bit of a cultural
advantage to financial time series due to its long history within the financial
services community.  The Python data science stack generally does well on large
blocks of floating point data (thank you C/Fortran heritage) so we should look
for another dataset to counterbalance this.

### Mixed Data Types

```python
df = dd.demo.make_timeseries('2001', '2002',
                             {'x': float, 'id': int, 'name': str},
                             freq='1s', partition_freq='1d')

>>> df.head()
                       id     name         x
2001-01-01 00:00:00  1033   Ursula  0.893336
2001-01-01 00:00:01  1058   Yvonne -0.894900
2001-01-01 00:00:02   968   Oliver -0.045531
2001-01-01 00:00:03  1026    Laura  0.735042
2001-01-01 00:00:04   979  Norbert  0.923535
```

We use a second function that produces uncorrelated data of common types.
Floating point data is uniformly distributed between [-1, 1].  Integers are
distributed with a Poisson distribution with parameter 1000 (so some variation,
but also many repeats).  Names come from a fixed list of 26 names, one for each
letter (many repeats)

This allows us to play to some of Python's weaknesses (strings) and some of
Spark's strengths (integer optimizations).


### Communication

The most performant way we've seen to move data between Dask.dataframes and
Spark dataframes is through the Parquet format, which both can read and write
quickly.  Even this is a bit tenuous however because Spark has established a
number of conventions on top of the normal Parquet standard (which moves
slowly) and so in some cases we will need to do a bit of transformation on
either side.

However, we will have the exact same data within each project.


### Feedback, comments?

I would love to find better ways to generate realistic data across both
projects.  I welcome pointers to any projects that do this well in the comments
at the bottom of this post.


Computational Setup
-------------------

### Notebook

While developing benchmarks my test machine was a laptop

1.  Intel(R) Core(TM) i7-6600U CPU @ 2.60GHz (though running without
    hyperthreading, and so has only four logical cores)
2.  16GB RAM
3.  An SSD with NVMe interconnect, generally yielding in the gigabyte range for
    disk bandwidth

### Clusters

While running benchmarks on a cluster I used Amazon's hardware.  I provisioned
a cluster using the [dask-ec2](https://github.com/dask/dask-ec2) project.  I
launched Spark on this cluster using a recent hack
[dask-spark](https://github.com/mrocklin/dask-spark) which allows one to launch
Dask from Spark or Spark from Dask.

These clusters had the following configurations:

TODO


Benchmarks
==========

We groups benchmarks based on their computation/communication patterns into the
following groups:

1.  Linear-ish, including arithmetic, aggregations, filters, some
    groupby-aggregations
2.  Communication-heavy, including all-to-alls/shuffles, notably groupby-apply,
    large-table joins on non-indexed columns, and sorts.
3.  Other cases where communication patterns are less straightforward,
    including windowing functions, random access, etc..

In each section we'll present a plot of benchmarks and then show code and
lightly discuss interesting bits.


Linear-ish
----------

Generally both projects perform ...

TODO: Plot

Details


Communication-heavy
-------------------

Generally ...

TODO: Plot

Details


Other Communication Patterns
----------------------------

Generally ...

TODO: Plot

Details

