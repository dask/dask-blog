---
layout: post
title: Skeleton analysis
author: Genevieve Buckley
tags: [imaging, life science]
theme: twitter
---
{% include JB/setup %}

## Executive Summary

In this blogpost, we show how to modify an skeleton network analysis with Dask to work with constrained RAM (eg: on your laptop).This makes it more accessible: it can run on a small laptop, instead of requiring access to a supercomputing cluster.

## Contents



Lots of biological structures have a skeleton or network-like shape. We see these in all kinds of places, including:
* blood vessel branching
* the branching of airways
* neuron networks in the brain
* the root structure of plants
* the capillaries in leaves
* ... and many more

Analysing the structure of these skeletons can give us important information about the biology of that system.

For this bogpost, we will look at the blood vessels inside of a lung. This data was shared with us by [Marcus Kitchen](https://research.monash.edu/en/persons/marcus-kitchen), [Andrew Stainsby](https://hudson.org.au/researcher-profile/andrew-stainsby/), and their team of collaborators.


![Skeleton network of blood vessels within the lung](/images/skeleton-analysis/skeleton-screenshot-crop.jpg)


- the problem

the computation problem

The science problem
healthy
brohchopulmonary dysplasia
hernia model


- the plan

We'll use [skan]() as the backbone of our analysis pipeline.

- skan
skan talk: https://www.youtube.com/watch?v=0pUPNMglnaE
skan talk docs: https://github.com/jni/skan-talk-scipy-2019

- Results

![Violin plot comparing blood vessel thickness between a healthy and herniated lung](/images/skeleton-analysis/compare-euclidean-distance.png)

![Violin plot comparing blood vessel branch lengths between a healthy and herniated lung](/images/skeleton-analysis/compare-branch-distance.png)


- Problems we faced

- How we solved them


- Limitations

- What's next?


- How you can help




