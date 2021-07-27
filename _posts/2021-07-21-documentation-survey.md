---
layout: post
title: Documentation Survey
author: Julia Signell
theme: twitter
---
{% include JB/setup %}

## Executive Summary

Dask has a tremendous amount of documentation, but I have the feeling that they could be organized in a way that is more compelling and easier for new users to interact with.

This article is a survey of what other libraries are doing and what we can learn from them.

## Contents

* [Current Documentation](#current-documentation)
* [Dataframe Libraries](#dataframe-libraries)
  - [pandas](#pandas)
  - [cudf](#cudf)
  - [xarray](#xarray)
* [R libraries](#r-libraries)
  - [dplyr](#r-dplyr)
* [ML libraries](#ml-libraries)
  - [PyTorch](#pytorch)
  - [TensorFlow](#tensorflow)
* [Libraries that use Diataxis Framework](#libraries-that-use-diataxis-framework)
  - [django](#django)
  - [numpy](#numpy)
* [Takeaways](#takeaways)

## Current Documentation

In this article I'll focus only on [Docs](https://docs.dask.org).

### How are they structured?

The Dask docs have two levels of navigation. The top bar is uniform across all the side projects (dask-ml, dask-image, dask-kubernetes, dask-gateway) and contains links to any of the subprojects as well as links to related sites such as examples, the youtube channel, and github.

Along the left side there is site-level nav with the sections:

* Getting Started - includes installation instructions as well as deployment information and external links
* User Interface - has subsections for each type of collection. API is nested under each collection.
* Scheduling - information on local schedulers and a link out to [distributed](https://distributed.dask.org)
* Diagnostics - basically all the visual bits about dashboards and task graphs
* Help & Reference - includes development docs as well as miscellaneous pages and also internal architecture discussions.

### Which pages are most used?

From Google Analytics we can see the most commonly viewed pages.

<img src="/images/docs-google-analytics.png" width="70%">

It is hard to understand whether those pages are the most visible, or if they actually contain the information that people are trying to find. But either way, it conveys the importance of navigation in directing users.


## Dataframe Libraries
These are the libraries that I consider the most similar to dask.

### [pandas](https://pandas.pydata.org/docs/)

Pandas presents a stripped down landing page that forces the user into "Getting Started", "User guide", "API reference" or "Developer guide". The top-level nav are all just links (no drop-downs).

<img src="/images/pandas-docs.png" width="70%">

The API reference is categorized by type of action that a user might take. Such as "Input/output" or "Series construction"

<img src="/images/pandas-api-reference.png" width="70%">

"Getting Started" starts with installation and has its own tutorial that it tries to push people into. It also does comparisons with other tools.

The "User Guide" has a "10 minutes to pandas" some explanation and then separates out by topic area (like categorical data, or missing data).

Some interesting bits in here are the [FAQs/Gotchas](https://pandas.pydata.org/docs/user_guide/gotchas.html) which describe some little part of internal structure as it applies to user-facing code.

### [cuDF](https://docs.rapids.ai/api/cudf/stable/)

The initial emphasis is on unsorted "API Reference", but there are subsections containing cookbook-style articles like "10 Minutes to cuDF and Dask-cuDF", "Basics", and "Input/Output".

<img src="/images/cudf-docs.png" width="70%">

Tutorials, API and some explanations of internals are intermingled without a clear hierarchy.

### [xarray](http://xarray.pydata.org/en/stable/)

There is no top-level nav at all and the left hand nav is split into "For Users", "For Developers/Contributors" and "Community".

<img src="/images/xarray-docs.png" width="70%">

There are several subsections within "For Users" that have their own dropdowns such as "Getting Started" which has "Overview: Why xarray?", "Installation", "Quick overview" and "Frequently Asked Questions"

There is also this "How do I ..." section:

<img src="/images/xarray-how-do-I.png" width="70%">

## R libraries

R has the concept of "vignettes" which offer narrative style introductions to R package. In addition each package has a pdf that is essentially an API Reference.

### [dplyr](https://dplyr.tidyverse.org/)

The landing page contains most of the contents. Including an overview that includes top-level function definitions, installation information, some usage examples, and links for getting in touch.

The most prominent links are to "Get Started", "Reference", and "Articles". "Get Started" links to the vignette which introduces concepts while working through a toy problem. "Reference" contains links to all functions grouped by rough use-case and development status.

<img src="/images/r-dplyr-reference.png" width="70%">

"Articles" links to something more like a traditional "User Guide" which provides explanation and more detail about particular methods.

## ML libraries

### [PyTorch](https://pytorch.org/docs/stable/index.html)

The PyTorch docs feature the Python API very prominently, and also contain implementation notes. The "Get Started" and "Tutorial" are entirely separated from the "Docs", but are accessible from the top nav. "Get Started" uses tabs effectively to separate out Local vs Remote solutions.

<img src="/images/pytorch-docs.png" width="70%">

The Tutorial features "Introduction to PyTorch" and also contains content-area specific Tutorials such as "Audio" and "Text". It looks like this is an aggregation where individual contributors submit tutorials with keyword tags.

### [TensorFlow](https://www.tensorflow.org/overview)

TensorFlow takes a similar approach of totally separating the API docs from the "Tutorials" and has an additional concept of a "Guide" which provides explanations and context. Both "Tutorials" and "Guide" are under the category of "Learn". "Learn" has an overview page that contains two self-contained hello world examples and has text explaining how to navigate the docs.

<img src="/images/tensorflow-tutorials.png" width="70%">

The Tutorials cover the same material as the PyTorch ones, but make the split between Beginner and Advanced with separate quickstarts for each type of user.

## Libraries that use Diataxis Framework

I just learned about [Diátaxis Framework](https://diataxis.fr/) and I am thinking about how to organize the Dask docs in a way that is more consistent with this framework.

![Diataxis Framework](/images/diataxis-framework.png)
_Credit: https://diataxis.fr/_

More on this in the [next Docs blog post](https://blog.dask.org/2021/07/27/documentation-framework)...


### [django](https://docs.djangoproject.com/en/3.2/)

Django uses the top nav for project-level links and the docs-level nav doesn't seem to really exist. There is a rather busy landing page which strongly pushes people into a special "intro" tutorial.

<img src="/images/django-docs.png" width="70%">

They specifically refer to the framework, but then they also seem to be trying to bring together all the information about particular aspects of the library. This takes the form of sections like "The view layer" that has a bunch of links to tutorial, howto, explanation, and reference related to that particular feature.

### [numpy](https://numpy.org/doc/stable/)

Numpy has a stripped down landing page divided into "For Users" and "For developers/contributors". The top level nav has just "User Guide", "API Reference" and "Development" (no dropdowns).

<img src="/images/numpy-docs.png" width="70%">

When you get into the "User Guide" there is an order to the pages that leads from "What is NumPy?" to "Installation", then "NumPy Quickstart" (a detour into "Numpy: the absolute basics for beginners") and then to "Numpy fundamentals".

<img src="/images/numpy-user-guide.png" width="70%">


## Takeaways

- Don't do dropdowns on the top nav bar
- Use the right margin for within-page nav
- Use the landing page to visually direct people to exact pages - pare it down as much as possible
- Use Guides for introducing concepts
- Use Tutorials for specific topic-areas
- Getting Started and User Guide should serve different purposes

### More minor things that I noticed

- The pandas docs has big action buttons on the landing page that direct you to one of their main sections.
- Next to the dplyr logo at the top left it says "part of the tidyverse". This helps to orient the user.
- The names of pages really matters. I think people are used to seeing a "10 minutes to ..." and the name is meaningful.
