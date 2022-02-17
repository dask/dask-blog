---
layout: post
title: Running Dask and MPI programs together
tagline: an experiment
author: Matthew Rocklin
tags: [MPI]
theme: twitter
---

{% include JB/setup %}

## Executive Summary

We present an experiment on how to pass data from a loosely coupled parallel
computing system like Dask to a tightly coupled parallel computing system like
MPI.

We give motivation and a complete digestible example.

[Here is a gist of the code and results](https://gist.github.com/mrocklin/193a9671f1536b9d13524214798da4a8).

## Motivation

_Disclaimer: Nothing in this post is polished or production ready. This is an
experiment designed to start conversation. No long-term support is offered._

We often get the following question:

> How do I use Dask to pre-process my data,
> but then pass those results to a traditional MPI application?

You might want to do this because you're supporting legacy code written
in MPI, or because your computation requires tightly coupled parallelism of the
sort that only MPI can deliver.

## First solution: Write to disk

The simplest thing to do of course is to write your Dask results to disk and
then load them back from disk with MPI. Given the relative cost of your
computation to data loading, this might be a great choice.

For the rest of this blogpost we're going to assume that it's not.

## Second solution

We have a trivial MPI library written in [MPI4Py](https://mpi4py.readthedocs.io/en/stable/)
where each rank just prints out all the data that it was given. In principle
though it could call into C++ code, and do arbitrary MPI things.

```python
# my_mpi_lib.py
from mpi4py import MPI

comm = MPI.COMM_WORLD

def print_data_and_rank(chunks: list):
    """ Fake function that mocks out how an MPI function should operate

    -   It takes in a list of chunks of data that are present on this machine
    -   It does whatever it wants to with this data and MPI
        Here for simplicity we just print the data and print the rank
    -   Maybe it returns something
    """
    rank = comm.Get_rank()

    for chunk in chunks:
        print("on rank:", rank)
        print(chunk)

    return sum(chunk.sum() for chunk in chunks)
```

In our dask program we're going to use Dask normally to load in data, do some
preprocessing, and then hand off all of that data to each MPI rank, which will
call the `print_data_and_rank` function above to initialize the MPI
computation.

```python
# my_dask_script.py

# Set up Dask workers from within an MPI job using the dask_mpi project
# See https://dask-mpi.readthedocs.io/en/latest/

from dask_mpi import initialize
initialize()

from dask.distributed import Client, wait, futures_of
client = Client()

# Use Dask Array to "load" data (actually just create random data here)

import dask.array as da
x = da.random.random(100000000, chunks=(1000000,))
x = x.persist()
wait(x)

# Find out where data is on each worker
# TODO: This could be improved on the Dask side to reduce boiler plate

from toolz import first
from collections import defaultdict
key_to_part_dict = {str(part.key): part for part in futures_of(x)}
who_has = client.who_has(x)
worker_map = defaultdict(list)
for key, workers in who_has.items():
    worker_map[first(workers)].append(key_to_part_dict[key])


# Call an MPI-enabled function on the list of data present on each worker

from my_mpi_lib import print_data_and_rank

futures = [client.submit(print_data_and_rank, list_of_parts, workers=worker)
           for worker, list_of_parts in worker_map.items()]

wait(futures)

client.close()
```

Then we can call this mix of Dask and an MPI program using normal `mpirun` or
`mpiexec` commands.

```
mpirun -np 5 python my_dask_script.py
```

## What just happened

So MPI started up and ran our script.
The [dask-mpi](https://dask-mpi.readthedocs.io/en/latest/) project set a Dask
scheduler on rank 0, runs our client code on rank 1, and then runs a bunch of workers on ranks 2+.

- Rank 0: Runs a Dask scheduler
- Rank 1: Runs our script
- Ranks 2+: Run Dask workers

Our script then created a Dask array, though presumably here it would read in
data from some source, do more complex Dask manipulations before continuing on.

We then wait until all of the Dask work has finished and is in a quiet state.
We then query the state in the scheduler to find out where all of that data
lives. That's this code here:

```python
# Find out where data is on each worker
# TODO: This could be improved on the Dask side to reduce boiler plate

from toolz import first
from collections import defaultdict
key_to_part_dict = {str(part.key): part for part in futures_of(x)}
who_has = client.who_has(x)
worker_map = defaultdict(list)
for key, workers in who_has.items():
    worker_map[first(workers)].append(key_to_part_dict[key])
```

Admittedly, this code is gross, and not particularly friendly or obvious to
non-Dask experts (or even Dask experts themselves, I had to steal this from the
[Dask XGBoost project](http://ml.dask.org/xgboost.html), which does
the same trick).

But after that we just call our MPI library's initialize function,
`print_data_and_rank` on all of our data using Dask's
[Futures interface](http://docs.dask.org/en/latest/futures.html).
That function gets the data directly from local memory (the Dask workers and
MPI ranks are in the same process), and does whatever the MPI application
wants.

## Future work

This could be improved in a few ways:

1.  The "gross" code referred to above could probably be placed into some
    library code to make this pattern easier for people to use.

2.  Ideally the Dask part of the computation wouldn't also have to be managed
    by MPI, but could maybe start up MPI on its own.

    You could imagine Dask running on something like Kubernetes doing highly
    dynamic work, scaling up and down as necessary. Then it would get to a
    point where it needed to run some MPI code so it would, itself, start up
    MPI on its worker processes and run the MPI application on its data.

3.  We haven't really said anything about resilience here. My guess is that
    this isn't hard to do (Dask has plenty of mechanisms to build complex
    inter-task relationships) but I didn't solve it above.

[Here is a gist of the code and results](https://gist.github.com/mrocklin/193a9671f1536b9d13524214798da4a8).
