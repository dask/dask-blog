---
layout: post
title: Dask-jobqueue
author: Joe Hamman
tagline: Easily deploy Dask on job queuing systems like PBS, Slurm, MOAB, SGE, and LSF.
tags: [HPC, distributed, jobqueue]
theme: twitter
---

{% include JB/setup %}

_This work was done in collaboration with [Matthew Rocklin](https://github.com/mrocklin) (Anaconda), Jim Edwards (NCAR), [Guillaume Eynard-Bontemps](https://github.com/guillaumeeb) (CNES), and [Loïc Estève](https://github.com/lesteve) (INRIA), and is supported, in part, by the US National Science Foundation [Earth Cube program](https://www.earthcube.org/). The dask-jobqueue package is a spinoff of the [Pangeo Project](https://medium.com/pangeo). This blogpost was previously published [here](https://medium.com/pangeo/dask-jobqueue-d7754e42ca53)_

**TLDR;** _Dask-jobqueue_ allows you to seamlessly deploy [dask](https://dask.org/) on HPC clusters that use a variety of job queuing systems such as PBS, Slurm, SGE, or LSF. Dask-jobqueue provides a _Pythonic_ user interface that manages dask workers/clusters through the submission, execution, and deletion of individual jobs on a HPC system. It gives users the ability to interactively scale workloads across large HPC systems; turning an interactive [Jupyter](http://jupyter.org/) Notebook into a powerful tool for scalable computation on very large datasets.

Install with:

```bash
conda install -c conda-forge dask-jobqueue
```

or

```bash
pip install dask-jobqueue
```

And checkout the dask-jobqueue documentation: [http://jobqueue.dask.org](http://jobqueue.dask.org)

## Introduction

Large high-performance computer (HPC) clusters are ubiquitous throughout the computational sciences. These HPC systems include powerful hardware, including many large compute nodes, high-speed interconnects, and parallel file systems. An example of such systems that we use at [NCAR](https://ncar.ucar.edu/) is named [Cheyenne](https://www2.cisl.ucar.edu/resources/computational-systems/cheyenne). Cheyenne is a fairly large machine, with about 150k cores and over 300 TB of total memory.

![Cheyenne is a 5.34-petaflops, high-performance computer operated by NCAR.](https://cdn-images-1.medium.com/max/2000/1*Jqm612rTcdWFkmcZWhcrTw.jpeg)_Cheyenne is a 5.34-petaflops, high-performance computer operated by NCAR._

These systems frequently use a job queueing system, such as PBS, Slurm, or SGE, to manage the queueing and execution of many concurrent jobs from numerous users. A “job” is a single execution of a program that is to be run on some set of resources on the user’s HPC system. These jobs are often submitted via the command line:

```bash
qsub do_thing_a.sh
```

Where do_thing_a.sh is a shell script that might look something like this:

```bash
#!/bin/bash
#PBS -N thing_a
#PBS -q premium
#PBS -A 123456789
#PBS -l select=1:ncpus=36:mem=109G

echo “doing thing A”
```

In this example “-N” specifies the name of this job, “-q” specifies the queue where the job should be run, “-A” specifies a project code to bill for the CPU time used while the job is run, and “-l” specifies the hardware specifications for this job. Each job queueing system has slightly different syntax for configuring and submitting these jobs.

This interface has led to the development of a few common workflow patterns:

1. _MPI if you want to scale_. MPI stands for the Message Passing Interface. It is a widely adopted interface allowing parallel computation across traditional HPC clusters. Many large computational models are written in languages like C and Fortran and use MPI to manage their parallel execution. For the old-timers out there, this is the go-to solution when it comes time to scale complex computations.

1. _Batch it_. It is quite common for scientific processing pipelines to include a few steps that can be easily parallelized by submitting multiple jobs in parallel. Maybe you want to “do_thing_a.sh” 500 times with slightly different inputs — easy, just submit all the jobs separately (or in what some queueing systems refer to as “array-job”).

1. _Serial is still okay_. Computers are pretty fast these days, right? Maybe you don’t need to parallelize your programing at all. Okay, so keep it serial and get some coffee while your job is running.

## The Problem

None of the workflow patterns listed above allow for interactive analysis on very large data analysis. When I’m prototyping new processing method, I often want to work interactively, say in a Jupyter Notebook. Writing MPI code on the fly is hard and expensive, batch jobs are inherently not interactive, and serial just won’t do when I start working on many TBs of data. Our experience is that these workflows tend to be fairly inelegant and difficult to transfer between applications, yielding lots of duplicated effort along the way.

One of the aims of the Pangeo project is to facilitate interactive data on very large datasets. Pangeo leverages Jupyter and dask, along with a number of more domain specific packages like [xarray](http://xarray.pydata.org) to make this possible. The problem is we didn’t have a particularly palatable method for deploying dask on our HPC clusters.

## The System

- _Jupyter Notebooks_ are web applications that support interactive code execution, display of figures and animations, and in-line explanatory text and equations. They are quickly becoming the standard open-source format for interactive computing in Python.

- _Dask_ is a library for parallel computing that coordinates well with Python’s existing scientific software ecosystem, including libraries like [NumPy](http://www.numpy.org/), [Pandas](https://pandas.pydata.org/), [Scikit-Learn](http://scikit-learn.org/stable/), and xarray. In many cases, it offers users the ability to take existing workflows and quickly scale them to much larger applications. [\*Dask-distributed](http://distributed.dask.org)\* is an extension of dask that facilitates parallel execution across many computers.

- _Dask-jobqueue_ is a new Python package that we’ve built to facilitate the deployment of _dask_ on HPC clusters and interfacing with a number of job queuing systems. Its usage is concise and Pythonic.

```python
from dask_jobqueue import PBSCluster
from dask.distributed import Client

cluster = PBSCluster(cores=36,
                     memory="108GB",
                     queue="premium")
cluster.scale(10)
client = Client(cluster)
```

### What’s happening under the hood?

1. In the call to PBSCluster() we are telling dask-jobqueue how we want to configure each job. In this case, we set each job to have 1 _Worker_, each using 36 cores (threads) and 108 GB of memory. We also tell the PBS queueing system we’d like to submit this job to the “premium” queue. This step also starts a Scheduler to manage workers that we’ll add later.

2. It is not until we call the cluster.scale() method that we interact with the PBS system. Here we start 10 workers, or equivalently 10 PBS jobs. For each job, dask-jobqueue creates a shell command similar to the one above (except dask-worker is called instead of echo) and submits the job via a subprocess call.

3. Finally, we connect to the cluster by instantiating the Client class. From here, the rest of our code looks just as it would if we were using one of [dask’s local schedulers](http://docs.dask.org/en/stable/scheduler-overview.html).

Dask-jobqueue is easily customizable to help users capitalize on advanced HPC features. A more complicated example that would work on NCAR’s Cheyenne super computer is:

```python
cluster = PBSCluster(cores=36,
                    processes=18,
                    memory="108GB",
                    project='P48500028',
                    queue='premium',
                    resource_spec='select=1:ncpus=36:mem=109G',
                    walltime='02:00:00',
                    interface='ib0',
                    local_directory='$TMPDIR')
```

In this example, we instruct the PBSCluster to 1) use up to 36 cores per job, 2) use 18 worker processes per job, 3) use the large memory nodes with 109 GB each, 4) use a longer walltime than is standard, 5) use the [InfiniBand](https://en.wikipedia.org/wiki/InfiniBand) network interface (ib0), and 6) use the fast SSD disks as its local directory space.

Finally, Dask offers the ability to “autoscale” clusters based on a set of heuristics. When the cluster needs more CPU or memory, it will scale up. When the cluster has unused resources, it will scale down. Dask-jobqueue supports this with a simple interface:

```python
cluster.adapt(minimum=18, maximum=360)
```

In this example, we tell our cluster to autoscale between 18 and 360 workers (or 1 and 20 jobs).

## Demonstration

We have put together a fairly comprehensive screen cast that walks users through all the steps of setting up Jupyter and Dask (and dask-jobqueue) on an HPC cluster:

<center><iframe width="560" height="315" src="https://www.youtube.com/embed/FXsgmwpRExM" frameborder="0" allowfullscreen></iframe></center>

## Conclusions

Dask jobqueue makes it much easier to deploy Dask on HPC clusters. The package provides a Pythonic interface to common job-queueing systems. It is also easily customizable.

The autoscaling functionality allows for a fundamentally different way to do science on HPC clusters. Start your Jupyter Notebook, instantiate your dask cluster, and then do science — let dask determine when to scale up and down depending on the computational demand. We think this bursting approach to interactive parallel computing offers many benefits.

Finally, in developing dask-jobqueue, we’ve run into a few challenges that are worth mentioning.

- Queueing systems are highly customizable. System administrators seem to have a lot of control over their particularly implementation of each queueing system. In practice, this means that it is often difficult to simultaneously cover all permutations of a particular queueing system. We’ve generally found that things seem to be flexible enough and welcome feedback in the cases where they are not.

- CI testing has required a fair bit of work to setup. The target environment for using dask-jobqueue is on existing HPC clusters. In order to facilitate continuous integration testing of dask-jobqueue, we’ve had to configure multiple queueing systems (PBS, Slurm, SGE) to run in docker using Travis CI. This has been a laborious task and one we’re still working on.

- We’ve built dask-jobqueue to operate in the dask-deploy framework. If you are familiar with [dask-kubernetes](http://kubernetes.dask.org) or [dask-yarn](http://yarn.dask.org), you’ll recognize the basic syntax in dask-jobqueue as well. The coincident development of these dask deployment packages has recently brought up some important coordination discussions (e.g. [https://github.com/dask/distributed/issues/2235](https://github.com/dask/distributed/issues/2235)).
