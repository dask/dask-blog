---
layout: post
title: Building GPU Groupby-Aggregations for Dask
author: Matthew Rocklin
tags: [dataframe, GPU, RAPIDS]
theme: twitter
---

{% include JB/setup %}

## Summary

We've sufficiently aligned Dask DataFrame and cuDF to get groupby aggregations
like the following to work well.

```python
df.groupby('x').y.mean()
```

This post describes the kind of work we had to do as a model for future
development.

## Plan

As outlined in a previous post, [Dask, Pandas, and GPUs: first
steps](../../../2019/01/13/dask-cudf-first-steps.html), our plan to produce
distributed GPU dataframes was to combine [Dask
DataFrame](https://docs.dask.org/en/latest/dataframe.html) with
[cudf](https://rapids.ai). In particular, we had to

- change Dask DataFrame so that it would parallelize not just around the
  Pandas DataFrames that it works with today, but around anything that looked
  enough like a Pandas DataFrame
- change cuDF so that it would look enough like a Pandas DataFrame to fit
  within the algorithms in Dask DataFrame

## Changes

On the Dask side this mostly meant replacing

- Replacing `isinstance(df, pd.DataFrame)` checks with `is_dataframe_like(df)`
  checks (after defining a suitable
  `is_dataframe_like`/`is_series_like`/`is_index_like` functions
- Avoiding some more exotic functionality in Pandas, and instead trying to
  use more common functionality that we can expect to be in most DataFrame
  implementations

On the cuDF side this means making dozens of tiny changes to align the cuDF API
to the Pandas API, and to add in missing features.

- **Dask Changes:**
  - [Remove explicit pandas checks and provide cudf lazy registration #4359](https://github.com/dask/dask/pull/4359)
  - [Replace isinstance(..., pandas) with is_dataframe_like #4375](https://github.com/dask/dask/pull/4375)
  - [Add has_parallel_type](https://github.com/dask/dask/pull/4395)
  - [Lazily register more cudf functions and move to backends file #4396](https://github.com/dask/dask/pull/4396)
  - [Avoid checking against types in is_dataframe_like #4418](https://github.com/dask/dask/pull/4418)
  - [Replace cudf-specific code with dask-cudf import #4470](https://github.com/dask/dask/pull/4470)
  - [Avoid groupby.agg(callable) in groupby-var #4482](https://github.com/dask/dask/pull/4482) -- this one is notable in that by simplifying our Pandas usage we actually got a significant speedup on the Pandas side.
- **cuDF Changes:**
  - [Build DataFrames from CUDA array libraries #529](https://github.com/rapidsai/cudf/issues/529)
  - [Groupby AttributeError](https://github.com/rapidsai/cudf/issues/534)
  - [Support comparison operations on Indexes #556](https://github.com/rapidsai/cudf/issues/556)
  - [Support byte ranges in read_csv (and other formats) #568](https://github.com/rapidsai/cudf/issues/568):w
  - [Allow "df.index = some_index" #824](https://github.com/rapidsai/cudf/issues/824)
  - [Support indexing on groupby objects #828](https://github.com/rapidsai/cudf/issues/828)
  - [Support df.reset_index(drop=True) #831](https://github.com/rapidsai/cudf/issues/831)
  - [Add Series.groupby #879](https://github.com/rapidsai/cudf/issues/879)
  - [Support Dataframe/Series groupby level=0 #880](https://github.com/rapidsai/cudf/issues/880)
  - [Implement division on DataFrame objects #900](https://github.com/rapidsai/cudf/issues/900)
  - [Groupby objects aren't indexable by column names #934](https://github.com/rapidsai/cudf/issues/934)
  - [Support comparisons on index operations #937](https://github.com/rapidsai/cudf/issues/937)
  - [Add DataFrame.rename #944](https://github.com/rapidsai/cudf/issues/944)
  - [Set the index of a dataframe/series #967](https://github.com/rapidsai/cudf/issues/967)
  - [Support concat(..., axis=1) #968](https://github.com/rapidsai/cudf/issues/968)
  - [Support indexing with a pandas index from columns #969](https://github.com/rapidsai/cudf/issues/969)
  - [Support indexing a dataframe with another boolean dataframe #970](https://github.com/rapidsai/cudf/issues/970)

I don't really expect anyone to go through all of those issues, but my hope is
that by skimming over the issue titles people will get a sense for the kinds of
changes we're making here. It's a large number of small things.

Also, kudos to [Thomson Comer](https://github.com/thomcom) who solved most of
the cuDF issues above.

## There are still some pending issues

- [Square Root #1055](https://github.com/rapidsai/cudf/issues/1055), needed for groupby-std
- [cuDF needs multi-index support for columns #483](https://github.com/rapidsai/cudf/issues/483), needed for:

  ```python
  gropuby.agg({'x': ['sum', mean'], 'y': ['min', 'max']})
  ```

## But things mostly work

But generally things work pretty well today:

```python
In [1]: import dask_cudf

In [2]: df = dask_cudf.read_csv('yellow_tripdata_2016-*.csv')

In [3]: df.groupby('passenger_count').trip_distance.mean().compute()
Out[3]: <cudf.Series nrows=10 >

In [4]: _.to_pandas()
Out[4]:
0    0.625424
1    4.976895
2    4.470014
3    5.955262
4    4.328076
5    3.079661
6    2.998077
7    3.147452
8    5.165570
9    5.916169
dtype: float64
```

## Experience

First, most of this work was handled by the cuDF developers (which may be
evident from the relative lengths of the issue lists above). When we started
this process it felt like a never-ending stream of tiny issues. We weren't
able to see the next set of issues until we had finished the current set.
Fortunately, most of them were pretty easy to fix. Additionally, as we went
on, it seemed to get a bit easier over time.

Additionally, lots of things work other than groupby-aggregations as a result
of the changes above. From the perspective of someone accustomed to Pandas,
The cuDF library is starting to feel more reliable. We hit missing
functionality less frequently when using cuDF on other operations.

## What's next?

More recently we've been working on the various join/merge operations in Dask
DataFrame like indexed joins on a sorted column, joins between large and small
dataframes (a common special case) and so on. Getting these algorithms from
the mainline Dask DataFrame codebase to work with cuDF is resulting in a
similar set of issues to what we saw above with groupby-aggregations, but so
far the list is much smaller. We hope that this is a trend as we continue on
to other sets of functionality into the future like I/O, time-series
operations, rolling windows, and so on.
