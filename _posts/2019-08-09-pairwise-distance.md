{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import scipy.spatial.distance as spd\n",
    "import dask.array as da"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "def pairwise_cityblock_cpu(x):\n",
    "    assert x.ndim == 2\n",
    "    out = spd.pdist(x.T, metric='cityblock')\n",
    "    out = out.reshape((1, out.shape[0]))\n",
    "    return out\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "TODO explain what the data mean."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "# simulate some genetic data\n",
    "x = np.random.choice(np.array([0, 1, 2], dtype='i1'), \n",
    "                     p=[.7, .2, .1,], \n",
    "                     size=(20_000, 1_000))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "CPU times: user 8.3 s, sys: 64 ms, total: 8.37 s\n",
      "Wall time: 8.36 s\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "array([[12067., 11977., 11998., ..., 12055., 11977., 12132.]])"
      ]
     },
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "%%time\n",
    "pairwise_cityblock_cpu(x)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<table>\n",
       "<tr>\n",
       "<td>\n",
       "<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr><th> Bytes </th><td> 20.00 MB </td> <td> 2.00 MB </td></tr>\n",
       "    <tr><th> Shape </th><td> (20000, 1000) </td> <td> (2000, 1000) </td></tr>\n",
       "    <tr><th> Count </th><td> 11 Tasks </td><td> 10 Chunks </td></tr>\n",
       "    <tr><th> Type </th><td> int8 </td><td> numpy.ndarray </td></tr>\n",
       "  </tbody></table>\n",
       "</td>\n",
       "<td>\n",
       "<svg width=\"84\" height=\"170\" style=\"stroke:rgb(0,0,0);stroke-width:1\" >\n",
       "\n",
       "  <!-- Horizontal lines -->\n",
       "  <line x1=\"0\" y1=\"0\" x2=\"34\" y2=\"0\" style=\"stroke-width:2\" />\n",
       "  <line x1=\"0\" y1=\"12\" x2=\"34\" y2=\"12\" />\n",
       "  <line x1=\"0\" y1=\"24\" x2=\"34\" y2=\"24\" />\n",
       "  <line x1=\"0\" y1=\"36\" x2=\"34\" y2=\"36\" />\n",
       "  <line x1=\"0\" y1=\"48\" x2=\"34\" y2=\"48\" />\n",
       "  <line x1=\"0\" y1=\"60\" x2=\"34\" y2=\"60\" />\n",
       "  <line x1=\"0\" y1=\"72\" x2=\"34\" y2=\"72\" />\n",
       "  <line x1=\"0\" y1=\"84\" x2=\"34\" y2=\"84\" />\n",
       "  <line x1=\"0\" y1=\"96\" x2=\"34\" y2=\"96\" />\n",
       "  <line x1=\"0\" y1=\"108\" x2=\"34\" y2=\"108\" />\n",
       "  <line x1=\"0\" y1=\"120\" x2=\"34\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "\n",
       "  <!-- Vertical lines -->\n",
       "  <line x1=\"0\" y1=\"0\" x2=\"0\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "  <line x1=\"34\" y1=\"0\" x2=\"34\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "\n",
       "  <!-- Colored Rectangle -->\n",
       "  <polygon points=\"0.000000,0.000000 34.501016,0.000000 34.501016,120.000000 0.000000,120.000000\" style=\"fill:#ECB172A0;stroke-width:0\"/>\n",
       "\n",
       "  <!-- Text -->\n",
       "  <text x=\"17.250508\" y=\"140.000000\" font-size=\"1.0rem\" font-weight=\"100\" text-anchor=\"middle\" >1000</text>\n",
       "  <text x=\"54.501016\" y=\"60.000000\" font-size=\"1.0rem\" font-weight=\"100\" text-anchor=\"middle\" transform=\"rotate(-90,54.501016,60.000000)\">20000</text>\n",
       "</svg>\n",
       "</td>\n",
       "</tr>\n",
       "</table>"
      ],
      "text/plain": [
       "dask.array<array, shape=(20000, 1000), dtype=int8, chunksize=(2000, 1000)>"
      ]
     },
     "execution_count": 5,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x_dask = da.from_array(x, chunks=(2_000, None))\n",
    "x_dask"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "def pairwise_cityblock_dask(x, f):\n",
    "    \n",
    "    # Compute number of blocks.\n",
    "    n_blocks = len(x.chunks[0])\n",
    "\n",
    "    # Compute number of pairs.\n",
    "    n = x.shape[1]\n",
    "    n_pairs = n * (n - 1) // 2\n",
    "    \n",
    "    # Compute distance in blocks.\n",
    "    chunks = ((1,) * n_blocks, (n_pairs,))\n",
    "    d = da.map_blocks(\n",
    "        f, x, chunks=chunks, dtype=np.float64\n",
    "    )\n",
    "\n",
    "    # Sum blocks.\n",
    "    out = da.sum(d, axis=0, dtype=np.float64)\n",
    "\n",
    "    return out\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "CPU times: user 9.06 s, sys: 168 ms, total: 9.22 s\n",
      "Wall time: 1.12 s\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "array([12067., 11977., 11998., ..., 12055., 11977., 12132.])"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "%%time\n",
    "pairwise_cityblock_dask(x_dask, f=pairwise_cityblock_cpu).compute()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Fri Aug  9 07:49:55 2019       \n",
      "+-----------------------------------------------------------------------------+\n",
      "| NVIDIA-SMI 396.44                 Driver Version: 396.44                    |\n",
      "|-------------------------------+----------------------+----------------------+\n",
      "| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |\n",
      "| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |\n",
      "|===============================+======================+======================|\n",
      "|   0  Tesla V100-SXM2...  On   | 00000000:06:00.0 Off |                    0 |\n",
      "| N/A   36C    P0    57W / 300W |   1365MiB / 32510MiB |      0%      Default |\n",
      "+-------------------------------+----------------------+----------------------+\n"
     ]
    }
   ],
   "source": [
    "!nvidia-smi | head"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "from numba import cuda"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "How long to move the data?"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "CPU times: user 8 ms, sys: 0 ns, total: 8 ms\n",
      "Wall time: 56.3 ms\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "<numba.cuda.cudadrv.devicearray.DeviceNDArray at 0x7ff01ec0f940>"
      ]
     },
     "execution_count": 19,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "%%time\n",
    "x_cuda = cuda.to_device(x)\n",
    "x_cuda"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "import math\n",
    "\n",
    "\n",
    "@cuda.jit(device=True)\n",
    "def square_coords_cuda(pair_index, n):\n",
    "    pair_index = np.float32(pair_index)\n",
    "    n = np.float32(n)\n",
    "    j = (((2 * n) - 1) - math.sqrt((1 - (2 * n)) ** 2 - (8 * pair_index))) // 2\n",
    "    k = pair_index - (j * ((2 * n) - j - 1) / 2) + j + 1\n",
    "    j = np.int64(j)\n",
    "    k = np.int64(k)\n",
    "    return j, k\n",
    "\n",
    "\n",
    "@cuda.jit\n",
    "def kernel_cityblock_cuda(x, out):\n",
    "    m = x.shape[0]\n",
    "    n = x.shape[1]\n",
    "    n_pairs = (n * (n - 1)) // 2\n",
    "    pair_index = cuda.grid(1)\n",
    "    if pair_index < n_pairs:\n",
    "        # Unpack the pair index to column indices.\n",
    "        j, k = square_coords_cuda(pair_index, n)\n",
    "        # Iterate over rows, accumulating distance.\n",
    "        d = np.float32(0)\n",
    "        for i in range(m):\n",
    "            u = np.float32(x[i, j])\n",
    "            v = np.float32(x[i, k])\n",
    "            d += math.fabs(u - v)\n",
    "        # Store distance result.\n",
    "        out[pair_index] = d\n",
    "\n",
    "        \n",
    "def pairwise_cityblock_cuda(x):\n",
    "\n",
    "    # Set up output array.\n",
    "    n = x.shape[1]\n",
    "    n_pairs = (n * (n - 1)) // 2\n",
    "    out = cuda.device_array(n_pairs, dtype=np.float32)\n",
    "\n",
    "    # Let numba decide number of threads and blocks.\n",
    "    kernel_spec = kernel_cityblock_cuda.forall(n_pairs)\n",
    "    kernel_spec(x, out)\n",
    "\n",
    "    # Reshape to allow for map blocks.\n",
    "    out = out.reshape((1, out.shape[0]))\n",
    "    \n",
    "    return out\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "# warm-up jit\n",
    "pairwise_cityblock_cuda(x_cuda)\n",
    "cuda.synchronize()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "CPU times: user 12 ms, sys: 8 ms, total: 20 ms\n",
      "Wall time: 24.1 ms\n"
     ]
    }
   ],
   "source": [
    "%%time\n",
    "dist_cuda = pairwise_cityblock_cuda(x_cuda)\n",
    "cuda.synchronize()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "CPU times: user 4 ms, sys: 0 ns, total: 4 ms\n",
      "Wall time: 768 µs\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "array([[12067., 11977., 11998., ..., 12055., 11977., 12132.]],\n",
       "      dtype=float32)"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# how long to copy data back to CPU\n",
    "%time dist_cuda.copy_to_host()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Larger dataset"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<table>\n",
       "<tr>\n",
       "<td>\n",
       "<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr><th> Bytes </th><td> 1000.00 MB </td> <td> 50.00 MB </td></tr>\n",
       "    <tr><th> Shape </th><td> (1000000, 1000) </td> <td> (50000, 1000) </td></tr>\n",
       "    <tr><th> Count </th><td> 22 Tasks </td><td> 20 Chunks </td></tr>\n",
       "    <tr><th> Type </th><td> int8 </td><td> numpy.ndarray </td></tr>\n",
       "  </tbody></table>\n",
       "</td>\n",
       "<td>\n",
       "<svg width=\"75\" height=\"170\" style=\"stroke:rgb(0,0,0);stroke-width:1\" >\n",
       "\n",
       "  <!-- Horizontal lines -->\n",
       "  <line x1=\"0\" y1=\"0\" x2=\"25\" y2=\"0\" style=\"stroke-width:2\" />\n",
       "  <line x1=\"0\" y1=\"6\" x2=\"25\" y2=\"6\" />\n",
       "  <line x1=\"0\" y1=\"12\" x2=\"25\" y2=\"12\" />\n",
       "  <line x1=\"0\" y1=\"18\" x2=\"25\" y2=\"18\" />\n",
       "  <line x1=\"0\" y1=\"24\" x2=\"25\" y2=\"24\" />\n",
       "  <line x1=\"0\" y1=\"30\" x2=\"25\" y2=\"30\" />\n",
       "  <line x1=\"0\" y1=\"36\" x2=\"25\" y2=\"36\" />\n",
       "  <line x1=\"0\" y1=\"42\" x2=\"25\" y2=\"42\" />\n",
       "  <line x1=\"0\" y1=\"48\" x2=\"25\" y2=\"48\" />\n",
       "  <line x1=\"0\" y1=\"54\" x2=\"25\" y2=\"54\" />\n",
       "  <line x1=\"0\" y1=\"60\" x2=\"25\" y2=\"60\" />\n",
       "  <line x1=\"0\" y1=\"66\" x2=\"25\" y2=\"66\" />\n",
       "  <line x1=\"0\" y1=\"72\" x2=\"25\" y2=\"72\" />\n",
       "  <line x1=\"0\" y1=\"78\" x2=\"25\" y2=\"78\" />\n",
       "  <line x1=\"0\" y1=\"84\" x2=\"25\" y2=\"84\" />\n",
       "  <line x1=\"0\" y1=\"90\" x2=\"25\" y2=\"90\" />\n",
       "  <line x1=\"0\" y1=\"96\" x2=\"25\" y2=\"96\" />\n",
       "  <line x1=\"0\" y1=\"102\" x2=\"25\" y2=\"102\" />\n",
       "  <line x1=\"0\" y1=\"108\" x2=\"25\" y2=\"108\" />\n",
       "  <line x1=\"0\" y1=\"114\" x2=\"25\" y2=\"114\" />\n",
       "  <line x1=\"0\" y1=\"120\" x2=\"25\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "\n",
       "  <!-- Vertical lines -->\n",
       "  <line x1=\"0\" y1=\"0\" x2=\"0\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "  <line x1=\"25\" y1=\"0\" x2=\"25\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "\n",
       "  <!-- Colored Rectangle -->\n",
       "  <polygon points=\"0.000000,0.000000 25.412617,0.000000 25.412617,120.000000 0.000000,120.000000\" style=\"fill:#ECB172A0;stroke-width:0\"/>\n",
       "\n",
       "  <!-- Text -->\n",
       "  <text x=\"12.706308\" y=\"140.000000\" font-size=\"1.0rem\" font-weight=\"100\" text-anchor=\"middle\" >1000</text>\n",
       "  <text x=\"45.412617\" y=\"60.000000\" font-size=\"1.0rem\" font-weight=\"100\" text-anchor=\"middle\" transform=\"rotate(-90,45.412617,60.000000)\">1000000</text>\n",
       "</svg>\n",
       "</td>\n",
       "</tr>\n",
       "</table>"
      ],
      "text/plain": [
       "dask.array<da.random.choice, shape=(1000000, 1000), dtype=int8, chunksize=(50000, 1000)>"
      ]
     },
     "execution_count": 20,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x_big = da.random.choice(\n",
    "    np.array([0, 1, 2], dtype='i1'), \n",
    "    p=[.7, .2, .1], \n",
    "    size=(1_000_000, 1_000),\n",
    "    chunks=(50_000, None))\n",
    "x_big"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [],
   "source": [
    "x_big.to_zarr('example.zarr', component='x_big', overwrite=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<table class=\"zarr-info\"><tbody><tr><th style=\"text-align: left\">Name</th><td style=\"text-align: left\">/x_big</td></tr><tr><th style=\"text-align: left\">Type</th><td style=\"text-align: left\">zarr.core.Array</td></tr><tr><th style=\"text-align: left\">Data type</th><td style=\"text-align: left\">int8</td></tr><tr><th style=\"text-align: left\">Shape</th><td style=\"text-align: left\">(1000000, 1000)</td></tr><tr><th style=\"text-align: left\">Chunk shape</th><td style=\"text-align: left\">(50000, 1000)</td></tr><tr><th style=\"text-align: left\">Order</th><td style=\"text-align: left\">C</td></tr><tr><th style=\"text-align: left\">Read-only</th><td style=\"text-align: left\">False</td></tr><tr><th style=\"text-align: left\">Compressor</th><td style=\"text-align: left\">Blosc(cname='lz4', clevel=5, shuffle=SHUFFLE, blocksize=0)</td></tr><tr><th style=\"text-align: left\">Store type</th><td style=\"text-align: left\">zarr.storage.DirectoryStore</td></tr><tr><th style=\"text-align: left\">No. bytes</th><td style=\"text-align: left\">1000000000 (953.7M)</td></tr><tr><th style=\"text-align: left\">No. bytes stored</th><td style=\"text-align: left\">571557863 (545.1M)</td></tr><tr><th style=\"text-align: left\">Storage ratio</th><td style=\"text-align: left\">1.7</td></tr><tr><th style=\"text-align: left\">Chunks initialized</th><td style=\"text-align: left\">20/20</td></tr></tbody></table>"
      ],
      "text/plain": [
       "Name               : /x_big\n",
       "Type               : zarr.core.Array\n",
       "Data type          : int8\n",
       "Shape              : (1000000, 1000)\n",
       "Chunk shape        : (50000, 1000)\n",
       "Order              : C\n",
       "Read-only          : False\n",
       "Compressor         : Blosc(cname='lz4', clevel=5, shuffle=SHUFFLE, blocksize=0)\n",
       "Store type         : zarr.storage.DirectoryStore\n",
       "No. bytes          : 1000000000 (953.7M)\n",
       "No. bytes stored   : 571557863 (545.1M)\n",
       "Storage ratio      : 1.7\n",
       "Chunks initialized : 20/20"
      ]
     },
     "execution_count": 22,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import zarr\n",
    "x_big_zarr = zarr.open('example.zarr')['x_big']\n",
    "x_big_zarr.info"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<table>\n",
       "<tr>\n",
       "<td>\n",
       "<table>  <thead>    <tr><td> </td><th> Array </th><th> Chunk </th></tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr><th> Bytes </th><td> 1000.00 MB </td> <td> 100.00 MB </td></tr>\n",
       "    <tr><th> Shape </th><td> (1000000, 1000) </td> <td> (100000, 1000) </td></tr>\n",
       "    <tr><th> Count </th><td> 11 Tasks </td><td> 10 Chunks </td></tr>\n",
       "    <tr><th> Type </th><td> int8 </td><td> numpy.ndarray </td></tr>\n",
       "  </tbody></table>\n",
       "</td>\n",
       "<td>\n",
       "<svg width=\"75\" height=\"170\" style=\"stroke:rgb(0,0,0);stroke-width:1\" >\n",
       "\n",
       "  <!-- Horizontal lines -->\n",
       "  <line x1=\"0\" y1=\"0\" x2=\"25\" y2=\"0\" style=\"stroke-width:2\" />\n",
       "  <line x1=\"0\" y1=\"12\" x2=\"25\" y2=\"12\" />\n",
       "  <line x1=\"0\" y1=\"24\" x2=\"25\" y2=\"24\" />\n",
       "  <line x1=\"0\" y1=\"36\" x2=\"25\" y2=\"36\" />\n",
       "  <line x1=\"0\" y1=\"48\" x2=\"25\" y2=\"48\" />\n",
       "  <line x1=\"0\" y1=\"60\" x2=\"25\" y2=\"60\" />\n",
       "  <line x1=\"0\" y1=\"72\" x2=\"25\" y2=\"72\" />\n",
       "  <line x1=\"0\" y1=\"84\" x2=\"25\" y2=\"84\" />\n",
       "  <line x1=\"0\" y1=\"96\" x2=\"25\" y2=\"96\" />\n",
       "  <line x1=\"0\" y1=\"108\" x2=\"25\" y2=\"108\" />\n",
       "  <line x1=\"0\" y1=\"120\" x2=\"25\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "\n",
       "  <!-- Vertical lines -->\n",
       "  <line x1=\"0\" y1=\"0\" x2=\"0\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "  <line x1=\"25\" y1=\"0\" x2=\"25\" y2=\"120\" style=\"stroke-width:2\" />\n",
       "\n",
       "  <!-- Colored Rectangle -->\n",
       "  <polygon points=\"0.000000,0.000000 25.412617,0.000000 25.412617,120.000000 0.000000,120.000000\" style=\"fill:#ECB172A0;stroke-width:0\"/>\n",
       "\n",
       "  <!-- Text -->\n",
       "  <text x=\"12.706308\" y=\"140.000000\" font-size=\"1.0rem\" font-weight=\"100\" text-anchor=\"middle\" >1000</text>\n",
       "  <text x=\"45.412617\" y=\"60.000000\" font-size=\"1.0rem\" font-weight=\"100\" text-anchor=\"middle\" transform=\"rotate(-90,45.412617,60.000000)\">1000000</text>\n",
       "</svg>\n",
       "</td>\n",
       "</tr>\n",
       "</table>"
      ],
      "text/plain": [
       "dask.array<array, shape=(1000000, 1000), dtype=int8, chunksize=(100000, 1000)>"
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x_big_dask = da.from_array(x_big_zarr)\n",
    "x_big_dask"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "CPU times: user 9min 17s, sys: 19.3 s, total: 9min 36s\n",
      "Wall time: 1min\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "array([598676., 598649., 599990., ..., 598433., 598728., 600953.])"
      ]
     },
     "execution_count": 24,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "%%time\n",
    "dist_big = pairwise_cityblock_dask(x_big_dask, f=pairwise_cityblock_cpu).compute()\n",
    "dist_big"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "metadata": {},
   "outputs": [],
   "source": [
    "x_big_dask_cuda = x_big_dask.map_blocks(cuda.to_device)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "metadata": {},
   "outputs": [],
   "source": [
    "# launch a local cuda cluster?"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "CPU times: user 1.54 s, sys: 856 ms, total: 2.4 s\n",
      "Wall time: 3.26 s\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "array([598676., 598649., 599990., ..., 598433., 598728., 600953.])"
      ]
     },
     "execution_count": 29,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "%%time\n",
    "dist_big_cuda = pairwise_cityblock_dask(x_big_dask_cuda, f=pairwise_cityblock_cuda).compute(num_workers=1)\n",
    "dist_big_cuda"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "CPU times: user 1.62 s, sys: 860 ms, total: 2.48 s\n",
      "Wall time: 1.61 s\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "array([598676., 598649., 599990., ..., 598433., 598728., 600953.])"
      ]
     },
     "execution_count": 30,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "%%time\n",
    "dist_big_cuda = pairwise_cityblock_dask(x_big_dask_cuda, f=pairwise_cityblock_cuda).compute(num_workers=2)\n",
    "dist_big_cuda"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
