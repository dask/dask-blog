---
layout: post
title: Dask on HPC
tagline: what works well, and what needs work
author: Dharhas Pothina (Army ERDC), Guillaume Eynard-Bontemps (CNES), Kevin Paul (NCAR), Matthew Rocklin (NVIDIA), Willi Rath (GEOMAR), Joe Hamman (NCAR)
tags: [Programming, Python, scipy, dask]
theme: twitter
---

{% include JB/setup %}

We analyze large datasets on HPC systems with Dask, a parallel computing
library that integrates well with the existing Python software ecosystem, and
works comfortably with native HPC hardware.

This article explains why this approach makes sense for us.
Our motivation is to share our experiences with our colleagues,
and to highlight opportunities for future work.

We start with six reasons why we use Dask,
followed by seven issues that affect us today.

## Reasons why we use Dask

### 1. Ease of use

Dask extends libraries like Numpy, Pandas, and Scikit-learn, which are well-known APIs for scientists and engineers. It also extends simpler APIs for
multi-node multiprocessing. This makes it easy for our existing user base to
get up to speed.

By abstracting the parallelism away from the user/developer, our analysis tools can be written by computer science non-experts, such as the scientists
themselves, meaning that our software engineers can take on more of a supporting role than a leadership role.
Experience has shown that, with tools like Dask and Jupyter, scientists spend less time coding and more time thinking about science, as they should.

### 2. Smooth HPC integration

With tools like [Dask Jobqueue](https://jobqueue.dask.org) and [Dask MPI](https://mpi.dask.org) there is no need of any boilerplate shell scripting code commonly found with job queueing systems.

Dask interacts natively with our existing job schedulers (`SLURM`/`SGE`/`LSF`/`PBS`/...)
so there is no additional system to set up and manage between users and IT.
All the infrastructure that we need is already in place.

Interactive analysis at scale is powerful, and lets
us use our existing infrastructure in new ways.
Auto scaling improves our occupancy and helps with acceptance by HPC operators / owners.
Dask's resilience against the death of all or part of its workers offers new ways of leveraging job-preemption when co-locating classical HPC workloads with analytics jobs.

### 3. Aimed for Scientific Processing

In addition to being integrated with the Scipy and PyData software ecosystems,
Dask is compatible with scientific data formats like HDF5, NetCDF, Parquet, and
so on. This is because Dask works with other libraries within the Python
ecosystem, like Xarray, which already have strong support for scientific data
formats and processing, and with C/C++/Fortran codes, such as is common for Python libraries.

This native support is one of the major advantages that we've seen of Dask over Apache Spark.

### 4. Versatility of APIs

And yet Dask is not designed for any particular workflow, but instead can
provide infrastructure to cover a variety of different problems within an
institution. Many different kinds of workloads are possible:

- You can easily handle Numpy arrays or Pandas Dataframes at scale, doing some numerical work or data analysis/cleaning,
- You can handle any objects collection, like JSON files, text, or log files,
- You can express more arbitrary task or job scheduling workloads with Dask Delayed, or real time and reactive processing with Dask Futures.

Dask covers and simplifies many of the wide range of HPC workflows we've seen over the years. Many workflows that were previously implemented using job arrays, simplified MPI (e.g. mpi4py) or plain bash scripts seem to be easier for our users with Dask.

### 5. Versatility of Infrastructure

Dask is compatible with laptops, servers, HPC systems, and cloud computing. The environment can change with very little code adaptation which reduces our burden to rewrite code as we migrate analysis between systems such as from a laptop to a supercomputer, or between a supercomputer and the cloud.

```python
# Local machines
from dask.distributed import LocalCluster
cluster = LocalCluster()

# HPC Job Schedulers
from dask_jobqueue import SLURMCluster, PBSCluster, SGECluster, ...
cluster = SLURMCluster(queue='default', project='ABCD1234')

# Hadoop/Spark clusters
from dask_yarn import YARNCluster
cluster = YarnCluster(environment='environment.tar.gz', worker_vcores=2)

# Cloud/Kubernetes clusters
from dask_kubernetes import KubeCluster
cluster = KubeCluster(pod_spec={...})
```

Dask is more than just a tool to us; it is a gateway to thinking about a completely different way of providing computing infrastructure to our users. Dask opens up the door to cloud computing technologies (such as elastic scaling and object storage) and makes us rethink what an HPC center should really look like.

### 6. Cost and Collaboration

Dask is free and open source, which means we do not have to rebalance our budget and staff to address the new immediate need of data analysis tools.
We don't have to pay for licenses, and we have the ability to make changes to the code when necessary. The HPC community has good representation among Dask developers. It's easy for us to participate and our concerns are well understood.

<!-- WR: Mention quick response to new use cases / demands as another benefit of the collaborative
approach?  And hint towards dask-mpi here? -->

## What needs work

### 1. Heterogeneous resources handling

Often we want to include different kinds of HPC nodes in the same deployment.
This includes situations like the following:

- Workers with low or high memory,
- Workers with GPUs,
- Workers from different node pools.

Dask provides some support for this heterogeneity already, but not enough.
We see two major opportunities for improvement.

- Tools like Dask-Jobqueue should make it easier to manage multiple worker
  pools within the same cluster. Currently the deployment solution assumes
  homogeneity.
- It should be easier for users to specify which parts of a computation
  require different hardware. The solution today works, but requires more
  detail from the user than is ideal.

### 2. Coarse-Grained Diagnostics and History

Dask provides a number of profiling tools that deliver real-time diagnostics at the individual task-level, but there is no way today to analyze or profile your Dask application at a coarse-grained level, and no built-in way to track performance over long periods of time.

Having more tools to analyze bulk performance would be helpful when making design decisions and future architecture choices.

Having the ability to persist or store history of computations (`compute()` calls)
and tasks executed on a scheduler could be really helpful to track problems and potential performance improvements.

<!-- JJH: One tangible idea here would be a benchmarking suite that helps users make decisions about how to use dask most effectively.
 -->

### 3. Scheduler Performance on Large Graphs

HPC users want to analyze Petabyte datasets on clusters of thousands of large nodes.

While Dask can theoretically handle this scale, it does tend to slow down a bit,
reducing the pleasure of interactive large-scale computing. Handling millions of tasks can lead to tens of seconds latency before a computation actually starts. This is perfectly fine for our Dask batch jobs, but tends to make the interactive Jupyter users frustrated.

Much of this slowdown is due to task-graph construction time and centralized scheduling, both of which can be accelerated through a variety of means. We expect that, with some cleverness, we can increase the scale at which Dask continues to run smoothly by another order of magnitude.

### 4. ~~Launch Batch Jobs with MPI~~

_This issue was resolved while we prepared this blogpost._

Most Dask workflows today are interactive. People log into a Jupyter notebook, import Dask, and then Dask asks the job scheduler (like SLURM, PBS, ...) for resources dynamically. This is great because Dask is able to fit into small gaps in the schedule, release workers when they're not needed, giving users a pleasant interactive experience while lessening the load on the cluster.

However not all jobs are interactive. Often scientists want to submit a large job similar to how they submit MPI jobs. They submit a single job script with the necessary resources, walk away, and the resource manager runs that job when those resources become available (which may be many hours from now). While not as novel as the interactive workloads, these workloads are critical to common processes, and important to support.

This point was raised by Kevin Paul at NCAR during discussion of this blogpost. Between when we started planning and when we released this blogpost Kevin had already solved the problem by prodiving [dask-mpi](https://dask-mpi.readthedocs.org), a project that makes it easy to launch Dask using normal `mpirun` or `mpiexec` commands, making it easy to deploy Dask anywhere that MPI is deployable.

### 5. More Data Formats

Dask works well today with bread-and-butter scientific data formats like HDF5, Grib, and NetCDF, as well as common data science formats like CSV, JSON, Parquet, ORC, and so on.

However, the space of data formats is vast and Dask users find themselves struggling a little, or even solving the data ingestion problem manually for a number of common formats in different domains:

- Remote sensing datasets: GeoTIFF, Jpeg2000,
- Astronomical data: FITS, VOTable,
- ... and so on

Supporting these isn't hard (indeed many of us have built our own support for them in Dask), but it would be handy to have a high quality centralized solution.

### 6. Link with Deep Learning

Many of our institutions are excited to leverage recent advances in deep learning and integrate powerful tools like Keras, TensorFlow, and PyTorch and powerful hardware like GPUs into our workflows.

However, we often find that our data and architecture look a bit different from what we find in standard deep learning tutorials. We like using Dask for data ingestion, cleanup, and pre-processing, but would like to establish better practices and smooth tooling to transition from scientific workflows on HPC using Dask to deep learning as efficiently as possible.

_For more information, see [this github
issue](https://github.com/pangeo-data/pangeo/issues/567) for an example topic._

### 7. More calculation guidelines

While there are means to analyse and diagnose computations interactively, and
a quite decent set of examples for Dask common calculations, trials and error appear to be the norm with big HPC computation before coming to optimized workflows.

We should develop more guidelines and strategy on how to perform large scale computation, and we need to foster the community around Dask, which is already done in projects such as Pangeo. Note that these guidelines may be infrastructure dependent.
