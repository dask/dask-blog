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
This was a mix of open source project maintainers
and active users from a broad range of institutions.
This post shares a summary of what happened at this workshop,
including slides, images, and lessons learned.

_Note: this event happened just before the widespread effects of the COVID-19
outbreak in the US and Europe. We were glad to see each other, but wouldn't recommend doing this today._

## Who came?

This was an invite-only event of fifty people, with a cap of three people per
organization. We intentionally invited an even mix of half people who
self-identified as open source maintainers, and half people who identified as
institutional users. We had attendees from academia, small startups, tech
companies, government institutions, and large enterprise. It was surprising
how much we all had in common.
We had attendees from the following companies:

- Anaconda
- Berkeley Institute for Datascience
- Blue Yonder
- Brookhaven National Lab
- Capital One
- Chan Zuckerberg Initiative
- Coiled Computing
- Columbia University
- D. E. Shaw & Co.
- Flatiron Health
- Howard Hughes Medial Institute, Janelia Research Campus
- Inria
- Kitware
- Lawrence Berkeley National Lab
- Los Alamos National Laboratory
- MetroStar Systems
- Microsoft
- NIMH
- NVIDIA
- National Center for Atmospheric Research (NCAR)
- National Energy Research Scientific Computing (NERSC) Center
- Prefect
- Quansight
- Related Sciences
- Saturn Cloud
- Smithsonian Institution
- SymphonyRM
- The HDF Group
- USGS
- Ursa Labs

## Objectives

The Dask community comes from a broad range of backgrounds.
It's an odd bunch, all solving very different problems,
but all with a surprisingly common set of needs.
We've all known each other on GitHub for several years,
and have a long shared history, but many of us had never met in person.

In hindsight, this workshop served two main purposes:

1. It helped us to see that we were all struggling with the same problems
   and so helped to form direction and motivate future work
2. It helped us to create social bonds and collaborations that help us manage
   the day to day challenges of building and maintaining community software
   across organizations

## Structure

We met for three days.

On days 1-2 we started with quick talks from the attendees and followed with
afternoon working sessions.

Talks were short around 10-15 minutes
(having only experts in the room meant that we could easily skip the introductory material)
and always had the same structure:

1. A brief description of the domain that they're in and why it's important

   _Example: We look at seismic readings from thousand of measurement devices around
   the world to understand and predict catastrophic earthquakes_

2. How they use Dask to solve this problem

   _Example: this means that we need to cross-correlate thousands of very
   long timeseries. We use Xarray on AWS with some custom operations._

3. What is wrong with Dask, and what they would like to see improved

   _Example: It turns out that our axes labels can grow larger than what
   Xarray was designed for. Also, the task graph size for Dask can become a
   limitation_

These talks were structured into six sections:

1. Workflow and pipelines
2. Deployment
3. Imaging
4. General data analysis
5. Performance and tooling
6. Xarray

We didn't capture video, but we do have slides from each of the talks below.

## 1: Workflow and Pipelines

### Blue Yonder

- Title: ETL Pipelines for Machine Learning
- Presenters: Florian Jetter
- Also attending:
  - Nefta Kanilmaz
  - Lucas Rademaker

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vSk2zAnSmzpbz5BgK70mpPmeQeV4h1IkCQh-EU8KXrZFJQGHmlMTuHvln3CmOQVTg/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="360" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### Prefect

- Title: Prefect + Dask: Parallel / Distributed Workflows
- Presenters: Chris White, CTO

<iframe src="//www.slideshare.net/slideshow/embed_code/key/4wiUwkDHmdzVTW" width="595" height="485" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" style="border:1px solid #CCC; border-width:1px; margin-bottom:5px; max-width: 100%;" allowfullscreen> </iframe> <div style="margin-bottom:5px"> <strong> <a href="//www.slideshare.net/ChrisWhite249/dask-prefect" title="Dask + Prefect" target="_blank">Dask + Prefect</a> </strong> from <strong><a href="https://www.slideshare.net/ChrisWhite249" target="_blank">Chris White</a></strong> </div>

### SymphonyRM

- Title: Dask and Prefect for Data Science in Healthcare
- Presenter: Joe Schmid, CTO

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vSCDbXrXtrL9vmA0hQ1NNk5DY0-3Azpcf9FbYgjoLuKV79vf_nm7wdUZl1NsL5DZqRmlUTP--u9HM56/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

## 2: Deployment

### Quansight

- Title: Building Cloud-based Data Science Platforms with Dask
- Presenters: Dharhas Pothina
- Also attending: - James Bourbeau - Dhavide Aruliah

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vSZ1fSrkWvzMPlx-f0qk7w2xj_uDp5q-Tg11S9UlynoohZV0VYjdFduDUrAdhptSYfpzFu9Wask1WSN/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="479" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### NVIDIA and Microsoft/Azure

- Title: Native Cloud Deployment with Dask-Cloudprovider
- Presenters: Jacob Tomlinson, Tom Drabas, and Code Peterson

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vT-B1c0r8MWMF8wvW4lNly-qmOCqhFqKdhshXnVql6UVkYQ-aGprY3Du0VH0PJBccOmM84ncw0lDV77/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### Inria

- Title: HPC Deployments with Dask-Jobqueue
- Presenters: Loïc Esteve

<iframe src="https://lesteve.github.io/talks/2020-dask-jobqueue-dask-workshop/slides.html" frameborder="0" width="1000" height="800"></iframe>

### Anaconda

- Title: Dask Gateway
- Presenters: Jim Crist
- Also attending: - Tom Augspurger - Eric Dill - Jonathan Helmus
  <style>
      iframe {
          overflow:hidden;
      }
  </style>

<iframe src="http://jcrist.github.io/talks/dask_summit_2020/slides.html" frameborder="1" width="600" height="355" scrolling="no"></iframe>

## 3: Imaging

### Kitware

- Title: Scientific Image Analysis and Visualization with ITK
- Presenters: Matt McCormick

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRz2SV2G-1LEXXCF0n9vugF13s7ABpLDT-yH3WtxQEOjt2FVHE7apl3nQhqkOiLeY9kSzM_Mrs6fJOk/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### Kitware

- Title: Image processing with X-rays and electrons
- Presenters: Marcus Hanwell

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRT--l76IcSPlIP_N6ClUtm2ECZaxkvIGrBNyyoFmJNQu6kS6CilWoleIMCur2FQ7ZpEkkCsw7UXnRd/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### National Institutes of Mental Health

- Title: Brain imaging
- Presenters: John Lee

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vTH1X0cSjozmCDvSQ8CtcxPPYejkLROC_b92W6uwznG5litWq_MwKJzUMnAQi0Prw/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### Janelia / Howard Hughes Medical Institute

- Title: Spark, Dask, and FlyEM HPC
- Presenters: Stuart Berg

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vSnZ-JgHAoAOUirqmLcI3GaKyC4oVo3vThZZ4oyx8vZjJ66An09JIhbcoy6k7ufTw/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="479" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

## 4: General Data Analysis

### Brookhaven National Labs

- Title: Dask at DOE Light Sources
- Presenters: Dan Allan

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRd8PVHjW7Umjo1rUjR7XWDT95CcEoE_3jH-ceDHsN_lMv_4M2qnlFiFvtMl9SX0Eb1EFQTGkzUWCDy/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### D.E. Shaw Group

- Title: Dask at D.E. Shaw
- Presenters: Akihiro Matsukawa

### Anaconda

- Title: Dask Dataframes and Dask-ML summary
- Presenters: Tom Augspurger

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vTs6nNsMkV92Uj4QUns1VB8pKlKSsRgUAGwvcbTOPqMazSAhxtawVNgb04YmHVFmb0z8-no-cdS8mE8/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

## 5: Performance and Tooling

### Berkeley Institute for Data Science

- Title: Numpy APIs
- Presenters: Sebastian Berg

### Ursa Labs

- Title: Arrow
- Presenters: Joris Van den Bossche

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vQY3ubjCFkMcU_b8p2xmuXN8VVR1BxxSWZDe5Vy-ftnH2CstZILvTo2pRBv5R_VDk85rNjVoWew2AJl/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### NVIDIA

- Title: RAPIDS
- Presenters: Keith Kraus
- Also attending: - Mike Beaumont - Richard Zamora

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vQiNrupzQlSqsu95AAHqIhU1V_iVUav_0WlIp4dXdSE6Izze1BL8mkFbIzg7p8CndEi9bjWaC2OVlyu/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### NVIDIA

- Title: UCX
- Presenters: Ben Zaitlen

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRU-vsXsnXgeLKdmtWZkZVV_-mOojsNesCbQKJgmWkwSjxj5ZdwkmS6X4tOt3HpFrIOfNROSlV_8l84/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

## 6: Xarray

### USGS and NCAR

- Title: Dask in Pangeo
- Presenters: Rich Signell and Anderson Banihirwe

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vStqGiQy6pJDYhRgF-BZylQussINK5BGlhnidOVCUECo_ebYqRH9cSY4e-2z7BfFFvTfvkqq_M1jXBX/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="366" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

### LBNL

- Title: Accelerating Experimental Science with Dask
- Presenters: Matt Henderson
- [Slides](https://drive.google.com/file/d/1DVVzYmhkDhO2xs0tmxpPCkxx5c4o63bO/view) - Fill too large to preview

### LANL

- Title: Seismic Analysis
- Presenters: Jonathan MacCarthy

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vSWAgKLxt1tBZxXjQfIRQNFPvAMFYZ-z0hkMy7euPnOHwO9pomH_gM8cKUTKXA68w/embed?start=false&loop=false&delayms=3000" frameborder="0" width="600" height="404" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

## Unstructured Time

Having rapid fire talks in the morning, followed by unstructured time in the
afternoon was a productive combination. Below you'll see pictures from
geo-scientists and quants talking about the same challenges, and library
maintainers from Pandas/Arrow/RAPDIS/Dask all working together on joint
solutions.

<img src="https://pbs.twimg.com/media/ERykEc9XUAEFq-L?format=jpg&name=large"
     width="40%">
<img src="https://pbs.twimg.com/media/ERzEcEeXkAU35sg?format=jpg&name=large"
    width="40%">

<img src="https://pbs.twimg.com/media/ERyz7B5X0AIrDkn?format=jpg&name=large"
    width="40%">
<img src="https://pbs.twimg.com/media/ERzXhHnWAAE_zDA?format=jpg&name=large"
    width="40%">

<img src="https://pbs.twimg.com/media/ERz3GDgXsAcE6Id?format=jpg&name=large"
    width="40%">
<img src="https://pbs.twimg.com/media/ERz4ur2WkAAGJwm?format=jpg&name=large"
    width="40%">

<img src="https://pbs.twimg.com/media/ER0sZceUYAAF5fW?format=jpg&name=large"
    width="40%">
<img src="https://pbs.twimg.com/media/ER0yY2rX0AEFfXi?format=jpg&name=large"
    width="40%">

<img src="https://pbs.twimg.com/media/ERyz98YWAAAmJbE?format=jpg&name=large"
    width="40%">
<img src="https://pbs.twimg.com/media/ERz5S2dWoAEhFHc?format=jpg&name=large"
    width="40%">

This unstructured time is a productive combination that we would recommend to
other technically diverse groups in the future. Engagement and productivity was
really high throughout the workshop.

## Final Thoughts

Dask's strength comes from this broad community of stakeholders.

An early technical focus on simplicity and pragmatism allowed the project to be
quickly adopted within many different domains. As a result, the practitioners
within these domains are largely the ones driving the project forward today.
This Community Driven Development brings an incredible diversity of technical
and cultural challenges and experience that force the project to quickly evolve
in a way that is constrained towards pragmatism.

There is still plenty of work to do.
Short term this workshop brought up many technical challenges that are shared
by all (simpler deployments, scheduling under task constraints, active memory
management). Longer term we need to welcome more people into this community,
both by increasing the diversity of domains, and the diversity of individuals
(the vast majority of attendees were white men in their thirties from the US
and western Europe).

We're in a good position to effect this change.
Dask's recent growth has captured the attention of many different institutions.
Now is a critical time to be intentional about the projects growth to make sure
that the project and community continue to reflect a broad and ethical set of
principles.

## Acknowledgements

### Sponsors

Without the support of our sponsors, this workshop would not have been possible.
Thanks to Anaconda, Capital One and NVIDIA for their support and generous
donations toward this event.

### Organizers

Thank you very much to the organizers who took time from their busy schedules
and worked so hard to put together this event.

- Brittany Treadway (Capital One)
- Keith Kraus (NVIDIA)
- Matthew Rocklin (Coiled Computing)
- Mike Beaumont (NVIDIA)
- Mike McCarty (Capital One)
- Neia Woodson (Capital One)
- Jake Schmitt (Capital One)
- Jim Crist (Anaconda)
