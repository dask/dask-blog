---
layout: post
title: Towards Out-of-core ND-Arrays -- Dask + Toolz = Bag
category : work
tags : [scipy, Python, Programming, Blaze, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

**tl;dr** We use dask to build a parallel Python list.

Introduction
------------

This is the seventh in a sequence of posts constructing an out-of-core nd-array
using NumPy, and dask.  You can view these posts here:

1. [Simple task scheduling](http://matthewrocklin.com/blog/work/2014/12/27/Towards-OOC/),
2. [Frontend usability](http://matthewrocklin.com/blog/work/2014/12/30/Towards-OOC-Frontend/)
3. [A multi-threaded scheduler](http://matthewrocklin.com/blog/work/2015/01/06/Towards-OOC-Scheduling/)
4. [Matrix Multiply Benchmark](http://matthewrocklin.com/blog/work/2015/01/14/Towards-OOC-MatMul/)
5. [Spilling to disk](http://matthewrocklin.com/blog/work/2015/01/16/Towards-OOC-SpillToDisk/)
6. [Slicing and Stacking](http://matthewrocklin.com/blog/work/2015/02/13/Towards-OOC-Slicing-and-Stacking/)

Today we take a break from ND-Arrays and show how task scheduling can attack
other collections like the simple `list` of Python objects.


Unstructured Data
-----------------

Often before we have an `ndarray` or a `table/DataFrame` we have unstructured
data like log files.  In this case tuned subsets of the language (e.g.
`numpy`/`pandas`) aren't sufficient, we need the full Python language.

My usual approach to the inconveniently large dump of log files is to use
Python [streaming
iterators](http://toolz.readthedocs.org/en/latest/streaming-analytics.html)
along with [multiprocessing or IPython
Parallel](http://toolz.readthedocs.org/en/latest/parallelism.html) on a single
large machine.  I often write/speak about this workflow when discussing
[`toolz`](http://toolz.readthedocs.org/).

This workflow grows complex for most users when you introduce many processes.
To resolve this we build our normal tricks into a new `dask.Bag` collection.


Bag
---

In the same way that `dask.array` mimics NumPy operations (e.g. matrix
multiply, slicing), `dask.bag` mimics functional operations like `map`,
`filter`, `reduce` found in the standard library as well as many of the
streaming functions found in `toolz`.

*  Dask array = NumPy + threads
*  Dask bag = Python/Toolz + processes


Example
-------

Here's the obligatory wordcount example

{% highlight Python %}
>>> from dask.bag import Bag

>>> b = Bag.from_filenames('data/*.txt')

>>> def stem(word):
...     """ Stem word to primitive form """
...     return word.lower().rstrip(",.!:;'-\"").lstrip("'\"")

>>> dict(b.map(str.split).map(concat).map(stem).frequencies())
{...}
{% endhighlight %}

We use all of our cores and stream through memory on each core.  We use
`multiprocessing` but could get fancier with some work.


Related Work
------------

There are a lot of much larger much more powerful systems that have a similar
API, notably [Spark](http://spark.apache.org/) and
[DPark](https://github.com/douban/dpark).  If you have *Big Data* and need to
use very many machines then you should stop reading this and go install them.

I mostly made dask.bag because

1.  It was very easy given the work already done on dask.array
2.  I often only need multiprocessing + a heavy machine
3.  I wanted something trivially pip installable that didn't use the JVM

But again, if you have *Big Data*, then this isn't for you.


Design
------

As before, a `Bag` is just a dict holding tasks, along with a little meta data.

{% highlight Python %}
>>> d = {('x', 0): (range, 5),
...      ('x', 1): (range, 5),
...      ('x', 2): (range, 5)}

>>> from dask.bag import Bag
>>> b = Bag(d, 'x', npartitions=3)
{% endhighlight %}

In this way we break up one collection

    [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4]

into three independent pieces

    [0, 1, 2, 3, 4]
    [0, 1, 2, 3, 4]
    [0, 1, 2, 3, 4]

When we abstractly operate on the large collection...

{% highlight Python %}
>>> b2 = b.map(lambda x: x * 10)
{% endhighlight %}

... we generate new tasks to operate on each of the components.

{% highlight Python %}
>>> b2.dask
{('x', 0): (range, 5),
 ('x', 1): (range, 5),
 ('x', 2): (range, 5)}
 ('bag-1', 0): (map, lambda x: x * 10, ('x', 0)),
 ('bag-1', 1): (map, lambda x: x * 10, ('x', 1)),
 ('bag-1', 2): (map, lambda x: x * 10, ('x', 2))}
{% endhighlight %}

And when we ask for concrete results (the call to `list`) we spin up a
scheduler to execute the resulting dependency graph of tasks.

{% highlight Python %}
>>> list(b2)
[0, 10, 20, 30, 40, 0, 10, 20, 30, 40, 0, 10, 20, 30, 40]
{% endhighlight %}

More complex operations yield more complex dasks.  Beware, dask code is pretty
Lispy.  Fortunately these dasks are internal; users don't interact with them.

{% highlight Python %}
>>> iseven = lambda x: x % 2 == 0
>>> b3 = b.filter(iseven).count().dask
{'bag-3': (sum, [('bag-2', 1), ('bag-2', 2), ('bag-2', 0)]),
 ('bag-2', 0): (count,
                (filter, iseven, (range, 5))),
 ('bag-2', 1): (count,
                (filter, iseven, (range, 5))),
 ('bag-2', 2): (count,
                (filter, iseven, (range, 5)))}
{% endhighlight %}

The current interface for `Bag` has the following operations:

    all             frequencies         min
    any             join                product
    count           map                 std
    filter          map_partitions      sum
    fold            max                 topk
    foldby          mean                var

Manipulations of bags create task dependency graphs.  We eventually execute
these graphs in parallel.


Execution
---------

We repurpose the threaded scheduler we used for arrays to support
`multiprocessing` to provide parallelism even on pure Python code.  We're
careful to avoid unnecessary data transfer.  None of the operations listed above
requires significant communication.  Notably we don't have any concept of
*shuffling* or scatter/gather.

We [use dill](http://trac.mystic.cacr.caltech.edu/project/pathos/wiki/dill) to
take care to serialize functions properly and collect/report errors, two issues
that [plague naive use of
`multiprocessing`](http://matthewrocklin.com/blog/work/2013/12/05/Parallelism-and-Serialization/) in Python.

{% highlight Python %}
>>> list(b.map(lambda x: x * 10))  # This works!
[0, 10, 20, 30, 40, 0, 10, 20, 30, 40, 0, 10, 20, 30, 40]

>>> list(b.map(lambda x: x / 0))   # This errs gracefully!
ZeroDivisionError:  Execption in remote Process

integer division or modulo by zero

Traceback:
    ...
{% endhighlight %}

These tricks remove need for user expertise.


Productive Sweet Spot
---------------------

I think that there is a productive sweet spot in the following configuration

1.  Pure Python functions
2.  Streaming/lazy data
3.  Multiprocessing
4.  A single large machine or a few machines in an informal cluster

This setup is common and it's capable of handling terabyte scale workflows.
In my brief experience people rarely take this route.  They use single-threaded
in-memory Python until it breaks, and then seek out *Big Data Infrastructure*
like Hadoop/Spark at relatively high productivity overhead.

*Your workstation can scale bigger than you think.*


Example
-------

Here is about a gigabyte of
[network flow data](http://ita.ee.lbl.gov/html/contrib/UCB.home-IP-HTTP.html),
recording which computers made connections to which other computers on the
UC-Berkeley campus in 1996.

    846890339:661920 846890339:755475 846890340:197141 168.237.7.10:1163 83.153.38.208:80 2 8 4294967295 4294967295 846615753 176 2462 39 GET 21068906053917068819..html HTTP/1.0

    846890340:989181 846890341:2147 846890341:2268 13.35.251.117:1269 207.83.232.163:80 10 0 842099997 4294967295 4294967295 64 1 38 GET 20271810743860818265..gif HTTP/1.0

    846890341:80714 846890341:90331 846890341:90451 13.35.251.117:1270 207.83.232.163:80 10 0 842099995 4294967295 4294967295 64 1 38 GET 38127854093537985420..gif HTTP/1.0

This is actually relatively clean.  Many of the fields are space delimited (not
all) and I've already compiled and run the decade old C-code needed to
decompress it from its original format.

Lets use Bag and regular expressions to parse this.

{% highlight Python %}
In [1]: from dask.bag import Bag, into

In [2]: b = Bag.from_filenames('UCB-home-IP*.log')

In [3]: import re

In [4]: pattern = """
   ...: (?P<request_time>\d+:\d+)
   ...: (?P<response_start>\d+:\d+)
   ...: (?P<response_end>\d+:\d+)
   ...: (?P<client_ip>\d+\.\d+\.\d+\.\d+):(?P<client_port>\d+)
   ...: (?P<server_ip>\d+\.\d+\.\d+\.\d+):(?P<server_port>\d+)
   ...: (?P<client_headers>\d+)
   ...: (?P<server_headers>\d+)
   ...: (?P<if_modified_since>\d+)
   ...: (?P<response_header_length>\d+)
   ...: (?P<response_data_length>\d+)
   ...: (?P<request_url_length>\d+)
   ...: (?P<expires>\d+)
   ...: (?P<last_modified>\d+)
   ...: (?P<method>\w+)
   ...: (?P<domain>\d+..)\.(?P<extension>\w*)(?P<rest_of_url>\S*)
   ...: (?P<protocol>.*)""".strip().replace('\n', '\s+')

In [5]: prog = re.compile(pattern)

In [6]: records = b.map(prog.match).map(lambda m: m.groupdict())
{% endhighlight %}

This returns instantly.  We only compute results when necessary.  We trigger
computation by calling `list`.

{% highlight Python %}
In [7]: list(records.take(1))
Out[7]:
[{'client_headers': '2',
  'client_ip': '168.237.7.10',
  'client_port': '1163',
  'domain': '21068906053917068819.',
  'expires': '2462',
  'extension': 'html',
  'if_modified_since': '4294967295',
  'last_modified': '39',
  'method': 'GET',
  'protocol': 'HTTP/1.0',
  'request_time': '846890339:661920',
  'request_url_length': '176',
  'response_data_length': '846615753',
  'response_end': '846890340:197141',
  'response_header_length': '4294967295',
  'response_start': '846890339:755475',
  'rest_of_url': '',
  'server_headers': '8',
  'server_ip': '83.153.38.208',
  'server_port': '80'}]
{% endhighlight %}

Because bag operates lazily this small result also returns immediately.

To demonstrate depth we find the ten client/server pairs with the most
connections.

{% highlight Python %}
In [8]: counts = records.pluck(['client_ip', 'server_ip']).frequencies()

In [9]: %time list(counts.topk(10, key=lambda x: x[1]))
CPU times: user 11.2 s, sys: 1.15 s, total: 12.3 s
Wall time: 50.4 s
Out[9]:
[(('247.193.34.56', '243.182.247.102'), 35353),
 (('172.219.28.251', '47.61.128.1'), 22333),
 (('240.97.200.0', '108.146.202.184'), 17492),
 (('229.112.177.58', '47.61.128.1'), 12993),
 (('146.214.34.69', '119.153.78.6'), 12554),
 (('17.32.139.174', '179.135.20.36'), 10166),
 (('97.166.76.88', '65.81.49.125'), 8155),
 (('55.156.159.21', '157.229.248.255'), 7533),
 (('55.156.159.21', '124.77.75.86'), 7506),
 (('55.156.159.21', '97.5.181.76'), 7501)]
{% endhighlight %}


Comparison with Spark
---------------------

First, it is silly and unfair to compare with PySpark running locally.  PySpark
offers much more in a distributed context.

{% highlight Python %}
In [1]: import pyspark

In [2]: sc = pyspark.SparkContext('local')

In [3]: from glob import glob
In [4]: filenames = sorted(glob('UCB-home-*.log'))
In [5]: rdd = sc.parallelize(filenames, numSlices=4)

In [6]: import re
In [7]: pattern = ...
In [8]: prog = re.compile(pattern)

In [9]: lines = rdd.flatMap(lambda fn: list(open(fn)))
In [10]: records = lines.map(lambda line: prog.match(line).groupdict())
In [11]: ips = records.map(lambda rec: (rec['client_ip'], rec['server_ip']))

In [12]: from toolz import topk
In [13]: %time dict(topk(10, ips.countByValue().items(), key=1))
CPU times: user 1.32 s, sys: 52.2 ms, total: 1.37 s
Wall time: 1min 21s
Out[13]:
{('146.214.34.69', '119.153.78.6'): 12554,
 ('17.32.139.174', '179.135.20.36'): 10166,
 ('172.219.28.251', '47.61.128.1'): 22333,
 ('229.112.177.58', '47.61.128.1'): 12993,
 ('240.97.200.0', '108.146.202.184'): 17492,
 ('247.193.34.56', '243.182.247.102'): 35353,
 ('55.156.159.21', '124.77.75.86'): 7506,
 ('55.156.159.21', '157.229.248.255'): 7533,
 ('55.156.159.21', '97.5.181.76'): 7501,
 ('97.166.76.88', '65.81.49.125'): 8155}
{% endhighlight %}

So, given a compute-bound mostly embarrassingly parallel task (regexes are
comparatively expensive) on a single machine they are comparable.

Reasons you would want to use Spark

*  You want to use many machines and interact with HDFS
*  Shuffling operations

Reasons you would want to use dask.bag

*  Trivial installation
*  No mucking about with JVM heap sizes or config files
*  Nice error reporting.  Spark error reporting includes the typical giant
   Java Stack trace that comes with any JVM solution.
*  Easier/simpler for Python programmers to hack on.
   The implementation is 350 lines including comments.

Again, this is really just a toy experiment to show that the dask model isn't
just about arrays.  I absolutely do not want to throw Dask in the ring with
Spark.


Conclusion
----------

However I do want to stress the importance of single-machine parallelism.
Dask.bag targets this application well and leverages common hardware in a
simple way that is both natural and accessible to most Python programmers.

A skilled developer could extend this to work in a distributed memory context.
The logic to create the task dependency graphs is separate from the scheduler.

Special thanks to [Erik Welch](http://github.com/eriknw) for finely crafting
the dask optimization passes that keep the data flowly smoothly.
