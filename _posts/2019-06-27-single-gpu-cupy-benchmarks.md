---
layout: post
title: Single-GPU CuPy Benchmarks
author: Peter Andreas Entschev
tags: [GPU, RAPIDS]
draft: true
theme: twitter
---

{% include JB/setup %}

## Summary

Array operations with GPUs can provide considerable speedups over CPU computing,
but the amount of speedup varies greatly depending on the operation. The intent
of this blog post is to benchmark CuPy performance for various different
operations. We can definitely plug Dask in to enable multi-GPU performance gains,
as discussed
[in this post from March](https://blog.dask.org/2019/03/18/dask-nep18), but here
we will only look at individual performance for single-GPU CuPy.

## Hardware and Software Setup

Before going any further, assume the following hardware and software is
utilized for all performance results described in this post:

- System: NVIDIA DGX-1
- CPU: 2x Intel Xeon E5-2698 v4 @ 2.20GHz
- Main memory: 1 TB
- GPU: NVIDIA Tesla V100 32 GB
- Python 3.7.3
- NumPy 1.16.4
- Intel MKL 2019.4.243
- CuPy 6.1.0
- CUDA Toolkit 9.2 (10.1 for SVD, see Increasing Performance section)

## General Performance

We have generated a graph comprising various operations. Most of them perform
well on a GPU using CuPy out of the box. See the graph below:

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

We have recently started working on a
[simple benchmark suite](https://github.com/pentschev/pybench) to help me
benchmark things quickly and reliably, as well as to automate some plotting,
it's still incomplete and lacks documentation, which we intend to improve during
the next days, and it is what was used to generate the plot above. If you're
interested in figuring out exactly how synthetic data was generated and the
exact compute operation benchmarked, you can look at
[this file](https://github.com/pentschev/pybench/blob/master/pybench/benchmarks/benchmark_array.py).
This post won't go into too much details of how this benchmark suite works right
now, but we intend to write something about it in the near future, when it's a
bit more mature and easier to use.

As seen on the graph, we can get 270x speedup for elementwise operations. Not
too bad for not having to write any parallel code by hand. However, the speedup
is immensely affected by nature of each operation. We are not going to get too
deep in why each operation performs differently in this post, but we might
continue that on a future post.

Let me briefly describe each of the operations from the graph above:

- Elementwise: scalar operation on all elements of the array
- Sum: Compute sum of entire array, reducing it to a single scalar, using
  [CUB](https://nvlabs.github.io/cub/), still
  [under development](https://github.com/cupy/cupy/pull/2090)
- Standard deviation: Compute standard deviation of entire array, reducing
  it to a single scalar
- Array Slicing: select every third element of first dimension
- Matrix Multiplication: Multiplication of two square matrices
- FFT: Fast Fourier Transform of matrix
- SVD: Singular Value Decomposition of matrix (tall-and-skinny for larger
  array)
- Stencil (_Not a CuPy operation!_):
  [uniform filtering with Numba](https://blog.dask.org/2019/04/09/numba-stencil)

It's important to note that there are two array sizes, 800 MB and 8 MB, the
first means 10000x10000 arrays and the latter 1000x1000, double-precision
floating-point (8 bytes) in both cases. SVD array size is an exception, where
the large size is actually a tall-and-skinny of size 10000x1000, or 80MB.

## Increasing Performance

When we first ran these benchmarks we actually saw a performance _decrease_ in
a couple of cases.

<div id="vis2"></div>

While it's true that GPUs are not _always_ faster,
we did expect these operations in particular to be faster than their CPU counterparts.
This had us puzzled.

Upon further investigation we found that both of these issues were either
already fixed, or were actively being fixed by others within the ecosystem.

- **SVD**: CuPy's SVD links to the official cuSolver library, which got a
  major speed boost to these kinds of solvers in CUDA 10.1 (thanks to Joe
  Eaton for pointing us to this!) Originally we had CUDA 9.2 installed, when
  things were still quite a bit slower.

  _Note: Most of the results above still use CUDA 9.2._
  _Only the SVD result uses CUDA 10.1._

- **Sum**: CuPy's sum code was genuinely quite slow.
  However, [Akira Naruse](https://github.com/anaruse) already had an
  [active pull request](https://github.com/cupy/cupy/pull/2090)
  to speed this up using
  [CUB](http://nvlabs.github.io/cub/),
  a library of collection primitives for CUDA.

We learned a lot from doing this benchmarking. In particular it was gratifying
to see that the performance issues we saw had already been identified and
corrected by other groups. This highlights one of the many benefits of working
in an open source community: things get faster without you having to do all of
the work.

## Future Work

For better understanding of the scalability, it's interesting to generate
benchmarks for various other sizes. In case this passed unnoticed, there was
no benchmark with Dask, and this is definitely something that needs to be
done as well!

It's also important to have standard benchmarks, the benchmark suite should
be improved, made more general-purpose and be properly documented as well.

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
                0,
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
                    0,
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
                    0,
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
        "speedup": 5.3,
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
        "speedup": 8.3,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Sum",
        "speedup": 66.0,
        "shape0": 10000,
        "shape1": 10000,
        "shape": "10000x10000",
        "size": "800MB"
      },
      {
        "operation": "Standard Deviation",
        "speedup": 1.1,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "Standard Deviation",
        "speedup": 3.5,
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
        "speedup": 3.6,
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
        "speedup": 1.5,
        "shape0": 1000,
        "shape1": 1000,
        "shape": "1000x1000",
        "size": "8MB"
      },
      {
        "operation": "SVD",
        "speedup": 17.0,
        "shape0": 10000,
        "shape1": 1000,
        "shape": "10000x1000",
        "size": "800MB"
      },
      {
        "operation": "Stencil",
        "speedup": 5.1,
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

  var spec2 = {
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
    "name": "data-2"
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
    "data-2": [
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
  vegaEmbed("#vis", spec, embedOpt)
    .catch(error => showError(el, error));
  vegaEmbed("#vis2", spec2, embedOpt)
    .catch(error => showError(el, error));
</script>
