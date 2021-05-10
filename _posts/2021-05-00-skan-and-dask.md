---
layout: post
title: How to modify a python library to suppport Dask (skan, a case study)
author: Genevieve Buckley, Juan Nunez-Iglesias
tags: [imaging, life science, skan, skeleton analysis]
theme: twitter
---
{% include JB/setup %}

## Executive Summary

In this blogpost, we show how you can modify a third party library to add support for Dask. We present a case study using [skan](https://jni.github.io/skan/), a python library written by [Juan Nunez-Iglesias](https://github.com/jni/).

## Contents
* [Background](#background)
* [How we did it](#what-we-did)
   * [Problem 1](#problem-1)
   * [Problem 2](#problem-2)
   * [Problem 3](#problem-3)
* [Conclusion](#conclusion)


## Background

link to other skeleton analysis blogpost
link to gist for skeleton analysis prototype

A small bit about the skan library
skan Github repository link: https://github.com/jni/skan
Link to Juan's github page: [Juan Nunez-Iglesias](https://github.com/jni/)

## How we did it

This is the basic approach we used:
1. First, find out where stuff breaks.
2. Second, restructure those pain points to be compatible with Dask.

I understand that this very high level description sounds a lot like drawing the rest of the owl.

![Meme: Draw the rest of the owl](/images/owl-meme-bleeped.jpg)


So that we can talk about things in more concrete terms, we're going to look at a particular case study: adding Dask support to the [skan](https://jni.github.io/skan/) library.

## Skeleton analysis

In order to understand some of the technical details, you'll need to know a bit about skeleton analysis.

scikit-image [skeletonize]()

Add pictures with skan's testdata skeleton1
- boolean skeleton
- skelint - integer labelled pixels
- degree_image - labelled skeleton

Explain what a skeleton graph is
- add a picture of the skeleton graph for skan._testdata.skeleton1

### Problem 1

**Summary of the first problem**

Allowing skelint to be passed in to
How we fixed it. Links to PRs, if that's useful.

### Problem 2

**Summary of the second problem**

Separating the construction of the sparse ekeleton graph, from the calculation of its data points.
How we fixed it. Links to PRs, if that's useful.


### Problem 3

**Summary of the thrid problem**

Avoiding the problem of Skeleton object instances automatically computing things we don't want in the __init__
How we fixed it. Links to PRs, if that's useful.

### Problem 4

**Summary of the thrid problem**

numpy.argsort triggers dask computation.

## Conclusion

