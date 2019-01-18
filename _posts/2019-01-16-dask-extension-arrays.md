---
layout: post
title: Extension Arrays in Dask DataFrame
author: Tom Augspurger
tagline: Extension Arrays in Dask DataFrame
tags: [dask, dataframe]
theme: twitter
---

{% include JB/setup %}

*This work is supported by [Anaconda Inc](http://anaconda.com)*

Summary
-------

Dask DataFrame works well with pandas' new Extension Array interface, including
third-party extension arrays.

Background
----------

Pandas 0.23 introduced the [`ExtensionArray`][EA], a way to store things other
than a simple NumPy array in a DataFrame or Series. Internally pandas uses this
for data types that aren't handled natively by NumPy (datetimes with timezones,
Categorical, and nullable integer arrays, to name a few).


```python
>>> s = pd.Series(pd.date_range('2000', periods=4, tz="US/Central"))
>>> s
0   2000-01-01 00:00:00-06:00
1   2000-01-02 00:00:00-06:00
2   2000-01-03 00:00:00-06:00
3   2000-01-04 00:00:00-06:00
dtype: datetime64[ns, US/Central]
```

`dask.dataframe` has always supported the extension types that pandas defines.

```python
>>> import dask.dataframe as dd
>>> dd.from_pandas(s, npartitions=2)
Dask Series Structure:
npartitions=2
0    datetime64[ns, US/Central]
2                           ...
3                           ...
dtype: datetime64[ns, US/Central]
Dask Name: from_pandas, 2 tasks
```

The Challenge
-------------

Newer versions of pandas allow third-party libraries to write custom extension
arrays. These arrays can be placed inside a DataFrame or Series, and work
just as well as any extension arary defined within pandas itself. However,
third-party extension arrays provide a slight challenge for Dask.

Recall: `dask.dataframe` is lazy. We use a familiar pandas-like API to build up
a task graph, rather than executing immediately. But if Dask DataFrame is lazy,
then how do things like the following work?

```python
>>> df = pd.DataFrame({"A": [1, 2], 'B': [3, 4]})
>>> ddf = dd.from_pandas(df, npartitions=2)
>>> ddf[['B']].columns
Index(['B'], dtype='object')
```


`ddf[['B']]` (lazily) selects the column `'B'` from the dataframe. But accessing
`.columns` *immediately* returns a pandas Index object with just the selected
columns.

No real computation has happened (you could just as easily swap out the
`from_pandas` for a `dd.read_parquet` on a larger-than-memory dataset, and the
behavior would be the same). Dask is able to do these kinds of "metadata-only"
computations, where the output depends only on the columns and the dtypes,
without executing the task graph. Internally, Dask does this by keeping a pair
of dummy pandas DataFrames on each Dask DataFrame.

```python
>>> ddf._meta
Empty DataFrame
Columns: [A, B]
Index: []

>>> ddf._meta_nonempty
ddf._meta_nonempty
   A  B
0  1  1
1  1  1
```

We need the `_meta_nonempty`, since some operations in pandas behave differently
on an Empty DataFrame than on a non-empty one (either by design or,
occasionally, a bug in pandas).

The issue with third-party extension arrays is that Dask doesn't know what
values to put in the `_meta_nonempty`. We're quite happy to do it for each NumPy
dtype and each of pandas' own extension dtypes. But any third-party library
could create an ExtensionArray for any type, and Dask would have no way of
knowing what's a valid value for it.

The Solution
---------------

Rather than Dask guessing what values to use for the `_meta_nonempty`, extension
array authors (or users) can register their extension dtype with Dask. Once
registered, Dask will be able to generate the `_meta_nonempty`, and things
should work fine from there. For example, we can register the dummy DecimalArray
that pandas uses for testing (this isn't part of pandas' public API) with Dask.

```python
from decimal import Decimal
from pandas.tests.extension.decimal import DecimalArray, DecimalDtype

# The actual registration that would be done in the 3rd-party library
from dask.dataframe.extensions import make_array_nonempty


@make_array_nonempty.register(DecimalDtype)
def _(dtype):
    return DecimalArray._from_sequence([Decimal('0'), Decimal('NaN')],
                                       dtype=dtype)
```

Now users of that extension type can place those arrays inside a Dask DataFrame
or Series.


```python
>>> df = pd.DataFrame({"A": DecimalArray([Decimal('1.0'), Decimal('2.0'),
...                                       Decimal('3.0')])})

>>> ddf = dd.from_pandas(df, 2)
>>> ddf
Dask DataFrame Structure:
                     A
npartitions=1
0              decimal
2                  ...
Dask Name: from_pandas, 1 tasks

>>> ddf.dtypes
A    decimal
dtype: object
```

And from there, the usual operations just as the would in pandas.

```python
>>> from random import choices
>>> df = pd.DataFrame({"A": DecimalArray(choices([Decimal('1.0'),
...                                               Decimal('2.0')],
...                                              k=100)),
...                    "B": np.random.choice([0, 1, 2, 3], size=(100,))})
>>> ddf = dd.from_pandas(df, 2)
In [35]: ddf.groupby("A").B.mean().compute()
Out[35]:
A
1.0    1.50
2.0    1.48
Name: B, dtype: float64

```

The Real Lesson
---------------

It's neat that Dask now supports extension arrays. But to me, the exciting thing
is just how little work this took. The [PR implementing
this](https://github.com/dask/dask/pull/4379/files) is quite short, just
defining the object that third-parties register with, and using it to generate
the data when dtype is detected. And for third-party extension array authors,
the work is minimal.

This highlights the importance of one of the Dask project's core values: working
with the community. If you visit [dask.org](https://dask.org), you'll see
phrases like

> Integrates with existing projects

and

> Built with the broader community

At the start of Dask, the developers *could* have gone off an re-written pandas
or NumPy from scratch to be parallel friendly (though we'd probably still be
working on that part today, since that's such a massive undertaking). Instead,
the Dask developers worked with the community, occasionally nudging it in
directions that would help out dask. For example, many places in pandas [held
the GIL](http://matthewrocklin.com/blog/work/2015/03/10/PyData-GIL), preventing
thread-based parallelism. Rather than abandoning pandas, the Dask and pandas
developers worked together to release the GIL where possible when it was a
bottleneck for `dask.dataframe`. This benefited Dask and anyone else trying to
do thread-based parallelism with pandas DataFrames.

And now, when pandas introduces new features like nullable integers,
`dask.dataframe` just needs to register it as an extension type and immediately
benefits from it. And third-party extension array authors can do the same for
their extension arrays.

If you're writing an ExtensionArray, make sure to add it to the [pandas
ecosystem](http://pandas.pydata.org/pandas-docs/version/0.24/ecosystem.html#extension-data-types)
page, and register it with Dask.

[EA]: http://pandas.pydata.org/pandas-docs/version/0.24/extending.html#extension-types
