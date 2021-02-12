---
layout: post
title: Getting to know the life science community
author: Genevieve Buckley
tags: [imaging]
theme: twitter
---
{% include JB/setup %}

Executive Summary
-----------------

Dask wants to better support the needs of life scientists. We've been getting to know the community, in order to better understand:
1. Who is out there?
2. What kind of problems are they trying to solve?

We've learned that:
# TODO

If you want to have your say -
[click this link to get in touch!](https://t.co/0NeknSdrO9?amp=1)


Introduction
------------

Recently Dask [won some funding](https://chanzuckerberg.com/eoss/proposals/) to hire a developer ([Genevieve Buckley]()) to improve Dask specifically for

Working with scientists is a really great way to drive growth in open source projects. Both scientists and software developers benefit. Early on, Dask had a lot of success integrating with the geosciences community. It'd be great to see similar success for life sciences too.


There are several areas of life science where we see Dask being used today:
* Biological image processing
* Single cell analysis
* Statistical genetics

What we learned
----------------

### Dask users
When we talked to people, a lot of similar themes to their comments.

People wanted:
1. Better documentation and examples
2. Better support for working with constrained resources
3. Better interoperability with other software tools

The most common request was for better documentation with more examples. People across many different areas of life science all said this could help them a lot.

GPU support was also commonly mentioned. Comments about GPUs fit into two of the categories above: GPU memory is often a constraint, and life scientists also want it to be easier to apply deep learning models to their data.

### Dask with other software
We didn't only talk with individual users of Dask. We also spoke to developers of scientific software projects.

Some of the software projects we spoke to include:
* [scanpy](https://scanpy.readthedocs.io/en/stable/)
* [ilastik](https://www.ilastik.org/)
* [CellProfiler](https://cellprofiler.org/)
* [napari](https://napari.org/)

Some projects, like [napari](https://napari.org/), already use Dask under the hood. Other projects don't use Dask at all, but think that it might be able to help them.

Software projects wanted to solve problems related to:
* Managing memory when processing large datasets
* Easier deployment to supercomputing clusters
* Parallelization of existing functionality

Because large scientific software projects have many users, improvements here would be high value for the scientific community.

Limitations
-----------
The information we found out is likely to be biased in a few different ways.

My network is strongest among imaging scientists, and among people in Australia (Genevieve). It's much less strong for other fields in life science, as my training is in physics.

The Dask project has strong links to other open source python projects, including scientific software. They are likely to be over-represented among the people we spoke to.

The Dask developer community has strong representation from companies including NVIDIA, Quansight, and others. This also means people linked to these companies are also likely to be over-represented among the people we spoke to.

It's much harder to find people who aren't using Dask at all yet but have problems that would be a good fit for it. These people are very unlikely to be, say following [Dask on twitter](https://twitter.com/dask_dev/), and probably won't be aware that we're looking for them.

I don't think there are any perfect solutions to these problems.

We've tried to mitigate these effects by using loose second and third degree connections to spread awareness, as well as posting in science public forums.

Methods
-------

We used a variety of approaches to gather feedback from the life science community.

* A [short survey](https://t.co/0NeknSdrO9?amp=1) was created to gather comments
* It was advertised by the [@dask_dev](https://twitter.com/dask_dev/) twitter account
* We asked related software projects consider retweeting for reach ([example](https://twitter.com/napari_imaging/status/1360090299901505543))
* We posted in scientific Slack groups and online public forums
* We emailed other life scientists in our network, asking them to let their networks know too
* We contacted a number of life science researchers directly.
* We contacted several other scientific software groups directly and spoke with the developers.
