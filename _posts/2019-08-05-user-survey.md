---
layout: post
title: 2019 Dask User Survey
tagline: 2019 dask user survey
author: Tom Augspurger
tags: [User Survey]
theme: twitter
---

{% include JB/setup %}

<style type="text/css">
table td {
    background: none;
}

table tr.even td {
    background: none;
}

table {
    text-shadow: none;
}

</style>

## 2019 Dask User Survey Results

This notebook presents the results of the 2019 Dask User Survey,
which ran earlier this summer. Thanks to everyone who took the time to fill out the survey!
These results help us better understand the Dask community and will guide future development efforts.

The raw data, as well as the start of an analysis, can be found in this binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dask/dask-examples/main?urlpath=%2Ftree%2Fsurveys%2F2019.ipynb)

Let us know if you find anything in the data.

## Highlights

We had 259 responses to the survey. Overall, we found that the survey respondents really care about improved documentation, and ease of use (including ease of deployment), and scaling. While Dask brings together many different communities (big arrays versus big dataframes, traditional HPC users versus cloud-native resource managers), there was general agreement in what is most important for Dask.

Now we'll go through some individual items questions, highlighting particularly interesting results.

## How do you use Dask?

For learning resources, almost every respondent uses the documentation.

![svg](/images/analyze_files/analyze_4_0.svg)

Most respondents use Dask at least occasionally. Fortunately we had a decent number of respondents who are just looking into Dask, yet still spent the time to take the survey.

![svg](/images/analyze_files/analyze_6_0.svg)

I'm curiuos about how learning resource usage changes as users become more experienced. We might expect those just looking into Dask to start with `examples.dask.org`, where they can try out Dask without installing anything.

![svg](/images/analyze_files/analyze_8_0.svg)

Overall, documentation is still the leader across user user groups.

The usage of the [Dask tutorial](https://github.com/dask/dask-tutorial) and the [dask examples](examples.dask.org) are relatively consistent across groups. The primary difference between regular and new users is that regular users are more likely to engage on GitHub.

From StackOverflow questions and GitHub issues, we have a vague idea about which parts of the library are used.
The survey shows that (for our respondents at least) DataFrame and Delayed are the most commonly used APIs.

![svg](/images/analyze_files/analyze_10_0.svg)

    About 65.49% of our respondests are using Dask on a Cluster.

But the majority of respondents _also_ use Dask on their laptop.
This highlights the importance of Dask scaling down, either for
prototyping with a `LocalCluster`, or for out-of-core analysis
using `LocalCluster` or one of the single-machine schedulers.

![svg](/images/analyze_files/analyze_13_0.svg)

Most respondents use Dask interactively, at least some of the time.

![svg](/images/analyze_files/analyze_15_0.svg)

Most repondents thought that more documentation and examples would be the most valuable improvements to the project. This is especially pronounced among new users. But even among those using Dask everyday more people thought that "More examples" is more valuable than "New features" or "Performance improvements".

<style  type="text/css" >
    #T_820ef326_b488_11e9_ad41_186590cd1c87row0_col0 {
            background-color:  #3b92c1;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row0_col1 {
            background-color:  #b4c4df;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row0_col2 {
            background-color:  #dad9ea;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row0_col3 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row0_col4 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row1_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row1_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row1_col2 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row1_col3 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row1_col4 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row2_col0 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row2_col1 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row2_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row2_col3 {
            background-color:  #1b7eb7;
            color:  #000000;
        }    #T_820ef326_b488_11e9_ad41_186590cd1c87row2_col4 {
            background-color:  #589ec8;
            color:  #000000;
        }</style><table id="T_820ef326_b488_11e9_ad41_186590cd1c87" ><caption>Normalized by row. Darker means that a higher proporiton of users with that usage frequency prefer that priority.</caption><thead>    <tr>        <th class="index_name level0" >Which would help you most right now?</th>        <th class="col_heading level0 col0" >Bug fixes</th>        <th class="col_heading level0 col1" >More documentation</th>        <th class="col_heading level0 col2" >More examples in my field</th>        <th class="col_heading level0 col3" >New features</th>        <th class="col_heading level0 col4" >Performance improvements</th>    </tr>    <tr>        <th class="index_name level0" >How often do you use Dask?</th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>    </tr></thead><tbody>

                <tr>
                        <th id="T_820ef326_b488_11e9_ad41_186590cd1c87level0_row0" class="row_heading level0 row0" >Every day</th>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row0_col0" class="data row0 col0" >9</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row0_col1" class="data row0 col1" >11</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row0_col2" class="data row0 col2" >25</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row0_col3" class="data row0 col3" >22</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row0_col4" class="data row0 col4" >23</td>
            </tr>
            <tr>
                        <th id="T_820ef326_b488_11e9_ad41_186590cd1c87level0_row1" class="row_heading level0 row1" >Just looking for now</th>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row1_col0" class="data row1 col0" >1</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row1_col1" class="data row1 col1" >3</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row1_col2" class="data row1 col2" >18</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row1_col3" class="data row1 col3" >9</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row1_col4" class="data row1 col4" >5</td>
            </tr>
            <tr>
                        <th id="T_820ef326_b488_11e9_ad41_186590cd1c87level0_row2" class="row_heading level0 row2" >Occasionally</th>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row2_col0" class="data row2 col0" >14</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row2_col1" class="data row2 col1" >27</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row2_col2" class="data row2 col2" >52</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row2_col3" class="data row2 col3" >18</td>
                        <td id="T_820ef326_b488_11e9_ad41_186590cd1c87row2_col4" class="data row2 col4" >15</td>
            </tr>
    </tbody></table>

Perhaps users of certain dask APIs feel differenlty from the group as a whole? We perform a similar analysis grouped by API use, rather than frequency of use.

<style  type="text/css" >
    #T_821479f4_b488_11e9_ad41_186590cd1c87row0_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row0_col1 {
            background-color:  #cacee5;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row0_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row0_col3 {
            background-color:  #f1ebf4;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row0_col4 {
            background-color:  #c4cbe3;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row1_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row1_col1 {
            background-color:  #3b92c1;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row1_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row1_col3 {
            background-color:  #62a2cb;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row1_col4 {
            background-color:  #bdc8e1;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row2_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row2_col1 {
            background-color:  #c2cbe2;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row2_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row2_col3 {
            background-color:  #94b6d7;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row2_col4 {
            background-color:  #e0dded;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row3_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row3_col1 {
            background-color:  #e6e2ef;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row3_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row3_col3 {
            background-color:  #ced0e6;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row3_col4 {
            background-color:  #c5cce3;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row4_col0 {
            background-color:  #dedcec;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row4_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row4_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row4_col3 {
            background-color:  #1c7fb8;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row4_col4 {
            background-color:  #73a9cf;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row5_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row5_col1 {
            background-color:  #b4c4df;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row5_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row5_col3 {
            background-color:  #b4c4df;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row5_col4 {
            background-color:  #eee9f3;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row6_col0 {
            background-color:  #faf2f8;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row6_col1 {
            background-color:  #e7e3f0;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row6_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row6_col3 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_821479f4_b488_11e9_ad41_186590cd1c87row6_col4 {
            background-color:  #f4eef6;
            color:  #000000;
        }</style><table id="T_821479f4_b488_11e9_ad41_186590cd1c87" ><caption>Normalized by row. Darker means that a higher proporiton of users of that API prefer that priority.</caption><thead>    <tr>        <th class="index_name level0" >Which would help you most right now?</th>        <th class="col_heading level0 col0" >Bug fixes</th>        <th class="col_heading level0 col1" >More documentation</th>        <th class="col_heading level0 col2" >More examples in my field</th>        <th class="col_heading level0 col3" >New features</th>        <th class="col_heading level0 col4" >Performance improvements</th>    </tr>    <tr>        <th class="index_name level0" >Dask APIs</th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>    </tr></thead><tbody>

                <tr>
                        <th id="T_821479f4_b488_11e9_ad41_186590cd1c87level0_row0" class="row_heading level0 row0" >Array</th>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row0_col0" class="data row0 col0" >10</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row0_col1" class="data row0 col1" >24</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row0_col2" class="data row0 col2" >62</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row0_col3" class="data row0 col3" >15</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row0_col4" class="data row0 col4" >25</td>
            </tr>
            <tr>
                        <th id="T_821479f4_b488_11e9_ad41_186590cd1c87level0_row1" class="row_heading level0 row1" >Bag</th>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row1_col0" class="data row1 col0" >3</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row1_col1" class="data row1 col1" >11</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row1_col2" class="data row1 col2" >16</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row1_col3" class="data row1 col3" >10</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row1_col4" class="data row1 col4" >7</td>
            </tr>
            <tr>
                        <th id="T_821479f4_b488_11e9_ad41_186590cd1c87level0_row2" class="row_heading level0 row2" >DataFrame</th>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row2_col0" class="data row2 col0" >16</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row2_col1" class="data row2 col1" >32</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row2_col2" class="data row2 col2" >71</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row2_col3" class="data row2 col3" >39</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row2_col4" class="data row2 col4" >26</td>
            </tr>
            <tr>
                        <th id="T_821479f4_b488_11e9_ad41_186590cd1c87level0_row3" class="row_heading level0 row3" >Delayed</th>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row3_col0" class="data row3 col0" >16</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row3_col1" class="data row3 col1" >22</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row3_col2" class="data row3 col2" >55</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row3_col3" class="data row3 col3" >26</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row3_col4" class="data row3 col4" >27</td>
            </tr>
            <tr>
                        <th id="T_821479f4_b488_11e9_ad41_186590cd1c87level0_row4" class="row_heading level0 row4" >Futures</th>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row4_col0" class="data row4 col0" >12</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row4_col1" class="data row4 col1" >9</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row4_col2" class="data row4 col2" >25</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row4_col3" class="data row4 col3" >20</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row4_col4" class="data row4 col4" >17</td>
            </tr>
            <tr>
                        <th id="T_821479f4_b488_11e9_ad41_186590cd1c87level0_row5" class="row_heading level0 row5" >ML</th>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row5_col0" class="data row5 col0" >5</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row5_col1" class="data row5 col1" >11</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row5_col2" class="data row5 col2" >23</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row5_col3" class="data row5 col3" >11</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row5_col4" class="data row5 col4" >7</td>
            </tr>
            <tr>
                        <th id="T_821479f4_b488_11e9_ad41_186590cd1c87level0_row6" class="row_heading level0 row6" >Xarray</th>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row6_col0" class="data row6 col0" >8</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row6_col1" class="data row6 col1" >11</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row6_col2" class="data row6 col2" >34</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row6_col3" class="data row6 col3" >7</td>
                        <td id="T_821479f4_b488_11e9_ad41_186590cd1c87row6_col4" class="data row6 col4" >9</td>
            </tr>
    </tbody></table>

Nothing really stands out. The "futures" users (who we expect to be relatively advanced) may prioritize features and performance over documentation. But everyone agrees that more examples are the highest priority.

## Common Feature Requests

For specific features, we made a list of things that we (as developers) thought might be important.

![svg](/images/analyze_files/analyze_22_0.svg)

The clearest standout is how many people thought "Better NumPy/Pandas support" was "most critical". In hindsight, it'd be good to have a followup fill-in field to undertand what each respondent meant by that. The parsimonious interpretion is "cover more of the NumPy / pandas API".

"Ease of deployment" had a high proportion of "critical to me". Again in hindsight, I notice a bit of ambiguity. Does this mean people want Dask to be easier to deploy? Or does this mean that Dask, which they currently find easy to deploy, is critically important? Regardless, we can prioritize simplicity in deployment.

Relatively few respondents care about things like "Managing many users", though we expect that this would be relatively popular among system administartors, who are a smaller population.

And of course, we have people pushing Dask to its limits for whom "Improving scaling" is critically important.

## What other systems do you use?

A relatively high proportion of respondents use Python 3 (97% compared to 84% in the most recent [Python Developers Survey](https://www.jetbrains.com/research/python-developers-survey-2018/)).

    3    97.29%
    2     2.71%
    Name: Python 2 or 3?, dtype: object

We were a bit surprised to see that SSH is the most popular "cluster resource manager".

    SSH                                                       98
    Kubernetes                                                73
    HPC resource manager (SLURM, PBS, SGE, LSF or similar)    61
    My workplace has a custom solution for this               23
    I don't know, someone else does this for me               16
    Hadoop / Yarn / EMR                                       14
    Name: If you use a cluster, how do you launch Dask? , dtype: int64

How does cluster-resource manager compare with API usage?

<style  type="text/css" >
    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col0 {
            background-color:  #056faf;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col3 {
            background-color:  #034e7b;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col4 {
            background-color:  #2685bb;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col5 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col6 {
            background-color:  #f2ecf5;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col0 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col1 {
            background-color:  #f7f0f7;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col2 {
            background-color:  #0771b1;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col3 {
            background-color:  #0771b1;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col4 {
            background-color:  #c5cce3;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col5 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col6 {
            background-color:  #79abd0;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col0 {
            background-color:  #8bb2d4;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col1 {
            background-color:  #b4c4df;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col3 {
            background-color:  #589ec8;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col4 {
            background-color:  #eee9f3;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col5 {
            background-color:  #8bb2d4;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col6 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col0 {
            background-color:  #4c99c5;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col3 {
            background-color:  #056dac;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col4 {
            background-color:  #73a9cf;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col5 {
            background-color:  #d9d8ea;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col6 {
            background-color:  #f3edf5;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col0 {
            background-color:  #056ba9;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col3 {
            background-color:  #1379b5;
            color:  #f1f1f1;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col4 {
            background-color:  #dfddec;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col5 {
            background-color:  #e8e4f0;
            color:  #000000;
        }    #T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col6 {
            background-color:  #f9f2f8;
            color:  #000000;
        }</style><table id="T_8326d0f8_b488_11e9_ad41_186590cd1c87" ><thead>    <tr>        <th class="index_name level0" >Dask APIs</th>        <th class="col_heading level0 col0" >Array</th>        <th class="col_heading level0 col1" >Bag</th>        <th class="col_heading level0 col2" >DataFrame</th>        <th class="col_heading level0 col3" >Delayed</th>        <th class="col_heading level0 col4" >Futures</th>        <th class="col_heading level0 col5" >ML</th>        <th class="col_heading level0 col6" >Xarray</th>    </tr>    <tr>        <th class="index_name level0" >If you use a cluster, how do you launch Dask? </th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>    </tr></thead><tbody>

                <tr>
                        <th id="T_8326d0f8_b488_11e9_ad41_186590cd1c87level0_row0" class="row_heading level0 row0" >Custom</th>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col0" class="data row0 col0" >15</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col1" class="data row0 col1" >6</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col2" class="data row0 col2" >18</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col3" class="data row0 col3" >17</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col4" class="data row0 col4" >14</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col5" class="data row0 col5" >6</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row0_col6" class="data row0 col6" >7</td>
            </tr>
            <tr>
                        <th id="T_8326d0f8_b488_11e9_ad41_186590cd1c87level0_row1" class="row_heading level0 row1" >HPC</th>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col0" class="data row1 col0" >50</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col1" class="data row1 col1" >13</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col2" class="data row1 col2" >40</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col3" class="data row1 col3" >40</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col4" class="data row1 col4" >22</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col5" class="data row1 col5" >11</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row1_col6" class="data row1 col6" >30</td>
            </tr>
            <tr>
                        <th id="T_8326d0f8_b488_11e9_ad41_186590cd1c87level0_row2" class="row_heading level0 row2" >Hadoop / Yarn / EMR</th>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col0" class="data row2 col0" >7</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col1" class="data row2 col1" >6</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col2" class="data row2 col2" >12</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col3" class="data row2 col3" >8</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col4" class="data row2 col4" >4</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col5" class="data row2 col5" >7</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row2_col6" class="data row2 col6" >3</td>
            </tr>
            <tr>
                        <th id="T_8326d0f8_b488_11e9_ad41_186590cd1c87level0_row3" class="row_heading level0 row3" >Kubernetes</th>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col0" class="data row3 col0" >40</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col1" class="data row3 col1" >18</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col2" class="data row3 col2" >56</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col3" class="data row3 col3" >47</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col4" class="data row3 col4" >37</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col5" class="data row3 col5" >26</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row3_col6" class="data row3 col6" >21</td>
            </tr>
            <tr>
                        <th id="T_8326d0f8_b488_11e9_ad41_186590cd1c87level0_row4" class="row_heading level0 row4" >SSH</th>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col0" class="data row4 col0" >61</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col1" class="data row4 col1" >23</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col2" class="data row4 col2" >72</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col3" class="data row4 col3" >58</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col4" class="data row4 col4" >32</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col5" class="data row4 col5" >30</td>
                        <td id="T_8326d0f8_b488_11e9_ad41_186590cd1c87row4_col6" class="data row4 col6" >25</td>
            </tr>
    </tbody></table>

HPC users are relatively heavy users of `dask.array` and xarray.

Somewhat surprisingly, Dask's heaviest users find dask stable enough. Perhaps they've pushed past the bugs and found workarounds (percentages are normalized by row).

![svg](/images/analyze_files/analyze_32_0.svg)

## Takeaways

1. We should prioritize improving and expanding our documentation and examples. This may be
   accomplished by Dask maintainers seeking examples from the community. Many of the examples
   on <https://examples.dask.org> were developed by domain specialist who use Dask.
2. Improved scaling to larger problems is important, but we shouldn't
   sacrifice the single-machine usecase to get there.
3. Both interactive and batch workflows are important.
4. Dask's various sub-communities are more similar than they are different.

Thanks again to all the respondents. We look forward to repeating this process to identify trends over time.
