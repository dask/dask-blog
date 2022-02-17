---
layout: post
title: Getting to know the life science community
author: Genevieve Buckley
tags: [imaging]
theme: twitter
---

{% include JB/setup %}

## Executive Summary

Dask wants to better support the needs of life scientists. We've been getting to know the community, in order to better understand:

1. Who is out there?
2. What kind of problems are they trying to solve?

We've learned that:

- Lots of people want more examples tailored to their specific scientifc domain.
- Better integration of Dask into other software is considered very important.
- Managing memory constraints when working with big data is a common pain point.

Our strategic plan for this year involves three parallel streams:

- [INFRASTRUCTURE](#infrastructure) (60%) - improvements to Dask, or to other software with many life science users.
- [OUTREACH](#outreach) (20%) - blogposts, talks, webinars, tutorials, and examples.
- [APPLICATIONS](#applications) (20%) - the application of Dask to a specific life science problem, collaborating with individual labs or groups.

If you still want to have your say, it's not too late -
[click this link to get in touch!](https://t.co/0NeknSdrO9?amp=1)

## Contents

- [Background](#background)
- [What we learned](#what-we-learned)
  - [From Dask users](#from-dask-users)
  - [From other software libraries](#from-other-software-libraries)
- [Opportunities we see](#opportunities-we-see)
- [Strategic plan](#strategic-plan)
- [Limitations](#limitations)
- [Methods](#methods)

## Background

Recently Dask [won some funding](https://chanzuckerberg.com/eoss/proposals/) to hire a developer ([Genevieve Buckley](https://github.com/GenevieveBuckley/)) to improve Dask specifically for life sciences.

Working with scientists is a really great way to drive growth in open source projects. Both scientists and software developers benefit. Early on, Dask had a lot of success integrating with the geosciences community. It'd be great to see similar success for life sciences too.

There are several areas of life science where we see Dask being used today:

- Biological image processing
- Single cell analysis
- Statistical genetics
- ...and many more

We've solicited feedback from the life science community, to come up with a strategic plan to direct our effort over the next year.

## What we learned

### From Dask users

When we talked to individual Dask users, we heard a lot of similar themes in their comments.

People wanted:

1. Better documentation and examples
2. Better support for working with constrained resources
3. Better interoperability with other software tools

The most common request was for better documentation with more examples. People across many different areas of life science all said this could help them a lot. A corresponding challenge here is the multitude of different areas of life science, all of which require targeted documentation.

GPU support was also commonly mentioned. Comments about GPUs fit into two of the categories above: GPU memory is often a constraint, and life scientists also want it to be easier to apply deep learning models to their data.

### From other software libraries

We didn't only talk with individual users of Dask. We also spoke to developers of scientific software projects.

#### Why would other software libraries adopt Dask?

Software projects wanted to solve problems related to:

- Easier deployment to distributed clusters
- Managing memory when processing large datasets
- Parallelization of existing functionality

Dask is good at solving those kinds of problems, and might be a good solution for this.

#### Who we've talked to

Some of the software projects we spoke to include:

- [napari](https://napari.org/)
- [sgkit](https://pystatgen.github.io/sgkit/latest/)
- [scanpy](https://scanpy.readthedocs.io/en/stable/)
- [squidpy](https://squidpy.readthedocs.io/en/latest/)
- [ilastik](https://www.ilastik.org/)
- [CellProfiler](https://cellprofiler.org/)

#### Current status

[napari](https://napari.org/) is a python based image viewer. Dask is already well-integrated with napari. Areas for opportunity here include:

- Improved documentation about how to work efficiently with Dask arrays in napari.
- Smarter caching of neighbouring image chunks to avoid lag.
- Guides for how to create plugins for napari, so the community can grow.

[sgkit](https://pystatgen.github.io/sgkit/latest/) is a statistical genetics toolkit. Dask is already well-integrated with sgkit. The developers would like improved infrastructure in the main Dask repositories that they can benefit from. Wishlist items include:

- Better ways to understand how things like array chunks change as they move through a Dask computation.
- Better high level graph visualizations. Graph visualizations showing all the low level operations can be overwhelming.
- Better ways to identify poorly efficient areas in Dask computations.
- Stability when new versions of Dask are released
- Making it easier to run Dask in the cloud. They are currently using [dask-cloudprovider](https://github.com/dask/dask-cloudprovider) and finding that very useful.

[scanpy](https://scanpy.readthedocs.io/en/stable/) is a library for single cell analysis in Python. It is built together with [anndata](https://anndata.readthedocs.io/en/latest/), an annotated data structure.

- Data size is less of an issue for scanpy users, although anndata developers do think support for Dask would be a useful thing to add.
- Support for sparse arrays is very important for these communities.

[squidpy](https://squidpy.readthedocs.io/en/latest/) is a tool for the analysis and visualization of spatial molecular data. It builds on top of scanpy and anndata. Because squidpy involves large imaging data on top of what we'd normally see for datasets in scanpy/anndata, this is a project with a large area of opportunity for Dask.

- Integrating Dask with the squidpy ImageContainer class is a good first step towards handling large image data within the availabe RAM constraints.

[ilastik](https://www.ilastik.org/) does not currently use Dask at all. They are curious to see if Dask can make it easier to scale up from a single machine to a cluster.
Users generally train an ilastik model interactively, and then want to apply it to many images. This second step is often when people want an easy way to scale up the computing resources available.

[CellProfiler](https://cellprofiler.org/) is a pipeline tool for image processing. They have briefly experimented with Dask before.

- Primarily, they want to parallelize existing functionality.
- Most common pipelines fall into three major "user stories" where focussing effort would make the most impact:
  1. Image processing
  2. Object processing
  3. Measurements

## Opportunities we see

Because large scientific software projects have many users, improvements here would be high value for the scientific community. This is a huge area of opportunity. We plan to collaborate with these developer communities as much as possible to drive this forward.

Another area of opportunity is improving infrastructure for [high level graph visualizations](https://github.com/dask/dask/issues/7141). Power users and novices alike would benefit from better tools for identifying areas of inefficiencies in Dask computations.

Finally, continuing to build support for Dask arrays with non-numpy chunks is also a high impact area of opportunity. In particular, support for sparse arrays, and support for arrays on the GPU were highlighted as very important to the life science community.

## Strategic direction

We're going to manage this project with three parallel streams:

- [INFRASTRUCTURE](#infrastructure) (60%)
- [OUTREACH](#outreach) (20%)
- [APPLICATIONS](#applications) (20%)

Each stream will likely have one primary project at any time, with many more queued. Within each stream, proposed projects will be ranked according to: level of impact, time commitment required, and the availability of other developer resources.

### Infrastructure

Infrastructure projects are improvements to either:

- Projects housed within the [Dask organisation](https://github.com/dask/), or
- Other software projects involving Dask with large numbers of life science users

We'll aim to spend around 60% of project effort on infrastructure.

### Outreach

Outreach activities include blogposts, talks, webinars, tutorials, and creating examples for documentation. We aim to spend around 20% of project effort on outreach.

If you have outreach ideas you want to share (perhaps you run a student group or popular meetup) then you can [get in touch with us here](https://docs.google.com/forms/d/e/1FAIpQLScBi8YOx3gGkL9rz8TsRTIZYiRha9qYOvXu4EZx9qGLtjLGCw/viewform?usp=sf_link).

### Applications

The final stream focusses on the application of Dask to a specific problem in life science.

These projects generally involve collaborating with individual labs or group, and have an end goal of summarizing their workflow in a blogpost. This feeds back into our outreach, so others in the community can learn from it.

Ideally these are short term projects, so we can showcase many different applications of Dask. We aim to spend around 20% of project effort on applications.

If you use Dask and have an example in mind you'd like to share, then you can [get in touch with us here](https://docs.google.com/forms/d/e/1FAIpQLScBi8YOx3gGkL9rz8TsRTIZYiRha9qYOvXu4EZx9qGLtjLGCw/viewform?usp=sf_link).

### How will we know what success looks like?

The role of Dask Life Science Fellow has a very broad scope, so there are a lot of different ways we could be successful within this space.

Some indicators of success are:

- Bugs being clearly described, or bottlenecks clearly identified
- Bug fixes
- Improvements or new features made to Dask infrastructure
- Improvements or new features made in related project repositories
- Better integration or support for Dask made in related project repositories for life sciences
- Better documentation with examples tailored to specific areas of life science
- Blogposts written (ideally in collaboration with Dask users)
- Talks given
- Webinars produced
- Tutorials created

We won't have the time or the resources to do all the things, but we will be able to make an impact by focussing on a subset.

## Limitations

The information we discovered talking to the life science community is likely to be biased in a few different ways.

My (Genevieve's) network is strongest among imaging scientists, and among people in Australia. It's much less strong for other fields in life science, as my original training is in physics.

The Dask project has strong links to other open source python projects, including scientific software. The Dask developer community also has strong links from companies including NVIDIA, Quansight, and others. They are likely to be over-represented among the people we spoke to.

It's much harder to find people who aren't using Dask at all yet but have problems that would be a good fit for it. These people are very unlikely to be, say following [Dask on twitter](https://twitter.com/dask_dev/), and probably won't be aware that we're looking for them.

I don't think there are any perfect solutions to these problems.
We've tried to mitigate these effects by using loose second and third degree connections to spread awareness, as well as posting in science public forums.

## Methods

We used a variety of approaches to gather feedback from the life science community.

- A [short survey](https://t.co/0NeknSdrO9?amp=1) was created to gather comments
- It was advertised by the [@dask_dev](https://twitter.com/dask_dev/) twitter account
- We asked related software projects consider retweeting for reach ([example](https://twitter.com/napari_imaging/status/1360090299901505543))
- We posted in scientific Slack groups and online public forums
- We emailed other life scientists in our network, asking them to let their networks know too
- We contacted a number of life science researchers directly.
- We contacted several other scientific software groups directly and spoke with the developers.

## Join the discussion

Come join us in the Dask slack! We have a #life-science channel so there's a place to discuss things relevant to the Dask life science community. You can [request an invite to the Slack here](https://join.slack.com/t/dask/shared_invite/zt-mfmh7quc-nIrXL6ocgiUH2haLYA914g).
