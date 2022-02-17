---
layout: post
title: Dask Deployment Updates
tags: []
theme: twitter
---

{% include JB/setup %}

## Summary

Over the last six months many Dask developers have worked on making Dask easier
to deploy in a wide variety of situations. This post summarizes those
efforts, and provides links to ongoing work.

## What we mean by Deployment

In order to run Dask on a cluster, you need to setup a scheduler on one
machine:

```console
$ dask-scheduler
Scheduler running at tcp://192.168.0.1
```

And start Dask workers on many other machines

```console
$ dask-worker tcp://192.168.0.1
Waiting to connect to:       tcp://scheduler:8786

$ dask-worker tcp://192.168.0.1
Waiting to connect to:       tcp://scheduler:8786

$ dask-worker tcp://192.168.0.1
Waiting to connect to:       tcp://scheduler:8786

$ dask-worker tcp://192.168.0.1
Waiting to connect to:       tcp://scheduler:8786
```

For informal clusters people might do this manually, by logging into each
machine and running these commands themselves. However it's much more common
to use a cluster resource manager such as Kubernetes, Yarn (Hadoop/Spark),
HPC batch schedulers (SGE, PBS, SLURM, LSF ...), some cloud service or some custom system.

As Dask is used by more institutions and used more broadly within those
institutions, making deployment smooth and natural becomes increasingly
important. This is so important in fact, that there have been seven separate
efforts to improve deployment in some regard or another by a few different
groups.

We'll briefly summarize and link to this work below, and then we'll finish up
by talking about some internal design that helped to make this work more
consistent.

## Dask-SSH

According to our user survey, the most common deployment mechanism was still
SSH. Dask has had a [command line dask-ssh
tool](https://docs.dask.org/en/latest/setup/ssh.html#command-line) to make it
easier to deploy with SSH for some time. We recently updated this to also
include a Python interface, which provides more control.

```python
>>> from dask.distributed import Client, SSHCluster
>>> cluster = SSHCluster(
...     ["host1", "host2", "host3", "host4"],
...     connect_options={"known_hosts": None},
...     worker_options={"nthreads": 2},
...     scheduler_options={"port": 0, "dashboard_address": ":8797"}
... )
>>> client = Client(cluster)
```

This isn't what we recommend for large institutions, but it can be helpful for
more informal groups who are just getting started.

## Dask-Jobqueue and Dask-Kubernetes Rewrite

We've rewritten Dask-Jobqueue for SLURM/PBS/LSF/SGE cluster managers typically
found in HPC centers and Dask-Kubernetes. These now share a common codebase
along with Dask SSH, and so are much more consistent and hopefully bug free.

Ideally users shouldn't notice much difference with existing workloads,
but new features like asynchronous operation, integration with the Dask
JupyterLab extension, and so on are more consistently available. Also, we've
been able to unify development and reduce our maintenance burden considerably.

The new version of Dask Jobqueue where these changes take place is 0.7.0, and
the work was done in [dask/dask-jobqueue #307](https://github.com/dask/dask-jobqueue/pull/307).
The new version of Dask Kubernetes is 0.10.0 and the work was done in
[dask/dask-kubernetes #162](https://github.com/dask/dask-kubernetes/pull/162).

## Dask-CloudProvider

For cloud deployments we generally recommend using a hosted Kubernetes or Yarn
service, and then using Dask-Kubernetes or Dask-Yarn on top of these.

However, some institutions have made decisions or commitments to use
certain vendor specific technologies, and it's more convenient to use APIs that
are more native to the particular cloud. The new package [Dask
Cloudprovider](https://cloudprovider.dask.org) handles this today for Amazon's
ECS API, which has been around for a long while and is more universally
accepted.

```python
from dask_cloudprovider import ECSCluster
cluster = ECSCluster(cluster_arn="arn:aws:ecs:<region>:<acctid>:cluster/<clustername>")

from dask_cloudprovider import FargateCluster
cluster = FargateCluster()
```

## Dask-Gateway

In some cases users may not have access to the cluster manager. For example
the institution may not give all of their data science users access to the Yarn
or Kubernetes cluster. In this case the [Dask-Gateway](https://gateway.dask.org)
project may be useful.
It can launch and manage Dask jobs,
and provide a proxy connection to these jobs if necessary.
It is typically deployed with elevated permissions but managed directly by IT,
giving them a point of greater control.

<img src="https://gateway.dask.org/_images/architecture.svg" width="50%">

## GPUs and Dask-CUDA

While using Dask with multi-GPU deployments the [NVIDIA
RAPIDS](https://rapids.ai) has needed the ability to specify increasingly
complex setups of Dask workers. They recommend the following deployment
strategy:

1. One Dask-worker per GPU on a machine
2. Specify the `CUDA_VISIBLE_DEVICES` environment variable to pin that worker
   to that GPU
3. If your machine has multiple network interfaces then choose the network interface that has the best connection to that GPU
4. If your machine has multiple CPUs then set thread affinities to use the closest CPU
5. ... and more

For this reason we wanted to specify these configurations in code, like the
following:

```python
specification = {
    "worker-0": {
        "cls": dask.distributed.Nanny,
        "options": {"nthreads": 1, "env": {"CUDA_VISIBLE_DEVICES": "0,1,2,3"}, interface="ib0"},
    },
    "worker-1": {
        "cls": dask.distributed.Nanny,
        "options": {"nthreads": 1, "env": {"CUDA_VISIBLE_DEVICES": "1,2,3,0"}, interface="ib0"},
    },
    "worker-2": {
        "cls": dask.distributed.Nanny,
        "options": {"nthreads": 1, "env": {"CUDA_VISIBLE_DEVICES": "2,3,0,1"}, interface="ib1"},
    },
    "worker-2": {
        "cls": dask.distributed.Nanny,
        "options": {"nthreads": 1, "env": {"CUDA_VISIBLE_DEVICES": "3,0,1,2"}, interface="ib1"},
    },
}
```

And the new SpecCluster class to deploy these workers:

```python
cluster = SpecCluster(workers=specification)
```

We've used this technique in the
[Dask-CUDA](https://github.com/rapidsai/dask-cuda) project to provide
convenient functions for deployment on multi-GPU systems.

This class was generic enough that it ended up forming the base of the SSH,
Jobqueue, and Kubernetes solutions as well.

## Standards and Conventions

The solutions above are built by different teams that work in different companies.
This is great because those teams have hands-on experience with the
cluster managers in the wild, but has historically been somewhat challenging to
standardize user experience. This is particularly challenging when we build
other tools like IPython widgets or the Dask JupyterLab extension, which want
to interoperate with all of the Dask deployment solutions.

The recent rewrite of Dask-SSH, Dask-Jobqueue, Dask-Kubernetes, and the new
Dask-Cloudprovider and Dask-CUDA libraries place them
all under the same `dask.distributed.SpecCluster` superclass. So we can expect a high degree of
uniformity from them. Additionally, all of the classes now match the
`dask.distributed.Cluster` interface, which standardizes things like
adaptivity, IPython widgets, logs, and some basic reporting.

- Cluster
  - SpecCluster
    - Kubernetes
    - JobQueue (PBS/SLURM/LSF/SGE/Torque/Condor/Moab/OAR)
    - SSH
    - CloudProvider (ECS)
    - CUDA (LocalCUDACluster, DGX)
    - LocalCluster
  - Yarn
  - Gateway

## Future Work

There is still plenty to do. Here are some of the themes we've seen among
current development:

1. Move the Scheduler off to a separate job/pod/container in the network,
   which is often helpful for complex networking situations
2. Improve proxying of the dashboard in these situations
3. Optionally separate the life-cycle of the cluster from the lifetime of the
   Python process that requested the cluster
4. Write up best practices how to compose GPU support generally with all of the cluster managers
