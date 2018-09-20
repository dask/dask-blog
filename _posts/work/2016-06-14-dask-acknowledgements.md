---
layout: post
title: Dask Acknowledgements
tagline: credit is due
draft: true
category: work
tags: [Programming, scipy, Python, dask]
theme: twitter
---
{% include JB/setup %}

tl;dr
-----

We highlight the people who thanklessly perform work on an open source software
project, dask.  We use this as a case study to discuss why communities are necessary
to build effective open source software.


Attribution is Hard
-------------------

Correctly giving attribution is hard.  I just released a new version of
[dask](https://dask.pydata.org/) and, as with all releases I mention the names
of everyone who contributed code at the end of the email:

> Since Dask 0.9.0 the following developers have contributed code commits

>   Hussain Sultan
>   Jim Crist
>   jslmann
>   Kristopher Overholt
>   Matthew Rocklin
>   Mike Graham
>   ...

This list is wrong in so many ways.  First, I just cut it off here with `...`,
omitting some 20 other names for brevity's sake.  Second, notice that it's
alphabetized by first name; that's because there is no easy way to order
impact.  Third, it only includes the names of people who committed code, not
the countless individuals who contribute endless support in other ways
including review, high-level direction and advice, build support, raising
issues, and funding.  For example, I neglected to add attribution to Victoria
O'Dell, who designed this wonderful logo for Dask:

<img src="http://dask.readthedocs.io/en/latest/_images/dask_horizontal.svg">

Look at that; there's no way I could have designed that nice of a logo.  Trust
me, I tried once and it didn't turn out well :)


Attribution is Important
------------------------

And yet attribution is important for open software and open research.  While
many of us perform this work for the public good, we are also motivated by the
knowledge that by attaching our names to well respected software we cement our
ability to maintain this activity in the future.  Even if our day jobs aren't
in open research, participation in successful open source software can be a
significant resume builder (and reasonably so, development practices in the
open community are generally well respected.)

So I'm going to briefly describe some of the awesome people that make Dask
useful.  Hopefully it'll become clear that, left to my own devices, Dask would
be a cute but rarely used piece of software.  I'm going to break these
people down by sub-project.


People
------

### Arrays

Stephan Hoyer's work integrating Dask.array with XArray (then XRay) for climate
science was the first major integration of Dask with an active user community.
I genuinely believe that Dask would not have gotten off the ground without
Stephan's week-long sprint (thanks to Climate Corp for allowing employees to
take sprint-baticals.)

XArray solved a last-mile problem, connecting a steady stream of users in
climate science to core dask technology.  This user pressure helped to harden
to harden Dask into a reliable piece of software.  Today the XArray developer
community remains helpful by filtering and passing up bug reports.  Dask
developers really aren't qualified to handle bug reports from climate
scientists but the XArray developers patiently handle these and pass the
infrastructural questions upstream to Dask, suitably translated where they
(usually) are well handled.

Other benefits of user-communities include a ready pool of willing early
adopters for new technology.  People like Phil Wolfram put in countless hours
as we worked together to get distributed dask-arrays online.

This is to say nothing of the many developers who built the dask.array
algorithms.  All of Jim Crist, Masaaki Horikoshi, Blake Griffith, Stehan Hoyer, Phil Wolfram, Mariano Tepper, John Kirkham, Wesley Emeneker, Phil Cloud, and Peter Steinberg all have significant contributions within dask.array that, in respect of your time I'm going to completely pass over.


### DataFrames

Pandas developers like Masaaki Horikoshi, Phil Cloud, and Tom Augspurger cross
over to reimplement Pandas algorithms faithfully in Dask.dataframe.  Their
experience in the Pandas codebase makes them far more useful than someone who
works on Dask full-time and they are the only reason why dask.dataframe
algorithms work faithfully to the original Pandas implementations.

The lead Pandas maintainer Jeff Reback has been incredibly supportive on the
Pandas development side as well.  Dask feature requests like releasing the GIL,
improving function serialization, and categorical indices have been resolved
with incredible speed and professionalism.

Additionally individual community developers have taken on individual aspects
of dask.dataframe.  For example Mike Graham has recently taken on `rolling`
operations, Nir has taken on `to_hdf`, etc..  The Pandas project is large
enough that any attempt to faithfully parallelize it is ambitious and requires
a diverse team of people to take on different pieces.  I encourage others to
get involved.


### Delayed

Dask.delayed is probably my favorite dask collection, which is surprising given
how hard I fought hard against the idea when Gael Varoquaux first pushed the
idea at ICML almost a year ago.  Since then Dask.Delayed has been mostly
managed by Jim Crist, who, if I haven't mentioned so far is only because Jim
works on everything.  If I get hit by a bus then please trust Jim.


### Optimizations

No one sees the work of Erik Welch (also known as the author of CyToolz and
current lead developer of Toolz) but that's only because he does it so well.
Internally dask includes some very fast optimization passes such as you might
see in a simple compiler.  The majority of these are written by Erik, who has
an incredible ability to craft delicate algorithms that run at blinding speed.


### Web Diagnostics

The slick web diagnostic page for dask.distributed was originally designed and
implemented by Luke Canavan.  The Bokeh server developers, notably Bryan Van
den ven and Havoc Pennington were also instrumental in making the Dask
diagnostic web interface run as quickly as it does (it streams through
thousands of rectangles a second, updating at 100ms frequencies.)  I'm also
excited by recent conversations with Sarah Bird about the improving the visual
design and layout.


### Distributed Scheduling

I built three or four implementations of the distributed scheduler before
getting to the nice system that we have today.  Patiently supportive through
all of that was Min Ragan-Kelley, the primary author of IPython Parallel (and
core contributor to Jupyter generally.)

Additionally conversations with Olivier Grisel helped to shape the interface
and continue to drive development in directions that are useful for custom
algorithms (one of the most exciting use cases in my opinion.)


### Cluster Computing

Continuum contains a crack cluster computing team composed of Ben Zaitlen,
Daniel Rodriguez, Martin Durant, and Kris Overholt.  This team's experience and
pain tolerance are the only reasons why dask.distributed runs well on
production systems.

Martin handles HDFS and S3 data interfaces.  Daniel handles deployment on AWS,
and Mesos and Docker expertise.  Kris manages conda builds everywhere (thanks
conda-forge!) and generally serves as an interface to the enterprise-focused
parts of Continuum.  Ben handles Yarn and everything else that needs handling.


### Financial Support

Travis Oliphant and Peter Wang built a company that is able to fund three of us
(Jim Crist, Martin Durant, and myself) to work on this project without deriving
significant financial gain.  Dask would be far less useful if we didn't have
paid time to answer support requests, respond to stack-overflow questions, and
write proper documentation.  Even with grants like XData and the occasional
paying customer it would be optimistic to say that Dask makes Continuum any
money.  We're almost certainly deeply in the red (most dask users are
scientists or open source projects) and yet we get nothing but positive
feedback and support from the rest of the Company.


Broader Point
-------------

People sometimes associate Dask as my project.  This is deeply wrong.  It's
clear that this is wrong because Dask is successful and I historically do not
make successful software projects.  I make neat and clever software (toolz,
multipledispatch, sympy.stats, logpy, an MPI branch of Theano), but not useful
software.  These neat projects are modular and maintainable but rarely
transformative.  Useful software requires such a variety of talent that few
individuals are capable of doing it on their own.
