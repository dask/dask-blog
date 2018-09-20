---
layout: post
title: Notes on Kafka in Python
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

Summary
-------

<img src="https://kafka.apache.org/images/logo.png"
     align="right"
     width="40%">

I recently investigated the state of Python libraries for Kafka.  This blogpost
contains my findings.

Both [PyKafka](http://pykafka.readthedocs.io/en/latest/) and
[confluent-kafka](https://github.com/confluentinc/confluent-kafka-python) have
mature implementations and are maintained by invested companies.
Confluent-kafka is generally faster while PyKafka is arguably better designed
and documented for Python usability.

Conda packages are now available for both.  I hope to extend one or both to
support asynchronous workloads with Tornado.

*Disclaimer: I am not an expert in this space.  I have no strong affiliation
with any of these projects.  This is a report based on my experience of the
past few weeks.  I don't encourage anyone to draw conclusions from this work.
I encourage people to investigate on their own.*


Introduction
------------

[Apache Kafka](https://kafka.apache.org/) is a common data system for streaming
architectures.  It manages rolling buffers of byte messages and provides a
scalable mechanism to publish or subscribe to those buffers in real time.
While Kafka was originally designed within the JVM space the fact that it only
manages bytes makes it easy to access from native code systems like C/C++ and
Python.


Python Options
--------------

Today there are three independent Kafka implementations in Python, two of which
are optionally backed by a C implementation,
[librdkafka](https://github.com/edenhill/librdkafka), for speed:

-  [kafka-python](https://kafka-python.readthedocs.io/en/master/): The first on
   the scene, a Pure Python Kafka client with robust documentation and an API
   that is fairly faithful to the original Java API.  This implementation has
   the most stars on GitHub, the most active development team (by number of
   committers) but also lacks a connection to the fast C library.  I'll admit
   that I didn't spend enough time on this project to judge it well because of
   this.

-  [PyKafka](http://pykafka.readthedocs.io/en/latest/): The second
   implementation chronologically.  This library is maintained by
   [Parse.ly](https://www.parse.ly/) a web analytics company that heavily uses
   both streaming systems and Python.  PyKafka's API is more creative and
   designed to follow common Python idioms rather than the Java API.  PyKafka
   has both a pure Python implementation and connections to the low-level
   `librdkafka` C library for increased performance.

-  [Confluent-kafka](https://github.com/confluentinc/confluent-kafka-python):
   Is the final implementation chronologically.  It is maintained by
   [Confluent](https://www.confluent.io/home), the primary for-profit company
   that supports and maintains Kafka.  This library is the fastest, but also
   the least accessible from a Python perspective.  This implementation is
   written in CPython extensions, and the documentation is minimal.  However,
   if you are coming from the Java API then this is entirely consistent with
   that experience, so that documentation probably suffices.


Performance
-----------

Confluent-kafka message-consumption bandwidths are around 50% higher and
message-production bandwidths are around 3x higher than PyKafka, both of which
are significantly higher than kafka-python.  I'm taking these numbers from
[this
blogpost](http://activisiongamescience.github.io/2016/06/15/Kafka-Client-Benchmarking/)
which gives benchmarks comparing the three libraries.  The primary numeric
results follow below:

*Note: It's worth noting that this blogpost was moving smallish 100 byte messages
around.  I would hope that Kafka would perform better (closer to network
bandwidths) when messages are of a decent size.*

### Producer Throughput

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time_in_seconds</th>
      <th>MBs/s</th>
      <th>Msgs/s</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>confluent_kafka_producer</th>
      <td>5.4</td>
      <td>17</td>
      <td>183000</td>
    </tr>
    <tr>
      <th>pykafka_producer_rdkafka</th>
      <td>16</td>
      <td>6.1</td>
      <td>64000</td>
    </tr>
    <tr>
      <th>pykafka_producer</th>
      <td>57</td>
      <td>1.7</td>
      <td>17000</td>
    </tr>
    <tr>
      <th>python_kafka_producer</th>
      <td>68</td>
      <td>1.4</td>
      <td>15000</td>
    </tr>
  </tbody>
</table>


### Consumer Throughput

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time_in_seconds</th>
      <th>MBs/s</th>
      <th>Msgs/s</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>confluent_kafka_consumer</th>
      <td>3.8</td>
      <td>25</td>
      <td>261000</td>
    </tr>
    <tr>
      <th>pykafka_consumer_rdkafka</th>
      <td>6.1</td>
      <td>17</td>
      <td>164000</td>
    </tr>
    <tr>
      <th>pykafka_consumer</th>
      <td>29</td>
      <td>3.2</td>
      <td>34000</td>
    </tr>
    <tr>
      <th>python_kafka_consumer</th>
      <td>26</td>
      <td>3.6</td>
      <td>38000</td>
    </tr>
  </tbody>
</table>


*Note: I discovered this article on [parsely/pykafka #559](https://github.com/Parsely/pykafka/issues/559), which has good conversation about the three libraries.*

I profiled PyKafka in these cases and it doesn't appear that these code paths
have yet been optimized.  I expect that modest effort could close that gap
considerably.  This difference seems to be more from lack of interest than any
hard design constraint.

It's not clear how critical these speeds are.  According to the PyKafka
maintainers at Parse.ly they haven't actually turned on the librdkafka
optimizations in their internal pipelines, and are instead using the slow
Pure Python implementation, which is apparently more than fast enough for
common use.  Getting messages out of Kafka just isn't their bottleneck.  It may
be that these 250,000 messages/sec limits are not significant in most
applications.  I suspect that this matters more in bulk analysis workloads than
in online applications.


Pythonic vs Java APIs
---------------------

It took me a few times to get confluent-kafka to work.  It wasn't clear what
information I needed to pass to the constructor to connect to Kafka and when I
gave the wrong information I received no message that I had done anything
incorrectly.  Docstrings and documentation were both minimal.  In contrast,
PyKafka's API and error messages quickly led me to correct behavior and I was
up and running within a minute.

However, I persisted with confluent-kafka, found the right [Java
documentation](https://kafka.apache.org/documentation/#api), and eventually did
get things up and running.  Once this happened everything fell into place and I
was able to easily build applications with Confluent-kafka that were both
simple and fast.


Development experience
----------------------

I would like to add asynchronous support to one or both of these libraries so
that they can read or write data in a non-blocking fashion and play nicely with
other asynchronous systems like Tornado or Asyncio.  I started investigating
this with both libraries on GitHub.

### Developers

Both libraries have a maintainer who is somewhat responsive and whose time is
funded by the parent company.  Both maintainers seem active on a day-to-day
basis and handle contributions from external developers.

Both libraries are fully active with a common pattern of a single main dev
merging work from a number of less active developers.  Distributions of commits
over the last six months look similar:

```
confluent-kafka-python$ git shortlog -ns --since "six months ago"
38  Magnus Edenhill
5  Christos Trochalakis
4  Ewen Cheslack-Postava
1  Simon Wahlgren

pykafka$ git shortlog -ns --since "six months ago"
52  Emmett Butler
23  Emmett J. Butler
20  Marc-Antoine Parent
18  Tanay Soni
5  messense
1  Erik Stephens
1  Jeff Widman
1  Prateek Shrivastava
1  aleatha
1  zpcui
```

### Codebase

In regards to the codebases I found that PyKafka was easier to hack on for a
few reasons:

1.  Most of PyKafka is written in Python rather than C extensions, and so it is
    more accessible to a broader development base.  I find that Python C
    extensions are not pleasant to work with, even if you are comfortable with
    C.
2.  PyKafka appears to be much more extensively tested.  PyKafka actually spins
    up a local Kafka instance to do comprehensive integration tests while
    Confluent-kafka seems to only test API without actually running against a
    real Kakfa instance.
3.  For what it's worth, PyKafka maintainers [responded
    quickly](https://github.com/Parsely/pykafka/issues/731) to an issue on
    Tornado.  Confluent-kafka maintainers still have not responded to a
    [comment on an existing Tornado
    issue](https://github.com/confluentinc/confluent-kafka-python/issues/100#issuecomment-334152182),
    even though that comment had signfiicnatly more content (a working
    prototype).

*To be clear, no maintainer has any responsibility to answer my questions on
github.  They are likely busy with other things that are of more relevance to
their particular mandate.*


Conda packages
--------------

I've pushed/updated recipes for both packages on conda-forge.  You can install
them as follows:

    conda install -c conda-forge pykafka                 # Linux, Mac, Windows
    conda install -c conda-forge python-confluent-kafka  # Linux, Mac

In both cases this these are built against the fast `librdkafka` C library
(except on Windows) and install that library as well.


Future plans
------------

I've recently started work on streaming systems and pipelines for
[Dask](http://dask.pydata.org/en/latest/), so I'll probably continue to
investigate this space.  I'm still torn between the two implementations.  There
are strong reasons to use either of them.

Culturally I am drawn to Parse.ly's PyKafka library.  They're clearly Python
developers writing for Python users.  However the costs of using a non-Pythonic
system here just aren't that large (Kafka's API is small), and Confluent's
interests are more aligned with investing in Kafka long term than are
Parse.ly's.
