---
layout: post
title: Co-locating a Jupyter Server and Dask Scheduler
author: Matthew Rocklin
tags: [HPC]
theme: twitter
---

{% include JB/setup %}

If you want, you can have Dask set up a Jupyter notebook server for you,
co-located with the Dask scheduler. There are many ways to do this, but this
blog post lists two.

### First, why would you do this?

Sometimes people inside of large institutions have complex deployment pains.
It takes them a while to stand up a process running on a machine in their
cluster, with all of the appropriate networking ports open and such.
In that situation, it can sometimes be nice to do this just once, say for Dask,
rather than twice, say for Dask and for Jupyter.

Probably in these cases people should invest in a long term solution like
[JupyterHub](https://jupyter.org/hub),
or one of its enterprise variants,
but this blogpost gives a couple of hacks in the meantime.

### Hack 1: Create a Jupyter server from a Python function call

If your Dask scheduler is already running, connect to it with a Client and run
a Python function that starts up a Jupyter server.

```python
from dask.distributed import Client

client = Client("scheduler-address:8786")

def start_juptyer_server():
    from notebook.notebookapp import NotebookApp
    app = NotebookApp()
    app.initialize([])  # add command line args here if you want

client.run_on_scheduler(start_jupyter_server)
```

If you have a complex networking setup (maybe you're on the cloud or HPC and
had to open up a port explicitly) then you might want to install
[jupyter-server-proxy](https://jupyter-server-proxy.readthedocs.io/en/latest/)
(which Dask also uses by default if installed), and then go to
[http://scheduler-address:8787/proxy/8888](https://example.com) . The Dask dashboard can route your
connection to Jupyter (Jupyter is also kind enough to do the same for Dask if
it is the main service).

### Hack 2: Preload script

This is also a great opportunity to learn about the various ways of [adding
custom startup and teardown](https://docs.dask.org/en/latest/setup/custom-startup.html).
One such way, is a preload script like the following:

```python
# jupyter-preload.py
from notebook.notebookapp import NotebookApp

def dask_setup(scheduler):
    app = NotebookApp()
    app.initialize([])
```

```bash
dask-scheduler --preload jupyter-preload.py
```

That script will run at an appropriate time during scheduler startup. You can
also put this into configuration

```yaml
distributed:
  scheduler:
    preload: ["/path/to/jupyter-preload.py"]
```

### Really though, you should use something else

This is mostly a hack. If you're at an institution then you should ask for
something like [JuptyerHub](https://jupyter.org/hub).

Or, you might also want to run this in a separate subprocess, so that Jupyter
and the Dask scheduler don't collide with each other. This shouldn't be so
much of a problem (they're both pretty light weight), but isolating them
probably makes sense.

### Thanks Nick!

Thanks to [Nick Bollweg](https://github.com/bollwyvl), who answered a [questions on this topic here](https://github.com/jupyter/notebook/issues/4873)
