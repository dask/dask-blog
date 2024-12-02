---
layout: post
title: Histogramming with Dask
author: <a href="https://ddavis.io/">Doug Davis</a> (Anaconda)
tags: [histogram, array, dask]
theme: twitter
---

{% include JB/setup %}

## Primer on Histogramming in Python

[Histograms][wiki] are a core data type for many uses of statistics.
Countless scientific computing libraries provide an interface for
binning data ("histogramming") in any number of dimensions. Python has
an embarrassment of riches with regards to histogramming, and we won't
go into all existing libraries. In the author's opinion, the best
avenues for histogramming in Python (as of August 2022) are NumPy and
[boost-histogram][bh]. NumPy provides a number of functions associated
with binning data; the main three are [`histogram`][nphist],
[`histogram2d`][nphist2d], and [`histogramdd`][nphistdd].
Boost-histogram provides an object oriented API for binning data, with
multiple types of [axes][bhaxes], [storages][bhstorage], and
[accumulators][bhaccum]. For simple cases NumPy is great and gets the
job done, but boost-histogram provides a much more feature-rich
library and it is also [more performant][perf].

## Enter Dask

Since `dask.array` implements a subset of the NumPy interface, it's
natural for `dask.array` to implement the functions that exist in
`NumPy`. That's exactly what we do!

The [dask-histogram][dh] project...

[bh]: https://boost-histogram.readthedocs.io/en/latest/
[wiki]: https://en.wikipedia.org/wiki/Histogram
[nphist]: https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
[nphistdd]: https://numpy.org/doc/stable/reference/generated/numpy.histogramdd.html
[nphist2d]: https://numpy.org/doc/stable/reference/generated/numpy.histogram2d.html
[bhaxes]: https://boost-histogram.readthedocs.io/en/latest/user-guide/axes.html
[bhaccum]: https://boost-histogram.readthedocs.io/en/latest/user-guide/accumulators.html
[bhstorage]: https://boost-histogram.readthedocs.io/en/latest/user-guide/storage.html
[perf]: https://boost-histogram.readthedocs.io/en/latest/notebooks/PerformanceComparison.html
[dh]: https://dask-histogram.readthedocs.io/en/stable/
