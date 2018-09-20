---
layout: post
title: Introducing Dask distributed
category : work
tags : [Programming, scipy, Python, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr**: We analyze JSON data on a cluster using pure Python projects.

Dask, a Python library for parallel computing, now works on clusters.  During
the past few months I and others have extended dask with a new distributed
memory scheduler.  This enables dask's existing parallel algorithms to scale
across 10s to 100s of nodes, and extends a subset of PyData to distributed
computing.  Over the next few weeks I and others will write about this system.
Please note that dask+distributed is developing quickly and so the API is
likely to shift around a bit.

Today we start simple with the typical cluster computing problem, parsing JSON
records, filtering, and counting events using dask.bag and the new distributed
scheduler.  We'll dive into more advanced problems in future posts.

*A video version of this blogpost is available
[here](https://www.youtube.com/watch?v=W0Q0uwmYD6o).*


GitHub Archive Data on S3
-------------------------

GitHub releases data dumps of their public event stream as gzipped compressed,
line-delimited, JSON.  This data is too large to fit comfortably into memory,
even on a sizable workstation.  We could stream it from disk but, due to the
compression and JSON encoding this takes a while and so slogs down interactive
use.  For an interactive experience with data like this we need a distributed
cluster.


### Setup and Data

We provision nine `m3.2xlarge` nodes on EC2.  These have eight cores and 30GB
of RAM each.  On this cluster we provision one scheduler and nine workers (see
[setup docs](http://distributed.readthedocs.org/en/latest/setup.html)).  (More
on launching in later posts.)  We have five months of data, from 2015-01-01 to
2015-05-31 on the `githubarchive-data` bucket in S3.  This data is publicly
avaialble if you want to play with it on EC2.  You can download the full
dataset at https://www.githubarchive.org/ .

The first record looks like the following:

```python
 {'actor': {'avatar_url': 'https://avatars.githubusercontent.com/u/9152315?',
   'gravatar_id': '',
   'id': 9152315,
   'login': 'davidjhulse',
   'url': 'https://api.github.com/users/davidjhulse'},
  'created_at': '2015-01-01T00:00:00Z',
  'id': '2489368070',
  'payload': {'before': '86ffa724b4d70fce46e760f8cc080f5ec3d7d85f',
   'commits': [{'author': {'email': 'david.hulse@live.com',
      'name': 'davidjhulse'},
     'distinct': True,
     'message': 'Altered BingBot.jar\n\nFixed issue with multiple account support',
     'sha': 'a9b22a6d80c1e0bb49c1cf75a3c075b642c28f81',
     'url': 'https://api.github.com/repos/davidjhulse/davesbingrewardsbot/commits/a9b22a6d80c1e0bb49c1cf75a3c075b642c28f81'}],
   'distinct_size': 1,
   'head': 'a9b22a6d80c1e0bb49c1cf75a3c075b642c28f81',
   'push_id': 536740396,
   'ref': 'refs/heads/master',
   'size': 1},
  'public': True,
  'repo': {'id': 28635890,
   'name': 'davidjhulse/davesbingrewardsbot',
   'url': 'https://api.github.com/repos/davidjhulse/davesbingrewardsbot'},
  'type': 'PushEvent'}
```

So we have a large dataset on S3 and a moderate sized play cluster on EC2,
which has access to S3 data at about  100MB/s per node.  We're ready to play.

Play
----

We start an `ipython` interpreter on our local laptop and connect to the
dask scheduler running on the cluster.  For the purposes of timing, the cluster
is on the East Coast while the local machine is in California on commercial
broadband internet.

```python
>>> from distributed import Executor, s3
>>> e = Executor('54.173.84.107:8786')
>>> e
<Executor: scheduler=54.173.84.107:8786 workers=72 threads=72>
```

Our seventy-two worker processes come from nine workers with eight processes
each.  We chose processes rather than threads for this task because
computations will be bound by the GIL.  We will change this to threads in later
examples.

We start by loading a single month of data into distributed memory.

```python
import json
text = s3.read_text('githubarchive-data', '2015-01', compression='gzip')
records = text.map(json.loads)
records = e.persist(records)
```

The data lives in S3 in hourly files as gzipped encoded, line delimited JSON.
The `s3.read_text` and `text.map` functions produce
[dask.bag](http://dask.pydata.org/en/latest/bag.html) objects which track our
operations in a lazily built task graph.  When we ask the executor to `persist`
this collection we ship those tasks off to the scheduler to run on all of the
workers in parallel.  The `persist` function gives us back another `dask.bag`
pointing to these remotely running results.  This persist function returns
immediately, and the computation happens on the cluster in the background
asynchronously.  We gain control of our interpreter immediately while the
cluster hums along.

The cluster takes around 40 seconds to download, decompress, and parse this
data.  If you watch the video embedded above you'll see fancy progress-bars.

We ask for a single record.  This returns in around 200ms, which is fast enough
that it feels instantaneous to a human.

```python
>>> records.take(1)
({'actor': {'avatar_url': 'https://avatars.githubusercontent.com/u/9152315?',
   'gravatar_id': '',
   'id': 9152315,
   'login': 'davidjhulse',
   'url': 'https://api.github.com/users/davidjhulse'},
  'created_at': '2015-01-01T00:00:00Z',
  'id': '2489368070',
  'payload': {'before': '86ffa724b4d70fce46e760f8cc080f5ec3d7d85f',
   'commits': [{'author': {'email': 'david.hulse@live.com',
      'name': 'davidjhulse'},
     'distinct': True,
     'message': 'Altered BingBot.jar\n\nFixed issue with multiple account support',
     'sha': 'a9b22a6d80c1e0bb49c1cf75a3c075b642c28f81',
     'url': 'https://api.github.com/repos/davidjhulse/davesbingrewardsbot/commits/a9b22a6d80c1e0bb49c1cf75a3c075b642c28f81'}],
   'distinct_size': 1,
   'head': 'a9b22a6d80c1e0bb49c1cf75a3c075b642c28f81',
   'push_id': 536740396,
   'ref': 'refs/heads/master',
   'size': 1},
  'public': True,
  'repo': {'id': 28635890,
   'name': 'davidjhulse/davesbingrewardsbot',
   'url': 'https://api.github.com/repos/davidjhulse/davesbingrewardsbot'},
  'type': 'PushEvent'},)
```

This particular event is a `'PushEvent'`.  Let's quickly see all the kinds of
events.  For fun, we'll also time the interaction:

```python
>>> %time records.pluck('type').frequencies().compute()
CPU times: user 112 ms, sys: 0 ns, total: 112 ms
Wall time: 2.41 s

[('ReleaseEvent', 44312),
 ('MemberEvent', 69757),
 ('IssuesEvent', 693363),
 ('PublicEvent', 14614),
 ('CreateEvent', 1651300),
 ('PullRequestReviewCommentEvent', 214288),
 ('PullRequestEvent', 680879),
 ('ForkEvent', 491256),
 ('DeleteEvent', 256987),
 ('PushEvent', 7028566),
 ('IssueCommentEvent', 1322509),
 ('GollumEvent', 150861),
 ('CommitCommentEvent', 96468),
 ('WatchEvent', 1321546)]
```

And we compute the total count of all commits for this month.

```python
>>> %time records.count().compute()
CPU times: user 134 ms, sys: 133 µs, total: 134 ms
Wall time: 1.49 s

14036706
```

We see that it takes a few seconds to walk through the data (and perform all
scheduling overhead.)  The scheduler adds about a millisecond overhead per
task, and there are about 1000 partitions/files here (the GitHub data is split
by hour and there are 730 hours in a month) so most of the cost here is
overhead.


Investigate Jupyter
-------------------

We investigate the activities of [Project Jupyter](http://jupyter.org/).  We
chose this project because it's sizable and because we understand the players
involved and so can check our accuracy.  This will require us to filter our
data to a much smaller subset, then find popular repositories and members.

```python
>>> jupyter = (records.filter(lambda d: d['repo']['name'].startswith('jupyter/'))
                      .repartition(10))
>>> jupyter = e.persist(jupyter)
```

All records, regardless of event type, have a repository which has a name like
`'organization/repository'` in typical GitHub fashion.  We filter all records
that start with `'jupyter/'`.  Additionally, because this dataset is likely
much smaller, we push all of these records into just ten partitions.  This
dramatically reduces scheduling overhead.  The `persist` call hands this
computation off to the scheduler and then gives us back our collection that
points to that computing result.  Filtering this month for Jupyter events takes
about 7.5 seconds.  Afterwards computations on this subset feel snappy.

```python
>>> %time jupyter.count().compute()
CPU times: user 5.19 ms, sys: 97 µs, total: 5.28 ms
Wall time: 199 ms

747

>>> %time jupyter.take(1)
CPU times: user 7.01 ms, sys: 259 µs, total: 7.27 ms
Wall time: 182 ms

({'actor': {'avatar_url': 'https://avatars.githubusercontent.com/u/26679?',
   'gravatar_id': '',
   'id': 26679,
   'login': 'marksteve',
   'url': 'https://api.github.com/users/marksteve'},
  'created_at': '2015-01-01T13:25:44Z',
  'id': '2489612400',
  'org': {'avatar_url': 'https://avatars.githubusercontent.com/u/7388996?',
   'gravatar_id': '',
   'id': 7388996,
   'login': 'jupyter',
   'url': 'https://api.github.com/orgs/jupyter'},
  'payload': {'action': 'started'},
  'public': True,
  'repo': {'id': 5303123,
   'name': 'jupyter/nbviewer',
   'url': 'https://api.github.com/repos/jupyter/nbviewer'},
  'type': 'WatchEvent'},)
```

So the first event of the year was by `'marksteve'` who decided to watch the
`'nbviewer'` repository on new year's day.

Notice that these computations take around 200ms.  I can't get below this from
my local machine, so we're likely bound by communicating to such a remote
location.  A 200ms latency is not great if you're playing a video game, but
it's decent for interactive computing.

Here are all of the Jupyter repositories touched in the month of January,

```python
>>> %time jupyter.pluck('repo').pluck('name').distinct().compute()
CPU times: user 2.84 ms, sys: 4.03 ms, total: 6.86 ms
Wall time: 204 ms

['jupyter/dockerspawner',
 'jupyter/design',
 'jupyter/docker-demo-images',
 'jupyter/jupyterhub',
 'jupyter/configurable-http-proxy',
 'jupyter/nbshot',
 'jupyter/sudospawner',
 'jupyter/colaboratory',
 'jupyter/strata-sv-2015-tutorial',
 'jupyter/tmpnb-deploy',
 'jupyter/nature-demo',
 'jupyter/nbcache',
 'jupyter/jupyter.github.io',
 'jupyter/try.jupyter.org',
 'jupyter/jupyter-drive',
 'jupyter/tmpnb',
 'jupyter/tmpnb-redirector',
 'jupyter/nbgrader',
 'jupyter/nbindex',
 'jupyter/nbviewer',
 'jupyter/oauthenticator']
```

And the top ten most active people on GitHub.

```python
>>> %time (jupyter.pluck('actor')
                  .pluck('login')
                  .frequencies()
                  .topk(10, lambda kv: kv[1])
                  .compute())
CPU times: user 8.03 ms, sys: 90 µs, total: 8.12 ms
Wall time: 226 ms

[('rgbkrk', 156),
 ('minrk', 87),
 ('Carreau', 87),
 ('KesterTong', 74),
 ('jhamrick', 70),
 ('bollwyvl', 25),
 ('pkt', 18),
 ('ssanderson', 13),
 ('smashwilson', 13),
 ('ellisonbg', 13)]
```

Nothing too surprising here if you know these folks.


Full Dataset
------------

The full five months of data is too large to fit in memory, even for this
cluster.  When we represent semi-structured data like this with dynamic data
structures like lists and dictionaries there is quite a bit of memory bloat.
Some careful attention to efficient semi-structured storage here could save us
from having to switch to such a large cluster, but that will have to be
the topic of another post.

Instead, we operate efficiently on this dataset by flowing it through
memory, persisting only the records we care about.  The distributed dask
scheduler descends from the single-machine dask scheduler, which was quite good
at flowing through a computation and intelligently removing intermediate
results.

From a user API perspective, we call `persist` only on the `jupyter` dataset,
and not the full `records` dataset.

```python
>>> full = (s3.read_text('githubarchive-data', '2015', compression='gzip')
              .map(json.loads)

>>> jupyter = (full.filter(lambda d: d['repo']['name'].startswith('jupyter/'))
                   .repartition(10))

>>> jupyter = e.persist(jupyter)
```

It takes 2m36s to download, decompress, and parse the five months of publicly
available GitHub events for all Jupyter events on nine `m3.2xlarges`.

There were seven thousand such events.

```python
>>> jupyter.count().compute()
7065
```

We find which repositories saw the most activity during that time:

```python
>>> %time (jupyter.pluck('repo')
                  .pluck('name')
                  .frequencies()
                  .topk(20, lambda kv: kv[1])
                  .compute())
CPU times: user 6.98 ms, sys: 474 µs, total: 7.46 ms
Wall time: 219 ms

[('jupyter/jupyterhub', 1262),
 ('jupyter/nbgrader', 1235),
 ('jupyter/nbviewer', 846),
 ('jupyter/jupyter_notebook', 507),
 ('jupyter/jupyter-drive', 505),
 ('jupyter/notebook', 451),
 ('jupyter/docker-demo-images', 363),
 ('jupyter/tmpnb', 284),
 ('jupyter/jupyter_client', 162),
 ('jupyter/dockerspawner', 149),
 ('jupyter/colaboratory', 134),
 ('jupyter/jupyter_core', 127),
 ('jupyter/strata-sv-2015-tutorial', 108),
 ('jupyter/jupyter_nbconvert', 103),
 ('jupyter/configurable-http-proxy', 89),
 ('jupyter/hubpress.io', 85),
 ('jupyter/jupyter.github.io', 84),
 ('jupyter/tmpnb-deploy', 76),
 ('jupyter/nbconvert', 66),
 ('jupyter/jupyter_qtconsole', 59)]
```

We see that projects like `jupyterhub` were quite active during that time
while, surprisingly, `nbconvert` saw relatively little action.

Local Data
----------

The Jupyter data is quite small and easily fits in a single machine.  Let's
bring the data to our local machine so that we can compare times:

```python
>>> %time L = jupyter.compute()
CPU times: user 4.74 s, sys: 10.9 s, total: 15.7 s
Wall time: 30.2 s
```

It takes surprisingly long to download the data, but once its here, we can
iterate far more quickly with basic Python.

```python
>>> from toolz.curried import pluck, frequencies, topk, pipe
>>> %time pipe(L, pluck('repo'), pluck('name'), frequencies,
               dict.items, topk(20, key=lambda kv: kv[1]), list)
CPU times: user 11.8 ms, sys: 0 ns, total: 11.8 ms
Wall time: 11.5 ms

[('jupyter/jupyterhub', 1262),
 ('jupyter/nbgrader', 1235),
 ('jupyter/nbviewer', 846),
 ('jupyter/jupyter_notebook', 507),
 ('jupyter/jupyter-drive', 505),
 ('jupyter/notebook', 451),
 ('jupyter/docker-demo-images', 363),
 ('jupyter/tmpnb', 284),
 ('jupyter/jupyter_client', 162),
 ('jupyter/dockerspawner', 149),
 ('jupyter/colaboratory', 134),
 ('jupyter/jupyter_core', 127),
 ('jupyter/strata-sv-2015-tutorial', 108),
 ('jupyter/jupyter_nbconvert', 103),
 ('jupyter/configurable-http-proxy', 89),
 ('jupyter/hubpress.io', 85),
 ('jupyter/jupyter.github.io', 84),
 ('jupyter/tmpnb-deploy', 76),
 ('jupyter/nbconvert', 66),
 ('jupyter/jupyter_qtconsole', 59)]
```

The difference here is 20x, which is a good reminder that, once you no longer
have a large problem you should probably eschew distributed systems and act
locally.


Conclusion
----------

Downloading, decompressing, parsing, filtering, and counting JSON records
is the new wordcount.  It's the first problem anyone sees.  Fortunately it's
both easy to solve and the common case.  Woo hoo!

Here we saw that dask+distributed handle the common case decently well and with
a Pure Python stack.  Typically Python users rely on a JVM technology like
Hadoop/Spark/Storm to distribute their computations.  Here we have Python
distributing Python; there are some usability gains to be had here like nice
stack traces, a bit less serialization overhead, and attention to other
Pythonic style choices.

Over the next few posts I intend to deviate from this common case.  Most "Big
Data" technologies were designed to solve typical data munging problems found
in web companies or with simple database operations in mind.  Python users care
about these things too, but they also reach out to a wide variety of fields.
In dask+distributed development we care about the common case, but also support
less traditional workflows that are commonly found in the life, physical, and
algorithmic sciences.

By designing to support these more extreme cases we've nailed some common pain
points in current distributed systems.  Today we've seen low latency and remote
control; in the future we'll see others.


What doesn't work
-----------------

I'll have an honest section like this at the end of each upcoming post
describing what doesn't work, what still feels broken, or what I would have
done differently with more time.

*  The imports for dask and distributed are still strange.  They're two
   separate codebases that play very nicely together.  Unfortunately the
   functionality you need is sometimes in one or in the other and it's not
   immediately clear to the novice user where to go.  For example dask.bag, the
   collection we're using for `records`, `jupyter`, etc. is in `dask` but the
   `s3` module is within the `distributed` library.  We'll have to merge things
   at some point in the near-to-moderate future.  Ditto for the API: there are
   compute methods both on the dask collections (`records.compute()`) and on
   the distributed executor (`e.compute(records)`) that behave slightly
   differently.

*  We lack an efficient distributed shuffle algorithm.  This is very important
   if you want to use operations like `.groupby` (which you should avoid
   anyway).  The user API here doesn't even cleanly warn users that this is
   missing in the distributed case which is kind of a mess. (It works fine on a
   single machine.)  Efficient alternatives like `foldby` *are* available.

*  I would have liked to run this experiment directly on the cluster to see
   how low we could have gone below the 200ms barrier we ran into here.


Links
-----

*   [dask](https://dask.pydata.org/en/latest/), the original project
*   [dask.distributed](https://distributed.readthedocs.org/en/latest/), the
    distributed memory scheduler powering the cluster computing
*   [dask.bag](http://dask.pydata.org/en/latest/bag.html), the user API we've
    used in this post.
*   This post largely repeats work by [Blake Griffith](https://github.com/cowlicks) in a
    [similar post](https://www.continuum.io/content/dask-distributed-and-anaconda-cluster)
    last year with an older iteration of the dask distributed scheduler
