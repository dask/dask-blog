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
* Lots of people want more examples tailored to their specific scientifc domain.
* Better integration of Dask into other software is considered very important.
* Managing memory constraints when working with big data is a common pain point.

Our strategic plan for this year involves three parallel streams:
* [INFRASTRUCTURE](#Infrastructure) (60%) - improvements to Dask, or to other software with many life science users.
* [OUTREACH](#Outreach) (20%) - blogposts, talks, webinars, tutorials, and examples.
* [APPLICATIONS](#Applications) (20%) - the application of Dask to a specific life science problem, collaborating with individual labs or graoups.

If you still want to have your say, it's not too late -
[click this link to get in touch!](https://t.co/0NeknSdrO9?amp=1)

## Contents
* [Background](#Background)
* [What we learned](#What-we-learned)
    * [From Dask users](#From-Dask-users)
    * [From other software libraries](#From-other-software-libraries)
* [Opportunities we see](#Opportunities-we-see)
* [Strategic plan](#strategic-plan)
* [Limitations](#Limitations)
* [Methods](#Methods)

## Background

Recently Dask [won some funding](https://chanzuckerberg.com/eoss/proposals/) to hire a developer ([Genevieve Buckley](https://github.com/GenevieveBuckley/)) to improve Dask specifically for life sciences.

Working with scientists is a really great way to drive growth in open source projects. Both scientists and software developers benefit. Early on, Dask had a lot of success integrating with the geosciences community. It'd be great to see similar success for life sciences too.

There are several areas of life science where we see Dask being used today:
* Biological image processing
* Single cell analysis
* Statistical genetics
* ...and many more

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

Some of the software projects we spoke to include:
* [sgkit](https://github.com/pystatgen/sgkit)
* [scanpy](https://scanpy.readthedocs.io/en/stable/)
* [squidpy](https://github.com/theislab/squidpy)
* [ilastik](https://www.ilastik.org/)
* [CellProfiler](https://cellprofiler.org/)
* [napari](https://napari.org/)

Some projects, like [napari](https://napari.org/), already use Dask under the hood. Other projects don't use Dask at all, but think that it might be able to help them.

Software projects wanted to solve problems related to:
* Easier deployment to distributed clusters
* Managing memory when processing large datasets
* Parallelization of existing functionality

## Opportunities we see

Because large scientific software projects have many users, improvements here would be high value for the scientific community. This is a huge area of opportunity. We plan to collaborate with these developer communities as much as possible to drive this forward.

Another area of opportunity is improving infrastructure for [high level graph visualizations](https://github.com/dask/dask/issues/7141). Power users and novices alike would benefit from better tools for identifying areas of inefficiencies in Dask computations.

Finally, continuing to build support for Dask arrays with non-numpy chunks is also a high impact area of opportunity. In particular, support for sparse arrays, and support for arrays on the GPU were highlighted as very important to the life science community.

## Strategic direction
We're going to manage this project with three parallel streams:
* [INFRASTRUCTURE](#Infrastructure) (60%)
* [OUTREACH](#Outreach) (20%)
* [APPLICATIONS](#Applications) (20%)

Each stream will likely have one primary project at any time, with many more queued. Within each stream, proposed projects will be ranked according to: level of impact, time commitment required, and the availability of other developer resources.

### Infrastructure
Infrastructure projects are improvements to either:
* Projects housed within the [Dask organisation](https://github.com/dask/), or
* Other software projects involving Dask with large numbers of life science users

We'll aim to spend around 60% of project effort on infrastructure.

### Outreach
Outreach activities include blogposts, talks, webinars, tutorials, and creating examples for documentation. We aim to spend around 20% of project effort on outreach.

### Applications
The final stream focusses on the application of Dask to a specific problem in life science.

These projects generally involve collaborating with individual labs or group, and have an end goal of summarizing their workflow in a blogpost. This feeds back into our outreach, so others in the community can learn from it.

Ideally these are short term projects, so we can showcase many different applications of Dask. We aim to spend around 20% of project effort on applications.

### How will we know what success looks like?
The role of Dask Life Science Fellow has a very broad scope, so there are a lot of different ways we could be successful within this space.

Some indicators of success are:
* Bugs being clearly described, or bottlenecks clearly identified
* Bug fixes
* Improvements or new features made to Dask infrastructure
* Improvements or new features made in related project repositories
* Better integration or support for Dask made in related project repositories for life sciences
* Better documentation with examples tailored to specific areas of life science
* Blogposts written (ideally in collaboration with Dask users)
* Talks given
* Webinars produced
* Tutorials created

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

* A [short survey](https://t.co/0NeknSdrO9?amp=1) was created to gather comments
* It was advertised by the [@dask_dev](https://twitter.com/dask_dev/) twitter account
* We asked related software projects consider retweeting for reach ([example](https://twitter.com/napari_imaging/status/1360090299901505543))
* We posted in scientific Slack groups and online public forums
* We emailed other life scientists in our network, asking them to let their networks know too
* We contacted a number of life science researchers directly.
* We contacted several other scientific software groups directly and spoke with the developers.
