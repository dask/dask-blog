---
layout: post
title: Easy CPU/GPU Arrays and Dataframes
author: Rick Zamora (NVIDIA), Ben Zaitlen (NVIDIA)
tags: [GPU]
theme: twitter
canonical_url: https://medium.com/rapids-ai/easy-cpu-gpu-arrays-and-dataframes-run-your-dask-code-where-youd-like-e349d92351d
---

_This article was originally posted on the [RAPIDS blog](https://medium.com/rapids-ai/easy-cpu-gpu-arrays-and-dataframes-run-your-dask-code-where-youd-like-e349d92351d)._

It's now easy to switch between CPU (NumPy / Pandas) and GPU (CuPy / cuDF) in Dask.
As of Dask 2022.10.0, users can optionally select the backend engine for input IO and data creation. In the short-term, the goal of the backend-configuration system is to enable Dask users to write code that will run on both CPU and GPU systems.

The preferred backend can be configured using the `array.backend` and `dataframe.backend` options with the standard Dask configuration system:

```python
dask.config.set({"array.backend": "cupy"})
dask.config.set({"dataframe.backend": "cudf"})
```

## Dispatching for Array Creation

To see how users can easily switch between NumPy and CuPy, let's start by creating an array of ones:

```python
>>> with dask.config.set({"array.backend": "cupy"}):
...     darr = da.ones(10, chunks=(5,))  # Get cupy-backed collection
...
>>> darr
dask.array<ones_like, shape=(10,), dtype=float64, chunksize=(5,), chunktype=cupy.ndarray>
```

The `chunktype` informs us that the array is constructed with `cupy.ndarray`
objects instead of `numpy.ndarray` objects.

We've also improved the user experience for random array creation. Previously, if a user wanted to create a CuPy-backed Dask array, they were required to define an explicit `RandomState` object in Dask using CuPy. For example, the following code worked prior to Dask 2022.10.0, but seems rather verbose:

```python
>>> import cupy
>>> import dask.array as da
>>> rs = da.random.RandomState(RandomState=cupy.random.RandomState)
>>>
>>> darr = rs.randint(0, 3, size=(10, 20), chunks=(2, 5))
>>> darr
dask.array<randint, shape=(10, 20), dtype=int64, chunksize=(2, 5), chunktype=cupy.ndarray>
```

Now, we can leverage the `array.backend` configuration to create a CuPy-backed dask array for random data:

```python
>>> with dask.config.set({"array.backend": "cupy"}):
...     darr = da.random.randint(0, 3, size=(10, 20), chunks=(2, 5))  # Get cupy-backed collection
...
>>> darr
dask.array<randint, shape=(10, 20), dtype=int64, chunksize=(2, 5), chunktype=cupy.ndarray>
```

Using `array.backend` is significantly easier and much more ergonomic -- it supports all basic array creation methods including: `ones`, `zeros`, `empty`, `full`, `arange`, and `random`

_Note: `from_array`, `from_zarr`, `from_tiledb` have not yet been implemented
with this functionality_

## Dispatching for Dataframe Creation

When creating Dask Dataframes backed by either Pandas or cuDF, the beginning is often the input I/O methods: read_csv, read_parquet, etc. We'll first start by constructing a dataframe on the fly with `from_dict`:

```python
>>> with dask.config.set({"dataframe.backend": "cudf"}):
...     data = {"a": range(10), "b": range(10)}
...     ddf = dd.from_dict(data, npartitions=2)
...
>>> ddf
<dask_cudf.DataFrame | 2 tasks | 2 npartitions>
```

Here we can tell we have a cuDF backed dataframe and we are using `dask-cudf`
because the repr shows us the type: `<dask_cudf.DataFrame | 2 tasks | 2 npartitions>`.
Let's also demonstrate the read functionality by generating CSV and
Parquet data.

```python
ddf.to_csv('example.csv', single_file=True)
ddf.to_parquet('example.parquet')
```

Now we are simply repeating the config setting but instead using the `read_csv`
and `read_parquet` methods:

```
>>> with dask.config.set({"dataframe.backend": "cudf"}):
...     ddf = dd.read_csv('example.csv')
...     print(type(ddf))
...
<class 'dask_cudf.core.DataFrame'>
>>> with dask.config.set({"dataframe.backend": "cudf"}):
...     ddf = dd.read_parquet('example.parquet')
...     type(ddf)
...
<class 'dask_cudf.core.DataFrame'>
>>>
```

## Why is this Useful ?

As hardware changes in exciting and exotic ways with: GPUs, TPUs, IPUs,
etc., we want to provide the same interface and treat hardware as an
abstraction. For example, many PyTorch workflows start with the following:

```python
device = 'cuda' if torch.cuda.is_available() else 'cpu'
```

And what follows is typically standard hardware agnostic PyTorch. This is
incredibly powerful as the user (in most cases) should not care what hardware
underlies the source. As such, it enables the user to develop PyTorch anywhere
and everywhere. The new Dask backend selection configurations gives users a
similar freedom.

Conclusion

Our long-term goal of this feature is to enable Dask users to use any backend library in dask.array and dask.dataframe, as long as that library conforms to the minimal "array" or "dataframe" standard defined by the data-api consortium, respectively.

The RAPIDS team consistently works with the open-source community to understand and address emerging needs. If you’re an open-source maintainer interested in bringing GPU-acceleration to your project, please reach out on Github or Twitter. The RAPIDS team would love to learn how potential new algorithms or toolkits would impact your work.
