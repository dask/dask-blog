---
layout: post
title: SciPy 2020 Maintainers Track Talk
tagline: An update on Dask over the last 12 months
author: Jacob Tomlinson (NVIDIA)
tags: [SciPy, Community, Talk]
theme: twitter
---

{% include JB/setup %}

We recently enjoyed the 2020 SciPy conference from the comfort of our own homes this year. The 19th annual Scientific Computing with Python conference was a virtual conference this year due to the global pandemic. The annual SciPy Conference brought together over 1500 participants from industry, academia, and government to showcase their latest projects, learn from skilled users and developers, and collaborate on code development.

This year we had the privilege of giving the first project update on the maintainers track.

## Video

COMING SOON! We will update this post once the SciPy organisers upload the recording to YouTube.

<!-- TODO: Add video once published -->

## Slides

<script async class="speakerdeck-embed" data-id="ae0f04df5b7341eaa3e2989221be1889" data-ratio="1.77777777777778" src="//speakerdeck.com/assets/embed.js"></script>

## Talk Summary

Here's a summary of the main topics covered in the talk. You can also check out the [original thread on Twitter](https://threadreaderapp.com/thread/1280885850914553856.html).

### Community overview

We've been trying to gauge the size of our community lately. The best proxy we have right now is the number of weekly visitors to the [Dask documentation](https://docs.dask.org/en/latest/). Which currently stands at around 10,000.

<img alt="Dask documentation analytics showing growth to 10,000 weekly users over the last four years" src="https://pbs.twimg.com/media/EcaS9DpWkAEBaB4.jpg" style="width: 100%;" />

Dask also came up in the [Jetbrains Python developer survey](https://www.jetbrains.com/lp/devecosystem-2020/python/). We were excited to see 5% of all the Python developers who filled out the survey said they use Dask. Which shows health in the PyData community as well as Dask.

<img alt="Jetbrains survey results showing Dask used by 5% of Python users, beaten only by the Spark/hadoop ecosystem" src="https://pbs.twimg.com/media/EcaTTuiX0AIT2KB.jpg" style="width: 100%;" />

We are running [our own survey](https://dask.org/survey) at the moment. If you are a Dask user please take a few minutes to fill it out. We would really appreciate it.

<img alt="Link to the Dask survey" src="https://pbs.twimg.com/media/EcaTlITXYAAVs-y.jpg" style="width: 100%;" />

### Community events

In February we had an in-person [Dask Summit](https://blog.dask.org/2020/04/28/dask-summit) where a mixture of OSS maintainers and institutional users met. We had talks and workshops to help figure out our challenges and set our direction.

<img alt="A room of attendees at the Dask summit" src="https://pbs.twimg.com/media/EcaUbHLXQAAHckq.jpg" style="width: 100%;" />

The Dask community also has a [monthly meeting](https://docs.dask.org/en/latest/support.html)! It is held on the first Thursday of the month at 10:00 US Central Time. If you're a Dask user you are welcome to come to hear updates from maintainers and share what you're working on.

### Community projects

There are many projects built on Dask. Looking at the preliminary results from the 2020 Dask survey shows some that are especially popular.

<img alt="Graph showing the most popular projects built on Dask; Xarray, RAPIDS, XGBoost, Prefect and Iris" src="https://pbs.twimg.com/media/EcaVSHpX0AAMDYs.png" style="width: 100%;" />

Let's take a look at each of those.

#### Xarray

[Xarray](https://xarray.pydata.org/en/stable/) allows you to work on multi-dimensional datasets that have supporting metadata arrays in a Pandas-like way.

<img alt="Slide showing xarray code example" src="https://pbs.twimg.com/media/EcaVbOaXkAMQ4SU.jpg" style="width: 100%;" />

#### RAPIDS

[RAPIDS](https://rapids.ai/) is an open-source suite of GPU accelerated Python libraries. Using these tools you can execute end-to-end data science and analytics pipelines entirely on GPUs. All using familiar PyData APIs.

<img alt="Slide showing RAPIDS dataframe code example" src="https://pbs.twimg.com/media/EcaWFfDXkAEX4B_.jpg" style="width: 100%;" />

#### BlazingSQL

[BlazingSQL](https://blazingsql.com) builds on RAPIDS and Dask to provide an open-source distributed, GPU accelerated SQL engine.

<img alt="Slide showing BlazingSQL code example" src="https://pbs.twimg.com/media/EcaWW_CXsAM7XP7.jpg" style="width: 100%;" />

#### XGBoost

While [XGBoost](https://examples.dask.org/machine-learning/xgboost.html) has been around for a long time you can now prepare your data on your Dask cluster and then bootstrap your XGBoost cluster on top of Dask and hand the distributed dataframes straight over.

<img alt="Slide showing XGBoost code example" src="https://pbs.twimg.com/media/EcaXKlRWsAAjLYe.jpg" style="width: 100%;" />

#### Prefect

[Prefect](https://www.prefect.io/) is a workflow manager which is built on top of Dask's scheduling engine. "Users organize Tasks into Flows, and Prefect takes care of the rest."

<img alt="Slide showing Prefect code example" src="https://pbs.twimg.com/media/EcaXlf-XYAEPY-Z.jpg" style="width: 100%;" />

#### Iris

[Iris](https://scitools.org.uk/iris/docs/latest/), part of the [SciTools](https://scitools.org.uk) suite of tools, uses the CF data model giving you a format-agnostic interface for working with your data. It excels when working with multi-dimensional Earth Science data, where tabular representations become unwieldy and inefficient.

<img alt="Slide showing Iris code example" src="https://pbs.twimg.com/media/EcaX3S9XsAAU-Sm.jpg" style="width: 100%;" />

#### More tools

These are the tools our community have told us they like so far. But if you use something which didn't make the list then head to [our survey](https://dask.org/survey) and let us know! According to PyPI there are many more out there.

<img alt="Screenshot of PyPI showing 239 packages with Dask in their name" src="https://pbs.twimg.com/media/EcaYZmPWoAANYhr.jpg" style="width: 100%;" />

### User groups

There are many user groups who use Dask. Everything from life sciences, geophysical sciences and beamline facilities to finance, retail and logistics. Check out the great ["Who uses Dask?" talk](https://youtu.be/t_GRK4L-bnw) from [Matthew Rocklin](https://twitter.com/mrocklin) for more info.

<img alt="Screenshot 'Who uses Dask?' YouTube video" src="https://pbs.twimg.com/media/EcaYj2JXQAEvgV3.jpg" style="width: 100%;" />

### For profit companies

There has been an increase in for-profit companies building tools with Dask. Including [Coiled Computing](https://coiled.io/), [Prefect](https://www.prefect.io/) and [Saturn Cloud](https://www.saturncloud.io/s/).

<img alt="Slide describing the for-profit companies Coiled, Prefect and Saturn Cloud" src="https://pbs.twimg.com/media/EcaZOqgX0AABFpQ.jpg" style="width: 100%;" />

We've also seen large companies like Microsoft's [Azure ML](https://azure.microsoft.com/en-gb/services/machine-learning/) team contributing a cluster manager to [Dask Cloudprovider](https://cloudprovider.dask.org/en/latest/#azure). This helps folks get up and running with Dask on AzureML quicker and easier.

### Recent improvements

#### Communications

Moving on to recent improvements there has been a lot of work to get [Open UCX](https://www.openucx.org/) supported as a protocol in Dask. Which allows worker-worker communication to be accelerated vastly with hardware that supports [Infiniband](https://en.wikipedia.org/wiki/InfiniBand) or [NVLink](https://en.wikipedia.org/wiki/NVLink).

<img alt="Slide showing worker communication comparison between UCX/Infiniband and TCP with UCX being much faster" src="https://pbs.twimg.com/media/EcaaTxiXQAE4TD0.jpg" style="width: 100%;" />

There have also been some [recent announcements](https://blogs.nvidia.com/blog/2020/06/22/big-data-analytics-tpcx-bb/) around NVIDIA blowing away the TPCx-BB benchmark by outperforming the current leader by 20x. This is a huge success for all the open-source projects that were involved, including Dask.

<img alt="Slide showing TPCx-BB benchmark results" src="https://pbs.twimg.com/media/EcabNUVWoAQGy8e.jpg" style="width: 100%;" />

#### Dask Gateway

We've seen increased adoption of [Dask Gateway](https://gateway.dask.org). Many institutions are using it as a way to provide their staff with on-demand Dask clusters.

<img alt="Slide showing Dask Gateway overview" src="https://pbs.twimg.com/media/EcabpirWkAYtx-W.jpg" style="width: 100%;" />

#### Cluster map plot (aka 'pew pew pew')

The update that got the most 👏 feedback from the SciPy 2020 attendees was the Cluster Map Plot (known to maintainers as the "pew pew pew" plot). This plot shows a high-level overview of your Dask cluster scheduler and workers and the communication between them.

<video autoplay="" loop="" controls="" poster="https://pbs.twimg.com/tweet_video_thumb/EcacHRcXkAE53eI.jpg"><source src="https://video.twimg.com/tweet_video/EcacHRcXkAE53eI.mp4" type="video/mp4"><img alt="" src="https://pbs.twimg.com/tweet_video_thumb/EcacHRcXkAE53eI.jpg"></video>

### Next steps

#### High-level graph optimization

To wrap up with what Dask is going to be doing next we are going to be continuing to work on high-level graph optimization.

<img alt="Slide showing High Level Graph documentation page" src="https://pbs.twimg.com/media/EcacZvfWsAIfqTz.jpg" style="width: 100%;" />

#### Scheduler performance

With feedback from our community we are also going to be focussing on making the [Dask scheduler more performant](https://github.com/dask/distributed/issues/3783). There are a few things happening including a Rust implementation of the scheduler, dynamic task creation and ongoing benchmarking.

<img alt="Scheduler performance tasks including a Rust implementation, benchmarking, dynamic tasks and Cython, PyPy and C experiments" src="https://pbs.twimg.com/media/Ecacr6pWoAEd4Tx.jpg" style="width: 100%;" />

### Chan Zuckerberg Foundation maintainer post

Lastly I'm excited to share that with funding from the [Chan Zuckerberg Foundation](https://chanzuckerberg.com/eoss/proposals/scaling-python-with-dask/), Dask will be hiring a maintainer who will focus on growing usage in the biological sciences field. If that is of interest to you keep an eye on [our twitter account](https://twitter.com/dask_dev) for more announcements.
