---
layout: post
title: Dask on HPC
tagline: what works well, and what needs work
author: Dharhas Pothina (Army ERDC), Guillaume Eynard-Bontemps (CNES), Kevin Paul (NCAR), Matthew Rocklin (NVIDIA), Willi Rath (GEOMAR)
tags: [Programming, Python, scipy, dask]
draft: true
theme: twitter
---
{% include JB/setup %}

We analyze large datasets on HPC systems with Dask, a library for scalability
that works well with the existing Python software ecosystem,
and works comfortably with native HPC hardware.

This article explains why this makes sense for us.
Our motivation is to share our experiences with our colleagues,
and to highlight opportunities for future work.

We'll start with seven reasons why we use Dask,
followed by seven common issues that affect us today.


## Reasons why we use Dask

### 1.  Ease of use

Dask extends libraries like Numpy, Pandas, and Scikit-learn, which are well
known APIs for scientists and engineers.  It also extends simpler APIs for
multi-node multiprocessing.  This makes it easy for our existing user base to
get up to speed.

By abstracting the parallelism away from the user/developer, our analysis tools
can be written by computer science non-experts, such as the scientists
themselves, meaning that our software engineers can take on a more supporting
role than a leadership role.


### 2.  Smooth HPC integration

With tools like [Dask Jobqueue](https://jobqueue.dask.org) and [Dask MPI](https://mpi.dask.org)
there is no need of any boilerplate bash code with `qsub/sbatch/...`.

Dask interacts natively with our existing job schedulers (SLURM/SGE/SGE/LSF/...)
so there is no additional system to set up and manage between users and IT.
All the infrastructure that we need is already in place.

Also, interactive analysis at scale and auto scaling is just awesome, and lets
us use our existing infrastructure in new ways and improves our occupancy
generally.


### 3.  Aimed for scientific processing

Dask is compatible with scientific data formats like HDF5, NetCDF, Parquet, and
so on.  This is because Dask works with other libraries within the Python
ecosystem, like XArray, which already has strong support for scientific data
formats and processing.


### 4.  Versatility of APIs

And yet Dask is not designed for any particular workflow, and instead can
provide infrastructure to cover a variety of different problems within an
institution.  Everything is possible.


### 5.  Versatility of Infrastructure

Dask is compatible with laptops, servers, HPC systems, and even cloud
computing if needed.  The environment can change with very little code
adaptation.

Dask is more than just a tool to us; it is a gateway to thinking about a
completely different way of providing computing infrastructure to our users.
Dask opens up the door to cloud computing technologies (such as elastic scaling
and object storage) and makes us rethink what an HPC center should really look
like!

### 6.  Cost and Collaboration

Dask is free and open source, which means we do not have to rebalance our
budget and staff to address the new immediate need of data analysis tools.
There are no licenses, and we have the ability to make changes when necessary.


# What needs work

### 1.  Heterogeneous resources handling

Often we want to include different kinds of HPC nodes in the same deployment.
This includes situations like the following:

-  Workers with low or high memory
-  Workers with GPUs
-  Workers from different node pools

Dask provides some support for this heterogeneity already, but not enough.
We see two major opportunities for improvement.

-  Tools like Dask-Jobqueue should make it easier to manage multiple worker
   pools within the same cluster.  Currently the deployment solution assumes
   homogeneity.
-  It should be easier for users to specify which parts of a computation
   require different hardware.  The solution today works, but requires more
   detail from the user than is ideal.


### 2.  Coarse-Grained Diagnostics

Dask provides a number of profiling tools that give you diagnostics at the
individual task-level, but there is no way today to analyze or profile your
Dask application at a coarse-grained level.  Having more tools to analyze bulk
performance would be helpful when making design decisions.


### 2.  Long-Term Diagnostics and History

Additionally, we would like to have better tracking for the cost of
computations long term for off-line and post-hoc performance analysis.


### 3.  Scheduler Performance on Large Graphs




### 4.  ~~Batch Launching~~

*This was resolved while we prepared this blogpost.  Hooray for open source.*


### 5.  More Data Formats


### 6.  Task and submission history


### 7.  Link with Deep Learning
