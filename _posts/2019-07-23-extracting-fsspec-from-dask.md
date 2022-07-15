---
layout: post
title: Extracting fsspec from Dask
author: Martin Durant
tags: [IO]
draft: false
theme: twitter
---

{% include JB/setup %}

## TL;DR

`fsspec`, the new base for file system operations in Dask, Intake, s3fs, gcsfs and others,
is now available as a stand-alone interface and central place to develop new backends
and file operations. Although it was developed as part of Dask, you no longer need Dask
to use this functionality.

## Introduction

Over the past few years, Dask's IO capability has grown gradually and organically, to
include a number of file-formats, and the ability to access data seamlessly on various
remote/cloud data systems. This has been achieved through a number of sister packages
for viewing cloud resources as file systems, and dedicated code in `dask.bytes`.
Some of the storage backends, particularly `s3fs`, became immediately useful outside of
Dask too, and were picked up as optional dependencies by `pandas`, `xarray` and others.

For the sake of consolidating the behaviours of the
various backends, providing a single reference specification for any new backends,
and to make this set of file system operations available even without Dask, I
created [`fsspec`](https://filesystem-spec.readthedocs.io/en/latest/).
This last week, Dask changed to use `fsspec` directly for its
IO needs, and I would like to describe in detail here the benefits of this change.

Although this was done initially to easy the maintenance burden, the important takeaway
is that we want to make file systems operations easily available to the whole pydata ecosystem,
with or without Dask.

## History

The first file system I wrote was [`hdfs3`](https://github.com/dask/hdfs3), a thin wrapper
around the `libhdfs3` C library. At the time, Dask had acquired the ability to run on a
distributed cluster, and HDFS was the most popular storage solution for these (in the
commercial world, at least), so a solution was required. The python API closely matched
the C one, which in turn followed the Java API and posix standards. Fortunately, python already
has a [file-like standard](https://docs.python.org/3/library/io.html#i-o-base-classes), so
providing objects that implemented that was enough to make remote bytes available to many
packages.

Pretty soon, it became apparent that cloud resources would be at least as important as in-cluster
file systems, and so followed [s3fs](https://github.com/dask/s3fs),
[adlfs](https://github.com/Azure/azure-data-lake-store-python), and [gcsfs](https://github.com/dask/gcsfs).
Each followed the same pattern, but with some specific code for the given interface, and
improvements based on the experience of the previous interfaces. During this time, Dask's
needs also evolved, due to more complex file formats such as parquet. Code to interface to
the different backends and adapt their methods ended up in the Dask repository.

In the meantime, other file system interfaces arrived, particularly
[`pyarrow`'s](https://arrow.apache.org/docs/python/filesystems.html), which had its own HDFS
implementation and direct parquet reading. But we would like all of the tools in
the ecosystem to work together well, so that Dask can read parquet using either
engine from any of the storage backends.

## Code duplication

Copying an interface, adapting it and releasing it, as I did with each iteration of the file system,
is certainly a quick way to get a job done. However, when you then want to change the behaviour, or
add new functionality, it turns out you need to repeat the work in each place
(violating the [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) principle) or have
the interfaces diverge slowly. Good examples of this were `glob` and `walk`, which supported various
options for the former, and returned different things (list, versions dir/files iterator) for the
latter.

```python
>>> fs = dask.bytes.local.LocalFileSystem()
>>> fs.walk('/home/path/')
<iterator of tuples>


>>> fs = s3fs.S3FileSystme()
>>> fs.walk('bucket/path')
[list of filenames]
```

We found that, for Dask's needs, we needed to build small wrapper
classes to ensure compatible APIs to all backends, as well as a class for operating on the local
file system with the same interface, and finally a registry for all of these with various helper
functions. Very little of this was specific to Dask, with only a couple of
functions concerning themselves with building graphs and deferred execution. It did, however,
raise the important issue that file systems should be serializable and that there should
be a way to specify a file to be opened, which is also serializable (and ideally supports
transparent text and compression).

## New file systems

I already mentioned the effort to make a local file system class which met the same interface as
the other ones which already existed. But there are more options that Dask users (and others)
might want, such as ssh, ftp, http, in-memory, and so on. Following requests from users to handle these options,
we started to write more file system interfaces, which all lived within `dask.bytes`; but it was unclear
whether they should only support very minimal functionality, just enough to get something done from
Dask, or a full set of file operations.

The in-memory file system, in particular, existed in an extremely long-lived PR - it's not
clear how useful such a thing is to Dask, when each worker has it's own memory, and so sees
a different state of the "file system".

## Consolidation

[file system Spec](https://github.com/intake/filesystem_spec), later `fsspec`, was born out of a desire
to codify and consolidate the behaviours of the storage backends, reduce duplication, and provide the
same functionality to all backends. In the process, it became much easier to write new implementation
classes: see the [implementation](https://filesystem-spec.readthedocs.io/en/latest/api.html#built-in-implementations),
which include interesting and highly experimental options such as the `CachingFileSystem`, which
makes local copies of every remote read, for faster access the second time around. However, more
important main-stream implementations also took shape, such as FTP, SSH, Memory and webHDFS
(the latter being the best bet for accessing HDFS from outside the cluster, following all the
problems building and authenticating with `hdfs3`).

Furthermore, the new repository gave the opportunity to implement new features, which would then have
further-reaching applicability than if they had been done in just selected repositories. Examples include
FUSE mounting, dictionary-style key-value views on file systems
(such as used by [zarr](https://zarr.readthedocs.io/en/stable/)), and transactional writing of
files. All file systems are serializable and pyarrow-compliant.

## Usefulness

Eventually it dawned on my that the operations offered by the file system classes are very useful
for people not using Dask too. Indeed, `s3fs`, for example, sees plenty of use stand-alone, or in
conjunction with something like fastparquet, which can accept file system functions to its method,
or pandas.

So it seemed to make sense to have a particular repo to write out the spec that a Dask-compliant
file system should adhere to, and I found that I could factor out a lot of common behaviour from
the existing implementations, provide functionality that had existed in only some to all, and
generally improve every implementation along the way.

However, it was when considering `fsspec` in conjunction with [Intake](https://github.com/intake/intake/pull/381)
that I realised how generally useful a stand-alone file system package can be: the PR
implemented a generalised file selector that can browse files in any file system that we
have available, even being able, for instance, to view a remote zip-file on S3 as a
browseable file system. Note that, similar to the general thrust of this blog, the
file selector itself need not live in the Intake repo and will eventually become either
its own thing, or an optional feature of `fsspec`. You shouldn't need Intake either just
to get generalised file system operations.

## Final Thoughts

This work is not quite on the level of "protocol standards" such as the well-know python buffer
protocol, but I think it is a useful step in making data in various storage services available
to people, since you can operate on each with the same API, expect the same behaviour, and
create real python file-like objects to pass to other functions. Having a single central repo
like this offers an obvious place to discuss and amend the spec, and build extra functionality
onto it.

Many improvements remain to be done, such as support for globstrings in more functions, or
a single file system which can dispatch to the various backends depending on the form of the
URL provided; but there is now an obvious place for all of this to happen.
