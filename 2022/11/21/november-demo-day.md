---
blogpost: true
date: Nov 21, 2022
title: Dask Demo Day November 2022
author: Richard Pelgrim (Coiled)
tags: Community
---

Once a month, the Dask Community team hosts Dask Demo Day: an informal and fun online hangout where folks can showcase new or lesser-known Dask features and the rest of us can learn about all the things we didn’t know Dask could do 😁

November’s Dask Demo Day had five great demos. We learned about:

- [Visualizing 2-billion lightning flashes with Dask, RAPIDS and Datashader](#visualization-at-lightning-speed)
- [The new Dask CLI](#the-new-dask-cli)
- [The Dask-Optuna integration for distributed hyperparameter optimization](#xgboost-hpo-with-dask-and-optuna)
- [Dask-Awkward](#dask-for-awkward-arrays)
- [Profiling your Dask code with Dask-PySpy](#profiling-dask-on-a-cluster-with-py-spy)

This blog gives you a quick overview of the five demos and demonstrates how they might be useful to you. You can [watch the full recording below](https://www.youtube.com/embed/_x7oaSEJDjA).

<iframe width="560" height="315" src="https://www.youtube.com/embed/_x7oaSEJDjA" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Visualization at Lightning Speed

Would it be possible to interactively visualize all the lightning strikes in his dataset, [Kevin Tyle](https://www.albany.edu/daes/faculty/kevin-tyle) (University of Albany) recently asked himself. In this demo, Kevin shows you how he leveraged [CUDA](https://developer.nvidia.com/cuda-zone), [RAPIDS-AI](https://rapids.ai/), [Dask](https://www.dask.org/) and [Datashader](https://datashader.org/) to build a smooth interactive visualization of 8 years’ worth of lightning strikes. That’s over 2 billion rows of data.

Kevin shows you how to finetune performance of such a large-scale data processing workflow by:

- Leveraging GPUs
- Using a Dask cluster to maximize hardware usage
- Making smart choices about file types

<img alt="Heatmap of lightning strikes in the US" src="/images/2022-11-demo-day/lightning.png" style="max-width: 100%;" width="100%" />

Watch the [full demo](https://youtu.be/_x7oaSEJDjA?t=167) or read more about [high-performance visualization strategies](https://www.coiled.io/blog/datashader-data-visualisation-performance) with Dask and Datashader.

## The New Dask CLI

During the Dask Sprint at [SciPy](https://conference.scipy.org/) this year, a group of Dask maintainers began work on an upgraded, high-level [Dask CLI](https://docs.dask.org/en/stable/cli.html). [Doug Davis](https://ddavis.io/about/) (Anaconda) walks us through how the CLI works and all the things you can do with it. After installing dask, you can access the CLI by typing dask into your terminal. The tool is designed to be easily extensible by anyone working on Dask. Doug shows you how to add your own components to the Dask CLI.

<img alt="Screenshot of the new Dask CLI in action" src="/images/2022-11-demo-day/dask-cli.png" style="max-width: 100%;" width="100%" />

Watch the [full demo](https://youtu.be/_x7oaSEJDjA?t=882) or read the [Dask CLI documentation](https://docs.dask.org/en/stable/cli.html).

## XGBoost HPO with Dask and Optuna

Have you ever wanted to speed up your hyperparameter searches by running them in parallel? [James Bourbeau](https://www.jamesbourbeau.com/about/) (Coiled) shows you how you can use the brand-new [`dask-optuna`](https://jrbourbeau.github.io/dask-optuna/) integration to run hundreds of hyperparameter searches in parallel on a Dask cluster. Running your Optuna HPO searches on a Dask cluster requires only two changes to your existing optuna code. After making those changes, we’re then able to run 500 HPO iterations in parallel in 25 seconds.

<img alt="Screenshot of Dask-Optuna running" src="/images/2022-11-demo-day/optuna-dask.png" style="max-width: 100%;" width="100%" />

Watch the [full demo](https://youtu.be/_x7oaSEJDjA?t=1300).

## Dask for Awkward Arrays

The PyData ecosystem has historically focused on rectilinear data structures like DataFrames and regular arrays. [Awkward Arrays](https://awkward-array.readthedocs.io/en/stable/) brings NumPy-like operations to non-rectilinear data structures and [dask-awkward](https://github.com/ContinuumIO/dask-awkward) enables you to work with awkward arrays on a distributed cluster in parallel. [Doug Davis](https://ddavis.io/about/) (Anaconda) walks you through a quick demo of how to use `dask-awkward` on a local cluster. This is a helpful tool if you find yourself working with nested data structures at scale.

<img alt="Screenshot of dask-awkward" src="/images/2022-11-demo-day/awkward.png" style="max-width: 100%;" width="100%" />

Watch the [full demo](https://youtu.be/_x7oaSEJDjA?t=2033).

## Profiling Dask on a Cluster with py-spy

[py-spy](https://github.com/benfred/py-spy) is a Python profiler that lets you dig deeper into your code than just your Python functions. [Gabe Joseph](https://github.com/gjoseph92) (Coiled) shows you how you can use [dask-pyspy](https://github.com/gjoseph92/dask-pyspy) to profile code on a Dask cluster. By digging down into compiled code, dask-pyspy is able to discover valuable insights about why your Dask code might be running slow and what you might be able to do to resolve this.

<img alt="Screenshot of dask-pyspy in action" src="/images/2022-11-demo-day/pyspy.png" style="max-width: 100%;" width="100%" />

Watch the [full demo](https://youtu.be/_x7oaSEJDjA?t=2758).

## Join us for the next Demo Day!

Dask Demo Day is a great opportunity to learn about the latest developments and features in Dask. It’s also a fun hangout where you can ask questions and interact with some of Dask’s core maintainers in an informal, casual online setting. We’d love to see you at the next Demo Day on December 15th!

Curious how you can stay connected and find out about the latest Dask news and events?

You can:

- follow us on Twitter [@dask_dev](https://twitter.com/dask_dev)
- subscribe to the Dask newsletter by sending a blank email to newsletter+subscribe@dask.org
- subscribe to the [Dask community calendar](https://docs.dask.org/en/latest/support.html)
