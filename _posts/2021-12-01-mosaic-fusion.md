---
layout: post
title: Mosaic Image Fusion
author: Volker Hilsenstein, Marvin Albert, and Genevieve Buckley
tags: [life science, image analysis]
theme: twitter
---

{% include JB/setup %}

## Executive Summary

This blogpost shows a case study where a researcher uses Dask for mosaic image fusion.
Mosaic image fusion is when you combine multiple smaller images taken at known locations and stitch them together into a single image with a very large field of view. Full code examples are available on GitHub from the [`DaskFusion`](https://github.com/VolkerH/DaskFusion) repository:
[https://github.com/VolkerH/DaskFusion](https://github.com/VolkerH/DaskFusion)

## The problem

### Image mosaicing in microscopy

In optical microscopy, a single field of view captured with a 20x objective typically
has a diagonal on the order of a few 100 μm (exact dimensions depend on other
parts of the optical system, including the size of the camera chip). A typical
sample slide has a size of 25mm by 75mm.
Therefore, when imaging a whole slide, one has to acquire hundreds of images, typically
with some overlap between individual tiles. With increasing magnification,
the required number of images increases accordingly.

To obtain an overview one has to fuse this large number of individual
image tiles into a large mosaic image. Here, we assume that the information required for
positioning and alignment of the individual image tiles is known. In the example presented here,
this information is available as metadata recorded by the microscope, namely the microscope stage
position and the pixel scale. Alternatively, this
information could also be derived from the image data directly, e.g. through a
registration step that matches corresponding image features in the areas where tiles overlap.

## The solution

The array that can hold the resulting mosaic image will often have a size that is too large
to fit in RAM, therefore we will use Dask arrays and the [`map_blocks`](https://docs.dask.org/en/latest/generated/dask.array.map_blocks.html) function to enable
out-of-core processing. The [`map_blocks`](https://docs.dask.org/en/latest/generated/dask.array.map_blocks.html)
function will process smaller blocks (a.k.a chunks) of the output array individually, thus eliminating the need to
hold the whole output array in memory. If sufficient resources are available, dask will also distribute the processing of blocks across several workers,
thus we also get parallel processing for free, which can help speed up the fusion process.

Typically whenever we want to join Dask arrays, we use [Stack, Concatenate, and Block](https://docs.dask.org/en/latest/array-stack.html). However, these are not good tools for mosaic image fusion, because:

1. The image tiles will be be overlapping,
2. Tiles may not be positioned on an exact grid and will typically also have slight rotations as the alignment of stage and camera is not perfect. In the most general case, for example in panaromic photo mosaics,
   individual image tiles could be arbitrarily rotated or skewed.

The starting point for this mosaic prototype was some code that reads in the stage metadate for all tiles and calculates an affine transformation for each tile that would place it at the correct location
in the output array.

The image below shows preliminary work placing mosaic image tiles into the correct positions using the napari image viewer.
Shown here is a small example with 63 image tiles.

<img src="/images/mosaic-fusion/NapariMosaics.png" alt="Mosaic fusion images in the napari image viewer" width="700" height="265">

And here is an animation of placing the individual tiles.

<img src="/images/mosaic-fusion/Lama_whole_slide.gif" alt="Animation of whole slide mosaic fusion images" width="700" height="361">

To leverage processing with Dask we created a `fuse` function that generates a small block of the final mosaic and is invoked by `map_blocks` for each chunk of the output array.
On each invocation of the `fuse` function `map_blocks` passes a dictionary (`block_info`). From the [Dask documentation](https://docs.dask.org/en/latest/generated/dask.array.map_blocks.html?highlight=block_info#dask.array.map_blocks):

> Your block function gets information about where it is in the array by accepting a special `block_info` or `block_id` keyword argument.

The basic outline of the `fuse` function of the mosaic workflow is as follows.
For each chunk of the output array:

1. Determine which source image tiles intersect with the chunk.
2. Adjust the image tiles' affine transformations to take the offset of the chunk within the array into account.
3. Load all intersectiong image tiles and apply their respective adjusted affine transformation to map them into the chunk.
4. Blend the tiles using a simple maximum projection.
5. Return the blended chunk.

Using a maximum projection to blend areas with overlapping tiles can lead to artifacts such as ghost images and visible tile
seams, so you would typically want to use something more sophisticated in production.

### Results

For datasets with many image tiles (~500-1000 tiles), we could speed up the mosaic generation from several hours to tens of minutes using this Dask based method
(compared to a previous workflow using ImageJ plugins runnning on the same workstation).
Due to Dask's ability to handle data out-of-core and chunked array storage using zarr it is also possible to run the
fusion on hardware with limited RAM.

Finally, we have the final mosaic fusion result.

<img src="/images/mosaic-fusion/final-mosaic-fusion-result.png" alt="Final mosaic fusion result" width="700" height="486">

### Code

Code relatiing to this mosaic image fusion project can be found in the [`DaskFusion`](https://github.com/VolkerH/DaskFusion) GitHub repository here:
[https://github.com/VolkerH/DaskFusion](https://github.com/VolkerH/DaskFusion)

There is a self-contained example available in [this notebook](https://github.com/VolkerH/DaskFusion/blob/main/DaskFusion_Example.ipynb), which downloads reduced-size example data to demonstrate the process.

## What's next?

Currently, the DaskFusion code is a proof of concept for single-channel 2D images and simple maximum projection for blending the tiles in overlapping areas, it is not production code.
However, the same principle can be used for fusing multi-channel image volumes,
such as from Light-Sheet data if the tile chunk intersection calculation is extended to higher-dimensional arrays.
Such even larger datasets will benefit even more from leveraging dask,
as the processing can be distributed across multiple nodes of a HPC cluster using [dask jobqueue](http://jobqueue.dask.org/en/latest/).

### Also see

Marvin's lightning talk on multi-view image fusion:
[15 minute video available here on YouTube](https://www.youtube.com/watch?v=YIblUvonMvo&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=10)

The GitHub repository [MVRegFus](https://github.com/m-albert/MVRegFus) that Marvin talks about in the video is available here:
[https://github.com/m-albert/MVRegFus](https://github.com/m-albert/MVRegFus)

The [napari-lazy-openslide](https://github.com/manzt/napari-lazy-openslide) visualization plugin by [Trevor Manz](https://github.com/manzt): _"An experimental plugin to lazily load multiscale whole-slide tiff images with openslide and dask."_

For further information on alternative approaches to image stitching:

- ASHLAR: Alignment by Simultaneous Harmonization of Layer / Adjacency Registration
  - [ASHLAR homepage](https://labsyspharm.github.io/ashlar/)
  - [ASHLAR GitHub repository](https://github.com/labsyspharm/ashlar)
  - [ASHLAR biorxiv pre-print](https://doi.org/10.1101/2021.04.20.440625)
- Microscopy Image Stitching Tool (MIST)
  - [MIST homepage](https://pages.nist.gov/MIST/)
  - [MIST GitHub repository](https://github.com/usnistgov/MIST)
  - [MIST algorithm documentation (PDF)](https://raw.githubusercontent.com/wiki/USNISTGOV/MIST/assets/mist-algorithm-documentation.pdf)
- The [m2stitch](https://github.com/yfukai/m2stitch) python package by [Yohsuke T. Fukai](https://github.com/yfukai): _"Provides robust stitching of tiled microscope images on a regular grid"_ (based on the MIST algorithm)

## Acknowledgements

This computational work was done by Volker Hilsenstein, in conjunction with Marvin Albert.
Volker Hilsenstein is a scientific software developer at [EMBL in Theodore Alexandrov's lab](https://www.embl.org/groups/alexandrov/) with a focus on spatial metabolomics and bio-image analysis.

The sample images were prepared and imaged by Mohammed Shahraz from the Alexandrov lab at EMBL Heidelberg.

Genevieve Buckley and Volker Hilsenstein wrote this blogpost.
