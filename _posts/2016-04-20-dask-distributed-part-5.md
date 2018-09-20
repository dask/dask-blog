---
layout: post
title: Ad Hoc Distributed Random Forests
tagline: when arrays and dataframes aren't flexible enough
category: work
tags: [Programming, scipy, Python, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

*A screencast version of this post is available here:
[https://www.youtube.com/watch?v=FkPlEqB8AnE](https://www.youtube.com/watch?v=FkPlEqB8AnE)*

TL;DR.
------

Dask.distributed lets you submit individual tasks to the cluster.  We use this
ability combined with Scikit Learn to train and run a distributed random forest
on distributed tabular NYC Taxi data.

Our machine learning model does not perform well, but we do learn how to
execute ad-hoc computations easily.


Motivation
----------

In the past few posts we analyzed data on a cluster with Dask collections:

1.  [Dask.bag on JSON records](http://matthewrocklin.com/blog/work/2016/02/17/dask-distributed-part1)
2.  [Dask.dataframe on CSV data](http://matthewrocklin.com/blog/work/2016/02/22/dask-distributed-part-2)
3.  [Dask.array on HDF5 data](http://matthewrocklin.com/blog/work/2016/02/26/dask-distributed-part-3)

Often our computations don't fit neatly into the bag, dataframe, or array
abstractions.  In these cases we want the flexibility of normal code with for
loops, but still with the computational power of a cluster.  With the
dask.distributed task interface, we achieve something close to this.


Application: Naive Distributed Random Forest Algorithm
------------------------------------------------------

As a motivating application we build a random forest algorithm from the ground
up using the single-machine Scikit Learn library, and dask.distributed's
ability to quickly submit individual tasks to run on the cluster.  Our
algorithm will look like the following:

1.  Pull data from some external source (S3) into several dataframes on the
    cluster
2.  For each dataframe, create and train one `RandomForestClassifier`
3.  Scatter single testing dataframe to all machines
4.  For each `RandomForestClassifier` predict output on test dataframe
5.  Aggregate independent predictions from each classifier together by a
    majority vote.  To avoid bringing too much data to any one machine, perform
    this majority vote as a tree reduction.

Data: NYC Taxi 2015
-------------------

As in our [blogpost on distributed
dataframes](http://matthewrocklin.com/blog/work/2016/02/22/dask-distributed-part-2)
we use the data on all NYC Taxi rides in 2015.  This is around 20GB on disk and
60GB in RAM.

We predict the number of passengers in each cab given the other
numeric columns like pickup and destination location, fare breakdown, distance,
etc..

We do this first on a small bit of data on a single machine and then on the
entire dataset on the cluster.  Our cluster is composed of twelve m4.xlarges (4
cores, 15GB RAM each).

*Disclaimer and Spoiler Alert*: I am not an expert in machine learning.  Our
algorithm will perform very poorly.  If you're excited about machine
learning you can stop reading here.  However, if you're interested in how to
*build* distributed algorithms with Dask then you may want to read on,
especially if you happen to know enough machine learning to improve upon my
naive solution.


API: submit, map, gather
------------------------

We use a small number of [dask.distributed
functions](http://distributed.readthedocs.org/en/latest/api.html) to build our
computation:

```python
futures = executor.scatter(data)                     # scatter data
future = executor.submit(function, *args, **kwargs)  # submit single task
futures = executor.map(function, sequence)           # submit many tasks
results = executor.gather(futures)                   # gather results
executor.replicate(futures, n=number_of_replications)
```

In particular, functions like `executor.submit(function, *args)` let us send
individual functions out to our cluster thousands of times a second.  Because
these functions consume their own results we can create complex workflows that
stay entirely on the cluster and trust the distributed scheduler to move data
around intelligently.


Load Pandas from S3
-------------------

First we load data from Amazon S3.  We use the `s3.read_csv(..., collection=False)`
function to load 178 Pandas DataFrames on our cluster from CSV data on S3.  We
get back a list of `Future` objects that refer to these remote dataframes.  The
use of `collection=False` gives us this list of futures rather than a single
cohesive Dask.dataframe object.

```python
from distributed import Executor, s3
e = Executor('52.91.1.177:8786')

dfs = s3.read_csv('dask-data/nyc-taxi/2015',
                  parse_dates=['tpep_pickup_datetime',
                               'tpep_dropoff_datetime'],
                  collection=False)
dfs = e.compute(dfs)
```

Each of these is a lightweight `Future` pointing to a `pandas.DataFrame` on the
cluster.

```python
>>> dfs[:5]
[<Future: status: finished, type: DataFrame, key: finalize-a06c3dd25769f434978fa27d5a4cf24b>,
 <Future: status: finished, type: DataFrame, key: finalize-7dcb27364a8701f45cb02d2fe034728a>,
 <Future: status: finished, type: DataFrame, key: finalize-b0dfe075000bd59c3a90bfdf89a990da>,
 <Future: status: finished, type: DataFrame, key: finalize-1c9bb25cefa1b892fac9b48c0aef7e04>,
 <Future: status: finished, type: DataFrame, key: finalize-c8254256b09ae287badca3cf6d9e3142>]
```

If we're willing to wait a bit then we can pull data from any future back to
our local process using the `.result()` method.  We don't want to do this too
much though, data transfer can be expensive and we can't hold the entire
dataset in the memory of a single machine.  Here we just bring back one of the
dataframes:

```python
>>> df = dfs[0].result()
>>> df.head()
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>VendorID</th>
      <th>tpep_pickup_datetime</th>
      <th>tpep_dropoff_datetime</th>
      <th>passenger_count</th>
      <th>trip_distance</th>
      <th>pickup_longitude</th>
      <th>pickup_latitude</th>
      <th>RateCodeID</th>
      <th>store_and_fwd_flag</th>
      <th>dropoff_longitude</th>
      <th>dropoff_latitude</th>
      <th>payment_type</th>
      <th>fare_amount</th>
      <th>extra</th>
      <th>mta_tax</th>
      <th>tip_amount</th>
      <th>tolls_amount</th>
      <th>improvement_surcharge</th>
      <th>total_amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>2015-01-15 19:05:39</td>
      <td>2015-01-15 19:23:42</td>
      <td>1</td>
      <td>1.59</td>
      <td>-73.993896</td>
      <td>40.750111</td>
      <td>1</td>
      <td>N</td>
      <td>-73.974785</td>
      <td>40.750618</td>
      <td>1</td>
      <td>12.0</td>
      <td>1.0</td>
      <td>0.5</td>
      <td>3.25</td>
      <td>0</td>
      <td>0.3</td>
      <td>17.05</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>2015-01-10 20:33:38</td>
      <td>2015-01-10 20:53:28</td>
      <td>1</td>
      <td>3.30</td>
      <td>-74.001648</td>
      <td>40.724243</td>
      <td>1</td>
      <td>N</td>
      <td>-73.994415</td>
      <td>40.759109</td>
      <td>1</td>
      <td>14.5</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>2.00</td>
      <td>0</td>
      <td>0.3</td>
      <td>17.80</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>2015-01-10 20:33:38</td>
      <td>2015-01-10 20:43:41</td>
      <td>1</td>
      <td>1.80</td>
      <td>-73.963341</td>
      <td>40.802788</td>
      <td>1</td>
      <td>N</td>
      <td>-73.951820</td>
      <td>40.824413</td>
      <td>2</td>
      <td>9.5</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>0.00</td>
      <td>0</td>
      <td>0.3</td>
      <td>10.80</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>2015-01-10 20:33:39</td>
      <td>2015-01-10 20:35:31</td>
      <td>1</td>
      <td>0.50</td>
      <td>-74.009087</td>
      <td>40.713818</td>
      <td>1</td>
      <td>N</td>
      <td>-74.004326</td>
      <td>40.719986</td>
      <td>2</td>
      <td>3.5</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>0.00</td>
      <td>0</td>
      <td>0.3</td>
      <td>4.80</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>2015-01-10 20:33:39</td>
      <td>2015-01-10 20:52:58</td>
      <td>1</td>
      <td>3.00</td>
      <td>-73.971176</td>
      <td>40.762428</td>
      <td>1</td>
      <td>N</td>
      <td>-74.004181</td>
      <td>40.742653</td>
      <td>2</td>
      <td>15.0</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>0.00</td>
      <td>0</td>
      <td>0.3</td>
      <td>16.30</td>
    </tr>
  </tbody>
</table>

Train on a single machine
-------------------------

To start lets go through the standard Scikit Learn fit/predict/score cycle with
this small bit of data on a single machine.

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split

df_train, df_test = train_test_split(df)

columns = ['trip_distance', 'pickup_longitude', 'pickup_latitude',
           'dropoff_longitude', 'dropoff_latitude', 'payment_type',
           'fare_amount', 'mta_tax', 'tip_amount', 'tolls_amount']

est = RandomForestClassifier(n_estimators=4)
est.fit(df_train[columns], df_train.passenger_count)
```

This builds a `RandomForestClassifer` with four decision trees and then trains
it against the numeric columns in the data, trying to predict the
`passenger_count` column.  It takes around 10 seconds to train on a single
core. We now see how well we do on the holdout testing data:

```python
>>> est.score(df_test[columns], df_test.passenger_count)
0.65808188654721012
```

This 65% accuracy is actually pretty poor.  About 70% of the rides in NYC have
a single passenger, so the model of "always guess one" would out-perform our
fancy random forest.

```python
>>> from sklearn.metrics import accuracy_score
>>> import numpy as np
>>> accuracy_score(df_test.passenger_count,
...                np.ones_like(df_test.passenger_count))
0.70669390028780987
```

This is where my ignorance in machine learning really
kills us.  There is likely a simple way to improve this.  However, because I'm
more interested in showing how to build distributed computations with Dask than
in actually doing machine learning I'm going to go ahead with this naive
approach.  Spoiler alert: we're going to do a lot of computation and still not
beat the "always guess one" strategy.


Fit across the cluster with executor.map
----------------------------------------

First we build a function that does just what we did before, builds a random
forest and then trains it on a dataframe.

```python
def fit(df):
    est = RandomForestClassifier(n_estimators=4)
    est.fit(df[columns], df.passenger_count)
    return est
```

Second we call this function on all of our training dataframes on the cluster
using the standard `e.map(function, sequence)` function.  This sends out many
small tasks for the cluster to run.  We use all but the last dataframe for
training data and hold out the last dataframe for testing.  There are more
principled ways to do this, but again we're going to charge ahead here.

```python
train = dfs[:-1]
test = dfs[-1]

estimators = e.map(fit, train)
```

This takes around two minutes to train on all of the 177 dataframes and now we
have 177 independent estimators, each capable of guessing how many passengers a
particular ride had.  There is relatively little overhead in this computation.


Predict on testing data
-----------------------

Recall that we kept separate a future, `test`, that points to a Pandas dataframe on
the cluster that was not used to train any of our 177 estimators.  We're going
to replicate this dataframe across all workers on the cluster and then ask each
estimator to predict the number of passengers for each ride in this dataset.

```python
e.replicate([test], n=48)

def predict(est, X):
    return est.predict(X[columns])

predictions = [e.submit(predict, est, test) for est in estimators]
```

Here we used the `executor.submit(function, *args, **kwrags)` function in a
list comprehension to individually launch many tasks.  The scheduler determines
when and where to run these tasks for optimal computation time and minimal data
transfer.  As with all functions, this returns futures that we can use to
collect data if we want in the future.

*Developers note: we explicitly replicate here in order to take advantage of
efficient tree-broadcasting algorithms.  This is purely a performance
consideration, everything would have worked fine without this, but the explicit
broadcast turns a 30s communication+computation into a 2s
communication+computation.*


Aggregate predictions by majority vote
--------------------------------------

For each estimator we now have an independent prediction of the passenger
counts for all of the rides in our test data.  In other words for each ride we
have 177 different opinions on how many passengers were in the cab.  By
averaging these opinions together we hope to achieve a more accurate consensus
opinion.

For example, consider the first four prediction arrays:

```python
>>> a_few_predictions = e.gather(predictions[:4])  # remote futures -> local arrays
>>> a_few_predictions
[array([1, 2, 1, ..., 2, 2, 1]),
 array([1, 1, 1, ..., 1, 1, 1]),
 array([2, 1, 1, ..., 1, 1, 1]),
 array([1, 1, 1, ..., 1, 1, 1])]
```

For the first ride/column we see that three of the four predictions are for a
single passenger while one prediction disagrees and is for two passengers.  We
create a consensus opinion by taking the mode of the stacked arrays:

```python
from scipy.stats import mode
import numpy as np

def mymode(*arrays):
    array = np.stack(arrays, axis=0)
    return mode(array)[0][0]

>>> mymode(*a_few_predictions)
array([1, 1, 1, ..., 1, 1, 1])
```

And so when we average these four prediction arrays together we see that the
majority opinion of one passenger dominates for all of the six rides visible
here.


Tree Reduction
--------------

We could call our `mymode` function on all of our predictions like this:

```python
>>> mode_prediction = e.submit(mymode, *predictions)  # this doesn't scale well
```

Unfortunately this would move all of our results to a single machine to compute
the mode there.  This might swamp that single machine.

Instead we batch our predictions into groups of size 10, average each group,
and then repeat the process with the smaller set of predictions until we have
only one left.  This sort of multi-step reduction is called a tree reduction.
We can write it up with a couple nested loops and `executor.submit`.  This is
only an approximation of the mode, but it's a much more scalable computation.
This finishes in about 1.5 seconds.

```python
from toolz import partition_all

while len(predictions) > 1:
    predictions = [e.submit(mymode, *chunk)
                   for chunk in partition_all(10, predictions)]

result = e.gather(predictions)[0]

>>> result
array([1, 1, 1, ..., 1, 1, 1])
```

Final Score
-----------

Finally, after completing all of our work on our cluster we can see how well
our distributed random forest algorithm does.

```python
>>> accuracy_score(result, test.result().passenger_count)
0.67061974451423045
```

Still worse than the naive "always guess one" strategy.  This just goes to show
that, no matter how sophisticated your Big Data solution is, there is no
substitute for common sense and a little bit of domain expertise.


What didn't work
----------------

As always I'll have a section like this that honestly says what doesn't work
well and what I would have done with more time.

*   Clearly this would have benefited from more machine learning knowledge.
    What would have been a good approach for this problem?
*   I've been thinking a bit about memory management of replicated data on the
    cluster.  In this exercise we specifically replicated out the test data.
    Everything would have worked fine without this step but it would have been
    much slower as every worker gathered data from the single worker that
    originally had the test dataframe.  Replicating data is great until you
    start filling up distributed RAM.  It will be interesting to think of
    policies about when to start cleaning up redundant data and when to keep it
    around.
*   Several people from both open source users and Continuum customers have
    asked about a general Dask library for machine learning, something akin to
    Spark's MLlib.  Ideally a future Dask.learn module would leverage
    Scikit-Learn in the same way that Dask.dataframe leverages Pandas.  It's
    not clear how to cleanly break up and parallelize Scikit-Learn algorithms.


Conclusion
----------

This blogpost gives a concrete example using basic task submission with
`executor.map` and `executor.submit` to build a non-trivial computation.  This
approach is straightforward and not restrictive.  Personally this interface
excites me more than collections like Dask.dataframe; there is a lot of freedom
in arbitrary task submission.

Links
-----

*  [Notebook](https://gist.github.com/mrocklin/9f5720d8658e5f2f66666815b1f03f00)
*  [Video](https://www.youtube.com/watch?v=FkPlEqB8AnE&list=PLRtz5iA93T4PQvWuoMnIyEIz1fXiJ5Pri&index=11)
*  [distributed](https://distributed.readthedocs.org/en/latest/)
