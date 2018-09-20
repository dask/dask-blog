---
layout: post
title: Dask EC2 Startup Script
tagline: The hardest step is standing up
category : work
draft: true
tags : [Programming, scipy, Python, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the [XDATA Program](http://www.darpa.mil/program/XDATA)
as part of the [Blaze Project](http://blaze.pydata.org)*

*A screencast version of this post is available here:
[https://youtu.be/KGlhU9kSfVk](https://youtu.be/KGlhU9kSfVk)*

Summary
-------

Copy-pasting the following commands gives you a Dask cluster on EC2.

```
pip install dec2
dec2 up --keyname YOUR-AWS-KEY-NAME
        --keypair ~/.ssh/YOUR-AWS-KEY-FILE.pem
        --count 9   # Provision nine nodes
        --nprocs 8  # Use eight separate worker processes per node

dec2 ssh            # SSH into head node
ipython             # Start IPython console on head node
```

```python
from distributed import Executor, s3, progress
e = Executor('127.0.0.1:8786')
df = s3.read_csv('dask-data/nyc-taxi/2015', lazy=False)
progress(df)
df.head()
```

You will have to use your own AWS credentials, but you'll get fast distributed
Pandas access on the NYCTaxi data across a cluster, loaded from S3.


Motivation
----------

*Reducing barriers to entry enables curious play.*

Curiosity drives us to play with new tools.  We love the idea that previously
difficult tasks will suddenly become easy, expanding our abilities and opening
up a range of newly solvable problems.

However, as our problems grow more complex our tools grow more cumbersome and
setup costs increase.  This cost stops us from playing around, which is a
shame, because playing is good both for the education of the user and for the
development of the tool.  Tool makers who want feedback are strongly
incentivized to decrease setup costs, especially for the play case.

In February we introduced dask.distributed, a lightweight distributed computing
framework for Python.  We focused on processing data with high level
abstractions like dataframes and arrays in the following blogposts:

1.  [Analyze GitHub JSON record data in S3](http://matthewrocklin.com/blog/work/2016/02/17/dask-distributed-part1)
2.  [Use Dask DataFrames on CSV data in HDFS](http://matthewrocklin.com/blog/work/2016/02/22/dask-distributed-part-2)
3.  [Process NetCDF data with Dask arrays on a traditional cluster](http://matthewrocklin.com/blog/work/2016/02/26/dask-distributed-part-3)

Today we present a simple setup script to launch dask.distributed on EC2,
enabling any user with AWS credentials to repeat these experiments easily.


dec2
----

*Devops tooling and EC2 to the rescue*

[DEC2](https://github.com/dask/dec2/) does the following:

1.  Provisions nodes on EC2 using your AWS credentials
2.  Installs Anaconda on those nodes
3.  Deploys a dask.distributed `Scheduler` on the head node and `Worker`s on
    the rest of the nodes
4.  Helps you to SSH into the head node or connect from your local machine

```
$ pip install dec2
$ dec2 up --help
Usage: dec2 up [OPTIONS]

Options:
  --keyname TEXT                Keyname on EC2 console  [required]
  --keypair PATH                Path to the keypair that matches the keyname [required]
  --name TEXT                   Tag name on EC2
  --region-name TEXT            AWS region  [default: us-east-1]
  --ami TEXT                    EC2 AMI  [default: ami-d05e75b8]
  --username TEXT               User to SSH to the AMI  [default: ubuntu]
  --type TEXT                   EC2 Instance Type  [default: m3.2xlarge]
  --count INTEGER               Number of nodes  [default: 4]
  --security-group TEXT         Security Group Name  [default: dec2-default]
  --volume-type TEXT            Root volume type  [default: gp2]
  --volume-size INTEGER         Root volume size (GB)  [default: 500]
  --file PATH                   File to save the metadata  [default: cluster.yaml]
  --provision / --no-provision  Provision salt on the nodes  [default: True]
  --dask / --no-dask            Install Dask.Distributed in the cluster [default: True]
  --nprocs INTEGER              Number of processes per worker  [default: 1]
  -h, --help                    Show this message and exit.
```

*Note: dec2 was largely built by [Daniel Rodriguez](https://github.com/danielfrg)*

Run
---

As an example we use `dec2` to create a new cluster of nine nodes.  Each worker
will run with eight processes, rather than using threads.

    dec2 up --keyname my-key-name
            --keypair ~/.ssh/my-key-file.pem
            --count 9       # Provision nine nodes
            --nprocs 8      # Use eight separate worker processes per node

### Connect

We ssh into the head node and start playing in an IPython terminal:

    localmachine:~$ dec2 ssh                          # SSH into head node
    ec2-machine:~$ ipython                            # Start IPython console

```python
In [1]: from distributed import Executor, s3, progress
In [2]: e = Executor('127.0.0.1:8786')
In [3]: e
Out[3]: <Executor: scheduler=127.0.0.1:8786 workers=64 threads=64>
```


### Notebooks

Alternatively we set up a globally visible Jupyter notebook server:

    localmachine:~$ dec2 dask-distributed address    # Get location of head node
    Scheduler Address: XXX:XXX:XXX:XXX:8786

    localmachine:~$ dec2 ssh                          # SSH into head node
    ec2-machine:~$ jupyter notebook --ip="*"          # Start Jupyter Server

Then navigate to `http://XXX:XXX:XXX:XXX:8888` from your local browser.  Note,
this method is not secure, see [Jupyter
docs](http://jupyter-notebook.readthedocs.org/en/latest/public_server.html) for
a better solution.


### Public datasets

We repeat the experiments from our
[earlier blogpost](http://matthewrocklin.com/blog/work/2016/02/22/dask-distributed-part-2)
on NYCTaxi data.

```python
df = s3.read_csv('dask-data/nyc-taxi/2015', lazy=False)
progress(df)
df.head()
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


Acknowledgments
---------------

The `dec2` startup script is largely the work of Daniel Rodriguez.  Daniel
usually works on [Anaconda for cluster
management](https://docs.continuum.io/anaconda-cluster/index) which is normally
part of an Anaconda subscription but is also free for moderate use (4 nodes.)
This does things similar to `dec2`, but much more maturely.

DEC2 was inspired by the excellent `spark-ec2` setup script, which is how most
Spark users, myself included, were first able to try out the library.  The
`spark-ec2` script empowered many new users to try out a distributed system for
the first time.

The S3 work was largely done by Hussain Sultan (Capital One) and Martin Durant
(Continuum).


What didn't work
----------------

*  Originally we automatically started an IPython console on the local machine
   and connected it to the remote scheduler.  This felt slick, but was error
   prone due to mismatches between the user's environment and the remote
   cluster's environment.
*  It's tricky to replicate functionality that's part of a proprietary
   product (Anaconda for cluster management.)  Fortunately, Continuum
   management has been quite supportive.
*  There aren't many people in the data science community who know Salt, the
   system that backs `dec2`.  I expect maintenance to be a bit tricky moving
   forward, especially during periods when Daniel and other developers are
   occupied.

Links
-----

*   [dec2](https://github.com/dask/dec2)
*   [dask.distributed](https://distributed.readthedocs.org/en/latest/)
