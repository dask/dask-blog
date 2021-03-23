---
layout: post
title: Dask with PyTorch for large scale image analysis
author: Nicholas Sofroniew, Matthew Rocklin
tags: [imaging]
theme: twitter
---
{% include JB/setup %}

Executive Summary
-----------------

This post explores applying a pre-trained [PyTorch](https://pytorch.org/) model in parallel with Dask Array.

We cover a simple example applying a pre-trained UNet to a stack of images to generate features for every pixel.

A Worked Example
-----------------

Let’s start with an example applying a pre-trained [UNet](https://arxiv.org/abs/1505.04597) to a stack of light sheet microscopy data.

In this example, we:
1. Load data from Zarr into a multi-chunked Dask array
2. Load a pre-trained PyTorch model that featurizes images
3. Construct a function to apply the model onto each chunk
4. Apply that function across the dask array with the dask.array.map_blocks function.
5. Store the result back into Zarr format


This particular UNet takes in an 2D image and returns a 2D x 16 array, where each pixel is now associate with a feature vector of length 16. Thanks to Mars Huang for training this particular UNet on a corpous of biological images to produce biologically relevant feature vectors during his work on [interactive bio-image segmentation](https://github.com/transformify-plugins/segmentify). These features can then be used for more downstream image processing tasks such as image segmentation. We will use the same data that we analysed in our last [blogpost on Dask and ITK](https://blog.dask.org/2019/08/09/image-itk), and you should note the similarities to that workflow even though we are now using new libaries and performing different analyses.


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

```python
# Apply UNet featurization¶
import numpy as np

def unet_featurize(image, model):
    """Featurize pixels in an image using pretrained UNet model.
    """
    import numpy as np
    import torch

    # remove leading two length-one dimensions
    img = image[0, 0, ...]

    # make sure image has four dimentions (b,c,w,h)
    img = np.expand_dims(np.expand_dims(img, 0), 0)
    img = np.transpose(img, (1,0,2,3))

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

out = da.map_blocks(unet_featurize, imgs, model, dtype=np.float32, chunks=(1, 1, imgs.shape[2], imgs.shape[3], 16), new_axis=-1)
out
```

```
dask.array<unet_featurize, shape=(20, 199, 768, 1024, 16), dtype=float32, chunksize=(1, 1, 768, 1024, 16)>
```

```python
# Trigger computation and store
out.to_zarr("AOLLSM_featurized.zarr", overwrite=True)
```

This workflow was very similar to our example using the dask.array.map_blocks function with ITK to perform image deconvolution. Because Dask arrays are just made out of Numpy arrays which are easily converted to Torch arrays, we're now also able to leverage the power of machine learning at scale.
