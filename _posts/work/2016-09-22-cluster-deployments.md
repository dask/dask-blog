---
layout: post
title: Dask Cluster Deployments
category: work
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

*All code in this post is experimental.  It should not be relied upon.  For
people looking to deploy dask.distributed on a cluster please refer instead to
the [documentation](https://distributed.readthedocs.org) instead.*

Dask is deployed today on the following systems in the wild:

*  SGE
*  SLURM,
*  Torque
*  Condor
*  LSF
*  Mesos
*  Marathon
*  Kubernetes
*  SSH and custom scripts
*  ... there may be more. This is what I know of first-hand.

These systems provide users access to cluster resources and ensure that
many distributed services / users play nicely together.  They're essential for
any modern cluster deployment.

The people deploying Dask on these cluster resource managers are power-users;
they know how their resource managers work and they read the [documentation on
how to setup Dask
clusters](http://distributed.readthedocs.io/en/latest/setup.html).  Generally
these users are pretty happy; however we should reduce this barrier so that
non-power-users with access to a cluster resource manager can use Dask on their
cluster just as easily.

Unfortunately, there are a few challenges:

1.  Several cluster resource managers exist, each with significant adoption.
    Finite developer time stops us from supporting all of them.
3.  Policies for scaling out vary widely.
    For example we might want a fixed number of workers, or we might want
    workers that scale out based on current use.  Different groups will want
    different solutions.
2.  Individual cluster deployments are highly configurable.  Dask needs to get
    out of the way quickly and let existing technologies configure themselves.

This post talks about some of these issues.  It does not contain a definitive
solution.


Example: Kubernetes
-------------------

For example, both [Olivier Griesl](http://ogrisel.com/) (INRIA, scikit-learn)
and [Tim O'Donnell](https://github.com/timodonnell) (Mount Sinai, Hammer lab)
publish instructions on how to deploy Dask.distributed on
[Kubernetes](http://kubernetes.io/).

*  [Olivier's repository](https://github.com/ogrisel/docker-distributed)
*  [Tim's repository](https://github.com/hammerlab/dask-distributed-on-kubernetes/)

These instructions are well organized.  They include Dockerfiles, published
images, Kubernetes config files, and instructions on how to interact with cloud
providers' infrastructure.  Olivier and Tim both obviously know what they're
doing and care about helping others to do the same.

Tim (who came second) wasn't aware of Olivier's solution and wrote up his own.
Tim was capable of doing this but many beginners wouldn't be.

**One solution** would be to include a prominent registry of solutions like
these within Dask documentation so that people can find quality references to
use as starting points.  I've started a list of resources here:
[dask/distributed #547](https://github.com/dask/distributed/pull/547) comments
pointing to other resources would be most welcome..

However, even if Tim did find Olivier's solution I suspect he would still need
to change it.  Tim has different software and scalability needs than Olivier.
This raises the question of *"What should Dask provide and what should it leave
to administrators?"*  It may be that the *best* we can do is to support
copy-paste-edit workflows.

What is Dask-specific, resource-manager specific, and what needs to be
configured by hand each time?


Adaptive Deployments
--------------------

In order to explore this topic of separable solutions I built a small adaptive
deployment system for Dask.distributed on
[Marathon](https://mesosphere.github.io/marathon/), an orchestration platform
on top of Mesos.

This solution does two things:

1.  It scales a Dask cluster dynamically based on the current use.  If there
    are more tasks in the scheduler then it asks for more workers.
2.  It deploys those workers using Marathon.

To encourage replication, these two different aspects are solved in two different pieces of code with a clean API boundary.

1.  A backend-agnostic piece for adaptivity that says when to scale workers up
    and how to scale them down safely
2.  A Marathon-specific piece that deploys or destroys dask-workers using the
    Marathon HTTP API

This combines a policy, *adaptive scaling*, with a backend, *Marathon* such
that either can be replaced easily.  For example we could replace the adaptive
policy with a fixed one to always keep N workers online, or we could replace
Marathon with Kubernetes or Yarn.

My hope is that this demonstration encourages others to develop third party
packages.  The rest of this post will be about diving into this particular
solution.


Adaptivity
----------

The `distributed.deploy.Adaptive` class wraps around a `Scheduler` and
determines when we should scale up and by how many nodes, and when we should
scale down specifying which idle workers to release.

The current policy is fairly straightforward:

1.  If there are unassigned tasks or any stealable tasks and no idle workers,
    or if the average memory use is over 50%, then increase the number of
    workers by a fixed factor (defaults to two).
2.  If there are idle workers and the average memory use is below 50% then
    reclaim the idle workers with the least data on them (after moving data to
    nearby workers) until we're near 50%

Think this policy could be improved or have other thoughts?  Great.  It was
easy to implement and entirely separable from the main code so you should be
able to edit it easily or create your own.  The current implementation is about
80 lines
([source](https://github.com/dask/distributed/blob/master/distributed/deploy/adaptive.py)).

However, this `Adaptive` class doesn't actually know how to perform the
scaling.  Instead it depends on being handed a separate  object, with two
methods, `scale_up` and `scale_down`:


```python
class MyCluster(object):
    def scale_up(n):
        """
        Bring the total count of workers up to ``n``

        This function/coroutine should bring the total number of workers up to
        the number ``n``.
        """
        raise NotImplementedError()

    def scale_down(self, workers):
        """
        Remove ``workers`` from the cluster

        Given a list of worker addresses this function should remove those
        workers from the cluster.
        """
        raise NotImplementedError()
```

This cluster object contains the backend-specific bits of *how* to scale up and
down, but none of the adaptive logic of *when* to scale up and down.  The
single-machine
[LocalCluster](http://distributed.readthedocs.io/en/latest/local-cluster.html)
object serves as reference implementation.

So we combine this adaptive scheme with a deployment scheme.  We'll use a tiny
Dask-Marathon deployment library available
[here](https://github.com/mrocklin/dask-marathon)

```python
from dask_marathon import MarathonCluster
from distributed import Scheduler
from distributed.deploy import Adaptive

s = Scheduler()
mc = MarathonCluster(s, cpus=1, mem=4000,
                     docker_image='mrocklin/dask-distributed')
ac = Adaptive(s, mc)
```

This combines a policy, Adaptive, with a deployment scheme, Marathon in a
composable way.  The Adaptive cluster watches the scheduler and calls the
`scale_up/down` methods on the MarathonCluster as necessary.


Marathon code
-------------

Because we've isolated all of the "when" logic to the Adaptive code, the
Marathon specific code is blissfully short and specific.  We include a slightly
simplified version below.  There is a fair amount of Marathon-specific setup in
the constructor and then simple scale_up/down methods below:

```python
from marathon import MarathonClient, MarathonApp
from marathon.models.container import MarathonContainer


class MarathonCluster(object):
    def __init__(self, scheduler,
                 executable='dask-worker',
                 docker_image='mrocklin/dask-distributed',
                 marathon_address='http://localhost:8080',
                 name=None, cpus=1, mem=4000, **kwargs):
        self.scheduler = scheduler

        # Create Marathon App to run dask-worker
        args = [
            executable,
            scheduler.address,
            '--nthreads', str(cpus),
            '--name', '$MESOS_TASK_ID',  # use Mesos task ID as worker name
            '--worker-port', '$PORT_WORKER',
            '--nanny-port', '$PORT_NANNY',
            '--http-port', '$PORT_HTTP'
        ]

        ports = [{'port': 0,
                  'protocol': 'tcp',
                  'name': name}
                 for name in ['worker', 'nanny', 'http']]

        args.extend(['--memory-limit',
                     str(int(mem * 0.6 * 1e6))])

        kwargs['cmd'] = ' '.join(args)
        container = MarathonContainer({'image': docker_image})

        app = MarathonApp(instances=0,
                          container=container,
                          port_definitions=ports,
                          cpus=cpus, mem=mem, **kwargs)

        # Connect and register app
        self.client = MarathonClient(marathon_address)
        self.app = self.client.create_app(name or 'dask-%s' % uuid.uuid4(), app)

    def scale_up(self, instances):
        self.client.scale_app(self.app.id, instances=instances)

    def scale_down(self, workers):
        for w in workers:
            self.client.kill_task(self.app.id,
                                  self.scheduler.worker_info[w]['name'],
                                  scale=True)
```

This isn't trivial, you need to know about Marathon for this to make sense, but
fortunately you don't need to know much else.  My hope is that people familiar
with other cluster resource managers will be able to write similar objects and
will publish them as third party libraries as I have with this Marathon
solution here:
[https://github.com/mrocklin/dask-marathon](https://github.com/mrocklin/dask-marathon)
(thanks goes to Ben Zaitlen for setting up a great testing harness for this and
getting everything started.)


Adaptive Policies
-----------------

Similarly, we can design new policies for deployment.  You can read more about
the policies for the `Adaptive` class in the
[documentation](http://distributed.readthedocs.io/en/latest/adaptive.html) or
the
[source](https://github.com/dask/distributed/blob/master/distributed/deploy/adaptive.py)
(about eighty lines long).  I encourage people to implement and use other
policies and contribute back those policies that are useful in practice.


Final thoughts
--------------

We laid out a problem

*  *How does a distributed system support a variety of cluster resource managers
and a variety of scheduling policies while remaining sensible?*

We proposed two solutions:

1.  *Maintain a registry of links to solutions, supporting copy-paste-edit practices*
2.  *Develop an API boundary that encourages separable development of third party libraries.*

It's not clear that either solution is sufficient, or that the current
implementation of either solution is any good.  This is is an important problem
though as Dask.distributed is, today, still mostly used by super-users.  I
would like to engage community creativity here as we search for a good
solution.
