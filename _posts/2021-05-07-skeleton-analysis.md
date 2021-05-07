---
layout: post
title: Skeleton analysis
author: Genevieve Buckley
tags: [imaging, life science]
theme: twitter
---
{% include JB/setup %}

## Executive Summary

In this blogpost, we show how to modify an skeleton network analysis with Dask to work with constrained RAM (eg: on your laptop). This makes it more accessible: it can run on a small laptop, instead of requiring access to a supercomputing cluster.

## Contents

* [Skeleton structures are everywhere](#skeleton-structures-are-everywhere)
* [The scientific problem](#the-scientific-problem)
* [The compute problem](#the-compute-problem)
* [Our approach](#our-approach)
* [Results](#results)
* [Difficulties encountered](#difficulties-encountered)
* [How we solved them](#how-we-solved-them)
* [Limitations](#limitations)
* [What's next](#what's-next)
* [How you can help](#how-you-can-help)

## Skeleton structures are everywhere

Lots of biological structures have a skeleton or network-like shape. We see these in all kinds of places, including:
* blood vessel branching
* the branching of airways
* neuron networks in the brain
* the root structure of plants
* the capillaries in leaves
* ... and many more

Analysing the structure of these skeletons can give us important information about the biology of that system.
## The scientific problem

For this bogpost, we will look at the blood vessels inside of a lung. This data was shared with us by [Marcus Kitchen](https://research.monash.edu/en/persons/marcus-kitchen), [Andrew Stainsby](https://hudson.org.au/researcher-profile/andrew-stainsby/), and their team of collaborators.

![Skeleton network of blood vessels within a healthy lung](/images/skeleton-analysis/skeleton-screenshot-crop.jpg)

This research group focusses on lung development.
We want to compare the blood vessels in a healthy lung, against a lung from a hernia model. In the hernia model the lung is underdeveloped, squashed, and smaller.

## The compute problem

These image volumes have a shape of roughtly 1000x1000x1000 pixels.
That doesn't seem huge but given the high RAM consumption involved in processing the analysis, it crashes when running on a laptop.

If you're running out of RAM, there are two possible appoaches:

1. Get more RAM. Run things on a bigger computer, or move things to a supercomputing cluster. This has the advantage that you don't need to rewrite your code, but it does require access to more powerful computer hardware.

2. Manage the RAM you've got. Dask is good for this. If we use Dask, and some reasonable chunking of our arrays, we can manage things so that we never hit the RAM ceiling and crash. This has the advantage that you don't need to buy more computer hardware, but it will require re-writing some code.

## Our approach

We're going to take the second approach, using Dask so we run our analysis on a small laptop without crashing. This makes it more accessible, to more people.

We use [skan](https://jni.github.io/skan/) as the backbone of our analysis pipeline. All the image pre-processing steps are be done with [dask-image](http://image.dask.org/en/latest/).

[skan](https://jni.github.io/skan/) is a library for skeleton image analysis. Given a skeleton image, it can describe statistics of the branches. To make it fast, the library is accelerated with [numba](https://numba.pydata.org/) (if you're curious, you can hear more about that in [this talk](https://www.youtube.com/watch?v=0pUPNMglnaE) and its [related notebook](https://github.com/jni/skan-talk-scipy-2019)).

## Results

The statistics from the blood vessel branches in the healthy and herniated lung shows clear differences between the two.

Most striking is the difference in the number of blood vessel branches.
The herniated lung has less than 40% of the number of blood vessel branches in the healthy lung.

There are also quantitative differences in the sizes of the blood vessels.
Here is a violin plot showing the distribution of the thickeness of blood vessel branches. We can see that there are more thick blood vessel branches in the healthy lung. This is consistent with what we might expect, since the healthy lung is more well developed than the lung from the hernia model.

![Violin plot comparing blood vessel thickness between a healthy and herniated lung](/images/skeleton-analysis/compare-euclidean-distance.png)

## Difficulties encountered

1. map_overlap and ragged shaped results

2. skan internals incompatible for distributed analysis


## How we solved them

We rely on one big assumption - once skeletonized, the reduced data will fit into memory. This holds true for datasets of this size (too big for)

slices_from_chunks_overlap

dask delayed

dummy Skeleton object instance, then overwriting

link to gist notebook
## Limitations

Our core assumption - - is a pretty big one.
compute is triggered at multiple points, rather than just once at the end

## What's next?

A good next step is modifing the [skan](https://github.com/jni/skan) library code so that it directly supports distributed skeleton analysis.

## How you can help

If you'd like to get involved, there are a couple of options:

1. Try a similar analysis on your own data. You can share or ask questions in the Dask slack or [on twitter](twitter.com/dask_dev).
2. Help add support for distributed skeleton analysis to skan. Head on over to the [skan issues page](https://github.com/jni/skan/issues/) and leave a comment if you'd like to join in.
