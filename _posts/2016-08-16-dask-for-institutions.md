---
layout: post
title: Dask for Institutions
category: work
tags: [Programming, scipy, Python, dask]
theme: twitter
---
{% include JB/setup %}

<img src="http://dask.readthedocs.io/en/latest/_images/dask_horizontal.svg"
     align="right"
     width="20%">


*This work is supported by [Continuum Analytics](http://continuum.io)*

Introduction
------------

Institutions use software differently than individuals.  Over the last few
months I've had dozens of conversations about using Dask within larger
organizations like universities, research labs, private companies, and
non-profit learning systems.  This post provides a very coarse summary of those
conversations and extracts common questions.  I'll then try to answer those
questions.

*Note: some of this post will be necessarily vague at points.  Some companies
prefer privacy.  All details here are either in public Dask issues or have come
up with enough institutions (say at least five) that I'm comfortable listing
the problem here.*


### Common story

Institution X, a university/research lab/company/... has many
scientists/analysts/modelers who develop models and analyze data with Python,
the PyData stack like NumPy/Pandas/SKLearn, and a large amount of custom code.
These models/data sometimes grow to be large enough to need a moderately large
amount of parallel computing.

Fortunately, Institution X has an in-house cluster acquired for exactly this
purpose of accelerating modeling and analysis of large computations and
datasets.  Users can submit jobs to the cluster using a job scheduler like
SGE/LSF/Mesos/Other.

However the cluster is still under-utilized and the users are still asking for
help with parallel computing.  Either users aren't comfortable using the
SGE/LSF/Mesos/Other interface, it doesn't support sufficiently complex/dynamic
workloads, or the interaction times aren't good enough for the interactive use
that users appreciate.

There was an internal effort to build a more complex/interactive/Pythonic
system on top of SGE/LSF/Mesos/Other but it's not particularly mature and
definitely isn't something that Institution X wants to pursue.  It turned out
to be a harder problem than expected to design/build/maintain such a system
in-house.  They'd love to find an open source solution that was well featured
and maintained by a community.

The Dask.distributed scheduler looks like it's 90% of the system that
Institution X needs.  However there are a few open questions:

*  How do we integrate dask.distributed with the SGE/LSF/Mesos/Other job
   scheduler?
*  How can we grow and shrink the cluster dynamically based on use?
*  How do users manage software environments on the workers?
*  How secure is the distributed scheduler?
*  Dask is resilient to worker failure, how about scheduler failure?
*  What happens if ``dask-worker``s are in two different data centers?  Can we
   scale in an asymmetric way?
*  How do we handle multiple concurrent users and priorities?
*  How does this compare with Spark?

So for the rest of this post I'm going to answer these questions.  As usual,
few of answers will be of the form "Yes Dask can solve all of your problems."
These are open questions, not the questions that were easy to answer.  We'll
get into what's possible today and how we might solve these problems in the
future.


### How do we integrate dask.distributed with SGE/LSF/Mesos/Other?

It's not difficult to deploy dask.distributed at scale within an existing
cluster using a tool like SGE/LSF/Mesos/Other.  In many cases there is already
a researcher within the institution doing this manually by running
`dask-scheduler` on some static node in the cluster and launching `dask-worker`
a few hundred times with their job scheduler and a small job script.

The goal now is how to formalize this process for the individual version of
SGE/LSF/Mesos/Other used within the institution while also developing and
maintaining a standard Pythonic interface so that all of these tools can be
maintained cheaply by Dask developers into the foreseeable future.  In some
cases Institution X is happy to pay for the development of a convenient "start
dask on my job scheduler" tool, but they are less excited about paying to
maintain it forever.

We want Python users to be able to say something like the following:

```python
from dask.distributed import Executor, SGECluster

c = SGECluster(nworkers=200, **options)
e = Executor(c)
```

... and have this same interface be standardized across different job
schedulers.


### How can we grow and shrink the cluster dynamically based on use?

Alternatively, we could have a single dask.distributed deployment running 24/7
that scales itself up and down dynamically based on current load.  Again, this
is entirely possible today if you want to do it manually (you can add and
remove workers on the fly) but we should add some signals to the scheduler like
the following:

*  "I'm under duress, please add workers"
*  "I've been idling for a while, please reclaim workers"

and connect these signals to a manager that talks to the job scheduler.  This
removes an element of control from the users and places it in the hands of a
policy that IT can tune to play more nicely with their other services on the
same network.


### How do users manage software environments on the workers?

Today Dask assumes that all users and workers share the exact same software
environment.  There are some small tools to send updated `.py` and `.egg` files
to the workers but that's it.

Generally Dask trusts that the full software environment will be handled by
something else.  This might be a network file system (NFS) mount on traditional
cluster setups, or it might be handled by moving docker or conda environments
around by some other tool like [knit](http://knit.readthedocs.io/en/latest/)
for YARN deployments or something more custom.  For example Continuum [sells
proprietary software](https://docs.continuum.io/anaconda-cluster/) that
does this.

Getting the standard software environment setup generally isn't such a big deal
for institutions.  They typically have some system in place to handle this
already.  Where things become interesting is when users want to use
drastically different environments from the system environment, like using Python
2 vs Python 3 or installing a bleeding-edge scikit-learn version.  They may
also want to change the software environment many times in a single session.

The best solution I can think of here is to pass around fully downloaded conda
environments using the dask.distributed network (it's good at moving large
binary blobs throughout the network) and then teaching the `dask-worker`s to
bootstrap themselves within this environment.  We should be able to tear
everything down and restart things within a small number of seconds.  This
requires some work; first to make relocatable conda binaries (which is usually
fine but is not always fool-proof due to links) and then to help the
dask-workers learn to bootstrap themselves.

Somewhat related, Hussain Sultan of Capital One recently contributed a
``dask-submit`` command to run scripts on the cluster:
[http://distributed.readthedocs.io/en/latest/submitting-applications.html](http://distributed.readthedocs.io/en/latest/submitting-applications.html)


### How secure is the distributed scheduler?

Dask.distributed is incredibly insecure.  It allows anyone with network access
to the scheduler to execute arbitrary code in an unprotected environment.  Data
is sent in the clear.  Any malicious actor can both steal your secrets and then
cripple your cluster.

This is entirely the norm however.  Security is usually handled by other
services that manage computational frameworks like Dask.

For example we might rely on Docker to isolate workers from destroying their
surrounding environment and rely on network access controls to protect data
access.

Because Dask runs on Tornado, a serious networking library and web framework,
there are some things we can do easily like enabling SSL, authentication, etc..
However I hesitate to jump into providing "just a little bit of security"
without going all the way for fear of providing a false sense of security.  In
short, I have no plans to work on this without a lot of encouragement.  Even
then I would strongly recommend that institutions couple Dask with tools
intended for security.  I believe that is common practice for distributed
computational systems generally.


### Dask is resilient to worker failure, how about scheduler failure?

Workers can come and go.  Clients can come and go.  The state in the scheduler
is currently irreplaceable and no attempt is made to back it up.  There are a
few things you could imagine here:

1.  Backup state and recent events to some persistent storage so that state can
    be recovered in case of catastrophic loss
2.  Have a hot failover node that gets a copy of every action that the
    scheduler takes
3.  Have multiple peer schedulers operate simultaneously in a way that they can
    pick up slack from lost peers
4.  Have clients remember what they have submitted and resubmit when a
    scheduler comes back online

Currently option 4 is currently the most feasible and gets us most of the way
there.  However options 2 or 3 would probably be necessary if Dask were to ever
run as critical infrastructure in a giant institution.  We're not there yet.

As of [recent work](https://github.com/dask/distributed/pull/413) spurred on by
Stefan van der Walt at UC Berkeley/BIDS the scheduler can now die and come back
and everyone will reconnect.  The state for computations in flight is entirely
lost but the computational infrastructure remains intact so that people can
resubmit jobs without significant loss of service.

Dask has a bit of a harder time with this topic because it offers a persistent
stateful interface.  This problem is much easier for distributed database
projects that run ephemeral queries off of persistent storage, return the
results, and then clear out state.


### What happens if dask-workers are in two different data centers?  Can we scale in an asymmetric way?

The short answer is no.  Other than number of cores and available RAM all
workers are considered equal to each other (except when the user [explicitly
specifies
otherwise](http://distributed.readthedocs.io/en/latest/locality.html#user-control)).

However this problem and problems like it have come up a lot lately.  Here are a
few examples of similar cases:

1.  Multiple data centers geographically distributed around the country
2.  Multiple racks within a single data center
4.  Multiple workers that have GPUs that can move data between each other easily
3.  Multiple processes on a single machine

Having some notion of hierarchical worker group membership or inter-worker
preferred relationships is probably inevitable long term.  As with all
distributed scheduling questions the hard part isn't deciding that this is
useful, or even coming up with a sensible design, but rather figuring out how
to make decisions on the sensible design that are foolproof and operate in
constant time.  I don't personally see a good approach here yet but expect one
to arise as more high priority use cases come in.


### How do we handle multiple concurrent users and priorities?

There are several sub-questions here:

*   Can multiple users use Dask on my cluster at the same time?

Yes, either by spinning up separate scheduler/worker sets or by sharing the same
set.

*   If they're sharing the same workers then won't they clobber each other's
    data?

This is very unlikely.  Dask is careful about naming tasks, so it's very
unlikely that the two users will submit conflicting computations that compute to
different values but occupy the same key in memory.  However if they both submit
computations that overlap somewhat then the scheduler will nicely avoid
recomputation.  This can be very nice when you have many people doing slightly
different computations on the same hardware.  This works in the same way that
Git works.

*   If they're sharing the same workers then won't they clobber each other's
    resources?

Yes, this is definitely possible.  If you're concerned about this then you
should give everyone their own scheduler/workers (which is easy and standard
practice).  There is not currently much user management built into Dask.


### How does this compare with Spark?

At an institutional level Spark seems to primarily target ETL + Database-like
computations.  While Dask modules like Dask.bag and Dask.dataframe can happily
play in this space this doesn't seem to be the focus of recent conversations.

Recent conversations are almost entirely around supporting interactive custom
parallelism (lots of small tasks with complex dependencies between them) rather
than the big Map->Filter->Groupby->Join abstractions you often find in a
database or Spark.  That's not to say that these operations aren't hugely
important; there is a lot of selection bias here.  The people I talk to are
people for whom Spark/Databases are clearly not an appropriate fit.  They are
tackling problems that are way more complex, more heterogeneous, and with a
broader variety of users.

I usually describe this situation with an analogy comparing "Big data" systems
to human transportation mechanisms in a city.  Here we go:

*  *A Database is like a train*: it goes between a set of well defined points
   with great efficiency, speed, and predictability.  These are popular and
   profitable routes that many people travel between (e.g. business analytics).
   You do have to get from home to the train station on your own (ETL), but once
   you're in the database/train you're quite comfortable.
*  *Spark is like an automobile*: it takes you door-to-door from your home to
   your destination with a single tool.  While this may not be as fast as the train for
   the long-distance portion, it can be extremely convenient to do ETL, Database
   work, and some machine learning all from the comfort of a single system.
*  *Dask is like an all-terrain-vehicle*: it takes you out of town on rough
   ground that hasn't been properly explored before.  This is a good match for
   the Python community, which typically does a lot of exploration into new
   approaches.  You can also drive your ATV around town and you'll be just fine,
   but if you want to do thousands of SQL queries then you should probably
   invest in a proper database or in Spark.

Again, there is a lot of selection bias here, if what you want is a database
then you should probably get a database.  Dask is not a database.

This is also wildly over-simplifying things.  Databases like Oracle have lots
of ETL and analytics tools, Spark is known to go off road, etc..  I obviously
have a bias towards Dask.  You really should never trust an author of a project
to give a fair and unbiased view of the capabilities of the tools in the
surrounding landscape.


Conclusion
----------

That's a rough sketch of current conversations and open problems for "How Dask
might evolve to support institutional use cases."  It's really quite surprising
just how prevalent this story is among the full spectrum from universities to
hedge funds.

The problems listed above are by no means halting adoption.  I'm not listing
the 100 or so questions that are answered with "yes, that's already supported
quite well".  Right now I'm seeing Dask being adopted by individuals and small
groups within various institutions.  Those individuals and small groups are
pushing that interest up the stack.  It's still several months before any 1000+
person organization adopts Dask as infrastructure, but the speed at which
momentum is building is quite encouraging.

I'd also like to thank the several nameless people who exercise Dask on various
infrastructures at various scales on interesting problems and have reported
serious bugs.  These people don't show up on the GitHub issue tracker but their
utility in flushing out bugs is invaluable.

As interest in Dask grows it's interesting to see how it will evolve.
Culturally Dask has managed to simultaneously cater to both the open science
crowd as well as the private-sector crowd.  The project gets both financial
support and open source contributions from each side.  So far there hasn't been
any conflict of interest (everyone is pushing in roughly the same direction)
which has been a really fruitful experience for all involved I think.
