---
layout: post
title: Use Apache Parquet
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Continuum Analytics](http://continuum.io)
and the Data Driven Discovery Initiative from the [Moore
Foundation](https://www.moore.org/).*

This is a tiny blogpost to encourage you to use
[Parquet](http://parquet.apache.org/) instead of CSV for your dataframe
computations.  I'll use Dask.dataframe here but Pandas would work just as well.
I'll also use my local laptop here, but Parquet is an excellent format to use
on a cluster.

### CSV is convenient, but slow

I have the NYC taxi cab dataset on my laptop stored as CSV

```
mrocklin@carbon:~/data/nyc/csv$ ls
yellow_tripdata_2015-01.csv  yellow_tripdata_2015-07.csv
yellow_tripdata_2015-02.csv  yellow_tripdata_2015-08.csv
yellow_tripdata_2015-03.csv  yellow_tripdata_2015-09.csv
yellow_tripdata_2015-04.csv  yellow_tripdata_2015-10.csv
yellow_tripdata_2015-05.csv  yellow_tripdata_2015-11.csv
yellow_tripdata_2015-06.csv  yellow_tripdata_2015-12.csv
```

This is a convenient format for humans because we can read it directly.

```
mrocklin@carbon:~/data/nyc/csv$ head yellow_tripdata_2015-01.csv
VendorID,tpep_pickup_datetime,tpep_dropoff_datetime,passenger_count,trip_distance,pickup_longitude,pickup_latitude,RateCodeID,store_and_fwd_flag,dropoff_longitude,dropoff_latitude,payment_type,fare_amount,extra,mta_tax,tip_amount,tolls_amount,improvement_surcharge,total_amount
2,2015-01-15 19:05:39,2015-01-15
19:23:42,1,1.59,-73.993896484375,40.750110626220703,1,N,-73.974784851074219,40.750617980957031,1,12,1,0.5,3.25,0,0.3,17.05
1,2015-01-10 20:33:38,2015-01-10
20:53:28,1,3.30,-74.00164794921875,40.7242431640625,1,N,-73.994415283203125,40.759109497070313,1,14.5,0.5,0.5,2,0,0.3,17.8
1,2015-01-10 20:33:38,2015-01-10
20:43:41,1,1.80,-73.963340759277344,40.802787780761719,1,N,-73.951820373535156,40.824413299560547,2,9.5,0.5,0.5,0,0,0.3,10.8
1,2015-01-10 20:33:39,2015-01-10
20:35:31,1,.50,-74.009086608886719,40.713817596435547,1,N,-74.004325866699219,40.719985961914063,2,3.5,0.5,0.5,0,0,0.3,4.8
1,2015-01-10 20:33:39,2015-01-10
20:52:58,1,3.00,-73.971176147460938,40.762428283691406,1,N,-74.004180908203125,40.742652893066406,2,15,0.5,0.5,0,0,0.3,16.3
1,2015-01-10 20:33:39,2015-01-10
20:53:52,1,9.00,-73.874374389648438,40.7740478515625,1,N,-73.986976623535156,40.758193969726563,1,27,0.5,0.5,6.7,5.33,0.3,40.33
1,2015-01-10 20:33:39,2015-01-10
20:58:31,1,2.20,-73.9832763671875,40.726009368896484,1,N,-73.992469787597656,40.7496337890625,2,14,0.5,0.5,0,0,0.3,15.3
1,2015-01-10 20:33:39,2015-01-10
20:42:20,3,.80,-74.002662658691406,40.734142303466797,1,N,-73.995010375976563,40.726325988769531,1,7,0.5,0.5,1.66,0,0.3,9.96
1,2015-01-10 20:33:39,2015-01-10
21:11:35,3,18.20,-73.783042907714844,40.644355773925781,2,N,-73.987594604492187,40.759357452392578,2,52,0,0.5,0,5.33,0.3,58.13
```

We can use tools like Pandas or Dask.dataframe to read in all of this data.
Because the data is large-ish, I'll use Dask.dataframe

```
mrocklin@carbon:~/data/nyc/csv$ du -hs .
22G .
```

```python
In [1]: import dask.dataframe as dd

In [2]: %time df = dd.read_csv('yellow_tripdata_2015-*.csv')
CPU times: user 340 ms, sys: 12 ms, total: 352 ms
Wall time: 377 ms

In [3]: df.head()
Out[3]:
VendorID tpep_pickup_datetime tpep_dropoff_datetime  passenger_count  \
0         2  2015-01-15 19:05:39   2015-01-15 19:23:42                1
1         1  2015-01-10 20:33:38   2015-01-10 20:53:28                1
2         1  2015-01-10 20:33:38   2015-01-10 20:43:41                1
3         1  2015-01-10 20:33:39   2015-01-10 20:35:31                1
4         1  2015-01-10 20:33:39   2015-01-10 20:52:58                1

   trip_distance  pickup_longitude  pickup_latitude  RateCodeID  \
0           1.59        -73.993896        40.750111           1
1           3.30        -74.001648        40.724243           1
2           1.80        -73.963341        40.802788           1
3           0.50        -74.009087        40.713818           1
4           3.00        -73.971176        40.762428           1

  store_and_fwd_flag  dropoff_longitude  dropoff_latitude  payment_type \
0                  N         -73.974785         40.750618             1
1                  N         -73.994415         40.759109             1
2                  N         -73.951820         40.824413             2
3                  N         -74.004326         40.719986             2
4                  N         -74.004181         40.742653             2

   fare_amount  extra  mta_tax  tip_amount  tolls_amount  \
0         12.0    1.0      0.5        3.25           0.0
1         14.5    0.5      0.5        2.00           0.0
2          9.5    0.5      0.5        0.00           0.0
3          3.5    0.5      0.5        0.00           0.0
4         15.0    0.5      0.5        0.00           0.0

   improvement_surcharge  total_amount
0                    0.3         17.05
1                    0.3         17.80
2                    0.3         10.80
3                    0.3          4.80
4                    0.3         16.30

In [4]: from dask.diagnostics import ProgressBar

In [5]: ProgressBar().register()

In [6]: df.passenger_count.sum().compute()
[########################################] | 100% Completed |
3min 58.8s
Out[6]: 245566747
```

We were able to ask questions about this data (and learn that 250 million
people rode cabs in 2016) even though it is too large to fit into memory.  This
is because Dask is able to operate lazily from disk.  It reads in the data on
an as-needed basis and then forgets it when it no longer needs it.  This takes
a while (4 minutes) but does just work.

However, when we read this data many times from disk we start to become
frustrated by this four minute cost.  In Pandas we suffered this cost once as
we moved data from disk to memory.  On larger datasets when we don't have
enough RAM we suffer this cost many times.


### Parquet is faster

Lets try this same process with Parquet.  I happen to have the same exact data
stored in Parquet format on my hard drive.

```
mrocklin@carbon:~/data/nyc$ du -hs nyc-2016.parquet/
17G nyc-2016.parquet/
```

It is stored as a bunch of individual files, but we don't actually care about
that.  We'll always refer to the directory as the dataset.  These files are
stored in binary format.  We can't read them as humans

```python
mrocklin@carbon:~/data/nyc$ head nyc-2016.parquet/part.0.parquet
<a bunch of illegible bytes>
```

But computers are much more able to both read and navigate this data.  Lets do
the same experiment from before:

```python
In [1]: import dask.dataframe as dd

In [2]: df = dd.read_parquet('nyc-2016.parquet/')

In [3]: df.head()
Out[3]:
  tpep_pickup_datetime  VendorID tpep_dropoff_datetime  passenger_count  \
0  2015-01-01 00:00:00         2   2015-01-01 00:00:00                3
1  2015-01-01 00:00:00         2   2015-01-01 00:00:00                1
2  2015-01-01 00:00:00         1   2015-01-01 00:11:26                5
3  2015-01-01 00:00:01         1   2015-01-01 00:03:49                1
4  2015-01-01 00:00:03         2   2015-01-01 00:21:48                2

    trip_distance  pickup_longitude  pickup_latitude  RateCodeID  \
0           1.56        -74.001320        40.729057           1
1           1.68        -73.991547        40.750069           1
2           4.00        -73.971436        40.760201           1
3           0.80        -73.860847        40.757294           1
4           2.57        -73.969017        40.754269           1

  store_and_fwd_flag  dropoff_longitude  dropoff_latitude  payment_type  \
0                  N         -74.010208         40.719662             1
1                  N           0.000000          0.000000             2
2                  N         -73.921181         40.768269             2
3                  N         -73.868111         40.752285             2
4                  N         -73.994133         40.761600             2

   fare_amount  extra  mta_tax  tip_amount  tolls_amount  \
0          7.5    0.5      0.5         0.0           0.0
1         10.0    0.0      0.5         0.0           0.0
2         13.5    0.5      0.5         0.0           0.0
3          5.0    0.5      0.5         0.0           0.0
4         14.5    0.5      0.5         0.0           0.0

   improvement_surcharge  total_amount
0                    0.3           8.8
1                    0.3          10.8
2                    0.0          14.5
3                    0.0           6.3
4                    0.3          15.8

In [4]: from dask.diagnostics import ProgressBar

In [5]: ProgressBar().register()

In [6]: df.passenger_count.sum().compute()
[########################################] | 100% Completed |
2.8s
Out[6]: 245566747
```

Same values, but now our computation happens in three seconds, rather than four
minutes.  We're cheating a little bit here (pulling out the passenger count
column is especially easy for Parquet) but generally Parquet will be *much*
faster than CSV.  This lets us work from disk comfortably without worrying
about how much memory we have.

Convert
-------

So do yourself a favor and convert your data

```python
In [1]: import dask.dataframe as dd
In [2]: df = dd.read_csv('csv/yellow_tripdata_2015-*.csv')
In [3]: from dask.diagnostics import ProgressBar
In [4]: ProgressBar().register()
In [5]: df.to_parquet('yellow_tripdata.parquet')
[############                            ] | 30% Completed |  1min 54.7s
```

If you want to be more clever you can specify dtypes and compression when
converting.  This can definitely help give you significantly greater speedups,
but just using the default settings will still be a large improvement.


Advantages
----------

Parquet enables the following:

1.  Binary representation of data, allowing for speedy conversion of
    bytes-on-disk to bytes-in-memory
2.  Columnar storage, meaning that you can load in as few columns as you need
    without loading the entire dataset
3.  Row-chunked storage so that you can pull out data from a particular range
    without touching the others
4.  Per-chunk statistics so that you can find subsets quickly
5.  Compression

Parquet Versions
----------------

There are two nice Python packages with support for the Parquet format:

1.  [pyarrow](https://arrow.apache.org/docs/python/parquet.html):
    Python bindings for the Apache Arrow and Apache Parquet C++ libraries
2.  [fastparquet](http://fastparquet.readthedocs.io/en/latest/): a direct
    NumPy + Numba implementation of the Parquet format

Both are good.  Both can do most things.  Each has separate strengths.  The
code above used `fastparquet` by default but you can change this in Dask with
the `engine='arrow'` keyword if desired.
