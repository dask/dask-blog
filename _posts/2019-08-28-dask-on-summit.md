---
layout: post
title: "Dask on HPC: a case study"
author: Matthew Rocklin
tags: [HPC]
theme: twitter
---

{% include JB/setup %}

Dask is deployed on traditional HPC machines with increasing frequency.
In the past week I've personally helped four different groups get set up.
This is a surprisingly individual process,
because every HPC machine has its own idiosyncrasies.
Each machine uses a job scheduler like SLURM/PBS/SGE/LSF/..., a network file
system, and fast interconnect, but each of those sub-systems have slightly
different policies on a machine-by-machine basis, which is where things get tricky.

Typically we can solve these problems in about 30 minutes if we have both:

- Someone familiar with the machine, like a power-user or an IT administrator
- Someone familiar with setting up Dask

These systems span a large range of scale. At different ends of this scale
this week I've seen both:

- A small in-house 24-node SLURM cluster for research work inside of a
  bio-imaging lab
- Summit, the world's most powerful supercomputer

In this post I'm going to share a few notes of what I went through in dealing
with Summit, which was particularly troublesome. Hopefully this gives a sense
for the kinds of situations that arise. These tips likely don't apply to your
particular system, but hopefully they give a flavor of what can go wrong,
and the processes by which we track things down.

### Power Architecture

First, Summit is an IBM PowerPC machine, meaning that packages compiled on
normal Intel chips won't work. Fortunately, Anaconda maintains a download of
their distribution that works well with the Power architecture, so that gave me
a good starting point.

<https://www.anaconda.com/distribution/#linux>

Packages do seem to be a few months older than for the normal distribution, but
I can live with that.

### Install Dask-Jobqueue and configure basic information

We need to tell Dask how many cores and how much memory is on each machine.
This process is fairly straightforward, is well documented at
[jobqueue.dask.org](https://jobqueue.dask.org) with an informative screencast,
and even self-directing with error messages.

```python
In [1]: from dask_jobqueue import PBSCluster
In [2]: cluster = PBSCluster()
ValueError: You must specify how many cores to use per job like ``cores=8``
```

I'm going to skip this section for now because, generally, novice users are
able to handle this. For more information, consider watching this YouTube
video (30m).

<iframe width="560" height="315"
        src="https://www.youtube.com/embed/FXsgmwpRExM?rel=0"
        frameborder="0" allow="autoplay; encrypted-media"
        allowfullscreen></iframe>

### Invalid operations in the job script

So we make a cluster object with all of our information, we call `.scale` and
we get some error message from the job scheduler.

```python
from dask_jobqueue import LSFCluster
cluster = LSFCluster(
    cores=128,
    memory="600 GB",
    project="GEN119",
    walltime="00:30",
)
cluster.scale(3)  # ask for three nodes
```

```
Command:
bsub /tmp/tmp4874eufw.sh
stdout:

Typical usage:
  bsub [LSF arguments] jobscript
  bsub [LSF arguments] -Is $SHELL
  bsub -h[elp] [options]
  bsub -V

NOTES:
 * All jobs must specify a walltime (-W) and project id (-P)
 * Standard jobs must specify a node count (-nnodes) or -ln_slots. These jobs cannot specify a resource string (-R).
 * Expert mode jobs (-csm y) must specify a resource string and cannot specify -nnodes or -ln_slots.

stderr:
ERROR: Resource strings (-R) are not supported in easy mode. Please resubmit without a resource string.
ERROR: -n is no longer supported. Please request nodes with -nnodes.
ERROR: No nodes requested. Please request nodes with -nnodes.
```

Dask-Jobqueue tried to generate a sensible job script from the inputs that you
provided, but the resource manager that you're using may have additional
policies that are unique to that cluster. We debug this by looking at the
generated script, and comparing against scripts that are known to work on the
HPC machine.

```python
print(cluster.job_script())
```

```bash
#!/usr/bin/env bash

#BSUB -J dask-worker
#BSUB -P GEN119
#BSUB -n 128
#BSUB -R "span[hosts=1]"
#BSUB -M 600000
#BSUB -W 00:30
JOB_ID=${LSB_JOBID%.*}

/ccs/home/mrocklin/anaconda/bin/python -m distributed.cli.dask_worker tcp://scheduler:8786 --nthreads 16 --nprocs 8 --memory-limit 75.00GB --name name --nanny --death-timeout 60 --interface ib0 --interface ib0
```

After comparing notes with existing scripts that we know to work on Summit,
we modify keywords to add and remove certain lines in the header.

```python
cluster = LSFCluster(
    cores=128,
    memory="500 GB",
    project="GEN119",
    walltime="00:30",
    job_extra=["-nnodes 1"],          # <--- new!
    header_skip=["-R", "-n ", "-M"],  # <--- new!
)
```

And when we call scale this seems to make LSF happy. It no longer dumps out
large error messages.

```python
>>> cluster.scale(3)  # things seem to pass
>>>
```

### Workers don't connect to the Scheduler

So things seem fine from LSF's perspective, but when we connect up a client to
our cluster we don't see anything arriving.

```python
>>> from dask.distributed import Client
>>> client = Client(cluster)
>>> client
<Client: scheduler='tcp://10.41.0.34:41107' processes=0 cores=0>
```

Two things to check, have the jobs actually made it through the queue?
Typically we use a resource manager operation, like `qstat`, `squeue`, or
`bjobs` for this. Maybe our jobs are trapped in the queue?

```
$ bash
JOBID   USER       STAT   SLOTS    QUEUE       START_TIME    FINISH_TIME   JOB_NAME
600785  mrocklin   RUN    43       batch       Aug 26 13:11  Aug 26 13:41  dask-worker
600786  mrocklin   RUN    43       batch       Aug 26 13:11  Aug 26 13:41  dask-worker
600784  mrocklin   RUN    43       batch       Aug 26 13:11  Aug 26 13:41  dask-worker
```

Nope, it looks like they're in a running state. Now we go and look at their
logs. It can sometimes be tricky to track down the log files from your jobs,
but your IT administrator should know where they are. Often they're where you
ran your job from, and have the Job ID in the filename.

```
$ cat dask-worker.600784.err
distributed.worker - INFO -       Start worker at: tcp://128.219.134.81:44053
distributed.worker - INFO -          Listening to: tcp://128.219.134.81:44053
distributed.worker - INFO -          dashboard at:       128.219.134.81:34583
distributed.worker - INFO - Waiting to connect to: tcp://128.219.134.74:34153
distributed.worker - INFO - -------------------------------------------------
distributed.worker - INFO -               Threads:                         16
distributed.worker - INFO -                Memory:                   75.00 GB
distributed.worker - INFO -       Local Directory: /autofs/nccs-svm1_home1/mrocklin/worker-ybnhk4ib
distributed.worker - INFO - -------------------------------------------------
distributed.worker - INFO - Waiting to connect to: tcp://128.219.134.74:34153
distributed.worker - INFO - Waiting to connect to: tcp://128.219.134.74:34153
distributed.worker - INFO - Waiting to connect to: tcp://128.219.134.74:34153
distributed.worker - INFO - Waiting to connect to: tcp://128.219.134.74:34153
distributed.worker - INFO - Waiting to connect to: tcp://128.219.134.74:34153
distributed.worker - INFO - Waiting to connect to: tcp://128.219.134.74:34153
...
```

So the worker processes have started, but they're having difficulty connecting
to the scheduler. When we ask at IT administrator they identify the address
here as on the wrong network interface:

```
128.219.134.74  <--- not accessible network address
```

So we run `ifconfig`, and find the infiniband network interface, `ib0`, which
is more broadly accessible.

```python
cluster = LSFCluster(
    cores=128,
    memory="500 GB",
    project="GEN119",
    walltime="00:30",
    job_extra=["-nnodes 1"],
    header_skip=["-R", "-n ", "-M"],
    interface="ib0",                    # <--- new!
)
```

We try this out and still, no luck :(

### Interactive nodes

The expert user then says "Oh, our login nodes are pretty locked-down, lets try
this from an interactive compute node. Things tend to work better there". We
run some arcane bash command (I've never seen two of these that look alike so
I'm going to omit it here), and things magically start working. Hooray!

We run a tiny Dask computation just to prove that we can do some work.

```python
>>> client = Client(cluster)
>>> client.submit(lambda x: x + 1, 10).result()
11
```

Actually, it turns out that we were eventually able to get things running from
the login nodes on Summit using a slightly different `bsub` command in LSF, but
I'm going to omit details here because we're fixing this in Dask and it's
unlikely to affect future users (I hope?). Locked down login nodes remain a
common cause of no connections across a variety of systems. I'll say something
like 30% of the systems that I interact with.

### SSH Tunneling

It's important to get the dashboard up and running so that you can see what's
going on. Typically we do this with SSH tunnelling. Most HPC people know how
to do this and it's covered in the Youtube screencast above, so I'm going to
skip it here.

### Jupyter Lab

Many interactive Dask users on HPC today are moving towards using JupyterLab.
This choice gives them a notebook, terminals, file browser, and Dask's
dashboard all in a single web tab. This greatly reduces the number of times
they have to SSH in, and, with the magic of web proxies, means that they only
need to tunnel once.

I conda installed JupyterLab and a proxy library, and then tried to
[set up the Dask JupyterLab extension](https://github.com/dask/dask-labextension#installation).

```
conda install jupyterlab
pip install jupyter-server-proxy  # to route dashboard through Jupyter's port
```

Next, we're going to install the
[Dask Labextension](https://github.com/dask/dask-labextension) into JupyterLab
in order to get the Dask Dashboard directly into our Jupyter session..
For that, we need `nodejs` in order to install things into JupyterLab.
I thought that this was going to be a pain, given the Power architecture, but
amazingly, this also seems to be in Anaconda's default Power channel.

```
mrocklin@login2.summit $ conda install nodejs  # Thanks conda packaging devs!
```

Then I install Dask-Labextension, which is both a Python and a JavaScript
package:

```
pip install dask_labextension
jupyter labextension install dask-labextension
```

Then I set up a password for my Jupyter sessions

```
jupyter notebook password
```

And run JupyterLab in a network friendly way

```
mrocklin@login2.summit $ jupyter lab --no-browser --ip="login2"
```

And set up a single SSH tunnel from my home machine to the login node

```
# Be sure to match the login node's hostname and the Jupyter port below

mrocklin@my-laptop $ ssh -L 8888:login2:8888 summit.olcf.ornl.gov
```

I can now connect to Jupyter from my laptop by navigating to
<http://localhost:8888> , run the cluster commands above in a notebook, and
things work great. Additionally, thanks to `jupyter-server-proxy`, Dask's
dashboard is also available at <http://localhost:8888/proxy/####/status> , where
`####` is the port currently hosting Dask's dashboard. You can probably find
this by looking at `cluster.dashboard_link`. It defaults to 8787, but if
you've started a bunch of Dask schedulers on your system recently it's possible
that that port is taken up and so Dask had to resort to using random ports.

### Configuration files

I don't want to keep typing all of these commands, so now I put things into a
single configuration file, and plop that file into `~/.config/dask/summit.yaml`
(any filename that ends in `.yaml` will do).

```yaml
jobqueue:
  lsf:
    cores: 128
    processes: 8
    memory: 500 GB
    job-extra:
      - "-nnodes 1"
    interface: ib0
    header-skip:
      - "-R"
      - "-n "
      - "-M"

labextension:
  factory:
    module: "dask_jobqueue"
    class: "LSFCluster"
    args: []
    kwargs:
      project: your-project-id
```

### Slow worker startup

Now that things are easier to use I find myself using the system more, and some
other problems arise.

I notice that it takes a long time to start up a worker. It seems to hang
intermittently during startup, so I add a few lines to
`distributed/__init__.py` to print out the state of the main Python thread
every second, to see where this is happening:

```python
import threading, sys, time
from . import profile

main_thread = threading.get_ident()

def f():
    while True:
        time.sleep(1)
        frame = sys._current_frames()[main_thread]
        print("".join(profile.call_stack(frame)

thread = threading.Thread(target=f, daemon=True)
thraed.start()
```

This prints out a traceback that brings us to this code in Dask:

```python
if is_locking_enabled():
    try:
        self._lock_path = os.path.join(self.dir_path + DIR_LOCK_EXT)
        assert not os.path.exists(self._lock_path)
        logger.debug("Locking %r...", self._lock_path)
        # Avoid a race condition before locking the file
        # by taking the global lock
        try:
                with workspace._global_lock():
                    self._lock_file = locket.lock_file(self._lock_path)
                    self._lock_file.acquire()
```

It looks like Dask is trying to use a file-based lock.
Unfortunately some NFS systems don't like file-based locks, or handle them very
slowly. In the case of Summit, the home directory is actually mounted
read-only from the compute nodes, so a file-based lock will simply fail.
Looking up the `is_locking_enabled` function we see that it checks a
configuration value.

```python
def is_locking_enabled():
    return dask.config.get("distributed.worker.use-file-locking")
```

So we add that to our config file. At the same time I switch from the
forkserver to spawn multiprocessing method (I thought that this might help, but
it didn't), which is relatively harmless.

```
distributed:
  worker:
    multiprocessing-method: spawn
    use-file-locking: False

jobqueue:
  lsf:
    cores: 128
    processes: 8
    memory: 500 GB
    job-extra:
      - "-nnodes 1"
    interface: ib0
    header-skip:
    - "-R"
    - "-n "
    - "-M"

labextension:
  factory:
     module: 'dask_jobqueue'
     class: 'LSFCluster'
     args: []
     kwargs:
       project: your-project-id
```

### Conclusion

This post outlines many issues that I ran into when getting Dask to run on
one specific HPC system. These problems aren't universal, so you may not run
into them, but they're also not super-rare. Mostly my objective in writing
this up is to give people a sense of the sorts of problems that arise when
Dask and an HPC system interact.

None of the problems above are that serious. They've all happened before and
they all have solutions that can be written down in a configuration file.
Finding what the problem is though can be challenging, and often requires the
combined expertise of individuals that are experienced with Dask and with that
particular HPC system.

There are a few configuration files posted here
[jobqueue.dask.org/en/latest/configurations.html](https://jobqueue.dask.org/en/latest/configurations.html), which may be informative. The [Dask Jobqueue issue tracker](https://github.com/dask/dask-jobqueue/issues) is also a fairly friendly place, full of both IT professionals and Dask experts.

Also, as a reminder, you don't need to have an HPC machine in order to use
Dask. Dask is conveniently deployable from other Cloud, Hadoop, and local
systems. See the [Dask setup
documentation](https://docs.dask.org/en/latest/setup.html) for more
information.

### Future work: GPUs

Summit is fast because it has a ton of GPUs. I'm going to work on that next,
but that will probably cover enough content to fill up a whole other blogpost :)

### Branches

For anyone playing along at home (or on Summit). I'm operating from the
following development branches:

- <https://github.com/dask/distributed@master>
- <https://github.com/mrocklin/dask-jobqueue@spec-rewrite>

Although hopefully within a month of writing this article, everything should be
in a nicely released state.
