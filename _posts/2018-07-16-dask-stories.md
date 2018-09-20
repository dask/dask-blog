---
layout: post
title: Who uses Dask?
category: work
tags: [Programming, Python, scipy, dask]
theme: twitter
---
{% include JB/setup %}

*This work is supported by [Anaconda Inc](http://anaconda.com)*

People often ask general questions like "Who uses Dask?" or more specific
questions like the following:

1.  For what applications do people use Dask dataframe?
2.  How many machines do people often use with Dask?
3.  How far does Dask scale?
4.  Does dask get used on imaging data?
5.  Does anyone use Dask with Kubernetes/Yarn/SGE/Mesos/... ?
6.  Does anyone in the insurance industry use Dask?
6.  ...

This yields interesting and productive conversations where new users can dive
into historical use cases which informs their choices if and how they use the
project in the future.

*New users can learn a lot from existing users.*

To further enable this conversation we've made a new tiny project,
[dask-stories](https://dask-stories.readthedocs.io).  This is a small
documentation page where people can submit how they use Dask and have that
published for others to see.

To seed this site six generous users have written down how their group uses
Dask.  You can read about them here:

1.  [Sidewalk Labs: Civic Modeling](http://dask-stories.readthedocs.io/en/latest/sidewalk-labs.html)
2.  [Genome Sequencing for Mosquitoes](http://dask-stories.readthedocs.io/en/latest/mosquito-sequencing.html)
3.  [Full Spectrum: Credit and Banking](http://dask-stories.readthedocs.io/en/latest/fullspectrum.html)
4.  [Ice Cube: Detecting Cosmic Rays](http://dask-stories.readthedocs.io/en/latest/icecube-cosmic-rays.html)
5.  [Pangeo: Earth Science](http://dask-stories.readthedocs.io/en/latest/pangeo.html)
6.  [NCAR: Hydrologic Modeling](http://dask-stories.readthedocs.io/en/latest/hydrologic-modeling.html)

We've focused on a few questions, available in [our
template](http://dask-stories.readthedocs.io/en/latest/template.html) that
focus on problems over technology, and include negative as well as positive
feedback to get a complete picture.

1.  Who am I?
2.  What problem am I trying to solve?
3.  How Dask helps?
4.  What pain points did I run into with Dask?
5.  What technology do I use around Dask?


### Easy to Contribute

Contributions to this site are simple Markdown documents submitted as pull
requests to
[github.com/dask/dask-stories](https://github.com/dask/dask-stories).  The site
is then built with ReadTheDocs and updated immediately.  We tried to make this
as smooth and familiar to our existing userbase as possible.

This is important.  Sharing real-world experiences like this are probably more
valuable than code contributions to the Dask project at this stage.  Dask is
more technically mature than it is well-known.  Users look to other users to
help them understand a project (think of every time you've Googled for "*some
tool* in *some topic*")

If you use Dask today in an interesting way then please share your story.
The world would love to hear your voice.

If you maintain another project you might consider implementing the same model.
I hope that this proves successful enough for other projects in the ecosystem
to reuse.
