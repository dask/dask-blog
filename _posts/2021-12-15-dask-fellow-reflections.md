---
layout: post
title: Reflections on one year as the Dask life science fellow
author: Genevieve Buckley
tags: [life science]
theme: twitter
---

{% include JB/setup %}

## Summary

[Genevieve Buckley](https://github.com/GenevieveBuckley/) was hired as a Dask Life Science Fellow in 2021 [funded by CZI](https://chanzuckerberg.com/eoss/proposals/). The goal was to improve Dask, with a [specific focus on the life science community](https://blog.dask.org/2021/03/04/the-life-science-community). This blogpost contains another progress update, and some personal reflections looking back over this year.

## Contents

- [Progress update](#progress-update)
- [Personal reflections](#personal-reflections)
  - [Highlights from this year](#highlights-from-this-year)
  - [What worked well](#what-worked-well)
  - [What didn't work so well](#what-didnt-work-so-well)
- [What's next in Dask?](#whats-next-in-dask)

## Progress update

A previous progress update for February to September 2021 is [available here](https://blog.dask.org/2021/10/20/czi-eoss-update). Read on for a progress update for the period September to December 2021.

To summarize, between September and December 2021 inclusive, there were:

- 32 merged pull requests acorss 7 repositories (`dask`, `distributed`, `dask-image`, `dask-tutorial`, `ITK`, `napari`, and `napari.github.io`)
- 8 pending pull requests
- 1 new `dask-image` release
- 1 Dask tutorial run, and assisted with a second tutorial.
- 4 new Dask blogposts published (five, if we count this one)

Read on for a more detailed description of special projects within this time.

**Dask stale issues sprint**

In two weeks I was able to:

- close 117 stale issues, and
- identify another 25 potential easy wins for the maintainer team to investigate further.

Lots of other people did work around the same time, following up on old pull requests and other maintanence work. The sprint was very successful overall.

**Dask user survey results analysis**

In September I analyzed the results from the 2021 Dask user survey.
This was a really fun task. Because we asked a lot more questions in 2021 (18 new questions, 43 questions in total) there was was a lot more data to dig into, compared with previous years. You can read the [full details about it here](https://blog.dask.org/2021/09/15/user-survey).

The biggest benefit from this work is that now we can use this data to prioritize improvements to the documentation and examples.
The top two user requests are for more documentation and more examples from their industry. But it wasn't until this year that we started asking what industries people worked in, so we can target new narrative documentation to the areas that need it most (geoscience, life science, and finance).

**ITK compatibility with Dask**

I implemented [pickle serialization for itk images (ITK PR #2829)](https://github.com/InsightSoftwareConsortium/ITK/pull/2829/). This should be one of the last major pieces of the puzzle needed to make ITK images compatible with Dask. It builds on earlier work by Matt McCormick and John Kirkham (you can read a blog post about their earlier work [here](https://blog.dask.org/2019/08/09/image-itk)).

Better cross-compatibility for Dask with other projects was a major goal of mine, so this is an important piece of work. I outline the next steps in the section [What's next in Dask?](#whats-next-in-dask)

**Improve rechunking**

I implemented [PR #8124](https://github.com/dask/dask/pull/8124) fix a bug where reshaping a Dask array can cause an output array with chunks that are much too large to fit in memory.
Feedback from the life science user survey indicates that improving Dask's performance around rechunking is a priority. This work helps to address that.

**High level graph work**

A major piece of work earlier this year was introducing high level graphs for array slicing and array overlap operations. That is a big effort requiring a lot of ongoing work.
[PR #8467](https://github.com/dask/dask/pull/8467) tackles one of the next steps for this work.

**Find objects function for dask-image**

I implemented a `find_objects` function for `dask-image` in [PR #240](https://github.com/dask/dask-image/pull/240). This implementation does not need to know the maximum label number ahead of time, a subtantial improement over the previous attempt. This is a major step forward, because it removes a major blocker to introducing scikit-image like `regionprops` functionality.

**Blogposts**

Dask blogposts published between September through to December 2021 include:

- [Choosing good chunk sizes in Dask](https://blog.dask.org/2021/11/02/choosing-dask-chunk-sizes)
  - This blogpost addresses some very common concerns and questions about using Dask.
    I'm very pleased with this article, due to several thoughtful reviewers the final work is a much stronger and more comprehensive than the [twitter thread](https://twitter.com/DataNerdery/status/1424953376043790341) that inspired it.
  - It's also high impact work. In the Dask survey the most common request is for more documentation, and this content helps to address that. Twitter analytics also show much higher engagement with this content than for other similar tweets, indicating a demand in the community for this type of explanation.
- [Mosaic Image Fusion](https://blog.dask.org/2021/12/01/mosaic-fusion) (co-authored with Volker Hisenstein and Marvin Albert)
  - This blogpost was several months in the making (started in mid-August and published in December). It's fantastic to have people sharing some of the very cool work they do with Dask on real world problems.
- [CZI EOSS Update](https://blog.dask.org/2021/10/20/czi-eoss-update)
  - This blogpost shares with the community an interim progress update provided to CZI.
- [2021 Dask user survey results](https://blog.dask.org/2021/09/15/user-survey)
  - Discussed in more detail above, the analysis results from the Dask User Survey were published in September 2021.

**Tutorials**

- I presented a Dask tutorial at the [ResBaz Sydney online conference](https://resbaz.github.io/resbaz2021/sydney/) on the 25th of November 2021. Thanks to the ResBaz organisers and to David McFarlane, Svetlana Tkachenko, and Oksana Tkachenko for monitoring the chat for questions on the day.
- Naty Clementi ran a Dask tutorial for the Women Who Code DC meetup on the 4th of November 2021. I assisted Naty, mostly by monitoring questions in the chat.

## Personal reflections

Reflecting back over the whole year, there were some things that worked well and some things that were less successful.

### Highlights from this year

My personal highlights include:

- ITK + Dask integration work (discussed in more detail above).
- A find objects fucntion for `dask-image` (discussed in more detail above).
- Visualization work, because it's very high impact. We're solving issues raised by life science groups, but the improved tools benefit EVERYONE who uses Dask.
- This bugfix from [dask PR #7391](https://github.com/dask/dask/pull/7391), because this single change fixed problems in four places at once (`scikit-image`, `dask-ml`, `xgcm/xhistogram`, and the cupy dask tests).
- Community building, conferences, and engagement. Lots of effort went into events over this year, and it's certainly paid dividends.

### What worked well

**Dask stale issues sprint**

- This was useful for the project, as well as useful for me.
  Sorting through old issues was an incredibly effective way to get familiar with who the experts are for particular topics. It would have been even better if this happened in the first few months of working on Dask, instead of the last few months.
- It's been suggested that one good way to gain familiarity is spending 6 months full time managing the issue tracker. Maybe that's true, but the much shorter stale issue sprint was a very efficient way of getting a lot of the same benefits in a short space of time. I'd recommend it for new maintainers or triage team members.

**Community building events**

We had a very successful year in terms of community building and events. This included tutorials, workshops, conferences, and community outreach. Summary of major events:

- Led a Dask tutorial at [ResBaz Sydney 2021](https://resbaz.github.io/resbaz2021/sydney/) in November.
- Co-led a half-day tutorial on napari and Dask at the [Light Microscopy Australia Meeting](https://www.lmameeting.com.au/) in August.
- SciPy 2021 presentation [Scaling Science: leveraging Dask for life sciences](https://www.youtube.com/watch?v=tY_lCGS1BMk&t=60s) in July.
- Organized the [Dask Life Science workshop](https://blog.dask.org/2021/05/24/life-science-summit-workshop) at the Dask Summit in May 2021. The life science workshop included 15 pre-recorded talks, and 3 interactive discussions.
- Co-organised the [Dask Down Under](https://blog.dask.org/2021/06/25/dask-down-under) workshop for the Dask Summit in May 2021. Dask Down Under contained 5 talks, 2 tutorials, 1 panel discussion, and 1 meet and greet networking event.
  Dask Down Under
- Expert panelist at the [VIS2021 symposium](https://www.vis2021.com.au/) in February.

**Visualization work**

This has been very high impact work, and I'm pleased with what we've achieved. Improved tools for visualization were requested by users in our survey of the life science community. This was a high priority, because improvements to visuzliation tools benefit EVERYONE who uses Dask.

### What didn't work so well

**Technical resources**

We never really solved the problem of finding someone I could go to with technical questions. I did have people to ask about some specific projects, but in most cases I didn't have a good way to direct questions to the right people. This is a challenging problem, especially because most Dask maintainers and contributors have full time jobs doing other things too. In my opinion, this negatively impacted the work and what we were able to achieve.

**Being added to the @dask/maintenance team**

There's no point getting notifications if you don't have GitHub permissions to do anything about them. In future I think we should add only people with at least triage or write permissions to the github teams.

**Real time interaction**

- We tried out "Ask a maintainer" office hours for the life science community, but they were poorly attended, so we cancelled this.
- We added some "Dask social chat" events to the calendar, but they were not very well attended outside of the first few. Most often, zero people attended. (There is another social chat for the Americas/Europe time zones, which is at a more convenient time for most people and might be more popular.)

**Slack**

Slack works well to DM specific people to set up meeting times, etc, but the public channels didn't end up being very useful for me personally.

**Lack of integration with other project teams**

You can only get so much done as a solo developer. We had hoped that I would naturally end up working with teams from several different projects, but this didn't really end up being the case. The `napari` project is an exception to this, and that relationship was well established before starting work for Dask. Perhaps there's something more we could have done here to facilitate more interaction.

## What's next for Genevieve?

Genevieve will be starting a new job next year, you can find her on GitHub [@GeneviveeBuckley](https://github.com/GenevieveBuckley/).

## What's next in Dask?

Lots of stuff has happened in Dask, but there is still lots left to do.
Here is a summary of the next steps for several projects. We'd love it if new people would like to take up the torch and contribute to any of these projects.

**ITK image compatibility with Dask**

- The next steps for the ITK + Dask project require ITK release candidate 5.3rc3 or above to become available (likely early in 2022).
- When the release is available, the next step is to try to re-run the code from the original [ITK blogpost](https://blog.dask.org/2019/08/09/image-itk).
- If there’s still work to be done we’ll need to open issues for the remaining blockers. And if it all works well, we'd like someone to write a second ITK + Dask blogpost to publicize the new functionality.

**Improving performance around rechunking**

More performance improvements related to rechunking is required (see [#7950](https://github.com/dask/dask/pull/7950) and [#7980](https://github.com/dask/dask/pull/7980)).

**High level graph work for arrays and slicing**

The high level graph work for slicing and overlapping arrays has a number of next steps.
Ian Rose has written [an excellent summary here](https://gist.github.com/ian-r-rose/4221ebf52f3423203640c498fb815f21). Briefly, the`cull` and `get_output_keys` methods must be implemented, then low level fusion and optimizations can be done.

Relevant links:

- Implement `cull` method for ArrayOverlapLayer [#7789](https://github.com/dask/dask/issues/7789)
- Implement `get_output_keys` method for ArrayOverlapLayer [#7791](https://github.com/dask/dask/issues/7791)
- [Array slicing HighLevelGraph layer #7655](https://github.com/dask/dask/pull/7655)

**Documentation**

- Dask needs better documentation for high level graphs. Both [user documentation](https://github.com/dask/dask/issues/7709) and [developer documentation](https://github.com/dask/dask/issues/7755) is required.

- At some future point, it might be worthwhile integrating blogpost content from
  [Choosing good chunk sizes in Dask](https://blog.dask.org/2021/11/02/choosing-dask-chunk-sizes) into the main [Dask documentation](https://docs.dask.org/en/latest/), for better discoverability.
