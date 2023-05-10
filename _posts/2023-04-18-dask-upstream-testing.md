---
layout: post
title: Upstream testing in Dask
author: James Bourbeau
tags: [dask, ecosystem, pydata]
theme: twitter
canonical_url: https://blog.coiled.io/blog/dask-upstream-testing.html
---

{% include JB/setup %}

_Original version of this post appears on [blog.coiled.io](https://blog.coiled.io/blog/dask-upstream-testing.html?utm_source=dask-blog&utm_medium=dask-upstream-testing)_

[Dask](https://www.dask.org/) has deep integrations with other libraries in the PyData ecosystem like NumPy, pandas, Zarr, PyArrow, and more.
Part of providing a good experience for Dask users is making sure that Dask continues to work well with this community
of libraries as they push out new releases. This post walks through how Dask maintainers proactively ensure Dask
continuously works with its surrounding ecosystem.

## Nightly testing

Dask has a [dedicated CI build](https://github.com/dask/dask/blob/834a19eaeb6a5d756ca4ea90b56ca9ac943cb051/.github/workflows/upstream.yml)
that runs Dask's normal test suite once a day with unreleased, nightly versions of
several libraries installed. This lets us check whether or not a recent change in a library like NumPy or pandas
breaks some aspect of Dask’s functionality.

To increase visibility when such a breakage occurs, as part of the upstream CI build, an
issue is automatically opened that provides a summary of what tests failed and links to the build
logs for the corresponding failure ([here's an example issue](https://github.com/dask/dask/issues/9736)).

<div align="center">

<img src="/images/example-upstream-CI-issue.png" style="max-width: 100%;" width="100%" />

</div>

This makes it less likely that a failing upstream build goes unnoticed.

## How things can break and are fixed

There are usually two different ways in which things break. Either:

1. A library made an intentional change in behavior and a corresponding compatibility change needs to be made in
   Dask (the next section has an example of this case).
2. There was some unintentional consequence of a change made in a library that resulted in a breakage in Dask.

When the latter case occurs, Dask maintainers can then engage with other library maintainers to resolve the
unintended breakage. This all happens before any libraries push out a new release, so no user code breaks.

## Example: pandas 2.0

One specific example of this process in action is the recent pandas 2.0 release.
This is a major version release and contains significant breaking changes like removing deprecated functionality.

As these breaking changes were merged into pandas, we started seeing related failures in Dask's upstream CI build.
Dask maintainers were then able to add
[a variety of compatibility changes](https://github.com/dask/dask/pulls?q=is%3Apr+%22pandas+2.0%22+in%3Atitle) so
that Dask works well with pandas 2.0 immediately.

## Acknowledgements

Special thanks to [Justus Magin](https://github.com/keewis) for his work on the
[`xarray-contrib/issue-from-pytest-log`](https://github.com/xarray-contrib/issue-from-pytest-log) GitHub action.
We’ve found this to be really convenient for easily opening up GitHub issues when test failures occur.

Also, thanks to [Irina Truong](https://github.com/j-bennet) ([Coiled](https://www.coiled.io/?utm_source=dask-blog&utm_medium=dask-upstream-testing)), [Patrick Hoefler](https://github.com/phofl) ([Coiled](https://www.coiled.io/?utm_source=dask-blog&utm_medium=dask-upstream-testing)),
and [Matthew Roeschke](https://github.com/mroeschke) ([NVIDIA](https://rapids.ai/)) for their efforts ensuring pandas and Dask
continue to work together.
