---
layout: post
title: Documentation Framework
author: Julia Signell and Jacob Tomlinson
theme: twitter
---

{% include JB/setup %}

## Executive Summary

Yesterday at the Dask BOF at [SciPy](https://www.scipy2022.scipy.org/) we were talking about the recent docs work and how we can fill holes in our documentation. We want to come up with a strategy to improve things.

For a while, we've been exploring moving our documentation to the [Diátaxis Framework](https://diataxis.fr/), and after catching up with other maintainers at SciPy it is clear that many projects are converging on this framework and we are confident about continuing on this journey. This post lays out how we will take the existing docs and apply the framework to make content clearer and easier to find. NOTE: This blog post sketches out where we are going, but the change will happen incrementally.

We want the docs to quickly answer questions like:

- I know my workflow is parallizable - can Dask help?
- How do I find my logs for a particular worker?
- Should I be using `.persist()`?

## Contents

- [Theory](#theory)
- [Current Documentation](#current-documentation)
- [New Structure](#new-structure)
- [How you can help](#how-you-can-help)

## Theory

The Diataxis Framework proposes that the documentation be split into 4 entirely separate sections.

![Diataxis Framework](/images/diataxis-framework.png)
_Credit: https://diataxis.fr/_

Each section serves a unique purpose.

- **Tutorials** provide a narrative that addresses a particular larger objective such as predicting global temperature or analyzing financial data.
- **How-Tos** target people who already know _what_ they want to do and are trying to figure out _how_ to do it. These people might ask questions like:
  - How do I apply a rolling mean to a timeseries?
  - How do I groupby a column?
  - How do I write to a geotiff?
- **Reference** provides the exact arguments and outputs of a particular operation.
- **Explanation** gives context and includes descriptions of how operations work internally.

## Current Documentation

There are several different sites that comprise different aspects of dask documentation. Of particular interest are [Examples](https://examples.dask.org), [Tutorials](https://tutorial.dask.org) and [Docs](https://docs.dask.org).

The bulk of the documentation that we currently have on [Docs](https://docs.dask.org) falls under "Explanation" and "Reference" but they are pretty intermingled. There are also some small "How-Tos" sprinkled in, particularly in the API docs.

The material on [Tutorials](https://tutorial.dask.org) is a mixture of "Tutorial" and "Explanation". They answer questions like: "What can I do with Dask Dataframes?" _and_ questions like "What is a Dask Dataframe?". These are styled like lectures in that there is often no motivating example and the assumption is that the audience wants to learn both about how to do specific operations in dask and how those operations work. This type of material can be consumed as standalone content and runs on binder.

[Examples](https://examples.dask.org) pretty much falls under "How-To" but there is a fair amount of setup and each example isn't split into small enough bits. They answer questions like: "How do I use dask dataframes?" and they have some more longer workflows.

### Which pages are most used?

From Google Analytics we can see the most commonly viewed pages.

<img src="/images/docs-google-analytics.png" width="70%">

It is hard to understand whether those pages are the most visible, or if they actually contain the information that people are trying to find. But either way, it conveys the importance of navigation in directing users.

## New Structure

[Tutorial](https://tutorial.dask.org) will be left as is and treated as a long-form overview.

[Examples](https://examples.dask.org) will be presented more as **How-Tos** with little explanation and more code. This will be similar to gallery or cookbook style documentation that you may see in other projects. Historically one of the current roles of examples is to demonstrate what Dask looks like, that role is now subsumed by "10 Minutes to Dask".

[Docs](https://docs.dask.org) will be reorganized and the left-nav will be slimmed down dramatically to provide direction. One idea for the left-nav is:

- Installation
- 10 Minutes to Dask (**How-To**)
- Tutorials & Talks (**Tutorial**)
- Examples (**How-To**)- this will be a landing page that points to individual sections of [Examples](https://examples.dask.org) or API Reference.
- Best Practices (**Explanation**)
- API (**Reference**)

- User Guide (**Explanation**)

  - DataFrame - explains what a dataframe is - links out aggressively to reference docs.
  - Array
  - Bag
  - Delayed
  - Futures
  - Task Graphs
  - Scheduling
  - Diagnostic Dashboard

- Configuration (**Reference**)
- Deploy Dask Clusters (**Reference**)
- Development Guidelines (**Reference**)
- Changelog (**Reference**)
- FAQs (**Reference**)

Many docstrings (aka **Reference**) already contain their own short-form **How-To** docs. I think this is a good place for these and we can thoroughly link from other places to these canonical docs.

## How you can help

Please raise issues on the dask issue tracker when you find holes in the docs! The largest gaps we see now are in "how to" which commonly are found via Google. So if you search for how to do something in Dask, and you're looking for copy-paste examples but can't find any then let us know.

If you see other gaps please let us know about those too. And if you know how your needs fit into the diataxis framework even better :)
