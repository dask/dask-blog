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
The acquistion techniques themselves are often state of the art and constantly
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

Despite data being stored in many different ways, often groups want to reapply the
same analytical pipeline to these datasets. However if the data pipeline is
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

A typical case is a large directory of image files. In particular,
TIFF files are quite common, though other formats could show up as well. It is
common to see a naming structure that mirrors that shown below. The `<i>`
represent different numbers.

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
might replace this with something like this.

```python
from dask.array.image import imread
a = imread("mydata_ch<i>_<j>t_<k>x_<l>y_<m>z.tif")
```

This offloads the actual image reading to scikit-image under the hood (much
like what happened explicitly before). Though this doesn't keep the data in
memory. Instead we briefly load the image once to figure out the metadata
(shape and type of the array loaded) and then drop it from memory. Once we
actually need this data for computation of some kind, it will be loaded back
in.

Though it's possible we run into data that we want to load that scikit-image
doesn't know to handle. In this case we have a few options. Though one pretty
easy one is we could supply our own [`imread` function for Dask to use](
https://docs.dask.org/en/latest/array-api.html#dask.array.image.imread ). This
way we could manage the subtleties of loading our own data image data format.
It might involve accessing some database to pull some image data out or could
involve interacting with cloud storage to pull some data down.

Thus far we have only showed how one might load one chunk. To load multiple
chunks we would need to iterate over our data some how and combine the chunks
together. Suppose we have one dimension to combine chunks along, we might write
some code that looks like that below. We would load all of the chunks of data
we have join them together with Dask Array's `block` to form a larger array. We
can easily extend this to more dimensions.

```python
data = []
for fn in files:
    data.append(dask.array.imread(fn))
data = dask.array.block(data)
```

Once we have performed this operation, we now have a Dask Array. All the
familiar operations that we have seen from NumPy can be used. Here's the [full
list of operations in the docs](
https://docs.dask.org/en/latest/array-api.html). This way we can leverage a
familiar API that we know from NumPy to operate more generally on our N-D image
data.

Future Work
-----------

Going forward it might make sense to wrap up this sort of operation behind a
standard API. We might also find that loading the full image data to parse
metadata is slow during graph construction. To workaround this, we might use
[dask-image's `imread`](
https://dask-image.readthedocs.io/en/latest/dask_image.imread.html ), which is
optimized for this use case. Though it may be more generally useful if the
community had [a standard way of parsing metadata quickly](
https://github.com/imageio/imageio/issues/382 ). If we have specialized
hardware lying around (like a GPU cluster), we might consider moving our loaded
data to GPU memory and leveraging GPU computations on our data.

* Note Zarr - standardizing multifile formats
* Note next steps with the data
* Other things to note?


* Do we want to reach out to the community here?
