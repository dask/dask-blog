---
layout: post
title: Dask Survey 2021, early anecdotes
author: Matthew Rocklin
theme: twitter
---

{% include JB/setup %}

The annual Dask user survey is under way and currently accepting responses at [dask.org/survey](https://dask.org/survey).

This post provides a preview into early results, focusing on anecdotal responses.

## Motivation

The Dask user survey helps developers focus and prioritize our larger efforts.  It’s also a fascinating and rewarding dataset of anecdotal use cases of how people use Dask today.  Thank you to everyone who has participated so far, you make a difference.

The survey is still open, and I encourage people to speak up about their experience.  This blogpost is intended to encourage participation by giving you a sense for how it affects development, and by sharing user stories provided within the survey.

This article skips all of the quantitative data that we collect, and focuses in on direct feedback listed in the final comments.  For a more quantitative analysis see the posts from previous years by Tom at [2020 Dask User Survey Results](https://blog.dask.org/2020/09/22/user_survey) and  [2019 Dask User Survey Results](https://blog.dask.org/2019/08/05/user-survey).

## How can Dask Improve?

In this post we're going to look at answers to this one question. This was a long-form response field asking _"How can Dask Improve?"_. Looking through some of the responses we see that a few of them fall into some common themes. I've grouped them here.

In each section we'll include raw responses, followed up with a few comments from me in response.

## Intermediate Documentation

> More long-form content about the internals of Dask to understand when things don't work and why. The "Hacking Dask" tutorial in the Dask 2021 summit was precisely the kind of content I really need, because 90% of my time with Dask is spent not understanding why I'm running out of memory and I feel like I've ready all the documentation pages 5 times already (although sometimes I also stumble upon a useful page I've never seen before).
>
> There's also a dearth of documentation of intermediate topics like blockwise in dask.array. (I think I ended up reverse engineering how it worked from docs, GitHub issue comments, reading the code, and black-box reverse engineering with different functions before I finally "got it".)
>
> Improve documentation and error messages to cover more of the 2nd-level problems that people run into beyond the first-level tutorial examples.
>
> more examples for complex concepts (passing metadata to custom functions, for example). more examples/support for using dask arrays and cupy.
>
> I think the hardest thing about Dask is debugging performance issues with dask delayed and complex mixing of other libraries and not knowing when things are being pickled or not. I am getting better at reading the performance reports, but I think that better documentation and tutorials surrounding understanding the reports would help me greater than new features. For example, make a tutorial that does some non-trivial dask-delayed work (ie not just computing a mean) that is written against best practices and show how the performance improves with each adopted best practice/explain why things were slow with each step. I think there could also be improvements to the performance reports to point out the slowest 5 parts of your code and what lines they are, and possibly relevant docs links.

### Response

I really like this theme.  We now have a solid community of intermediate-advanced Dask users that we should empower.  We usually write materials that target the broad base of beginning users, but maybe we should rethink this a bit.  There is a lot of good potential material that advanced users have around performance and debugging that could be fun to publish.

## Documentation Organization

> Documentation website is sometimes confusing to navigate, better separation of API and examples would help. Maybe this can inspire: <https://documentation.divio.com/>
>
> I actually think Dask's documentation is pretty good. But the docs could use some reorganizing -- it is often difficult to find the relevant APIs. And there is an incredible amount of HPC insider knowledge that is required to launch a typical workflow - right now much of this knowledge is hidden in the github issues (which is great! but more of it could be pushed into the FAQs to make it more accessible).
>
> More detailed documentation and examples. Start to finish examples that do not assume I know very much (about Dask, command line tools, Cloud technologies, Kubernetes, etc.).
>
> I think an easier introduction to delayed/bags and additional examples for more complex use-cases could be helpful.

### Response

We get alternating praise and scorn for our documentation.  We have what I would call excellent _reference documentation_.  In fact, if anyone wants to build a dynamic distributed task scheduler today I’m going to claim that distributed.dask.org is probably the most comprehensive reference out there.

However, we lack good _narrative documentation_, which is the concern raised by most of these comments. This is hard to do because Dask is used in so many _different user narratives_.  It’s challenging to orient the Dask documentation around all of them simultaneously.

I appreciated the direct reference in the first comment to a website with a framework.  In general I’d love to talk to people who lay out documentation semi-professionally and learn more.

## Functionality

Here is a soup of various feature requests, there are a few themes among them

> Have a better pandas support (like multi-index), which can help me migrate my existing code to Dask.
>
> I'd like to see better support for actors. I think having a remote object is a common use case.
>
> Improve Dataframes - multi index!! More feature parity with Pandas API.
>
> Maybe a little less machine learning, more "classical" big data applications (CDF, PDEs, particle physics etc.). Not everything is map-reducable.
>
> Better database integration. Re-writing an SQL query in SQL Alchemy can be very impractical. Would also be great if there were better ways to ensure the process didn't die from misjudging how much memory was needed per chunk.
>
> Better diagnostic tools; what operations are bottlenecking a task graph? Support for multiindex.
>
> I do work that regularly requires sorting a DataFrame by multiple columns. Pandas can do this single-core; H2O and Spark can do this multicore and distributed. But dask cannot sort_values() on multiple columns at all (such as `df.sort_values([ "col1", "col2" ,"col3" ], ascending=False)`).
>
> Type-hints! It is very tedious using Dask in a huge ML-Application without even having the option to do some static type-checking.
>
> Additionally it is very frustrating that Dask tries to mimic Pandas API, but then 40% of the API doesn't work (isn't implemented), or deviates so far from the Pandas API that some parameters aren't implemented. Only way to find out about that is to read the docs. With some typehints one could mitigate much of this trial-and-error process when switching from Pandas to Dask.
>
> It's hard to track everything around dask!!! Actors are a bit unloved, but I find them super useful
>
> Type annotations for all methods for better IDE (VSCode) support
>
> I think the Actor model could use a little love

### Response

Interesting trends, not many that I would have expected

- MultiIndex (well, this was expected)
- Actors
- Type hinting for IDE support
- SQL access

## High Level Optimization

> Needs better physical data independence. Manual data chunking, memory management, query optimization are all a big hassle. Automate those more.
>
> Dask makes it easy for users with no parallel computing experience to scale up quickly (me), but we have no sense of how to judge our resource needs. It’d be great if Dask had some tools or tutorials that helped me judge the size of my problem (e.g. memory usage). These may already exist, but examples of how to do it may be hard to find.

## Runtime Stability and Advanced Troubleshooting

> Stability is the most important factor
>
> I have answered no to the Long Term Support version of dask but often the really great opportunities are those that arre on demand. The problem is that when these fixes are released, their not well advertised and something under the hood has changed. So, it ends up breaking something else or my particular knowledge of the workings are no longer correct. Dask maintainers have a bit of a weird clique and it can feel as a newbie or a learner that your talked down to or in reality. They don't have the time to help someone. So they should probably have some more maintainers answering some of the more mundane questions via the blog or via some other method, Things we have seen people do wrong or having difficulty in . A bit of basic, a bit of intermediate and a bit of advanced. If the underlying dask API has changed, then these should be updated with new posts with updates of what has changed. Showing a breakdown of doing it the hard way. So people can see what is done step by step with standard workflows that work. Then vs dask, with less boilerplate and/or speed improvement. If there are places where speed isn't improved. Show that the difference of where it doesnt work alongside the workflow where it might.
>
> We have long deployed dask clusters (weeks to months) and have noticed that they sometimes go into a wonky state. We've been unable to identify root cause(s). Redeployment is simple and easy when it does occur, but slightly annoying nonetheless.
>
> My biggest pain point is the scheduler, as I tend to spend time writing infrastructure to manage the scheduler and breaking apart / rewriting tasks graphs to minimize impact on the scheduler.
>
> As my answers make clear (and from previous conversations with Matt, James, and Genevieve) the biggest improvement I'd like to see is stable releases. Stable from both a runtime point of view (i.e. rock solid Dask distributed), and from an API point of view (so I don't have to fix my code every couple of weeks). So a big +1 to LTS releases.
>
> Better error handling/descriptions of errors, better interoperability between (slightly) different versions
>
> If something goes wrong (in Dask, the batch system, or the interaction between Dask and the batch system), the problem is very opaque and difficult to diagnose. Dask needs significant additional documentation, and probably additional features, to make debugging easier and more transparent.
>
> Better ways of getting out logs of worker memory usage, especially after dask crashes/failures. Ways of getting performance reports written to log files, rather than html files which don't write if the dask client process fails.
>
> Two big problems for me are when dask fails determining what when wrong and how to fix it.

### Response

Stability definitely took a dive last December.  I’m feeling good right now though.  There is a lot of good work that should be merged in and released in the next few weeks that I think will significantly improve many of the common pain points.

However, there are still many significant improvements yet to be made.  I in particular like the theme above in reporting and logging when things fail.  We’re ok at this today, but there is a lot of room for growth.

## What's Next?

Do the views above fully express your thoughts on where Dask should go, or is there something missing?

Share your perspective at [**dask.org/survey**](https://dask.org/survey).  The whole process should take less than five minutes.
