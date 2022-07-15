---
layout: post
title: CZI EOSS Update
author: Genevieve Buckley
tags: [life science]
theme: twitter
---

{% include JB/setup %}

Dask was awarded funding last year in round 2 of the [CZI Essential Open Source Software](https://chanzuckerberg.com/eoss/proposals/) grant program.
That funding was used to hire [Genevieve Buckley](https://github.com/GenevieveBuckley/) to work on Dask with a focus on [life sciences](https://blog.dask.org/2021/03/04/the-life-science-community).
Last month Dask submitted an interim progress report to CZI, covering the period from February to September 2021.
That progress update is published verbatim below, to share with the wider Dask community.

---

## Progress Overview

### Brief summary

The scope of work performed by the Dask fellow includes code contributions, conference presentations and tutorials, community engagement, and outreach including blogposts.

> The primary deliverable of this proposal is consistency and the success of neighboring software
> projects

Project work to date includes:

- 38 pull requests merged (plus 6 draft pull requests) across 5 different repositories.
- 3 conferences (presentations and organising of specialist workshops)
- 1 half day workshop (plus another one upcoming)
- Student supervision for Dask's Google Summer of Code project
- 9 blogposts (plus 2 drafts for upcoming publication)

### Code contributions

Code contributions are not limiteed to the main Dask repository, but also neighbouring software projects which use Dask as well (like the [napari](https://napari.org/) software project), including: `dask`, `dask-image`, `dask-examples`, `napari`, & `napari.github.io`.

To date, across the five repositories named above the Dask fellow has contributed:

- 38 pull requests
- 6 draft pull requests
- 12 closed pull requests (not merged, discarded in favour of another approach)

The Dask fellow is an official maintainer of the `dask-image` project, and additional milestones achieved for that project include:

- The maintainer team has been grown by one (we welcome Marvin Albert to our ranks)
- 2 new dask-image releases in 2020

### Code contribution highlights

Highlights include:

- Bugfixes benefitting the broader community
  - [dask PR #7391](https://github.com/dask/dask/pull/7391): This PR fixed slicing the output from Dask's bincount function. The impact of this fix was substantial, as it solved issues filed in four separate projects: `scikit-image`, `dask-ml`, `xgcm/xhistogram` and the cupy dask tests.
- Expanded GPU support
  - [dask PR #6680](https://github.com/dask/dask/pull/6680): This PR provided support for different array types in the `*_like` array creation functions. Now users can create `cupy` like Dask arrays for GPU processing, or indeed any other array type (eg: `sparse`).
  - [dask-image PR #157](https://github.com/dask/dask-image/pull/157): This PR provided GPU support for binary morphological functions in the `dask-image` project.
- Visualization tools benefitting all Dask users
  - [dask PR #7716](https://github.com/dask/dask/pull/7716): This PR automatically displays the high level graph visualization in the jupyter notebook cell output (somthing already done automatically for low level graphs).
  - [dask PR #7763](https://github.com/dask/dask/pull/7763): This PR introduced a HTML representation for Dask `HighLevelGraph` objects. This allows users and developers a much easier way to inspect the structure and status of HighLevelGraphs.
  - Further developed on during the Dask Google Summer of Code project, full report available [here](https://blog.dask.org/2021/08/23/gsoc-2021-project).
- High Level Graphs
  - [dask PR #7595](https://github.com/dask/dask/pull/7595): This PR introduced a high level graph layer for array overlaps. High level graphs are a tool we can use to optimize Dask's performance.
  - [dask PR #7655](https://github.com/dask/dask/pull/7655) (ongoing): This PR introduces a high level graph for Dask array slicing operations.
- Memory improvements (ongoing)
  - [dask PR #8124](https://github.com/dask/dask/pull/8124) (ongoing): This PR investigates improved automatic rechunking strategies for [memory problems](https://github.com/dask/dask/issues/8110) caused by reshaping Dask arrays.
  - [dask PR #7950](https://github.com/dask/dask/pull/7950) (ongoing): This PR aims to improve memory and performance of the `tensordot` function with auto-rechunking of Dask arrays.
  - [dask PR #7980](https://github.com/dask/dask/pull/7980) (ongoing): This PR aims to fix the unbounded memory use problem in `tensordot`, reported [here](https://github.com/dask/dask/issues/6916).

### Conferences

Notable conference events in 2021 included the SciPy conference, the Dask Summit, and VIS2021.

#### SciPy conference

The Dask fellow presented a talk titled _"Scaling Science: leveraging Dask for life sciences"_ at the 2021 SciPy conference. Full recording [available here](https://www.youtube.com/watch?v=tY_lCGS1BMk&t=60s).

#### Dask Summit

The Dask fellow organised two workshops at the 2021 [Dask Summit](https://summit.dask.org/):

1. Dask Down Under (co-organised with Nick Mortimer), and
2. The Dask life science workshop

##### Dask Down Under

The scope of Dask Down Under was more like a mini-conference for Australian timezones, rather than a typical workshop. Dask Down Under involved two days of events, covering:

- 5 talks
- 2 tutorials
- 1 panel discussion
- 1 meet and greet networking event

It was very well recieved by the community. A full report on the Dask Down under events is available [here](https://blog.dask.org/2021/06/25/dask-down-under). A YouTube playlist of the Dask Down Under events is available [here on the Dask YouTube channel](https://www.youtube.com/watch?v=10Ws59NGDaE&list=PLJ0vO2F_f6OAXBfb_SAF2EbJve9k1vkQX).

##### Dask life science workshop

The Dask life science workshop involved:

- 15 pre-recorded lightning talks
- 3 interactive discussion times (accessible across timezones in Europe, Oceania, and the Americas)
- Asynchronous text chat throughout the Dask Summit

A full report on the Dask life science workshop is available [here](https://blog.dask.org/2021/05/24/life-science-summit-workshop). A YouTube playlist of all the Dask life science lightning talks is available [here on the Dask YouTube channel](https://www.youtube.com/watch?v=6PerbQhcupM&list=PLJ0vO2F_f6OBAY6hjRHM_mIQ9yh32mWr0).

##### VIS2021 symposium

The Dask fellow was an invited panellist at the [VIS2021 symposium](https://www.vis2021.com.au/) in February 2021. The "Problem Solver" panel discussion covered practical problems in image analysis and how tools like Dask and napari can help solve them.

### Tutorials and workshops

The Dask fellow co-presented a half-day workshop (five hours) at the 2021 [Light Microscopy Australia Meeting](https://www.lmameeting.com.au/) with Juan Nunez-Iglesias. [napari](https://napari.org/) is an open source multidimensional image viewer built using Dask for out-of-core image processing. Workshop content is available at this link: <https://github.com/jni/lma-2021-bioimage-analysis-python/>

**Upcoming workshop:**
The Dask fellow has been invited to deliver a workshop on [napari](https://napari.org/) and big data using [Dask](https://dask.org/) at an upcoming [NEUBIAS Academy](http://eubias.org/NEUBIAS/training-schools/neubias-academy-home/). Workshop content is available at this link: <https://github.com/GenevieveBuckley/napari-big-data-training>

### Google Summer of Code

The Dask fellow supervised a Google Summer of Code student in 2021. Martin Durant acted as a secondary supervisor. The project ran over a 3 month period, and involved implementing a number of features to improve visualization of Dask graphs and objects. A full report on the Dask GSOC project is available [here](https://blog.dask.org/2021/08/23/gsoc-2021-project).

### Blogposts

We set a goal of one blogpost per month, and exceeded it. To date, nine blogposts have been published by the Dask fellow, with another two currently in draft status.

1. [Getting to know the life science community](https://blog.dask.org/2021/03/04/the-life-science-community)
2. [Dask with PyTorch for large scale image analysis](https://blog.dask.org/2021/03/29/apply-pretrained-pytorch-model) (co-authored with Nick Sofreniew)
3. [Skeleton analysis](https://blog.dask.org/2021/05/07/skeleton-analysis)
4. [Life sciences at the 2021 Dask Summit](https://blog.dask.org/2021/05/24/life-science-summit-workshop)
5. [The 2021 Dask User Survey is out now](https://blog.dask.org/2021/05/25/user-survey)
6. [Dask Down Under](https://blog.dask.org/2021/06/25/dask-down-under) (co-authored with Nick Mortimer)
7. [Ragged output, how to handle awkward shaped results](https://blog.dask.org/2021/07/02/ragged-output)
8. [High Level Graphs update](https://blog.dask.org/2021/07/07/high-level-graphs)
9. [Google Summer of Code 2021 - Dask Project](https://blog.dask.org/2021/08/23/gsoc-2021-project)

Draft status, will be published soon:

- [Mosaic Image Fusion](https://github.com/dask/dask-blog/pull/108) (co-authored with Volker Hisenstein)
- [2021 Dask user survey results](https://github.com/dask/dask-blog/pull/109)
