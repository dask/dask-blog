---
layout: post
title: Exploring loading large image data with Dask Array
author: John Kirkham
draft: true
tags: [python,scipy,scikit-image,dask-image]
theme: twitter
---
{% include JB/setup %}

Series Overview
---------------

A common case in fields that acquire large amounts of imaging data is to write
out smaller acquisitions into many small files. These files can tile a larger
space, subsample from a larger time period, and may contain multiple channels.
The acquisition techniques themselves are often state of the art and constantly
pushing the envelope in term of how large a field of view can be acquired, at
what resolution, and what quality.

Once acquired this data presents a number of challenges. Algorithms often
designed and tested to work on very small pieces of this data need to be scaled
up to work on the full dataset. It might not be clear at the outset what will
actually work and so exploration still plays a very big part of the whole
process.

Historically this analytical process has involved a lot of custom code. Often
the analytical process is stitched together by a series of scripts possibly in
several different languages that write various intermediate results to disk.
Thanks to advances in modern tooling these process can be significantly
improved. In this series of blogposts, we will outline ways for image
scientists to leverage different tools to move towards a high level, friendly,
cohesive, interactive analytical pipeline.

Executive Summary
-----------------

This post explores a few simple workflows that a user might leverage to load
their image with Dask. At the end of this post users should be able to
construct a Dask Array, which they can use to further explore and manipulate
their image data.

Motivation
----------

Loading large image data can be a complex and often unique problem. Different
groups may choose to store this across many files on disk, a commodity or
custom database solution, or they may opt to store it in the cloud. Not all
datasets within the same group may be treated the same for a variety of
reasons. In short, this means loading data is a hard and expensive problem.

Despite data being stored in many different ways, often groups want to reapply
the same analytical pipeline to these datasets. However if the data pipeline is
tightly coupled to a particular way of loading the data for later analytical
steps, it may be very difficult if not impossible to reuse an existing
pipeline. In other words, there is friction between the loading and analysis
steps, which frustrates efforts to make things reusable.

Having a modular and general way to load data makes it easy to present data
stored differently in a standard way. Further having a standard way to present
data to analytical pipelines allows that part of the pipeline to focus on what
it does best, analysis! In general, this should decouple these to components in
a way that improves the experience of users involved in all parts of the
pipeline.


Loading image data with Dask
----------------------------

A typical case is a large directory of image files. In particular, TIFF files
are quite common, though other formats could show up as well. It is common to
see a naming structure that mirrors that shown below. Each filename then may
indicate a channel, time step, and spatial location with the `<i>` being some
numeric values (possibly with units). Individual filenames may have more or
less information and may notate it differently than we have.

```
mydata_ch<i>_<j>t_<k>x_<l>y_<m>z.tif
```

To load a single image, a user might write some code like the following:

```python
from skimage.io import imread
a = imread("mydata_ch<i>_<j>t_<k>x_<l>y_<m>z.tif")
```

While this works fine for reading a single image into memory, this will quickly
become prohibitive once we try to load more data than we have memory. So we
might use `delayed` to replace this with something like this. We can sub in the
shape and type from a single file that we have inspected. This could be used
for multiple files if we know them to be uniform and of the same type. This
gives us a Dask Array that represents the data on disk for us without using up
our memory to store it. Pulling from the data on demand.

```python
import dask.array as da
from dask.delayed import delayed
from skimage.io import imread
a = da.from_delayed(delayed(imread)("mydata_ch<i>_<j>t_<k>x_<l>y_<m>z.tif"),
                    <shape>,
                    <dtype>)
```

If we want to simplify this a bit, we can use a pre-rolled implementation that
does this work for us like [dask-image's `imread`](
https://dask-image.readthedocs.io/en/latest/dask_image.imread.html ). This
combines the simplicity of an API like scikit-image's with the benefits of
leveraging Dask to manage the larger data.

```python
from dask_image.imread import imread
a = imread("mydata_ch<i>_<j>t_<k>x_<l>y_<m>z.tif")
```

If we want to handle loading some other kind of data, we can take our own
loading function and combine it with `delayed`. This way we can handle
operations like reading from a database or requesting data from the cloud.

Combining data loaded with Dask
-------------------------------

Thus far we have only showed how one might load one image file. However we
generally have many such files. At a first pass we might try to load up the
collection of files in a list.

```python
from dask_image.imread import imread
l = [imread(fn) for fn in myfiles]
```

This is fine, but it's not that easy to manage. It would be better if we could
turn this into one Dask Array instead of a list of many. We have a couple
options. If we want to combine our Dask Arrays along an *existing* axis, we can
use [`concatenate`](
http://docs.dask.org/en/latest/array-api.html#dask.array.concatenate ).


```python
import dask.array as da
from dask_image.imread import imread

a = da.concatenate([imread(fn) for fn in myfiles])
```

Alternatively if we want to combine multiple arrays along a *new* axis, we can
use [`stack`]( http://docs.dask.org/en/latest/array-api.html#dask.array.stack
). This looks pretty similar.

```python
import dask.array as da
from dask_image.imread import imread

a = da.stack([imread(fn) for fn in myfiles])
```

Both of these provide an `axis` argument. So we can specify which axis to join
along or where to add a new axis. By default `axis=0`.

```python
import dask.array as da
from dask_image.imread import imread

a = da.concatenate([imread(fn) for fn in myfiles], axis=-1)
```

This works fine for combining along a single axis. However if we need to
combine across multiple we need to perform multiple concatenate steps.
Fortunately there is a simpler option [`block`](
http://docs.dask.org/en/latest/array-api.html#dask.array.block ), which can
concatenate along multiple axes at once.

```python
import dask.array as da
from dask_image.imread import imread

a = da.block([[imread(fn00), imread(fn01)],
              [imread(fn10), imread(fn11)]])
```

Though we know our original data looked a bit more like this
`mydata_<i>x_<j>y.tif`. Using block with this format might
looking something like this.

```python
from dask_image.imread import imread
a = da.block([[imread("mydata_{i}x_{j}y.tif") for i in xs] for j in ys])
```

Once we have performed this operation, we now have a Dask Array. All the
familiar operations that we have seen from NumPy can be used. Here's the [full
list of operations in the docs]( https://docs.dask.org/en/latest/array-api.html
). This way we can leverage a familiar API that we know from NumPy to operate
more generally on our N-D image data.

Future Work
-----------

Reading full images to inspect metadata (like shape and type) is very
expensive. Under the hood implementations like dask-image's `imread` read only
the metadata instead of the full image. This works with some scientific image
formats, but not all general image formats. It would be useful to have a
community standard for reading image metadata quickly ( [ imageio/imageio#382
]( https://github.com/imageio/imageio/issues/382 ) ). This could form a basis
for a new standard Dask `imread` function.

If we have specialized
hardware lying around (like a GPU cluster), we might consider moving our loaded
data to GPU memory and leveraging GPU computations on our data.

* Note Zarr - standardizing multifile formats
* Note next steps with the data
* Other things to note?


* Do we want to reach out to the community here?
