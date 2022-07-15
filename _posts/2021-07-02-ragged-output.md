---
layout: post
title: Ragged output, how to handle awkward shaped results
author: Genevieve Buckley
theme: twitter
---

{% include JB/setup %}

## Executive Summary

This blogpost explains some of the difficulties associated with distributed computation and ragged or irregularly shaped outputs. We present a recommended method for using Dask in these circumstances.

## Background

Often, we come across workflows where analyzing the data involves searching for features (which may or may not be present) then computing some results from those features.
Because we don't know ahead of time how many features will be found, we can expect the processing output size to vary.

For distributed workloads, we need to split up the data, process it, and then recombine the results. That means ragged output can cause cause problems (like broadcasting errors) when Dask combines the output.

## Problem constraints

In this blogpost, we'll look at an example with the following constraints:

- Input array data
- A processing function requiring overlap between chunks
- The output returned

## Solution

The simplest strategy is a two step process:

1. Expand the array chunks using the [`overlap` function](https://docs.dask.org/en/latest/array-api.html?#dask.array.overlap.overlap).
2. Use [`map_blocks`](https://docs.dask.org/en/latest/array-api.html#dask.array.map_blocks) with the [`drop_axis` keyword argument](https://docs.dask.org/en/latest/array-api.html#dask.array.map_blocks)

## Example code

```python
import dask.array as da

arr = da.random.random((100, 100), chunks=(50,50))  # example input data
expanded = da.overlap.overlap(arr, depth=2, boundary="reflect")
result = expanded.map_blocks(processing_func, drop_axis=1, dtype=float)
result.compute()
```

## Multiple output types supported

This pattern supports multiple types of output from the processing function, including:

- numpy arrays
- pandas Series
- pandas DataFrames

You can try this for yourself using any of the example processing functions below, generating dummy data output. Or, you can try out a function of your own.

```python
# Random length, 1D output returned
import numpy as np
import pandas as pd

# function returns numpy array
def processing_func(x):
    random_length = np.random.randint(1, 7)
    return np.arange(random_length)

# function returns pandas series
def processing_func(x):
    random_length = np.random.randint(1, 7)
    output_series = np.arange(random_length)
    return pd.Series(output_series)

# function returns pandas dataframe
def processing_func(x):
    random_length = np.random.randint(1, 7)
    x_data = np.arange(random_length)
    y_data = np.random.random((random_length))
    return pd.DataFrame({"x": x_data, "y": y_data})
```

## Why can't I use `map_overlap` or `reduction`?

Ragged output sizes can cause [broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) errors when the outputs are combined for some Dask functions.

However, if ragged output sizes aren't a constraint for your particular programming problem, then you can continue to use the Dask [`map_overlap`](https://docs.dask.org/en/latest/array-api.html?#dask.array.overlap.map_overlap) and [`reduction`](https://docs.dask.org/en/latest/array-api.html?#dask.array.reduction) functions as much as you like.

## Alternative solution

### Dask delayed

As an alternative solution, you can use [Dask delayed](https://docs.dask.org/en/latest/delayed.html) (a tutorial is [available here](https://tutorial.dask.org/01_dask.delayed.html)).

Advantages:

- Your processing function can have any type of output (it not restricted to numpy or pandas objects)
- There is more flexibility in the ways you can use Dask delayed.

Disadvantages:

- You will have to handle combining the outputs yourself.
- You will have to be more careful about performance:
  - For example, because the code below uses delayed in a list comprehension, it's very important for performance reasons that we pass in the expected metadata. Fortunately, dask has a [`make_meta`](https://docs.dask.org/en/latest/dataframe-api.html#dask.dataframe.utils.make_meta) function available.
  - You can read more about performance considerations for Dask delayed and [best practices here](https://docs.dask.org/en/latest/delayed-best-practices.html).

Example code:

```python
import dask.array as da
import dask.dataframe as dd
import numpy as np
import pandas as pd
import dask

arr = da.ones((20, 10), chunks=(10, 10))

@dask.delayed
def processing_func(x):
    # returns dummy dataframe output
    random_length = np.random.randint(1,10)
    return pd.DataFrame({'x': np.arange(random_length),
                         'y': np.random.random(random_length)})

meta = dd.utils.make_meta([('x', np.int64), ('y', np.int64)])
expanded = da.overlap.overlap(arr, depth=2, boundary="reflect")
blocks = expanded.to_delayed().ravel()
results = [dd.from_delayed(processing_func(b), meta=meta) for b in blocks]
ddf = dd.concat(results)
ddf.compute()
```

## Summing up

That's it! We've learned how to avoid common errors when working with processing functions returning ragged outputs. The method recommended here works well with multiple output types including: numpy arrays, pandas series, and pandas DataFrames.
