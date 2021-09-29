---
layout: post
title: Benchmarking imread functions
author: Genevieve Buckley
tags: [image analysis, life science]
theme: twitter
---
{% include JB/setup %}

## Summary

This blogpost is only for people who are interested in the behind the scenes

If you just want to know how to read image data into Dask, see [this blogpost instead](https://blog.dask.org/2019/06/20/load-image-data).

## Contents

* [Too many options](#too-many-options)
* [How to choose](#how-to-choose)
* [Performance results](#performance-results)
* [Final thoughts](#final-thoughts)

## Too many options

Previously, we've learned about how to read images into Dask in this blogpost by John Kirkham: [Load Large Image Data with Dask Array](https://blog.dask.org/2019/06/20/load-image-data).

However, there are several other ways to read images into Dask not discussed in the previous blogpost. Currently, they include...

1. The [dask-image imread function](http://image.dask.org/en/latest/dask_image.imread.html#dask_image.imread.imread): `from dask_image.imread import imread`
2. There is also an [imread function inside Dask itself](https://docs.dask.org/en/latest/generated/dask.array.image.imread.html?highlight=image#dask.array.image.imread): `from dask.array.image import imread`
3. Wrapping the `imread` function of another library (eg: imageio) with [dask delayed](https://tutorial.dask.org/01_dask.delayed.html)
4. The [aicsimageio](https://github.com/AllenCellModeling/aicsimageio) library (there is an 11 minute video introduction to aicsimageio [is available here](https://www.youtube.com/watch?v=LNa_gGpSnvc&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=8))
5. ... and maybe more

This is not ideal. If we go by the [Zen of Python](https://www.python.org/dev/peps/pep-0020/):
> There should be one-- and preferably only one --obvious way to do it.

Having too many ways to do the same task makes it hard to choose the *best* way to do that task. Ideally, we would guide users to the preferred method.

## How to choose

In order to guide users to the preferred method, we need to assess the advantages and disadvantages of each of the current methods.

Requirements:
- MUST cope with input /path/to/many/files/*.tif
- MUST cope with multiple 3D input arrays https://github.com/dask/dask-image/issues/220
- MUST cope with s3 string provided as input https://github.com/dask/dask-image/issues/234  (if sort=True... then sort filenames)
- MUST not be unreasonably slow
- should be able to load into cupy/other libraries (maybe we just add a map statement at the end there? the asanyarray is causing issues)
- should cope with list of filenames provided

## Performance results



## Final thoughts

