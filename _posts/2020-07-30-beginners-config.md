---
layout: post
title: Configuring a Distributed Dask Cluster
tagline: a Beginner’s Guide
author: Laura Lorenz (Prefect), Julia Signell (Saturn Cloud)
tags: [distributed, config]
theme: twitter
---

{% include JB/setup %}

_Configuring a Dask cluster can seem daunting at first, but the good news is that the Dask project has a lot of built in heuristics that try its best to anticipate and adapt to your workload based on the machine it is deployed on and the work it receives. Possibly for a long time you can get away with not configuring anything special at all. That being said, if you are looking for some tips to move on from using Dask locally, or have a Dask cluster that you are ready to optimize with some more in-depth configuration, these tips and tricks will help guide you and link you to the best Dask docs on the topic!_

## How to host a distributed Dask cluster

The biggest jump for me was from running a local version of Dask for just an hour or so at a time during development, to standing up a production-ready version of Dask. Broadly there are two styles:

1. a static dask cluster -- one that is always on, always awake, always ready to accept work
2. an ephemeral dask cluster -- one that is spun up or down easily with a Python API, and, when on, starts a minimal dask master node that itself only spins up dask workers when work is actually submitted

Though those are the two broad main categories, there are tons of choices of how to actually achieve that. It depends on a number of factors including what cloud provider products you want to use and if those resources are pre-provisioned for you and whether you want to use a python API or a different deployment tool to actually start the Dask processes. A very exhaustive list of all the different ways you could provision a dask cluster is in the dask docs under [Setup](https://docs.dask.org/en/latest/setup.html). As just a taste of what is described in those docs, you could:

- Install and start up the dask processes [manually from the CLI](https://docs.dask.org/en/latest/setup/cli.html) on cloud instances you provision, such as AWS EC2 or GCP GCE
- Use popular deployment interfaces such as [helm for kubernetes](https://docs.dask.org/en/latest/setup/kubernetes-helm.html) to deploy dask in cloud container clusters you provision, such as AWS Fargate or GCP GKE
- Use ‘native’ deployment python APIs, provided by the dask developers, to create (and interactively configure) dask on deployment infrastructure they support, either through the general-purpose [Dask Gateway](https://gateway.dask.org/) which supports multiple backends, or directly against cluster managers such as kubernetes with [dask-kubernetes](https://kubernetes.dask.org/en/latest/) or YARN with [dask-yarn](https://yarn.dask.org/en/latest/), as long as you’ve already provisioned the kubernetes cluster or hadoop cluster already
- Use a nearly full-service deployment python API called [Dask Cloud Provider](https://cloudprovider.dask.org/en/latest/), that will go one step farther and provision the cluster for you too, as long as you give it AWS credentials (and as of time of writing, it only supports AWS)

As you can see, there are a ton of options. On top of all of those, you might contract a managed service provider to provision and configure your dask cluster for you according to your specs, such as [Saturn Cloud](https://www.saturncloud.io) (_Disclaimer: one of the authors (Julia Signell) works for Saturn Cloud_).

Whatever you choose, the whole point is to unlock the power of parallelism in Python that Dask provides, in as scalable a manner as possible which is what getting it running on distributed infrastructure is all about. Once you know where and with what API you are going to deploy your dask cluster, the real configuration process for your Dask cluster and its workload begins.

## How to choose instance type for your cluster

When you are ready to set up your dask cluster for production, you will need to make some decisions about the infrastructure your scheduler and your workers will be running on, especially if you are using one of the options from [How to host a distributed dask cluster](#how-to-host-a-distributed-dask-cluster) that requires pre-provisioned infrastructure. Whether your infrastructure is on-prem or in the cloud, the classic decision points need to be made:

- Memory requirements
- CPU requirements
- Storage requirements

If you have tested your workload locally, a simple heuristic is to multiply the CPU, storage, and memory usage of your work by some multiplier that is related to how scaled down your local experiments are from your expected production usage. For example, if you test your workload locally with a 10% sample of data, multiplying any observed resource usage by at least 10 may get you close to your minimum instance size. Though in reality Dask's many underlying optimizations means that it shouldn't regularly require linear growth of resources to work on more data, this simple heuristic may give you a starting point as a good first pass technique.

In the same vein, choosing the smallest instance and running with a predetermined subset of data and scaling up until it runs effectively gives you a hint towards the minimum instance size. If your local environment is too underpowered to run your flows locally with 10%+ of your source data, if it is a highly divergent environment (for example a different OS, or with many competing applications running in the background), or if it is difficult or annoying to monitor CPU, memory, and storage of your flow’s execution using your local machine, isolating the test case on the smallest workable node is a better option.

On the flip side, choosing the biggest instance you can afford and observing the discrepancy between max CPU/memory/storage metrics and scaling back based on the ratio of unused resources can be a quicker way to find your ideal size.

Wherever you land on node size might be heavily influenced by what you want to pay for, but as long as your node size is big enough that you are avoiding strict out of memory errors, the flip side of what you pay for with nodes closest to your minimum run specs is time. Since the point of your Dask cluster is to run distributed, parallel computations, you can get significant time savings if you scale up your instance to allow for more parallelism. If you have long running models that take hours to train that you can reduce to minutes, and get back some of your time or your employee’s time to see the feedback loop quickly, then scaling up over your minimum specs is worth it.

Should your scheduler node and worker nodes be the same size? It may certainly be tempting to provision them at separate instance sizes to optimize resources. It’s worth a quick dive into the general resource requirements of each to get a good sense.

For the scheduler, a serialized version of each task is submitted to it is held in memory for as long as it needs to determine which worker should take the work. This is not necessarily the same amount of memory needed to actually execute the task, but skimping too much on memory here may prevent work from being scheduled. From a CPU perspective, the needs of the scheduler are likely much lower than your workers, but starving the scheduler of CPU will cause deadlock, and when the scheduler is stuck or dies your workers also cannot get any work. Storage wise, the Dask scheduler does not persist much to disk, even temporarily, so it’s storage needs are quite low.

For the workers, the specific resource needs of your task code may overtake any generalizations we can make. If nothing else, they need enough memory and CPU to deserialize each task payload, and serialize it up again to return as a Future to the Dask scheduler. Dask workers may persist the results of computations in memory, including distributed across the memory of the cluster, which you can read more about [here](https://distributed.dask.org/en/latest/memory.html). Regarding storage needs, fundamentally tasks submitted to Dask workers should not write to local storage - the scheduler does not guarantee work will be run on a given worker - so the storage costs should be directly related to the installation footprint of your worker’s dependencies and any ephemeral storage of the dask workers. Temporary files the workers create may include spilling in-memory data to local disk if they run out of memory as long as [that behavior isn't disabled](https://docs.dask.org/en/latest/configuration-reference.html#distributed.worker.memory.spill), which means that reducing memory can have an effect on your ephemeral storage needs.

Generally we would recommend simplifying your life and keeping your scheduler and worker nodes the same node size, but if you wanted to optimize them, use the above CPU, memory and storage patterns to give you a starting point for configuring them separately.

## How to choose number of workers

Every dask cluster has one scheduler and any number of workers. The scheduler keeps track of what work needs to be done and what has already been completed. The workers do work, share results between themselves and report back to the scheduler. More background on what this entails is available in the [dask.distributed documentation](https://distributed.dask.org/en/latest/worker.html).

When setting up a dask cluster you have to decide how many workers to use. It can be tempting to use many workers, but that isn’t always a good idea. If you use too many workers some may not have enough to do and spend much of their time idle. Even if they have enough to do, they might need to share data with each other which can be slow. Additionally if your machine has finite resources (rather than one node per worker), then each worker will be weaker - they might run out of memory, or take a long time to finish a task.

On the other hand if you use too few workers you don’t get to take full advantage of the parallelism of dask and your work might take longer to complete overall.

Before you decide how many workers to use, try using the default. In many cases dask can choose a default that makes use of the size and shape of your machine. If that doesn’t work, then you’ll need some information about the size and shape of your work. In particular you’ll want to know:

1. What size is your computer or what types of compute nodes do you have access to?
2. How big is your data?
3. What is the structure of the computation that you are trying to do?

If you are working on your local machine, then the size of the computer is fixed and knowable. If you are working on HPC or cloud instances then you can choose the resources allotted to each worker. You make the decision about the size of your cluster based on factors we discussed in [How to choose instance type for your cluster](#how-to-choose-instance-type-for-your-cluster).

Dask is often used in situations where the data are too big to fit in memory. In these cases the data are split into chunks or partitions. Each task is computed on the chunk and then the results are aggregated. You will learn about how to change the shape of your data [below](#how-to-host-a-distributed-dask-cluster).

The structure of the computation might be the hardest to reason about. If possible, it can be helpful to try out the computation on a very small subset of the data. You can see the task graph for a particular computation by calling `.visualize()`. If the graph is too large to comfortably view inline, then take a look at the [Dask dashboard](https://docs.dask.org/en/latest/diagnostics-distributed.html) graph tab. This shows the task graph as it runs and lights up each section. To make dask most efficient, you want a task graph that isn’t too big or too interconnected. The [dask docs](https://docs.dask.org/en/latest/best-practices.html#avoid-very-large-graphs) discuss several techniques for optimizing your task graph.

To pick the number of workers to use, think about how many concurrent tasks are happening at any given part of the graph. If each task contains a non-trivial amount of work, then the fastest way to run dask is to have a worker for each concurrent task. For chunked data, if each worker is able to comfortably hold one data chunk in memory and do some computation on that data, then the number of chunks should be a multiple of the number of workers. This ensures that there is always enough work for a worker to do.

If you have a highly variable number of tasks, then you can also consider using an adaptive cluster. In an adaptive cluster, you set the minimum and maximum number of workers and let the cluster add and remove workers as needed. When the scheduler determines that some workers aren’t needed anymore it asks the cluster to shut them down, and when more are needed, the scheduler asks the cluster to spin more up. This can work nicely for task graphs that start out with few input tasks then have more tasks in the middle, and then some aggregation or reductions at the end.

Once you have started up your cluster with some workers, you can monitor their progress in the [dask dashboard](https://docs.dask.org/en/latest/diagnostics-distributed.html). There you can check on their memory consumption, watch their progress through the task graph, and access worker-level logs. Watching your computation in this way, provides insight into potential speedups and builds intuition about the number of workers to use in the future.

The tricky bit about choosing the number of workers to use is that in practice the size and shape of your machine, data, and task graph can change. Figuring out how many workers to use can end up feeling like an endless fiddling of knobs. If this is starting to drive you crazy then remember that you can always change the number or workers, even while the cluster is running.

## How to choose nthreads to utilize multithreading

When starting dask workers themselves, there are two very important configuration options to play against each other: how many workers and how many threads per worker. You can actually manipulate both on the same worker process with flags, such as in the form `dask-worker --nprocs 2 --nthreads 2`, though `--nprocs` simply spins up another worker in the background so it is cleaner configuration to avoid setting `--nprocs` and instead manipulate that configuration with whatever you use to specify total number of workers. We already talked about [how to choose number of workers](#how-to-host-a-distributed-dask-cluster), but you may modify your decision about that if you change a workers’ `--nthreads` to increase the amount of work an individual worker can do.

When deciding the best number of `nthreads` for your workers, it all boils down to the type of work you expect those workers to do. The fundamental principle is that multiple threads are best to share data between tasks, but worse if running code that doesn’t release Python’s GIL (“Global Interpreter Lock”). Increasing the `nthreads` for work that does not release the Python’s GIL has no effect; the worker cannot use threading to optimize the speed of computation if the GIL is locked. This is a possible point of confusion for new Dask users who want to increase their parallelism, but don’t see any gains from increasing the threading limit of their workers.

As discussed in [the Dask docs on workers](<[https://distributed.dask.org/en/latest/worker.html](https://distributed.dask.org/en/latest/worker.html)>), there are some rules of thumb when to worry about GIL lockages, and thus prefer more workers over heavier individual workers with high `nthreads`:

- If your code is mostly pure Python (in non-optimized Python libraries) on non-numerical data
- If your code causes computations external to Python that are long running and don’t release the GIL explicitly

Conveniently, a lot of dask users are running exclusively numerical computations using Python libraries optimized for multithreading, namely NumPy, Pandas, SciPy, etc in the PyData stack. If you do mostly numerical computations using those or similarly optimized libraries, you should emphasize a higher thread count. If you truly are doing mostly numerical computations, you can specify as many total threads as you have cores; if you are doing any work that would cause a thread to pause, for example any I/O (to write results to disk, perhaps), you can specify _more_ threads than you have cores, since some will be occasionally sitting idle. The ideal number regarding how many more threads than cores to set in that situation is complex to estimate and dependent on your workload, but taking some advice from [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor), 5 times the processors on your machine is a historical upper bound to limit your total thread count to for heavily I/O dependent workloads.

## How to chunk arrays and partition DataFrames

There are many different methods of triggering work in dask. For instance: you can wrap functions with delayed or submit work directly to the client (for a comparison of the options see [User Interfaces](https://docs.dask.org/en/latest/user-interfaces.html)). If you are loading structured data into dask objects, then you are likely using [dask.array](https://docs.dask.org/en/latest/array.html) or [dask.dataframe](https://docs.dask.org/en/latest/dataframe.html). These modules mimic numpy and pandas respectively - making it easier to interact with large arrays and large tabular datasets.

When using dask.dataframe and dask.array, computations are divided among workers by splitting the data into pieces. In dask.dataframe these pieces are called [partitions](https://docs.dask.org/en/latest/dataframe-design.html#partitions) and in dask.array they are called [chunks](https://docs.dask.org/en/latest/array-chunks.html), but the principle is the same. In the case of dask.array each chunk holds a numpy array and in the case of dask.dataframe each partition holds a pandas dataframe. Either way, each one contains a small part of the data, but is representative of the whole and must be small enough to comfortably fit in worker memory.

Often when loading in data, the partitions/chunks will be determined automatically. For instance, when reading from a directory containing many csv files, each file will become a partition. If your data are not split up by default, then it can be done manually using df.set_index or array.rechunk. If they are split up by default and you want to change the shape of the chunks, the file-level chunks should be a multiple of the dask level chunks (read more about this [here](https://docs.dask.org/en/latest/array-best-practices.html#orient-your-chunks)).

As the user, you know how the data are going to be used, so you can often partition it in ways that lead to more efficient computations. For instance if you are going to be aggregating to a monthly step, it can make sense to chunk along the time axis. If instead you are going to be looking at a particular feature at different altitudes, it might make sense to chunk along the altitude. More tips for chunking dask.arrays are described in [Best Practices](https://docs.dask.org/en/latest/array-best-practices.html). Another scenario in which it might be helpful to repartition is if you have filtered the data down to a subset of the original. In that case your partitions will likely be too small. See the dask.dataframe [Best Practices](https://docs.dask.org/en/latest/dataframe-best-practices.html#repartition-to-reduce-overhead) for more details on how to handle that case.

When choosing the size of chunks it is best to make them neither too small, nor too big (around 100MB is often reasonable). Each chunk needs to be able to fit into the worker memory and operations on that chunk should take some non-trivial amount of time (more than 100ms). For many more recommendations take a look at the docs on [chunks](https://docs.dask.org/en/latest/array-chunks.html) and on [partitions](https://docs.dask.org/en/latest/dataframe-design.html#partitions).

---

_We hope this helps you make decisions about whether to configure your Dask deployment differently and give you the confidence to try it out. We found all of this great information in the Dask docs, so if you are feeling inspired please follow the links we’ve sprinkled throughout and learn even more about Dask!_
