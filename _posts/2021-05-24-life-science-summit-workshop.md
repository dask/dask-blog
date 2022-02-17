---
layout: post
title: Life sciences at the 2021 Dask Summit
author: Genevieve Buckley
tags: [Dask Summit, life science]
theme: twitter
---

{% include JB/setup %}

## Executive Summary

The Dask life science workshop ran as part of the 2021 Dask Summit. Lightning talks from this workshop are [available here](https://www.youtube.com/playlist?list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0), and you can read on for a summary of the event.

## What is the Dask life science workshop?

The Dask life science workshop ran as part of the 2021 Dask Summit. Currently many people in life sciences use Dask, but individual groups are relatively isolated from one another. This workshop gave us an opportunity to learn from each other, as well as opportunities to identify common frustrations and areas for improvement.

The workshop involved:

- Pre-recorded lightning talks
- Interactive discussion times (accessible across timezones in Europe, Oceania, and the Americas)
- Asynchronous text chat throughout the Dask Summit

## If I missed it, how can I catch up?

If you missed the Dask Summit, you can catch up on YouTube.
There is a playlist of all the life science lightning talks [available here](https://www.youtube.com/playlist?list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0).

You can also join our `#life-science` channel on Slack:
[Click here for an invitation link](https://join.slack.com/t/dask/shared_invite/zt-mfmh7quc-nIrXL6ocgiUH2haLYA914g).

## Who came?

We invited attendees at the life science workshop to do a short Q&A about their work with Dask. This is a small subset of the people who joined us, many people came to the conference and did not do a Q&A.

The responses give us an overview of the diversity of work people in the community are doing. In no particular order, here are some of those Q&As:

**Name:** Tom White\
**Timezone:** EU/UK\
**What kind of science do you work on?** Statistical genetics\
**Something you've tried (or would like to try) with Dask?** Run per-row linear regressions at scale.\
**What do you want to do next with Dask?** Collaborative optimization of a public workflow (GWAS).\
**Lightning talk:** [click here](https://www.youtube.com/watch?v=qt6YsHoPpZs&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=2)

**Name:** Giovanni Palla\
**Affiliation:** Helmholtz Center Munich\
**Timezone:** Europe\
**What kind of science do you work on?** Computational Biology and Spatial transcriptomics\
**Something you've tried (or would like to try) with Dask?** [dask-image](http://image.dask.org/en/latest/) for image processing.\
**What do you want to do next with Dask? Further integration with [Squidpy](https://squidpy.readthedocs.io/en/latest/).\
**Lightning talk:\*\* [click here](https://www.youtube.com/watch?v=sGr7O8spfvE&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=8)

**Name:** Isaac Virshup\
**Affiliation:** University of Melbourne. Open source projects Scanpy and AnnData
**Timezone:** AEST\
**What kind of science do you work on?** Single cell omics data.\
**Something you've tried (or would like to try) with Dask?**\
I've used dask for some nested embarrassingly parallel calculations. Having an intelligent scheduler with good monitoring made this task as easy as it should be, especially compared with multiprocessing or joblib.\
**What do you want to do next with Dask?**\
I would love to get AnnData, a container for working with single cell assays integrated with dask. Dataset sizes in this field are constantly increasing, and it would be good to be able to work with the coolest new dataset regardless of available RAM.\
Since we rely heavily on sparse arrays, a key step towards this will be getting better sparse array support (CSC and CSR especially) inside dask. After all, it's not great if our strategy for scaling out requires many times the total memory! As a maintainer, I'm interested in hearing people's experience with distributing tools that integrate well with dask.\
**Lightning talk:** [click here](https://www.youtube.com/watch?v=e8pWpRo5Ars&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=14)

**Name:** Anna Kreshuk\
**Affiliation:** European Molecular Biology Laboratory\
**Timezone:** CEST (GMT+2)\
**What kind of science do you work on?** Machine learning for microscopy image analysis.\
**Something you've tried (or would like to try) with Dask?** We run a lot of image processing workflows and want to see how Dask can be exploited in this context.

**Name:** Beth Cimini\
**Affiliation:** Broad Institute\
**Timezone:** US-East\
**What kind of science do you work on?** User friendly image analysis tools for microscopy imaging.\
**Something you've tried (or would like to try) with Dask?** Making Dask work in CellProfiler, to make it easy to analyze big images in high throughput!\
**Lightning talk:** [click here](https://www.youtube.com/playlist?list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0)

**Name:** Volker Hilsenstein\
**Affiliation:** EMBL / Alexandrov lab\
**Timezone:** Central European Summer Time\
**What kind of science do you work on?** Spatial Metabolomics, combining microscopy and mass spectrometry.\
**Something I would like to try with dask:** fusing large mosaics of individual images or image volumes for which affine transformation into a joint coordinate system are available.

**Name:** Marvin Albert\
**Affiliation:** University of Zurich\
**Timezone:** UTC/GMT +2\
**What kind of science do you work on?** Life sciences / image analysis\
**Something you've tried (or would like to try) with Dask? What do you want to do next with Dask?** Parallelise / reduce the memory footprint of image processing tasks and define workflows that can run on different compute environments.\
**Lightning talk:** [click here](https://www.youtube.com/watch?v=YIblUvonMvo&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=9)

**Name:** Jordao Bragantini\
**Affiliation:** CZ Biohub\
**Timezone:** Pacific Daylight Time (UTC -7)\
**What kind of science do you work on?** Light-sheet microscopy\
**Something you've tried (or would like to try) with Dask?** Image processing of very large data.\
**What do you want to do next with Dask?** Implement algorithms for cell segmentation.\
**Lightning talk:** [click here](https://www.youtube.com/watch?v=xadb-oXMFKI&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=3)

**Name:** Josh Moore\
**Affiliation:** Open Microscopy Environment (OME)\
**Timezone:** CEST\
**What kind of science do you work on?** Bioimaging (infrastructure for RDM)\
**Something you've tried (or would like to try) with Dask?** Accessing large image (Zarr) volumes over HTTP, primarily.
What do you want to do next with Dask? Improve pre-fetching for typical usage patterns, possibly integrating multiscale data (i.e. google maps zooming)\
**Lightning talk:** [click here](https://www.youtube.com/watch?v=6PerbQhcupM&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=1)

**Name:** Jackson Maxfield Brown\
**Timezone:** PST\
**What kind of science do you work in?** Cell biology, specifically microscopy and computational biology.\
**Something you've tried (or would like to try) with Dask?** Built a metadata aware / backed microscopy imaging reading library that uses Dask to read any size image w/ chunking by metadata dimension information. As well as TB-scale image processing pipelines using Dask + Prefect.\
**What do you want to do next with Dask?** Tighter integration with other libraries. I see cuCim from the RAPIDs team and would love to extend work with them to have a more general "bio-image-spec" so we can all play nicely together.\
**Lightning talk:** [click here](https://www.youtube.com/watch?v=LNa_gGpSnvc&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=8)

**Name:** Gregory R. Lee\
**Affiliation:** Quansight\
**Timezone:** EST (UTC-5)\
**What kind of science do you work on?** Scientific software development (with a background doing research in magnetic resonance imaging).\
**Something you've tried (or would like to try) with Dask?**\
In past research work, I used Dask primarily in two scenarios, both on a single workstation:

1. To achieve multi-threading by processing image blocks in parallel on the CPU (e.g. like in dask-image)
2. Serial blockwise processing of large volumetric data on the GPU (i.e. CuPy arrays of 10-100 GB in size) to reduce peak memory requirements.

**What do you want to do next with Dask?**\
Audit scikit-image functions to determine which can easily be accelerated using block-wise approaches as in dask-image. Ideally a subset of functions would work directly with dask-arrays as inputs rather than requiring users to learn about Dask's map_overlap, etc. to use this feature.\
**Lightning talk:** [click here](https://www.youtube.com/watch?v=vPorCnEhM6g&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0&index=16)

## What's next?

Dask is now considering holding "office hours" for the life science community. If we can find enough maintainers able to host one-hour Q&A sessions, then we'll trial this for a short period of time.
