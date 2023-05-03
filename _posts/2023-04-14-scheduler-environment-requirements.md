---
layout: post
title: Do you need consistent environments between the client, scheduler and workers?
author: Jacob Tomlinson, Rick Zamora, Florian Jetter
tags: [dataframe, IO]
theme: twitter
---

{% include JB/setup %}

_Update May 3rd 2023: [Clarify GPU recommendations](https://github.com/dask/dask-blog/pull/166)._

With the release `2023.4.0` of dask and distributed we are making a change which may require the Dask scheduler to have consistent software and hardware capabilities as the client and workers.

It has always been recommended that your client and workers have a consistent software and hardware environment so that data structures and dependencies can be pickled and passed between them. However recent changes to the Dask scheduler mean that we now also require your scheduler to have the same consistent environment as everything else.

## What does this mean for me?

For most users, this change should go unnoticed as it is common to run all Dask components in the same conda environment or docker image and typically on homogenous machines.

However, for folks who may have optimized their schedulers to use cut-down environments, or for users with specialized hardware such as GPUs available on their client/workers but not the scheduler there may be some impact.

## What will the impact be?

If you run into errors such as `"RuntimeError: Error during deserialization of the task graph. This frequently occurs if the Scheduler and Client have different environments."` please ensure your software environment is consistent between your client, scheduler and workers.

If you are passing GPU objects between the client and workers we now recommend that your scheduler has a GPU too. This recommendation is just so that GPU-backed objects contained in Dask graphs can be deserialized on the scheduler if necessary. Typically the GPU available to the scheduler doesn't need to be as powerful as long as it has [similar CUDA compute capabilities](https://en.wikipedia.org/wiki/CUDA#GPUs_supported). For example for cost optimization reasons you may want to use A100s on your client and workers and a T4 on your scheduler.

Users who do not have a GPU on the client and are leveraging GPU workers shouldn't run into this as the GPU objects will only exist on the workers.

## Why are we doing this?

The reason we now suggest that you have the same hardware/software capabilities on the scheduler is that we are giving the scheduler the ability to deserialize graphs before distributing them to the workers. This will allow the scheduler to make smarter scheduling decisions in the future by having a better understanding of the operation it is performing.

The downside to this is that graphs can contain complex Python objects created by any number of dependencies on the client side, so in order for the scheduler to deserialize them it needs to have the same libraries installed. Equally, if the client-side packages create GPU objects then the scheduler will also need one.

We are sure you'll agree that this breakage for a small percentage of users will be worth it for the long-term improvements to Dask.
