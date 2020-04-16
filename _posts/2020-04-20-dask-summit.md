---
layout: post
title: Dask Summit
tagline: Gathering together
tags: []
theme: twitter
author: Mike McCarty (Capital One Center for Machine Learning) and Matthew Rocklin (Coiled Computing)
---
{% include JB/setup %}

In late February members of the Dask community gathered together in Washington, DC.
This was a mix of open source project maintainers,
and highly active users from a broad range of institutions.
This post shares a summary of what happened at this workshop,
including slides, images, and lessons learned.

*Note: this event happened just before the widespread effects of the COVID-19
outbreak.  We wouldn't recommend doing this today.*

Who came?
---------

This was an invite-only event of fifty people, with a cap of three people per
organization.  We intentionally invited an even mix of half people who
self-identified as open source maintainers, and half people who identified as
institutional users.  We had attendees from the following companies:

-  ...
-  TODO
-  ...


Objectives
----------

The Dask community comes from a broad range of institutions.
We have climate scientists talking with bankers,
and open source evangelists talking with startup founders.
It's an odd bunch, all solving very different problems,
but all with a surprisingly common set of needs.
We've all known each other on GitHub for several years,
and have a long shared history, but many of us had never met in person.

In hindsight, this workshop served two main purposes:

1.  It helped us to see that we were all struggling with the same problems
    and so helped to form direction and motivate future work
2.  It helped us to create social bonds and collaborations that help us manage
    ...


Structure
---------

We met for three days.
On the first two we started with quick talks from the attendees that always had
the same structure:

1.  A brief description of the domain that they're in and why it's important

    *It's really fun to see all of the different use cases*

2.  How they use Dask to solve this problem

    *This is something that everyone can relate to, even if they're in a
    different field*

3.  What is wrong with Dask, and what they would like to see improved

    *...*

Talks were short around 10-15 minutes
(having only experts in the room meant that we could easily skip the introductory material).

We didn't capture video, but we do have slides from each of the talks below:

### Workflow and Pipelines

#### Blue Yonder

-   Title: ETL Pipelines for Machine Learning
-   Presenters: Florian Jetter
-   Also attending:
    -   Nefta Kanilmaz
    -   Lucas Rademaker
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vSk2zAnSmzpbz5BgK70mpPmeQeV4h1IkCQh-EU8KXrZFJQGHmlMTuHvln3CmOQVTg/pub?start=false&loop=false&delayms=60000)

Notes ...


#### Prefect

-   Title: Prefect + Dask: Parallel / Distributed Workflows
-   Presenters: Chris White, CTO
-   [Slides](https://www.slideshare.net/ChrisWhite249/dask-prefect)

Notes ...

#### SymphonyRM

-   Title: Dask and Prefect for Data Science in Healthcare
-   Presenter: Joe Schmid, CTO
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vSCDbXrXtrL9vmA0hQ1NNk5DY0-3Azpcf9FbYgjoLuKV79vf_nm7wdUZl1NsL5DZqRmlUTP--u9HM56/pub?start=false&loop=false&delayms=60000)

Notes ...


### Deployment

#### Quansight

-   Title: Building Cloud-based Data Science Platforms with Dask
-   Presenters: Dharhas Pothina
-   Also attending:
    -   James Bourbeau
    -   Dhavide Aruliah
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vSZ1fSrkWvzMPlx-f0qk7w2xj_uDp5q-Tg11S9UlynoohZV0VYjdFduDUrAdhptSYfpzFu9Wask1WSN/pub?start=false&loop=false&delayms=3000)

#### NVIDIA and Microsoft/Azure

-   Title: Native Cloud Deployment with Dask-Cloudprovider
-   Presenters: Jacob Tomlinson, Tom Drabas, and Code Peterson
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vT-B1c0r8MWMF8wvW4lNly-qmOCqhFqKdhshXnVql6UVkYQ-aGprY3Du0VH0PJBccOmM84ncw0lDV77/pub?start=false&loop=false&delayms=3000)

#### Inria

-   Title: HPC Deployments with Dask-Jobqueue
-   Presenters: Loïc Esteve
-   [Slides](https://lesteve.github.io/talks/2020-dask-jobqueue-dask-workshop/slides.html#/slide-org5239ab5)

#### Anaconda

-   Title: Dask Gateway
-   Presenters: Jim Crist
-   Also attending:
    -   Tom Augspurger
    -   Eric Dill
    -   Jonathan Helmus
-   [Slides](http://jcrist.github.io/talks/dask_summit_2020/slides.html)


### Imaging

#### Kitware

-   Title: Scientific Image Analysis and Visualization with ITK
-   Presenters: Matt McCormick
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vRz2SV2G-1LEXXCF0n9vugF13s7ABpLDT-yH3WtxQEOjt2FVHE7apl3nQhqkOiLeY9kSzM_Mrs6fJOk/pub?start=false&loop=false&delayms=3000)

#### Kitware

-   Title: Image processing with X-rays and electrons
-   Presenters: Marcus Hanwell
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vRT--l76IcSPlIP_N6ClUtm2ECZaxkvIGrBNyyoFmJNQu6kS6CilWoleIMCur2FQ7ZpEkkCsw7UXnRd/pub?start=false&loop=false&delayms=3000)

#### NIMH

-   Title: Brain imaging
-   Presenters: John Lee
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vTH1X0cSjozmCDvSQ8CtcxPPYejkLROC_b92W6uwznG5litWq_MwKJzUMnAQi0Prw/pub?start=false&loop=false&delayms=3000)


Pictures from happy hour.

On the second day we also captured pictures during presentations ...
TODO: pull from here for day two https://twitter.com/mrocklin/status/1233037116885458944


### General Data Analysis

#### Brookhaven National Labs

-   Title: Dask at DOE Light Sources
-   Presenters: Dan Allan
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vRd8PVHjW7Umjo1rUjR7XWDT95CcEoE_3jH-ceDHsN_lMv_4M2qnlFiFvtMl9SX0Eb1EFQTGkzUWCDy/pub?start=false&loop=false&delayms=3000)

#### D.E. Shaw Group

-   Title: Dask at D.E. Shaw
-   Presenters: Akihiro Matsukawa
-   Need slides - PDF

#### JD.com

-   Title: Dask for Automated Time Series Forecasting
-   Presenters: Ethan Zhang
-   Need slides - Did not attend?

#### Anaconda

-   Title: Dask Dataframes and Dask-ML summary
-   Presenters: Tom Augspurger
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vTs6nNsMkV92Uj4QUns1VB8pKlKSsRgUAGwvcbTOPqMazSAhxtawVNgb04YmHVFmb0z8-no-cdS8mE8/pub?start=false&loop=false&delayms=3000)


### Performance and Tooling

#### Berkeley Institute for Data Science

-   Title: Numpy APIs
-   Presenters: Sebastian Berg
-   Need slides - PDF

#### Ursa Labs

-   Title: Arrow
-   Presenters: Joris Van den Bossche
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vQY3ubjCFkMcU_b8p2xmuXN8VVR1BxxSWZDe5Vy-ftnH2CstZILvTo2pRBv5R_VDk85rNjVoWew2AJl/pub?start=false&loop=false&delayms=3000)

#### NVIDIA

-   Title: RAPIDS
-   Presenters: Keith Kraus
-   Also attending:
    -   Mike Beaumont
    -   Richard Zamora
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vQiNrupzQlSqsu95AAHqIhU1V_iVUav_0WlIp4dXdSE6Izze1BL8mkFbIzg7p8CndEi9bjWaC2OVlyu/pub?start=false&loop=false&delayms=3000)

#### NVIDIA

-   Title: UCX
-   Presenters: Ben Zaitlen
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vRU-vsXsnXgeLKdmtWZkZVV_-mOojsNesCbQKJgmWkwSjxj5ZdwkmS6X4tOt3HpFrIOfNROSlV_8l84/pub?start=false&loop=false&delayms=3000)

### Xarray

#### USGS and NCAR

-   Title: Dask in Pangeo
-   Presenters: Rich Signell and Anderson Banihirwe
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vStqGiQy6pJDYhRgF-BZylQussINK5BGlhnidOVCUECo_ebYqRH9cSY4e-2z7BfFFvTfvkqq_M1jXBX/pub?start=false&loop=false&delayms=3000)

#### LBNL

-   Title: Accelerating Experimental Science with Dask
-   Presenters: Matt Henderson
-   [Slides](https://drive.google.com/file/d/1DVVzYmhkDhO2xs0tmxpPCkxx5c4o63bO/view) - Fill too large to preview

#### LANL

-   Title: Seismic Analysis
-   Presenters: Jonathan MacCarthy
-   [Slides](https://docs.google.com/presentation/d/e/2PACX-1vSWAgKLxt1tBZxXjQfIRQNFPvAMFYZ-z0hkMy7euPnOHwO9pomH_gM8cKUTKXA68w/pub?start=false&loop=false&delayms=3000)


Final Thoughts
--------------

...
