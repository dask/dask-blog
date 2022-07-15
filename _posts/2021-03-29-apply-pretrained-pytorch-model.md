---
layout: post
title: Dask with PyTorch for large scale image analysis
author: Nicholas Sofroniew, Genevieve Buckley
tags: [imaging, deep learning, PyTorch]
theme: twitter
---

{% include JB/setup %}

## Executive Summary

This post explores applying a pre-trained [PyTorch](https://pytorch.org/) model in parallel with Dask Array.

We cover a simple example applying a pre-trained UNet to a stack of images to generate features for every pixel.

## A Worked Example

Let’s start with an example applying a pre-trained [UNet](https://arxiv.org/abs/1505.04597) to a stack of light sheet microscopy data.

In this example, we:

1. Load the image data from Zarr into a multi-chunked Dask array
2. Load a pre-trained PyTorch model that featurizes images
3. Construct a function to apply the model onto each chunk
4. Apply that function across the Dask array with the dask.array.map_blocks function.
5. Store the result back into Zarr format

### Step 1. Load the image data

First, we load the image data into a Dask array.

The example dataset we're using here is lattice lightsheet microscopy of the tail region of a zebrafish embryo. It is described in [this Science paper](http://dx.doi.org/10.1126/science.aaq1392) (see Figure 4), and provided with permission from Srigokul Upadhyayula.

> Liu _et al._ 2018 "Observing the cell in its native state: Imaging subcellular dynamics in multicellular organisms" _Science_, Vol. 360, Issue 6386, eaaq1392 DOI: 10.1126/science.aaq1392 ([link](http://dx.doi.org/10.1126/science.aaq1392))

This is the same data that we analysed in our last [blogpost on Dask and ITK](https://blog.dask.org/2019/08/09/image-itk). You should note the similarities to that workflow even though we are now using new libaries and performing different analyses.

```
cd '/Users/nicholassofroniew/Github/image-demos/data/LLSM'
```

```python
# Load our data
import dask.array as da
imgs = da.from_zarr("AOLLSM_m4_560nm.zarr")
imgs
```

```
dask.array<from-zarr, shape=(20, 199, 768, 1024), dtype=float32, chunksize=(1, 1, 768, 1024)>
```

### Step 2. Load a pre-trained PyTorch model

Next, we load our pre-trained UNet model.

This UNet model takes in an 2D image and returns a 2D x 16 array, where each pixel is now associate with a feature vector of length 16.

We thank Mars Huang for training this particular UNet on a corpous of biological images to produce biologically relevant feature vectors, as part of his work on [interactive bio-image segmentation](https://github.com/transformify-plugins/segmentify). These features can then be used for more downstream image processing tasks such as image segmentation.

```python
# Load our pretrained UNet¶
import torch
from segmentify.model import UNet, layers

def load_unet(path):
    """Load a pretrained UNet model."""

    # load in saved model
    pth = torch.load(path)
    model_args = pth['model_args']
    model_state = pth['model_state']
    model = UNet(**model_args)
    model.load_state_dict(model_state)

    # remove last layer and activation
    model.segment = layers.Identity()
    model.activate = layers.Identity()
    model.eval()

    return model

model = load_unet("HPA_3.pth")
```

### Step 3. Construct a function to apply the model to each chunk

We make a function to apply our pre-trained UNet model to each chunk of the Dask array.

Because Dask arrays are just made out of Numpy arrays which are easily converted to Torch arrays, we're able to leverage the power of machine learning at scale.

```python
# Apply UNet featurization
import numpy as np

def unet_featurize(image, model):
    """Featurize pixels in an image using pretrained UNet model.
    """
    import numpy as np
    import torch

    # Extract the 2D image data from the Dask array
    # Original Dask array dimensions were (time, z-slice, y, x)
    img = image[0, 0, ...]

    # Put the data into a shape PyTorch expects
    # Expected dimensions are (Batch x Channel x Width x Height)
    img = img[None, None, ...]

    # convert image to torch Tensor
    img = torch.Tensor(img).float()

    # pass image through model
    with torch.no_grad():
        features = model(img).numpy()

    # generate feature vectors (w,h,f)
    features = np.transpose(features, (0,2,3,1))[0]

    # Add back the leading length-one dimensions
    result = features[None, None, ...]

    return result

```

Note: Very observant readers might notice that the steps for extracting the 2D image data and then putting it into a shape PyTorch expects appear to be redundant. It is redundant for our particular example, but that might easily not have been the case.

To explain this in more detail, the UNet expects 4D input, with dimensions `(Batch x Channel x Width x Height)`. The original Dask array dimensions were `(time, z-slice, y, x)`. In our example it just so happens those match in a way that makes removing and then adding the leading dimensions redundant, but depending on the shape of the original Dask array this might not have been true.

### Step 4. Apply that function across the Dask array

Now we apply that function to the data in our Dask array using [`dask.array.map_blocks`](https://docs.dask.org/en/latest/array-api.html?highlight=map_blocks#dask.array.map_blocks).

```python
# Apply UNet featurization
out = da.map_blocks(unet_featurize, imgs, model, dtype=np.float32, chunks=(1, 1, imgs.shape[2], imgs.shape[3], 16), new_axis=-1)
out
```

```
dask.array<unet_featurize, shape=(20, 199, 768, 1024, 16), dtype=float32, chunksize=(1, 1, 768, 1024, 16)>
```

### Step 5. Store the result back into Zarr format

Last, we store the result from the UNet model featurization as a zarr array.

```python
# Trigger computation and store
out.to_zarr("AOLLSM_featurized.zarr", overwrite=True)
```

Now we've saved our output, these features can be used for more downstream image processing tasks such as image segmentation.

### Summing up

Here we've shown how to apply a pre-trained PyTorch model to a Dask array of image data.

Because our Dask array chunks are Numpy arrays, they can be easily converted to Torch arrays. This way, we're able to leverage the power of machine learning at scale.

This workflow was very similar to [our example](https://blog.dask.org/2019/08/09/image-itk) using the dask.array.map_blocks function with ITK to perform image deconvolution. This shows you can easily adapt the same type of workflow to achieve many different types of analysis with Dask.
