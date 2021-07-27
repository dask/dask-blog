---
layout: post
title: Documentation Framework
author: Julia Signell
theme: twitter
---
{% include JB/setup %}

## Executive Summary

In the [previous blog post](https://blog.dask.org/2021/07/21/documentation-survey). I looked at how other libraries tackle their docs. In this article I look at the [Diátaxis Framework](https://diataxis.fr/) and proposes how we can take the existing docs and apply the framework to them in a way that makes sense.

The goal of this work is to propose a site where both a new user and an existing user can easily find what they need.

## Contents

* [Theory](#theory)
* [Current Documentation](#current-documentation)
* [Proposal](#proposal)

## Theory

The Diataxis Framework proposes that the documentation be split into 4 entirely separate sections.

![Diataxis Framework](/images/diataxis-framework.png)
_Credit: https://diataxis.fr/_

Each section serves a unique purpose.

* **Tutorials** provide a narrative that addresses a particular larger objective such as predicting global temperature or analyzing financial data.
* **How-Tos** target people who already know _what_ they want to do and are trying to figure out _how_ to do it. These people might ask questions like:
  - How do I apply a rolling mean to a timeseries?
  - How do I groupby a column?
  - How do I write to a geotiff?
* **Reference** provides the exact arguments and outputs of a particular operation.
* **Explanation** gives context and includes descriptions of how operations work internally.

## Current Documentation

There are several different sites that comprise different aspects of dask documentation. Of particular interest are [Examples](https://examples.dask.org), [Tutorials](https://tutorial.dask.org) and [Docs](https://docs.dask.org).

The bulk of the documentation that we currently have on [Docs](https://docs.dask.org) falls under "Explanation" and "Reference" but they are pretty intermingled. There are also some small "How-Tos" sprinkled in, particularly in the API docs.

The material on [Tutorials](https://tutorial.dask.org) is a mixture of "Tutorial" and "Explanation". They answer questions like: "What can I do with dask dataframes?"

[Examples](https://examples.dask.org) pretty much falls under "How-To" but there is a fair amount of setup and each example isn't split into small enough bits. They answer questions like: "How do I use dask dataframes?"

One of the limitations of the Diataxis framework is that the tutorials that we present at conferences are a mixture of **How-To** and **Explanation**. These are styled like lectures in that there is often no motivating example and the assumption is that the audience wants to learn both about how to do specific operations in dask and how those operations work. Notably this type of material can be consumed as standalone content and runs on binder.

## Proposal

[Tutorial](https://tutorial.dask.org) should be left as is and treated as a long-form overview.

[Examples](https://examples.dask.org) should be presented more as **How-Tos** with no explanation and just a lot of code. One of the current roles of examples is to demonstrate what Dask looks like. That role will be subsumed by the "10 minutes to Dask".

[Docs](https://docs.dask.org) should be reorganized and the left-nav should be slimmed down dramatically to provide direction. None of the links here should go directly to another site. One idea for the left-nav is:

* Installation - this should not get into different dask cluster options. But can point to distributed for the docs on that.
* 10 Minutes to Dask (**How-To**)

* User Guide (**Explanation**)
 - Why Dask?
 - DataFrame - explains what a dataframe is - links out aggressively to reference docs.
 - Array
 - Bag
 - Delayed
 - Futures
 - Scheduler
 - Task Graphs

* How do I... (**How-To**)- this is a landing page that points to individual sections of [Examples](https://examples.dask.org) or API Reference.
* API Reference (**Reference**)
* Tutorials & talks (**Tutorial**)
* Developer Guide (**How-To**)
* FAQs
* Ecosystem
* Community

Many docstrings (aka **Reference**) already contain their own short-form **How-To** docs. I think this is a good place for these and we should thoroughly link from other places to these canonical docs.

I'm not sure what to do with top-level nav or whether it should exist across the sites. I like what tidyverse does with the link right next to the logo.

### What about...?

There are several topics that initially don't seem to align with the proposed structure. I'll address some of them here and offer an idea of where they could go:

* [Development Guidelines](https://docs.dask.org/en/latest/develop.html) - This is kind of a **How-To**, but I think it belongs at the top-level of the docs. We want it to be very prominent.
* [Why Dask?](https://docs.dask.org/en/latest/why.html) - This can be at the top-level in **Explanation** and it can in turn link out to other (potentially orphan) pages.
* [Diagnostics] - This should be a **How-To** section.

### Implementation plan

The existing split between the examples, tutorials, and docs sites should be maintained, but we should gradually split examples into bite-size chunks.

There are a few parts that can happen relatively quickly and don't require any docs overhaul:

* Write a "10 minutes to dask", [Examples](https://examples.dask.org) can provide the basis for this.
* Make one top-level dask API reference.
* Make a FAQs page that can link out to various orphan pages
* Make a How do I... page that can link to reference docs.
