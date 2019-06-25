---
layout: post
title: "Python and GPUs: A Status Update"
author: Matthew Rocklin
tags: [python,scipy]
theme: twitter
---
{% include JB/setup %}

*This blogpost was delivered in talk form at the recent [PASC
2019](https://pasc19.pasc-conference.org/) conference.
[Slides for that talk are
here](https://docs.google.com/presentation/d/e/2PACX-1vSajAH6FzgQH4OwOJD5y-t9mjF9tTKEeljguEsfcjavp18pL4LkpABy4lW2uMykIUvP2dC-1AmhCq6l/pub?start=false&loop=false&delayms=60000).*

Executive Summary
-----------------

We're improving the state of scalable GPU computing in Python.

This post lays out the current status broadly, and describes future work.  It
also summarizes several other more focused blogposts from recent months, and
includes links for the interested reader.

Broadly we cover briefly the following categories:

-  Python libraries written in CUDA like CuPy and RAPIDS
-  Python-CUDA compilers, specifically Numba
-  Scaling these libraries out with Dask
-  Network communication with UCX
-  Packaging with Conda


Performance of GPU accelerated Python Libraries
-----------------------------------------------

Libraries like [CuPy](https://cupy.chainer.org/) and
[RAPIDS](https://rapids.ai/) build GPU accelerated variants of popular Python
libraries like NumPy, Pandas, and Scikit-Learn.  In order to better understand
the relative performance differences
[Peter Entschev](https://github.com/pentschev) recently put together a
[benchmark suite](https://github.com/pentschev/pybench) to help with comparisons.
He has produced the following image showing the relative speedup between GPU
and CPU:

<style>
.vega-actions a {
    margin-right: 12px;
    color: #757575;
    font-weight: normal;
    font-size: 13px;
}
.error {
    color: red;
}
</style>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega@5"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-lite@3.3.0"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-embed@4"></script>

<div id="vis"></div>
<script>
  var spec = {
  "config": {
    "view": {
      "width": 300,
      "height": 200
    },
    "mark": {
      "tooltip": null
    },
    "axis": {
      "grid": false,
      "labelColor": "#666666",
      "labelFontSize": 16,
      "titleColor": "#666666",
      "titleFontSize": 20
    },
    "axisX": {
      "labelAngle": -30,
      "labelColor": "#666666",
      "labelFontSize": 0,
      "titleColor": "#666666",
      "titleFontSize": 0
    },
    "header": {
      "labelAngle": -20,
      "labelColor": "#666666",
      "labelFontSize": 16,
      "titleColor": "#666666",
      "titleFontSize": 20
    },
    "legend": {
      "fillColor": "#fefefe",
      "labelColor": "#666666",
      "labelFontSize": 18,
      "padding": 10,
      "strokeColor": "gray",
      "titleColor": "#666666",
      "titleFontSize": 18
    }
  },
  "data": {
    "name": "data-4957f64f65957150f8029f7df2e6936f"
  },
  "facet": {
    "column": {
      "type": "nominal",
      "field": "operation",
      "sort": {
        "field": "speedup",
        "op": "sum",
        "order": "descending"
      },
      "title": "Operation"
    }
  },
  "spec": {
    "layer": [
      {
        "mark": {
          "type": "bar",
          "fontSize": 18,
          "opacity": 1.0
        },
        "encoding": {
          "color": {
            "type": "nominal",
            "field": "size",
            "scale": {
              "domain": [
                "800MB",
                "8MB"
              ],
              "range": [
                "#7306ff",
                "#36c9dd"
              ]
            },
            "title": "Array Size"
          },
          "x": {
            "type": "nominal",
            "field": "size"
          },
          "y": {
            "type": "quantitative",
            "axis": {
              "title": "GPU Speedup Over CPU"
            },
            "field": "speedup",
            "scale": {
              "domain": [
                -100,
                1000
              ],
              "type": "symlog"
            },
            "stack": null
          }
        },
        "height": 300,
        "width": 50
      },
      {
        "layer": [
          {
            "mark": {
              "type": "text",
              "dy": -5
            },
            "encoding": {
              "color": {
                "type": "nominal",
                "field": "size",
                "scale": {
                  "domain": [
                    "800MB",
                    "8MB"
                  ],
                  "range": [
                    "#7306ff",
                    "#36c9dd"
                  ]
                },
                "title": "Array Size"
              },
              "text": {
                "type": "quantitative",
                "field": "speedup"
              },
              "x": {
                "type": "nominal",
                "field": "size"
              },
              "y": {
                "type": "quantitative",
                "axis": {
                  "title": "GPU Speedup Over CPU"
                },
                "field": "speedup",
                "scale": {
                  "domain": [
                    -100,
                    1000
                  ],
                  "type": "symlog"
                },
                "stack": null
              }
            },
            "height": 300,
            "width": 50
          },
          {
            "mark": {
              "type": "text",
              "dy": 7
            },
            "encoding": {
              "color": {
                "type": "nominal",
                "field": "size",
                "scale": {
                  "domain": [
                    "800MB",
                    "8MB"
                  ],
                  "range": [
                    "#7306ff",
                    "#36c9dd"
                  ]
                },
                "title": "Array Size"
              },
              "text": {
                "type": "quantitative",
                "field": "speedup"
              },
              "x": {
                "type": "nominal",
                "field": "size"
              },
              "y": {
                "type": "quantitative",
                "axis": {
                  "title": "GPU Speedup Over CPU"
                },
                "field": "speedup",
                "scale": {
                  "domain": [
                    -100,
                    1000
                  ],

                  "type": "symlog"
                },
                "stack": null
              }
            },
            "height": 300,
            "width": 50
          }
        ]
      }
    ]
  },
  "$schema": "https://vega.github.io/schema/vega-lite/v3.3.0.json",
  "datasets": {
    "data-4957f64f65957150f8029f7df2e6936f": [
      {
        "operation": "FFT",
        "speedup": 5.0,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "FFT",
        "speedup": 210.0,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "Sum",
        "speedup": -2.3,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Sum",
        "speedup": -1.3,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "Sum",
        "speedup": -2.3,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Sum",
        "speedup": -1.3,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "Sum With CUB",
        "speedup": 8.0,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Sum With CUB",
        "speedup": 66.0,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "Standard Deviation",
        "speedup": 1.0,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Standard Deviation",
        "speedup": 4.0,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "Elementwise",
        "speedup": 150.0,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Elementwise",
        "speedup": 270.0,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "Matrix Multiplication",
        "speedup": 18.0,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Matrix Multiplication",
        "speedup": 11.0,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "Array Slicing",
        "speedup": 4.0,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Array Slicing",
        "speedup": 190.0,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "SVD",
        "speedup": -3.6,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "SVD",
        "speedup": -1.8,
        "shape0": 10000,
        "shape1": 1000,
        "shape": "10000x1000",
        "size": "800MB"
      },
      {
        "operation": "Stencil",
        "speedup": 5.0,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Stencil",
        "speedup": 150.0,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      }
    ]
  }
};
  var embedOpt = {"mode": "vega-lite"};

  function showError(el, error){
      el.innerHTML = ('<div class="error" style="color:red;">'
                      + '<p>JavaScript Error: ' + error.message + '</p>'
                      + "<p>This usually means there's a typo in your chart specification. "
                      + "See the javascript console for the full traceback.</p>"
                      + '</div>');
      throw error;
  }
  const el = document.getElementById('vis');
  vegaEmbed("#vis", spec, embedOpt)
    .catch(error => showError(el, error));

</script>

This is all quite early stage (the numbers above are likely to shift as we
learn more) but it's been valuable for us to develop an intuition about
what will and won't be faster to be quite valuable in navigating this space.
This has been effective as we've explored using Python-accessible GPU libraries
in real-world data science workloads.


Numba: Compiling Python to CUDA
-------------------------------

*See also this [recent blogpost about Numba
stencils](https://blog.dask.org/2019/04/09/numba-stencil) and the attached [GPU
notebook](https://gist.github.com/mrocklin/9272bf84a8faffdbbe2cd44b4bc4ce3c)*

The built-in operations in GPU libraries like CuPy or RAPIDS are great, and
cover the most common operations.  However, in real-world settings we often run
across messy situations that require writing a little bit of custom code.  With
CPUs we tend to use tools like Cython or Numba, which let Python programmers
write fast numeric code without learning too much beyond the Python language.

For example, Numba accelerates the for-loop style code below about 500x,
from slow Python speeds up to fast C/Fortran speeds.

```python
import numba  # We added these two lines for a 500x speedup

@numba.jit    # We added these two lines for a 500x speedup
def sum(x):
    total = 0
    for i in range(x.shape[0]):
        total += x[i]
    return total
```

The ability to drop down to low-level performant code without context switching
out of Python is useful, particularly if you don't already know C/C++ or
have a compiler chain set up for you (which is the case for most Python users
today).

This benefit is even more pronounced on the GPU.  While many Python programmers
know a little bit of C, very few of them know CUDA.  Even if they did, they
would probably have difficulty in setting up the compiler tools and development
environment.

Enter [numba.cuda.jit](https://numba.pydata.org/numba-doc/dev/cuda/index.html)
Numba's backend for CUDA, which allows Python users to author, compile, and run
CUDA code, written in Python, interactively without leaving a Python session.
Here is an image of writing a stencil computation that smoothes a 2d-image all
from within a Jupyter Notebook:

<img src="images/numba.cuda.jit.png"
     width="60%"
     alt="Numba.cuda.jit in a Jupyter Notebook">

Here is a simplified comparison of Numba CPU/GPU code to compare programming
style..
The GPU code gets a 200x speed improvement over a single CPU core.

### CPU -- 600 ms

```python
@numba.jit
def _smooth(x):
    out = np.empty_like(x)
    for i in range(1, x.shape[0] - 1):
        for j in range(1, x.shape[1] - 1):
            out[i, j] = x[i + -1, j + -1] + x[i + -1, j + 0] + x[i + -1, j + 1] +
                        x[i +  0, j + -1] + x[i +  0, j + 0] + x[i +  0, j + 1] +
                        x[i +  1, j + -1] + x[i +  1, j + 0] + x[i +  1, j + 1]) // 9

    return out
```

or if we use the fancy numba.stencil decorator ...

```python
@numba.stencil
def _smooth(x):
    return (x[-1, -1] + x[-1, 0] + x[-1, 1] +
            x[ 0, -1] + x[ 0, 0] + x[ 0, 1] +
            x[ 1, -1] + x[ 1, 0] + x[ 1, 1]) // 9
```

### GPU -- 3 ms

```python
@numba.cuda.jit
def smooth_gpu(x, out):
    i, j = cuda.grid(2)
    n, m = x.shape
    if 1 <= i < n - 1 and 1 <= j < m - 1:
        out[i, j] = (x[i - 1, j - 1] + x[i - 1, j] + x[i - 1, j + 1] +
                     x[i    , j - 1] + x[i    , j] + x[i    , j + 1] +
                     x[i + 1, j - 1] + x[i + 1, j] + x[i + 1, j + 1]) // 9
```



Numba.cuda.jit has been out in the wild for quite a while now.  It's
accessible, mature, and fun to play with.  If you have a machine with a GPU in
it and some curiosity then we strongly recommend that you try it out.

```
conda install numba
# or
pip install numba
```

```python
>>> import numba.cuda
```


Scaling with Dask
-----------------

As mentioned in previous blogposts
(
[1](https://blog.dask.org/2019/01/03/dask-array-gpus-first-steps),
[2](https://blog.dask.org/2019/01/13/dask-cudf-first-steps),
[3](https://blog.dask.org/2019/03/04/building-gpu-groupbys),
[4](https://blog.dask.org/2019/03/18/dask-nep18)
)
we've been generalizing [Dask](https://dask.org), to operate not just with
Numpy arrays and Pandas dataframes, but with anything that looks enough like
Numpy (like [CuPy](https://cupy.chainer.org/) or
[Sparse](https://sparse.pydata.org/en/latest/) or
[Jax](https://github.com/google/jax)) or enough like Pandas (like [RAPIDS
cuDF](https://docs.rapids.ai/api/cudf/nightly/))
to scale those libraries out too.  This is working out well.  Here is a brief
video showing Dask array computing an SVD in parallel, and seeing what happens
when we swap out the Numpy library for CuPy.

<iframe width="560"
        height="315"
        src="https://www.youtube.com/embed/QyyxpzNPuIE?start=1046"
        frameborder="0"
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen></iframe>

We see that there is about a 10x speed improvement on the computation.  Most
importantly, we were able to switch between a CPU implementation and a GPU
implementation with a small one-line change, but continue using the
sophisticated algorithms with Dask Array, like it's parallel SVD
implementation.

We also saw a relative slowdown in communication.  In general almost all
non-trivial Dask + GPU work today is becoming communication-bound.  We've
gotten fast enough at computation that the relative importance of communication
has grown significantly.


Communication with UCX
----------------------

*See [this talk](https://developer.download.nvidia.com/video/gputechconf/gtc/2019/video/S9679/s9679-ucx-python-a-flexible-communication-library-for-python-applications.mp4) by [Akshay
Venkatesh](https://github.com/Akshay-Venkatesh) or view [the
slides](https://www.slideshare.net/MatthewRocklin/ucxpython-a-flexible-communication-library-for-python-applications)*

*Also see [this recent blogpost about UCX and
Dask](https://blog.dask.org/2019/06/09/ucx-dgx)*

We've been integrating the [OpenUCX](https://openucx.org) library into Python
with [UCX-Py](https://github.com/rapidsai/ucx-py).  UCX provides uniform access
to transports like TCP, InfiniBand, shared memory, and NVLink.  UCX-Py is the
first time that access to many of these transports has been easily accessible
from the Python language.

Using UCX and Dask together we're able to get significant speedups.  Here is a
trace of the SVD computation from before both before and after adding UCX:

**Before UCX**:

<iframe src="https://matthewrocklin.com/raw-host/task_stream_lcc_dgx16.html" width="100%" height="200"></iframe>

**After UCX**:

<iframe src="https://matthewrocklin.com/raw-host/task_stream_dgx_dgx16.html" width="100%" height="200"></iframe>

There is still a great deal to do here though (the blogpost linked above has
several items in the Future Work section).

People can try out UCX and UCX-Py with highly experimental conda packages:

```
conda create -n ucx -c conda-forge -c jakirkham/label/ucx cudatoolkit=9.2 ucx-proc=*=gpu ucx ucx-py python=3.7
```

We hope that this work will also affect non-GPU users on HPC systems with
Infiniband, or even users on consumer hardware due to the easy access to shared
memory communication.


Packaging
---------

In an [earlier
blogpost](https://matthewrocklin.com/blog/work/2018/12/17/gpu-python-challenges)
we discussed the challenges around installing the wrong versions of CUDA
enabled packages that don't match the CUDA driver installed on the system.
Fortunately due to recent work from [Stan Seibert](https://github.com/seibert)
and [Michael Sarahan](https://github.com/msarahan) at Anaconda, Conda 4.7 now
has a special `cuda` meta-package that is set to the version of the installed
driver.  This should make it much easier for users in the future to install the
correct package.

Conda 4.7 isn't out yet, but you can install it from the [Conda Canary
Channel](https://www.anaconda.com/what-conda-canary/)

```
conda config --add channels conda-canary
conda update conda
```

There is still plenty of work to do in the packaging space today.
Everyone who builds conda packages does it their own way, resulting in headache
and heterogeneity.  This is largely due to not having centralized
infrastructure to build and test CUDA enabled packages, like we have in [Conda
Forge](https://conda-forge.org).  There have been early conversations between
NVIDIA and Anaconda and the Conda-Forge community about setting up this
infrastructure, but this is still quite early.
