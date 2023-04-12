---
layout: post
title: Deep Dive: Creating a Dask DataFrame Collection with from_map
author: Rick Zamora
tags: [dataframe, IO]
theme: twitter
---

{% include JB/setup %}

[Dask DataFrame](https://docs.dask.org/en/stable/dataframe.html) provides dedicated IO functions for several popular tabular-data formats, like CSV and Parquet. If you are working with a supported format, then the corresponding function (e.g `read_csv`) is likely to be the most reliable way to create a new Dask DataFrame collection. For other workflows, [`from_map`](https://docs.dask.org/en/stable/generated/dask.dataframe.from_map.html) now offers a convenient way to define a DataFrame collection as an arbitrary function mapping. While these kinds of workflows have historically required users to adopt the Dask Delayed API, `from_map` now makes custom collection creation both easier and more performant.

## What is `from_map`?

The `from_map` API was added to Dask DataFrame in v2022.05.1 with the intention of replacing `from_delayed` as the recommended means of custom DataFrame creation. At its core, `from_map` simply converts each element of an iterable object (`inputs`) into a distinct Dask DataFrame partition, using a common function (`func`):

```python
dd.from_map(func: Callable, iterable: Iterable) -> dd.DataFrame
```

The overall behavior is essentially the Dask DataFrame equivalent of the standard-Python `map` function:

```python
map(func: Callable, iterable: Iterable) -> Iterator
```

Note that both `from_map` and `map` actually support an arbitrary number of iterable inputs. However, we will only focus on the use of a single iterable argument in this post.

## A simple example

To better understand the behavior of `from_map`, let’s consider the simple case that we want to interact with Feather-formatted data created with the following Pandas code:

```python
import pandas as pd

size = 3
paths = ["./data.0.feather", "./data.1.feather"]
for i, path in enumerate(paths):
    index = range(i * size, i * size + size)
    a = [i] * size
    b = list("xyz")
    df = pd.DataFrame({"A": a, "B": b, "index": index})
    df.to_feather(path)
```

Since Dask does not yet offer a dedicated `read_feather` function (as of `dask-2023.3.1`), most users would assume that the only option to create a Dask DataFrame collection is to use `dask.delayed`. The “best practice” for creating a collection in this case, however, is to wrap `pd.read_feather` or `cudf.read_feather` in a `from_map` call like so:

```python
>>> import dask.dataframe as dd
>>> ddf = dd.from_map(pd.read_feather, paths)
>>> ddf
Dask DataFrame Structure:
                   A       B  index
npartitions=2
               int64  object  int64
                 ...     ...    ...
                 ...     ...    ...
Dask Name: read_feather, 1 graph layer
```

Which produces the following Pandas (or cuDF) object after computation:

```python
>>> ddf.compute()
   A  B  index
0  0  x      0
1  0  y      1
2  0  z      2
0  1  x      3
1  1  y      4
2  1  z      5
```

Although the same output can be achieved using the conventional `dd.from_delayed` strategy, using `from_map` will improve the available opportunities for task-graph optimization within Dask.

## Performance considerations: Specifying `meta` and `divisions`

Although `func` and `iterable` are the only _required_ arguments to `from_map`, one can significantly improve the overall performance of a workflow by specifying optional arguments like `meta` and `divisions`.

Due to the lazy nature of Dask DataFrame, each collection is required to carry around a schema (column name and dtype information) in the form of an empty Pandas (or cuDF) object. If `meta` is not directly provided to the `from_map` function, the schema will need to be populated by eagerly materializing the first partition, which can increase the apparent latency of the `from_map` API call itself. For this reason, it is always recommended to specify an explicit `meta` argument if the expected column names and dtypes are known a priori.

While passing in a `meta` argument is likely to reduce the`from_map` API call latency, passing in a `divisions` argument makes it possible to reduce the end-to-end compute time. This is because, by specifying `divisions`, we are allowing Dask DataFrame to track useful per-partition min/max statistics. Therefore, if the overall workflow involves grouping or joining on the index, Dask can avoid the need to perform unnecessary shuffling operations.

## Using `from_map` to implement a custom API

Although it is currently difficult to automatically extract division information from the metadata of an arbitrary Feather dataset, `from_map` makes it relatively easy to implement your own highly-functional `read_feather` API using [PyArrow](https://arrow.apache.org/docs/python/index.html). For example, the following code is all that one needs to enable lazy Feather IO with both column projection and index selection:

```python
def from_arrow(table):
    """(Optional) Utility to enforce 'backend' configuration"""
    from dask import config

    if config.get("dataframe.backend") == "cudf":
        import cudf

        return cudf.DataFrame.from_arrow(table)
    else:
        return table.to_pandas()


def read_feather(paths, columns=None, index=None):
    """Create a Dask DataFrame from Feather files

    Example of a "custom" `from_map` IO function

    Parameters
    ----------
    paths: list
        List of Feather-formatted paths. Each path will
        be mapped to a distinct DataFrame partition.
    columns: list or None, default None
        Optional list of columns to select from each file.
    index: str or None, default None
        Optional column name to set as the DataFrame index.

    Returns
    -------
    dask.dataframe.DataFrame
    """
    import dask.dataframe as dd
    import pyarrow.dataset as ds

    # Step 1: Extract `meta` from the dataset
    dataset = ds.dataset(paths, format="feather")
    meta = from_arrow(dataset.schema.empty_table())
    meta = meta.set_index(index) if index else meta
    columns = columns or list(meta.columns)
    meta = meta[columns]

    # Step 2: Define the `func` argument
    def func(frag, columns=None, index=None):
        # Create a Pandas DataFrame from a dataset fragment
        # NOTE: In practice, this function should
        # always be defined outside `read_feather`
        assert columns is not None
        read_columns = columns
        if index and index not in columns:
            read_columns = columns + [index]
        df = from_arrow(frag.to_table(columns=read_columns))
        df = df.set_index(index) if index else df
        return df[columns] if columns else df

    # Step 3: Define the `iterable` argument
    iterable = dataset.get_fragments()

    # Step 4: Call `from_map`
    return dd.from_map(
        func,
        iterable,
        meta=meta,
        index=index,  # `func` kwarg
        columns=columns,  # `func` kwarg
    )
```

Here we see that using `from_map` to enable completely-lazy collection creation only requires four steps. First, we use `pyarrow.dataset` to define a `meta` argument for `from_map`, so that we can avoid the unnecessary overhead of an eager read operation. For some file formats and/or applications, it may also be possible to calculate `divisions` at this point. However, as explained above, such information is not readily available for this particular example.

The second step is to define the underlying function (`func`) that we will use to produce each of our final DataFrame partitions. Third, we define one or more iterable objects containing the unique information needed to produce each partition (`iterable`). In this case, the only iterable object corresponds to a generator of `pyarrow.dataset` fragments, which is essentially a wrapper around the input path list.

The fourth and final step is to use the final `func`, `interable`, and `meta` information to call the `from_map` API. Note that we also use this opportunity to specify additional key-word arguments, like `columns` and `index`. In contrast to the iterable positional arguments, which are always mapped to `func`, these key-word arguments will be broadcasted.

Using the`read_feather` implementation above, it becomes both easy and efficient to convert an arbitrary Feather dataset into a lazy Dask DataFrame collection:

```python
>>> ddf = read_feather(paths, columns=["A"], index="index")
>>> ddf
Dask DataFrame Structure:
                   A
npartitions=2
               int64
                 ...
                 ...
Dask Name: func, 1 graph layer
>>> ddf.compute()
       A
index
0      0
1      0
2      0
3      1
4      1
5      1
```

## Advanced: Enhancing column projection

Although a `read_feather` implementation like the one above is likely to meet the basic needs of most applications, it is certainly possible that users will often leave out the `column` argument in practice. For example:

```python
a = read_feather(paths)["A"]
```

For code like this, as the implementation currently stands, each IO task would be forced to read in an entire Feather file, and then select the `”A”` column from a Pandas/cuDF DataFrame only after it had already been read into memory. The additional overhead is insignificant for the toy-dataset used here. However, avoiding this kind of unnecessary IO can lead to dramatic performance improvements in real-world applications.

So, how can we modify our `read_feather` implementation to take advantage of external column-projection operations (like `ddf["A"]`)? The good news is that `from_map` is already equipped with the necessary graph-optimization hooks to handle this, so long as the `func` object satisfies the `DataFrameIOFunction` protocol:

```python
@runtime_checkable
class DataFrameIOFunction(Protocol):
    """DataFrame IO function with projectable columns
    Enables column projection in ``DataFrameIOLayer``.
    """

    @property
    def columns(self):
        """Return the current column projection"""
        raise NotImplementedError

    def project_columns(self, columns):
        """Return a new DataFrameIOFunction object
        with a new column projection
        """
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        """Return a new DataFrame partition"""
        raise NotImplementedError
```

That is, all we need to do is change “Step 2” of our implementation to use the following code instead:

```python
    from dask.dataframe.io.utils import DataFrameIOFunction

    class ReadFeather(DataFrameIOFunction):
        """Create a Pandas/cuDF DataFrame from a dataset fragment"""
        def __init__(self, columns, index):
            self._columns = columns
            self.index = index

        @property
        def columns(self):
            return self._columns

        def project_columns(self, columns):
            # Replace this object with one that will only read `columns`
            if columns != self.columns:
                return ReadFeather(columns, self.index)
            return self

        def __call__(self, frag):
            # Same logic as original `func`
            read_columns = self.columns
            if index and self.index not in self.columns:
                read_columns = self.columns + [self.index]
            df = from_arrow(frag.to_table(columns=read_columns))
            df = df.set_index(self.index) if self.index else df
            return df[self.columns] if self.columns else df

    func = ReadFeather(columns, index)
```

## Conclusion

It is now easier than ever to create a Dask DataFrame collection from an arbitrary data source. Although the `dask.delayed` API has already enabled similar functionality for many years, `from_map` now makes it possible to implement a custom IO function without sacrificing any of the high-level graph optimizations leveraged by the rest of the Dask DataFrame API.

Start experimenting with [`from_map`](https://docs.dask.org/en/stable/generated/dask.dataframe.from_map.html) today, and let us know how it goes!
