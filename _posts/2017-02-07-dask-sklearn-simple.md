---
layout: post
title: Two Easy Ways to Use Scikit Learn and Dask
category: work
tags: [Programming, Python, scipy]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
the [XDATA Program](http://www.darpa.mil/program/XDATA)
and the Data Driven Discovery Initiative from the [Moore
Foundation](https://www.moore.org/)*

Summary
-------

This post describes two simple ways to use Dask to parallelize Scikit-Learn
operations either on a single computer or across a cluster.

1.  Use the Dask Joblib backend
2.  Use the `dklearn` projects drop-in replacements for `Pipeline`,
`GridSearchCV`, and `RandomSearchCV`

For the impatient, these look like the following:

```python
### Joblib

from joblib import parallel_backend
with parallel_backend('dask.distributed', scheduler_host='scheduler-address:8786'):
    # your now-cluster-ified sklearn code here


### Dask-learn pipeline and GridSearchCV drop-in replacements

# from sklearn.grid_search import GridSearchCV
  from dklearn.grid_search import GridSearchCV
# from sklearn.pipeline import Pipeline
  from dklearn.pipeline import Pipeline
```

However, neither of these techniques are perfect.  These are the easiest things
to try, but not always the best solutions.  This blogpost focuses on
low-hanging fruit.


Joblib
------

Scikit-Learn already parallelizes across a multi-core CPU using
[Joblib](https://pythonhosted.org/joblib/), a simple but powerful and mature
library that provides an extensible map operation.  Here is a simple example of
using Joblib on its own without sklearn:

```python
# Sequential code
from time import sleep
def slowinc(x):
    sleep(1)  # take a bit of time to simulate real work
    return x + 1

>>> [slowinc(i) for i in range(10)]  # this takes 10 seconds
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Parallel code
from joblib import Parallel, delayed
>>> Parallel(n_jobs=4)(delayed(slowinc)(i) for i in range(10))  # this takes 3 seconds
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

Dask users will recognize the `delayed` function modifier.  Dask stole
the `delayed` decorator from Joblib.

Many of Scikit-learn's parallel algorithms use Joblib internally.  If we can
extend Joblib to clusters then we get some added parallelism from
joblib-enabled Scikit-learn functions immediately.


### Distributed Joblib

Fortunately Joblib provides an interface for other parallel systems to step in
and act as an execution engine.  We can do this with the `parallel_backend`
context manager to run with hundreds or thousands of cores in a nearby cluster:

```python
import distributed.joblib
from joblib import parallel_backend

with parallel_backend('dask.distributed', scheduler_host='scheduler-address:8786'):
    print(Parallel()(delayed(slowinc)(i) for i in list(range(100))))
```

The main value for Scikit-learn users here is that Scikit-learn already uses
`joblib.Parallel` within its code, so this trick works with the Scikit-learn
code that you already have.

So we can use Joblib to parallelize normally on our multi-core processor:

```python
estimator = GridSearchCV(n_jobs=4, ...)  # use joblib on local multi-core processor
```

*or* we can use Joblib together with Dask.distributed to parallelize across a
multi-node cluster:

```python
with parallel_backend('dask.distributed', scheduler_host='scheduler-address:8786'):
    estimator = GridSearchCV(...)  # use joblib with Dask cluster
```

(There will be a more thorough example towards the end)

### Limitations

Joblib is used throughout many algorithms in Scikit-learn, but not all.
Generally any operation that accepts an `n_jobs=` parameter is a possible
choice.

From Dask's perspective Joblib's interface isn't ideal.  For example it will
always collect intermediate results back to the main process, rather than
leaving them on the cluster until necessary.  For computationally intense
operations this is fine but does add some unnecessary communication overhead.
Also Joblib doesn't allow for operations more complex than a parallel map, so
the range of algorithms that this can parallelize is somewhat limited.

Still though, given the wide use of Joblib-accelerated workflows (particularly
within Scikit-learn) this is a simple thing to try if you have a cluster nearby
with a possible large payoff.


Dask-learn Pipeline and Gridsearch
----------------------------------

In July 2016, Jim Crist built and [wrote
about](http://jcrist.github.io/blog.html) a small project,
[dask-learn](https://github.com/dask/dask-learn).  This project was a
collaboration with SKLearn developers and an attempt to see which parts of
Scikit-learn were trivially and usefully parallelizable.  By far the most
productive thing to come out of this work were Dask variants of Scikit-learn's
Pipeline, GridsearchCV, and RandomSearchCV objects that better handle nested
parallelism.  Jim observed significant speedups over SKLearn code by using
these drop-in replacements.

So if you replace the following imports you may get both better single-threaded
performance *and* the ability to scale out to a cluster:

```python
# from sklearn.grid_search import GridSearchCV
  from dklearn.grid_search import GridSearchCV
# from sklearn.pipeline import Pipeline
  from dklearn.pipeline import Pipeline
```

Here is a simple example from [Jim's more in-depth blogpost](http://jcrist.github.io/dask-sklearn-part-1.html):

```python
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=10000,
                           n_features=500,
                           n_classes=2,
                           n_redundant=250,
                           random_state=42)

from sklearn import linear_model, decomposition
from sklearn.pipeline import Pipeline
from dklearn.pipeline import Pipeline

logistic = linear_model.LogisticRegression()
pca = decomposition.PCA()
pipe = Pipeline(steps=[('pca', pca),
                       ('logistic', logistic)])


#Parameters of pipelines can be set using ‘__’ separated parameter names:
grid = dict(pca__n_components=[50, 100, 150, 250],
            logistic__C=[1e-4, 1.0, 10, 1e4],
            logistic__penalty=['l1', 'l2'])

# from sklearn.grid_search import GridSearchCV
from dklearn.grid_search import GridSearchCV

estimator = GridSearchCV(pipe, grid)

estimator.fit(X, y)
```

SKLearn performs this computation in around 40 seconds while the dask-learn
drop-in replacements take around 10 seconds.  Also, if you add the following
lines to connect to a [running
cluster](http://distributed.readthedocs.io/en/latest/quickstart.html) the whole
thing scales out:

```python
from dask.distributed import Client
c = Client('scheduler-address:8786')
```

Here is a live [Bokeh](http://bokeh.pydata.org/en/latest/) plot of the
computation on a tiny eight process "cluster" running on my own laptop.  I'm
using processes here to highlight the costs of communication between processes
(red).  It's actually about 30% faster to run this computation within the same
single process.

<iframe src="https://cdn.rawgit.com/mrocklin/a2a42d71d0dd085753277821e24925a4/raw/e29b24bc656ea619eedfaba9ef176d5f3c19a040/dask-learn-task-stream.html"
        width="800" height="400"></iframe>

Conclusion
----------

This post showed a couple of simple mechanisms for scikit-learn users to
accelerate their existing workflows with Dask.  These aren't particularly
sophisticated, nor are they performance-optimal, but they are easy to
understand and easy to try out.  In a future blogpost I plan to cover more
complex ways in which Dask can accelerate sophisticated machine learning
workflows.


What we could have done better
------------------------------

As always, I include a brief section on what went wrong or what we could have
done better with more time.

-   See the bottom of [Jim's post](http://jcrist.github.io/dask-sklearn-part-1.html)
    for a more thorough explanation of "what we could have done better" for
    dask-learn's pipeline and gridsearch
-   Joblib + Dask.distributed interaction is convenient, but leaves some
    performance on the table.  It's not clear how Dask can help the sklearn
    codebase without being too invasive.
-   It would have been nice to spin up an actual cluster on parallel hardware
    for this post.  I wrote this quickly (in a few hours) so decided to skip
    this.  If anyone wants to write a follow-on experiment I would be happy
    to publish it.
