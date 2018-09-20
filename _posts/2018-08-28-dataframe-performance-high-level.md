---
layout: post
title: High level performance of Pandas, Dask, Spark, and Arrow
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---

{% include JB/setup %}

*This work is supported by [Anaconda Inc](http://anaconda.com)*

## Question

> How does Dask dataframe performance compare to Pandas?  Also, what about
> Spark dataframes and what about Arrow?  How do they compare?

I get this question every few weeks.  This post is to avoid repetition.


## Caveats

1.  This answer is likely to change over time.  I'm writing this in August 2018
2.  This question and answer are very high level.
    More technical answers are possible, but not contained here.

## Answers

### Pandas

If you're coming from Python and have smallish datasets then Pandas is the
right choice.  It's usable, widely understood, efficient, and well maintained.


### Benefits of Parallelism

The performance benefit (or drawback) of using a parallel dataframe like Dask
dataframes or Spark dataframes over Pandas will differ based on the kinds of
computations you do:

1.  If you're doing small computations then Pandas is always the right choice.
    The administrative costs of parallelizing will outweigh any benefit.
    You should not parallelize if your computations are taking less than, say,
    100ms.

2.  For simple operations like filtering, cleaning, and aggregating large data
    you should expect linear speedup by using a parallel dataframes.

    If you're on a 20-core computer you might expect a 20x speedup.  If you're
    on a 1000-core cluster you might expect a 1000x speedup, assuming that you
    have a problem big enough to spread across 1000 cores.  As you scale up
    administrative overhead will increase, so you should expect the speedup to
    decrease a bit.

2.  For complex operations like distributed joins it's more complicated.  You
    might get linear speedups like above, or you might even get slowdowns.
    Someone experienced in database-like computations and parallel computing
    can probably predict pretty well which computations will do well.

However, configuration may be required.  Often people find that parallel
solutions don't meet expectations when they first try them out.  Unfortunately
most distributed systems require some configuration to perform optimally.


### There are other options to speed up Pandas

Many people looking to speed up Pandas don't need parallelism.  There are often
several other tricks like encoding text data, using efficient file formats,
avoiding groupby.apply, and so on that are more effective at speeding up Pandas
than switching to parallelism.


### Comparing Apache Spark and Dask

> Assuming that yes, I do want parallelism, should I choose Apache Spark, or Dask dataframes?

This is often decided more by cultural preferences (JVM vs Python,
all-in-one-tool vs integration with other tools) than performance differences,
but I'll try to outline a few things here:

-  Spark dataframes will be much better when you have large SQL-style queries
   (think 100+ line queries) where their query optimizer can kick in.
-  Dask dataframes will be much better when queries go beyond typical database
   queries.  This happens most often in time series, random access, and other
   complex computations.
-  Spark will integrate better with JVM and data engineering technology.
   Spark will also come with everything pre-packaged.  Spark is its own
   ecosystem.
-  Dask will integrate better with Python code.  Dask is designed to integrate
   with other libraries and pre-existing systems.  If you're coming from an
   existing Pandas-based workflow then it's usually much easier to evolve to
   Dask.

Generally speaking for most operations you'll be fine using either one.  People
often choose between Pandas/Dask and Spark based on cultural preference.
Either they have people that really like the Python ecosystem, or they have
people that really like the Spark ecosystem.

Dataframes are also only a small part of each project.  Spark and Dask both do
many other things that aren't dataframes.  For example Spark has a graph
analysis library, Dask doesn't.  Dask supports multi-dimensional arrays, Spark
doesn't.  Spark is generally higher level and all-in-one while Dask is
lower-level and focuses on integrating into other tools.

For more information, see [Dask's "Comparison to Spark documentation"](http://dask.pydata.org/en/latest/spark.html).


### Apache Arrow

> What about Arrow?  Is Arrow faster than Pandas?

This question doesn't quite make sense... *yet*.

Arrow is not a replacement for Pandas.  Today Arrow is useful to people
building *systems* and not to analysts directly like Pandas.  Arrow is used to
move data between different computational systems and file formats.  Arrow does
not do computation today, but is commonly used as a component in other
libraries that do do computation.  For example, if you use Pandas or Spark or
Dask today you may be using Arrow without knowing it.  Today Arrow is more
useful for other libraries than it is to end-users.

However, this is likely to change in the future.  Arrow developers plan
to write computational code around Arrow that we would expect to be faster than
the code in either Pandas or Spark.  This is probably a year or two away
though.  There will probably be some effort to make this semi-compatible with
Pandas, but it's much too early to tell.
