---
layout: post
title: Image Analysis Redux
tagline: Dask + CuPy + RL
author: John Kirkham (NVIDIA) and Ben Zaitlen (NVIDIA)
theme: twitter
---
{% include JB/setup %}

Summary
-------


Image Analysis Redux
--------------------

[Last year](https://blog.dask.org/2019/08/09/image-itk) we experimented with Dask/ITK/Scikit-Image
to perform large scale image analysis on a stack of 3D images.  Specifically, we looked at `deconvolution`,
a common method to _deblur_ images.  Now, a year later, we return to these experiments with a better
understanding of how Dask and CuPy can interact, enhanced serialization methods, and support from the
open-source community.

Previously we used the [Richardson Lucy (RL)](https://en.wikipedia.org/wiki/Richardson%E2%80%93Lucy_deconvolution) deconvolution
algorithm from ITK and [Scikit-Image](https://github.com/scikit-image/scikit-image/blob/master/skimage/restoration/deconvolution.py#L329).
We left off at theorizing how GPUs could potentially help accelerate these workflows.  Starting with Scikit-Image's
implementation, we naively tried replacing `scipy.signal.convolve` calls with `cupyx.scipy.ndimage.convolve`, and while
performance improved, it did not improve _significantly_ -- that is, we did not get the 100X speed we were looking for.

Often, in working with images, we hit performance roadblocks in real space where data represents position.  When this happens,
we can reach for a common tool, the [Fast-Fourirer Transform FFT](https://en.wikipedia.org/wiki/Fast_Fourier_transform).  FFTs convert
the data to from real space to frequency space where data now represents the rate of change of intensity between pixels.  This conversion
is extremely fast on both CPUs and GPUs and the algorithm we can write with FFTs similarly are accelerated.
And while it is challenging to write an equivalent algorithm in FFT space (thank you mathematicians!)
the cost of transformation + the cost of the algorithm is still lower than performing the original algorithm in real space.
We (and others before us) found this was the case for Richardson Lucy (on both CPUs and GPUs) and performance continued increasing
when we parallelized with Dask over multiple GPUs.

Help from Open-Source
---------------------

An FFT RL equivalent has been around for some time and the good folks at the [Solar Dynamics Observatory](https://sdo.gsfc.nasa.gov/mission/instruments.php) built and shared a NumPy/CuPy implementation as part the [Atmospheric Imaging Assembly](https://aiapy.readthedocs.io/en/v0.2.0/_modules/aiapy/psf/deconvolve.html) Python package (aiapy).  We slightly modified their implementation to handle 3D as well as 2D [Point Spread Functions](https://en.wikipedia.org/wiki/Point_spread_function) and to take advantage of
[NEP-18](https://numpy.org/neps/nep-0018-array-function-protocol.html) for convenient dispatching of NumPy and CuPy to NumPy and CuPy functions:


```python
def deconvolve(img, psf=None, iterations=20):
    """
    """
    # 2D vs 3D psfs
    if len(psf.shape) == 2:
        psf = psf
    else:
        psf = psf[0]

    # pad psf with zeros to match image shape
    # use NumPy for padding
    pad_l, pad_r = np.divmod(np.array(img[0].shape) - np.array(psf.shape), 2)
    pad_r += pad_l

    psf = np.pad(psf, tuple(zip(pad_l, pad_r)), 'constant', constant_values=0)

    # padding centers the PSF so we no longer need to roll
    # Center PSF at pixel (0,0)
    for i in range(psf.ndim):
        psf = np.roll(psf, psf.shape[i]//2, axis=i)

    # Convolution requires FFT of the PSF
    psf = np.fft.rfftn(psf)
    psf = psf[None]

    psf_conj = psf.conj()

    img_decon = np.copy(img)
    for _ in range(iterations):
        ratio = (
            img / np.fft.irfftn(np.fft.rfftn(img_decon,
                                             axes=tuple(range(1, psf.ndim))) * psf,
                                             axes=tuple(range(1, psf.ndim)))
        )
        img_decon *= np.fft.irfftn(np.fft.rfftn(ratio,
                                                axes=tuple(range(1, psf.ndim))) * psf_conj,
                                                axes=tuple(range(1, psf.ndim)))
    return img_decon
```

For a 1.3 GB image we measured the following:

- CuPy ~3 seconds for 20 iterations
- NumPy ~36 second for 2 iterations

We see 10x increase in speed for 10 times the number of iterations -- very close to our desired 100X speedup!  Let's explore how this implementation
performs with real biological data and Dask...

Define a Dask Cluster and Load the Data
---------------------------------------

We were provided sample data from [Prof. Shroff's](https://www.nibib.nih.gov/about-nibib/staff/hari-shroff) lab at the NIH.  The data originally was
provided as a 3D TIFF file which we subsequently converted to Zarr with a shape of (950, 2048, 2048).

We start by creating a Dask cluster on a DGX2 and loading in Zarr data:

```python
from dask.distributed import Client
from dask_cuda import LocalCUDACluster
import dask.array as da

cluster = LocalCUDACluster(local_directory="/tmp/bzaitlen",
                           rmm_pool_size="26GB",
                    )
client = Client(cluster)

imgs = da.from_zarr("/public/NVMICROSCOPY/y1z1_C1_A.zarr/")
```

<table>
<tr>
<td>
<table>
  <thead>
    <tr><td> </td><th> Array </th><th> Chunk </th></tr>
  </thead>
  <tbody>
    <tr><th> Bytes </th><td> 7.97 GB </td> <td> 8.39 MB </td></tr>
    <tr><th> Shape </th><td> (950, 2048, 2048) </td> <td> (1, 2048, 2048) </td></tr>
    <tr><th> Count </th><td> 951 Tasks </td><td> 950 Chunks </td></tr>
    <tr><th> Type </th><td> uint16 </td><td> numpy.ndarray </td></tr>
  </tbody>
</table>
</td>
<td>
<svg width="212" height="202" style="stroke:rgb(0,0,0);stroke-width:1" >

  <!-- Horizontal lines -->
  <line x1="10" y1="0" x2="42" y2="32" style="stroke-width:2" />
  <line x1="10" y1="120" x2="42" y2="152" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="10" y1="0" x2="10" y2="120" style="stroke-width:2" />
  <line x1="12" y1="2" x2="12" y2="122" />
  <line x1="14" y1="4" x2="14" y2="124" />
  <line x1="16" y1="6" x2="16" y2="126" />
  <line x1="18" y1="8" x2="18" y2="128" />
  <line x1="20" y1="10" x2="20" y2="130" />
  <line x1="22" y1="12" x2="22" y2="132" />
  <line x1="24" y1="14" x2="24" y2="134" />
  <line x1="26" y1="16" x2="26" y2="136" />
  <line x1="28" y1="18" x2="28" y2="138" />
  <line x1="30" y1="20" x2="30" y2="140" />
  <line x1="32" y1="22" x2="32" y2="142" />
  <line x1="34" y1="24" x2="34" y2="144" />
  <line x1="36" y1="26" x2="36" y2="146" />
  <line x1="38" y1="28" x2="38" y2="148" />
  <line x1="41" y1="31" x2="41" y2="151" />
  <line x1="42" y1="32" x2="42" y2="152" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="10.000000,0.000000 42.743566,32.743566 42.743566,152.743566 10.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Horizontal lines -->
  <line x1="10" y1="0" x2="130" y2="0" style="stroke-width:2" />
  <line x1="12" y1="2" x2="132" y2="2" />
  <line x1="14" y1="4" x2="134" y2="4" />
  <line x1="16" y1="6" x2="136" y2="6" />
  <line x1="18" y1="8" x2="138" y2="8" />
  <line x1="20" y1="10" x2="140" y2="10" />
  <line x1="22" y1="12" x2="142" y2="12" />
  <line x1="24" y1="14" x2="144" y2="14" />
  <line x1="26" y1="16" x2="146" y2="16" />
  <line x1="28" y1="18" x2="148" y2="18" />
  <line x1="30" y1="20" x2="150" y2="20" />
  <line x1="32" y1="22" x2="152" y2="22" />
  <line x1="34" y1="24" x2="154" y2="24" />
  <line x1="36" y1="26" x2="156" y2="26" />
  <line x1="38" y1="28" x2="158" y2="28" />
  <line x1="41" y1="31" x2="161" y2="31" />
  <line x1="42" y1="32" x2="162" y2="32" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="10" y1="0" x2="42" y2="32" style="stroke-width:2" />
  <line x1="130" y1="0" x2="162" y2="32" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="10.000000,0.000000 130.000000,0.000000 162.743566,32.743566 42.743566,32.743566" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Horizontal lines -->
  <line x1="42" y1="32" x2="162" y2="32" style="stroke-width:2" />
  <line x1="42" y1="152" x2="162" y2="152" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="42" y1="32" x2="42" y2="152" style="stroke-width:2" />
  <line x1="162" y1="32" x2="162" y2="152" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="42.743566,32.743566 162.743566,32.743566 162.743566,152.743566 42.743566,152.743566" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Text -->
  <text x="102.743566" y="172.743566" font-size="1.0rem" font-weight="100" text-anchor="middle" >2048</text>
  <text x="182.743566" y="92.743566" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,182.743566,92.743566)">2048</text>
  <text x="16.371783" y="156.371783" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(45,16.371783,156.371783)">950</text>
</svg>
</td>
</tr>
</table>

From the Dask output above you can see the data is a z-stack of 950 images where each slice is 2048x2048.  For this data set, we can improve GPU performance if we operate on larger chunks.  Because DGX2 has 16 GPUs and we can comfortably fit the data and perform FFTs on the GPUs we `rechunk` the data for one chunk (or block) per GPU then apply the deconvolution to each block:

```python
# build bigger chunks
imgs = imgs.rechunk(chunks={0: 60})
imgs
```

<td>
<table>
  <thead>
    <tr><td> </td><th> Array </th><th> Chunk </th></tr>
  </thead>
  <tbody>
    <tr><th> Bytes </th><td> 7.97 GB </td> <td> 503.32 MB </td></tr>
    <tr><th> Shape </th><td> (950, 2048, 2048) </td> <td> (60, 2048, 2048) </td></tr>
    <tr><th> Count </th><td> 967 Tasks </td><td> 16 Chunks </td></tr>
    <tr><th> Type </th><td> uint16 </td><td> numpy.ndarray </td></tr>
  </tbody>
</table>
</td>

Next, we convert to float32 for faster GPU computation and load the data onto each GPU (note: this takes about 1.5 seconds for an 8GB image).
Below we map `cupy.asarray` onto each block of data.  `cupy.asarray` moves the data from host memory (NumPy) to the device/GPU (CuPy).

```python
imgs = imgs.astype(np.float32)
c_imgs = imgs.map_blocks(cupy.asarray)
```

<table>
<tr>
<td>
<table>
  <thead>
    <tr><td> </td><th> Array </th><th> Chunk </th></tr>
  </thead>
  <tbody>
    <tr><th> Bytes </th><td> 15.94 GB </td> <td> 1.01 GB </td></tr>
    <tr><th> Shape </th><td> (950, 2048, 2048) </td> <td> (60, 2048, 2048) </td></tr>
    <tr><th> Count </th><td> 999 Tasks </td><td> 16 Chunks </td></tr>
    <tr><th> Type </th><td> float32 </td><td> cupy.ndarray </td></tr>
  </tbody>
</table>
</td>
<td>
<svg width="212" height="202" style="stroke:rgb(0,0,0);stroke-width:1" >

  <!-- Horizontal lines -->
  <line x1="10" y1="0" x2="42" y2="32" style="stroke-width:2" />
  <line x1="10" y1="120" x2="42" y2="152" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="10" y1="0" x2="10" y2="120" style="stroke-width:2" />
  <line x1="12" y1="2" x2="12" y2="122" />
  <line x1="14" y1="4" x2="14" y2="124" />
  <line x1="16" y1="6" x2="16" y2="126" />
  <line x1="18" y1="8" x2="18" y2="128" />
  <line x1="20" y1="10" x2="20" y2="130" />
  <line x1="22" y1="12" x2="22" y2="132" />
  <line x1="24" y1="14" x2="24" y2="134" />
  <line x1="26" y1="16" x2="26" y2="136" />
  <line x1="28" y1="18" x2="28" y2="138" />
  <line x1="30" y1="20" x2="30" y2="140" />
  <line x1="32" y1="22" x2="32" y2="142" />
  <line x1="34" y1="24" x2="34" y2="144" />
  <line x1="36" y1="26" x2="36" y2="146" />
  <line x1="38" y1="28" x2="38" y2="148" />
  <line x1="41" y1="31" x2="41" y2="151" />
  <line x1="42" y1="32" x2="42" y2="152" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="10.000000,0.000000 42.743566,32.743566 42.743566,152.743566 10.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Horizontal lines -->
  <line x1="10" y1="0" x2="130" y2="0" style="stroke-width:2" />
  <line x1="12" y1="2" x2="132" y2="2" />
  <line x1="14" y1="4" x2="134" y2="4" />
  <line x1="16" y1="6" x2="136" y2="6" />
  <line x1="18" y1="8" x2="138" y2="8" />
  <line x1="20" y1="10" x2="140" y2="10" />
  <line x1="22" y1="12" x2="142" y2="12" />
  <line x1="24" y1="14" x2="144" y2="14" />
  <line x1="26" y1="16" x2="146" y2="16" />
  <line x1="28" y1="18" x2="148" y2="18" />
  <line x1="30" y1="20" x2="150" y2="20" />
  <line x1="32" y1="22" x2="152" y2="22" />
  <line x1="34" y1="24" x2="154" y2="24" />
  <line x1="36" y1="26" x2="156" y2="26" />
  <line x1="38" y1="28" x2="158" y2="28" />
  <line x1="41" y1="31" x2="161" y2="31" />
  <line x1="42" y1="32" x2="162" y2="32" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="10" y1="0" x2="42" y2="32" style="stroke-width:2" />
  <line x1="130" y1="0" x2="162" y2="32" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="10.000000,0.000000 130.000000,0.000000 162.743566,32.743566 42.743566,32.743566" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Horizontal lines -->
  <line x1="42" y1="32" x2="162" y2="32" style="stroke-width:2" />
  <line x1="42" y1="152" x2="162" y2="152" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="42" y1="32" x2="42" y2="152" style="stroke-width:2" />
  <line x1="162" y1="32" x2="162" y2="152" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="42.743566,32.743566 162.743566,32.743566 162.743566,152.743566 42.743566,152.743566" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Text -->
  <text x="102.743566" y="172.743566" font-size="1.0rem" font-weight="100" text-anchor="middle" >2048</text>
  <text x="182.743566" y="92.743566" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,182.743566,92.743566)">2048</text>
  <text x="16.371783" y="156.371783" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(45,16.371783,156.371783)">950</text>
</svg>
</td>
</tr>
</table>


What we now have is a Dask array composed of 16 CuPy blocks of data.  Notice how Dask provides nice typing information in the SVG output.  When we moved from NumPy to CuPy, the block diagram above displays `Type: cupy.ndarray` -- these are especially helpful and remind us we are operating on data which lives on the GPU.

The last piece we need before running the deconvolution is the PSF which should also be loaded onto the GPU:

```python
avg_psf = skimage.io.imread("/public/NVMICROSCOPY/AVG_PSF.tif")
c_avg_psf = cp.asarray(avg_psf)
```

Lastly, we map the `deconvolve` function onto each block in our Dask array:

```
out = da.map_blocks(deconvolve,
                    c_imgs,
                    c_psf,
                    iterations=20,
                    dtype=cp.float32)
```

TIMING INFO

<a href="/images/deconvolve.png">
    <img src="/images/deconvolve.png" width="100%"></a>

IMAGE DESCRIPTION

Napari + Remote GPUs
--------------------

Deconvolution is just one operation and one tool, an image scientist or microscopist will need.  They will need other tools to help as the push to understand
more of the underlying biology.  As a first step though, they will need tools to visualize the data. [Napari](https://napari.org/) is a multi-dimensional image viewer popular in the PyData Bio ecosystem.  As an experiment, we extended the demo above to not only work with Napari, but to also work on remote GPUs provided
by [coiled.io](https://coiled.io/)

By adding another `map_blocks` call to our array, we can move _back_ from GPU to CPU (device to host)

```python
def cupy_to_numpy(x):
    import cupy as cp
    return cp.asnumpy(x)

np_out = out.map_blocks(cupy_to_numpy, meta=out)
```

<a href="/images/napari-deconv.png">
    <img src="/images/napari-deconv.png" width="100%"></a>

When the user moves the slider on the Napari UI, we are instructing dask to the following:
- Load the data from S3 onto the GPU (CuPy)
- Compute the deconvolution
- Move back to the host (NumPy)
- Download the data from EC2 to the local Jupyter instance and the visualize with Napari

This has about 1 second latency which is great for a naive implementation!  We can improve this by adding compression, caching, and other
optimizations within Napari.

It is becoming increasingly more common to operate on hardware not co-located with the scientist/developer/user.  This might be an HPC cluster outfitted with exotic
accelerated computing and networking devices or now common place cloud based infrastructure.

Summary
-------