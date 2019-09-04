---
layout: post
title: Dataframe Groupby Aggregations
tagline: deepdive on groupbys
author: James Bourbeau & Benjamin Zaitlen
tags: [dask, datagrame]
theme: twitter
---
{% include JB/setup %}


## GroupyBy Aggregations with Dask


In this blogpost we want to dive into how Dask calculates groupby operations.  These are common operations for ETL and analysis where we want to split unordered data into groups, apply some function to those groups, then combine the groups back together.

// image of split apply combine

In the R/PyData world this is often referred to as the split-apply-combine strategy first coined by [Hadley Wickham](https://www.jstatsoft.org/article/view/v040i01) but also widely used throughout the [Pandas eco-system](https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html)

Dask leveraged this idea and also produced a similarly catchy name, `apply-conact-apply` or `aca` for short.  In this blog post, we dive into aca strategy:

Recall that Dask works on blocks of objects.  In the case of a Dataframe, these [partitions](https://docs.dask.org/en/latest/dataframe-design.html#partitions).  For example, let's say we have the following dataframe:


```python
>>> df = pd.DataFrame(dict(a=[1, 1, 2, 3, 3, 1, 1, 2, 3, 3, 99, 10, 1],
...                        b=[1, 3, 10, 3, 2, 1, 3, 10, 3, 3, 12, 0, 9],
...                        c=[2, 4, 5, 2, 3, 5, 2, 3, 9, 2, 44, 33, 2]))
>>> df
     a   b   c
0    1   1   2
1    1   3   4
2    2  10   5
3    3   3   2
4    3   2   3
5    1   1   5
6    1   3   2
7    2  10   3
8    3   3   9
9    3   3   2
10  99  12  44
11  10   0  33
12   1   9   2
```

We can load the dataframe into dask and define the number of partitions.  We'll pick 3 partitions -- as it will give us complexity to illustrate what is happening but not too much to the point that we can't keep everything in our heads.

```python
>>> ddf = dd.from_pandas(df, npartitions=3)
```

The 3 partitions are simply 3 individual dataframes

```python
>>> ddf.partitions[0].compute()
   a   b  c
0  1   1  2
1  1   3  4
2  2  10  5
3  3   3  2
4  3   2  3
```

So when dask is applying any function and/or algorithm on dataframes, the atomic unit is the dataframe itself.

## apply-conact-apply

Internally, dask re-uses the same methodology `apply-conact-apply` for much of the dataframe computations.  That is, "Apply a function to blocks, then concat, then apply again".  One of the more common operations on dataframe objects is split-apply-combine aka groupby aggregations.  Taking the dataframe above, let's spend a minute breaking down what `ddf.groupby(['a', 'b']).c.sum()` looks like

### Define Partitions

The equivalent 3 partitions is 3 dataframes -- starting with the original dataframe defined above:

```python
>>> df_1 = df[:5].copy()
>>> df_2 = df[5:10].copy()
>>> df_3 = df[-3:].copy()
```

With three partitions, we perform the same operation, `groupby(['a', 'b']).c.sum()`:

```python
>>> sr1 = df_1.groupby(['a', 'b']).c.sum()
>>> sr2 = df_2.groupby(['a', 'b']).c.sum()
>>> sr3 = df_3.groupby(['a', 'b']).c.sum()
```

The result of this operation is a Series with a MultiIndex

<table>
  <tr>
    <th>
      <pre>
>>> sr1
a  b
1  1     2
   3     4
2  10    5
3  2     3
   3     2
Name: c, dtype: int64
      </pre>
    </th>
    <th>
      <pre>
>>> sr2
a  b
1  1      5
   3      2
2  10     3
3  3     11
Name: c, dtype: int64
      </pre>
    </th>
    <th>
      <pre>
>>> sr3
a   b
1   9      2
10  0     33
99  12    44
Name: c, dtype: int64
      </pre>
    </th>
  </tr>
</table>

### The conCat!

We did the `apply`, and now the `concat` is fairly straightforward:

```python
>>> sr_concat = pd.concat([sr1, sr2, sr3])
>>> sr_concat
a   b
1   1      2
    3      4
2   10     5
3   2      3
    3      2
1   1      5
    3      2
2   10     3
3   3     11
1   9      2
10  0     33
99  12    44
Name: c, dtype: int64
```

### Apply Redux

And now we apply `groupby(['a', 'b']).c.sum()` on the concated series.  But we no longer have columns `a` and `b`.  Zooming out a bit, we are after adding the values in the column which have the same index.  For example, there are two rows with the index `(1, 1)` with corresponding values: 2, 7.  So how can we groupby the indicies with the same value?  A MutliIndex uses [levels](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.MultiIndex.html#pandas.MultiIndex) to define what the value is at a give index.  Dask [determines the level](https://github.com/dask/dask/blob/973c6e1b2e38c2d9d6e8c75fb9b4ab7a0d07e6a7/dask/dataframe/groupby.py#L69-L75), and uses [these levels](https://github.com/dask/dask/blob/973c6e1b2e38c2d9d6e8c75fb9b4ab7a0d07e6a7/dask/dataframe/groupby.py#L1065) in final calculation.  In our case, the level is [0,1], that is, we want both the index at the 0th level and the 1st level and if we group by both `0, 1` we will have effectively grouped the same indicies together:

```
>>> total = sr_concat.groupby(level=[0, 1]).sum()
```

<table>
  <tr>
    <th>
      <pre>
>>> total
a   b
1   1      7
    3      6
    9      2
2   10     8
3   2      3
    3     13
10  0     33
99  12    44
Name: c, dtype: int64
      </pre>
    </th>
    <th>
      <pre>
>>> ddf.groupby(['a', 'b']).c.sum()
a   b
1   1      7
    3      6
2   10     8
3   2      3
    3     13
1   9      2
10  0     33
99  12    44
Name: c, dtype: int64
      </pre>
    </th>
    <th>
      <pre>
>>> df.groupby(['a', 'b']).c.sum()
a   b
1   1      7
    3      6
    9      2
2   10     8
3   2      3
    3     13
10  0     33
99  12    44
Name: c, dtype: int64
      </pre>
    </th>
  </tr>
</table>

Rather than do all this calculation we can easily easily visualize the task graph and see `apply-concat-apply`

![svg](/images/sum.svg)

Sum, is rather a straight-forward calculation.  What about something a bit more complex like `mean`

![svg](/images/mean.svg)
