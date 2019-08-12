In large scale genomics analysis, scientists try to reduce sequencing data from
multiple individuals into groups that share common traits. This requires
measuring how sequences differ from each other. A common way to do this is to
use a distance metric like [city block](
https://en.wikipedia.org/wiki/Taxicab_geometry ) or others. As this metric ends
up being computed pairwise over all of the samples, this can be a real
bottleneck. Thus it is pairmount to have a performant distance computation
implementation to really leverage the hardware.


TODO Might be nice to have a picture or graph of what some data looks like

TODO explain what the data mean.

So a representative dataset, might look something like this.

```python
# simulate some genetic data
x = np.random.choice(np.array([0, 1, 2], dtype='i1'),
                     p=[.7, .2, .1,],
                     size=(20_000, 1_000))
```

To start out, one might leverage a distance implementation from the highly
optimized SciPy library. This is quick and can be dropped with relatively
little effort as long as one's data fits what the function expects. So one
might end up with an implementation like this.

```python
import numpy as np
import scipy.spatial.distance as spd

def pairwise_cityblock_cpu(x):
    out = spd.pdist(x.T, metric='cityblock')
    out = out.reshape((1, out.shape[0]))
    return out
```

We can then try to run this on our representative dataset. This does reasonably
well and we haven't had to think to hard about the implementation. In some
cases, this may already be sufficient.

However we may find that while the performance is reasonable, we have a lot of
samples to process. We could speed things up a bit by running through small
batches of data in parallel. An easy way to get started on this work would be
to make a Dask Array that handles operating on our data.

```python
import dask.array as da

x_dask = da.from_array(x, chunks=(2_000, None))
x_dask
```

<table>
<tr>
<td>
<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>
  </thead>
  <tbody>
    <tr><th> Bytes </th><td> 20.00 MB </td> <td> 2.00 MB </td></tr>
    <tr><th> Shape </th><td> (20000, 1000) </td> <td> (2000, 1000) </td></tr>
    <tr><th> Count </th><td> 11 Tasks </td><td> 10 Chunks </td></tr>
    <tr><th> Type </th><td> int8 </td><td> numpy.ndarray </td></tr>
  </tbody></table>
</td>
<td>
<svg width="84" height="170" style="stroke:rgb(0,0,0);stroke-width:1" >

  <!-- Horizontal lines -->
  <line x1="0" y1="0" x2="34" y2="0" style="stroke-width:2" />
  <line x1="0" y1="12" x2="34" y2="12" />
  <line x1="0" y1="24" x2="34" y2="24" />
  <line x1="0" y1="36" x2="34" y2="36" />
  <line x1="0" y1="48" x2="34" y2="48" />
  <line x1="0" y1="60" x2="34" y2="60" />
  <line x1="0" y1="72" x2="34" y2="72" />
  <line x1="0" y1="84" x2="34" y2="84" />
  <line x1="0" y1="96" x2="34" y2="96" />
  <line x1="0" y1="108" x2="34" y2="108" />
  <line x1="0" y1="120" x2="34" y2="120" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="0" y1="0" x2="0" y2="120" style="stroke-width:2" />
  <line x1="34" y1="0" x2="34" y2="120" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="0.000000,0.000000 34.501016,0.000000 34.501016,120.000000 0.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Text -->
  <text x="17.250508" y="140.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" >1000</text>
  <text x="54.501016" y="60.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,54.501016,60.000000)">20000</text>
</svg>
</td>
</tr>
</table>


With our Dask Array in hand, we can write a simple function to facilitate
applying our distance function on the data. By doing a little bit of work to
keep things general, we can easily swap in different distance functions based
on the computation we need to do or leverage more performant implementations
that may exist for our data.


```python
def pairwise_cityblock_dask(x, f):
    
    # Compute number of blocks.
    n_blocks = len(x.chunks[0])

    # Compute number of pairs.
    n = x.shape[1]
    n_pairs = n * (n - 1) // 2
    
    # Compute distance in blocks.
    chunks = ((1,) * n_blocks, (n_pairs,))
    d = da.map_blocks(
        f, x, chunks=chunks, dtype=np.float64
    )

    # Sum blocks.
    out = da.sum(d, axis=0, dtype=np.float64)

    return out

```

Now we can write something like this.

```python
pairwise_cityblock_dask(x_dask, f=pairwise_cityblock_cpu).compute()
```

With this, we are able to get more of a speedup. We did a little bit of work,
but not so much. Also we have managed to leverage the distance function from
our serial case without issues.

What if we still want more performance than even this offers? Well if we have a
GPU in our computer or a cluster of them, we could leverage that compute
resource for our problem.

First we need to move our data to the GPU. There are several ways we could do
this. Though one reasonably approachable way is to use Numba. We could write
the following to handle our in-memory case.

```python
x_cuda = cuda.to_device(x)
```

We can also handle the Dask case pretty easily by simply writing this.

```python
x_dask_cuda = da.map_blocks(cuda.to_device, x)
```

This may take a moment as data moves from the CPU to the GPU.

At a first pass, we might write something Numba's CUDA JIT. Here we might need
to tune how many threads we use per block.


TODO Add this code


Alternatively we could be a bit clever and write this code using `forall`. This is pretty handy as we now no longer need to think about CUDA threads per block. There is a caveat though; we need to collapse our `for`-loops into 1 loop. One can do this with a bit of ingenuity.

```python
import math


@cuda.jit(device=True)
def square_coords_cuda(pair_index, n):
    pair_index = np.float32(pair_index)
    n = np.float32(n)
    j = (((2 * n) - 1) - math.sqrt((1 - (2 * n)) ** 2 - (8 * pair_index))) // 2
    k = pair_index - (j * ((2 * n) - j - 1) / 2) + j + 1
    j = np.int64(j)
    k = np.int64(k)
    return j, k


@cuda.jit
def kernel_cityblock_cuda(x, out):
    m = x.shape[0]
    n = x.shape[1]
    n_pairs = (n * (n - 1)) // 2
    pair_index = cuda.grid(1)
    if pair_index < n_pairs:
        # Unpack the pair index to column indices.
        j, k = square_coords_cuda(pair_index, n)
        # Iterate over rows, accumulating distance.
        d = np.float32(0)
        for i in range(m):
            u = np.float32(x[i, j])
            v = np.float32(x[i, k])
            d += math.fabs(u - v)
        # Store distance result.
        out[pair_index] = d

        
def pairwise_cityblock_cuda(x):

    # Set up output array.
    n = x.shape[1]
    n_pairs = (n * (n - 1)) // 2
    out = cuda.device_array(n_pairs, dtype=np.float32)

    # Let numba decide number of threads and blocks.
    kernel_spec = kernel_cityblock_cuda.forall(n_pairs)
    kernel_spec(x, out)

    # Reshape to allow for map blocks.
    out = out.reshape((1, out.shape[0]))
    
    return out
```

As with any JIT, we benefit by doing a warmup run first. Though that's easy
enough to do. Then we are ready to compute our result.

```python
dist_cuda = pairwise_cityblock_cuda(x_cuda)
cuda.synchronize()
```

If work needs to be done on the CPU afterwards, we can copy it back like so.

```python
dist_cuda.copy_to_host()
```


## Larger dataset


```python
x_big = da.random.choice(
    np.array([0, 1, 2], dtype='i1'), 
    p=[.7, .2, .1], 
    size=(1_000_000, 1_000),
    chunks=(50_000, None))
x_big
```




<table>
<tr>
<td>
<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>
  </thead>
  <tbody>
    <tr><th> Bytes </th><td> 1000.00 MB </td> <td> 50.00 MB </td></tr>
    <tr><th> Shape </th><td> (1000000, 1000) </td> <td> (50000, 1000) </td></tr>
    <tr><th> Count </th><td> 22 Tasks </td><td> 20 Chunks </td></tr>
    <tr><th> Type </th><td> int8 </td><td> numpy.ndarray </td></tr>
  </tbody></table>
</td>
<td>
<svg width="75" height="170" style="stroke:rgb(0,0,0);stroke-width:1" >

  <!-- Horizontal lines -->
  <line x1="0" y1="0" x2="25" y2="0" style="stroke-width:2" />
  <line x1="0" y1="6" x2="25" y2="6" />
  <line x1="0" y1="12" x2="25" y2="12" />
  <line x1="0" y1="18" x2="25" y2="18" />
  <line x1="0" y1="24" x2="25" y2="24" />
  <line x1="0" y1="30" x2="25" y2="30" />
  <line x1="0" y1="36" x2="25" y2="36" />
  <line x1="0" y1="42" x2="25" y2="42" />
  <line x1="0" y1="48" x2="25" y2="48" />
  <line x1="0" y1="54" x2="25" y2="54" />
  <line x1="0" y1="60" x2="25" y2="60" />
  <line x1="0" y1="66" x2="25" y2="66" />
  <line x1="0" y1="72" x2="25" y2="72" />
  <line x1="0" y1="78" x2="25" y2="78" />
  <line x1="0" y1="84" x2="25" y2="84" />
  <line x1="0" y1="90" x2="25" y2="90" />
  <line x1="0" y1="96" x2="25" y2="96" />
  <line x1="0" y1="102" x2="25" y2="102" />
  <line x1="0" y1="108" x2="25" y2="108" />
  <line x1="0" y1="114" x2="25" y2="114" />
  <line x1="0" y1="120" x2="25" y2="120" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="0" y1="0" x2="0" y2="120" style="stroke-width:2" />
  <line x1="25" y1="0" x2="25" y2="120" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="0.000000,0.000000 25.412617,0.000000 25.412617,120.000000 0.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Text -->
  <text x="12.706308" y="140.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" >1000</text>
  <text x="45.412617" y="60.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,45.412617,60.000000)">1000000</text>
</svg>
</td>
</tr>
</table>




```python
x_big.to_zarr('example.zarr', component='x_big', overwrite=True)
```


```python
import zarr
x_big_zarr = zarr.open('example.zarr')['x_big']
x_big_zarr.info
```




<table class="zarr-info"><tbody><tr><th style="text-align: left">Name</th><td style="text-align: left">/x_big</td></tr><tr><th style="text-align: left">Type</th><td style="text-align: left">zarr.core.Array</td></tr><tr><th style="text-align: left">Data type</th><td style="text-align: left">int8</td></tr><tr><th style="text-align: left">Shape</th><td style="text-align: left">(1000000, 1000)</td></tr><tr><th style="text-align: left">Chunk shape</th><td style="text-align: left">(50000, 1000)</td></tr><tr><th style="text-align: left">Order</th><td style="text-align: left">C</td></tr><tr><th style="text-align: left">Read-only</th><td style="text-align: left">False</td></tr><tr><th style="text-align: left">Compressor</th><td style="text-align: left">Blosc(cname='lz4', clevel=5, shuffle=SHUFFLE, blocksize=0)</td></tr><tr><th style="text-align: left">Store type</th><td style="text-align: left">zarr.storage.DirectoryStore</td></tr><tr><th style="text-align: left">No. bytes</th><td style="text-align: left">1000000000 (953.7M)</td></tr><tr><th style="text-align: left">No. bytes stored</th><td style="text-align: left">571557863 (545.1M)</td></tr><tr><th style="text-align: left">Storage ratio</th><td style="text-align: left">1.7</td></tr><tr><th style="text-align: left">Chunks initialized</th><td style="text-align: left">20/20</td></tr></tbody></table>




```python
x_big_dask = da.from_array(x_big_zarr)
x_big_dask
```




<table>
<tr>
<td>
<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>
  </thead>
  <tbody>
    <tr><th> Bytes </th><td> 1000.00 MB </td> <td> 100.00 MB </td></tr>
    <tr><th> Shape </th><td> (1000000, 1000) </td> <td> (100000, 1000) </td></tr>
    <tr><th> Count </th><td> 11 Tasks </td><td> 10 Chunks </td></tr>
    <tr><th> Type </th><td> int8 </td><td> numpy.ndarray </td></tr>
  </tbody></table>
</td>
<td>
<svg width="75" height="170" style="stroke:rgb(0,0,0);stroke-width:1" >

  <!-- Horizontal lines -->
  <line x1="0" y1="0" x2="25" y2="0" style="stroke-width:2" />
  <line x1="0" y1="12" x2="25" y2="12" />
  <line x1="0" y1="24" x2="25" y2="24" />
  <line x1="0" y1="36" x2="25" y2="36" />
  <line x1="0" y1="48" x2="25" y2="48" />
  <line x1="0" y1="60" x2="25" y2="60" />
  <line x1="0" y1="72" x2="25" y2="72" />
  <line x1="0" y1="84" x2="25" y2="84" />
  <line x1="0" y1="96" x2="25" y2="96" />
  <line x1="0" y1="108" x2="25" y2="108" />
  <line x1="0" y1="120" x2="25" y2="120" style="stroke-width:2" />

  <!-- Vertical lines -->
  <line x1="0" y1="0" x2="0" y2="120" style="stroke-width:2" />
  <line x1="25" y1="0" x2="25" y2="120" style="stroke-width:2" />

  <!-- Colored Rectangle -->
  <polygon points="0.000000,0.000000 25.412617,0.000000 25.412617,120.000000 0.000000,120.000000" style="fill:#ECB172A0;stroke-width:0"/>

  <!-- Text -->
  <text x="12.706308" y="140.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" >1000</text>
  <text x="45.412617" y="60.000000" font-size="1.0rem" font-weight="100" text-anchor="middle" transform="rotate(-90,45.412617,60.000000)">1000000</text>
</svg>
</td>
</tr>
</table>




```python
%%time
dist_big = pairwise_cityblock_dask(x_big_dask, f=pairwise_cityblock_cpu).compute()
dist_big
```

    CPU times: user 9min 17s, sys: 19.3 s, total: 9min 36s
    Wall time: 1min





    array([598676., 598649., 599990., ..., 598433., 598728., 600953.])




```python
x_big_dask_cuda = x_big_dask.map_blocks(cuda.to_device)
```


```python
# launch a local cuda cluster?
```


```python
%%time
dist_big_cuda = pairwise_cityblock_dask(x_big_dask_cuda, f=pairwise_cityblock_cuda).compute(num_workers=1)
dist_big_cuda
```

    CPU times: user 1.54 s, sys: 856 ms, total: 2.4 s
    Wall time: 3.26 s





    array([598676., 598649., 599990., ..., 598433., 598728., 600953.])




```python
%%time
dist_big_cuda = pairwise_cityblock_dask(x_big_dask_cuda, f=pairwise_cityblock_cuda).compute(num_workers=2)
dist_big_cuda
```

    CPU times: user 1.62 s, sys: 860 ms, total: 2.48 s
    Wall time: 1.61 s





    array([598676., 598649., 599990., ..., 598433., 598728., 600953.])




```python

```
