---
layout: post
title: 2019 Dask User Survey
tagline: 2019 dask user survey
author: Tom Augspurger
tags: []
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


# 2019 Dask User Survey Results

This notebook presents the results of the 2019 Dask User Survey,
which ran earlier this summer. Thanks to everyone who took the time to fill out the survey!
These results help us better understand the Dask community and will guide future development efforts.

The raw data, as well as the start of an analysis, can be found in this binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/TomAugspurger/dask-survey-results/master?filepath=analyze.ipynb)

Let us know if you find anything in the data.

## Highlights

We had 259 responses to the survey. Overall, we found that the survey respondents really care about improved documentation, and ease of use (including ease of deployment), and scaling. While Dask brings together many different communities (big arrays versus big dataframes, traditional HPC users versus cloud-native resource managers), there was general agreement in what is most important for Dask.


Each row of the DataFrame is a single response. Each column is some metadata (e.g. `Timestamp`) or a specific question.

## Results per day

The bulk of our responses came on the first day. After that, we had a handful of trickling in daily.



![svg](/images/analyze_files/analyze_4_0.svg)


We had good response rates on each question. Most were skipped by fewer than 2% of the respondents.
Those with higher non-response rates (like "Preferred Cloud") aren't applicable to everyone.





    Timestamp                                             0.000000
    Dask APIs                                             0.011583
    Interactive or Batch?                                 0.019305
    Local machine or Cluster?                             0.015444
    How often do you use Dask?                            0.003861
    What Dask resources have you used for [...]           0.015444
    Which would help you most right now?                  0.027027
    Is Dask stable enough for you?                        0.023166
    What common feature requests do you care [...]        0.011583
    What common feature requests do you care [...]        0.061776
    What common feature requests do you care [...]        0.054054
    What common feature requests do you care [...]        0.073359
    What common feature requests do you care [...]        0.054054
    What common feature requests do you care [...]        0.046332
    What common feature requests do you care [...]        0.057915
    What common feature requests do you care [...]        0.065637
    What common feature requests do you care [...]        0.065637
    What common feature requests do you care [...]        0.038610
    Python 2 or 3?                                        0.003861
    If you use a cluster, how do you launch Dask?         0.193050
    Preferred Cloud?                                      0.281853
    What are some other libraries that you often [...]    0.362934
    How easy is it for you to upgrade to newer [...]      0.015444
    Do you use Dask as part of a larger group?            0.011583
    dtype: float64



Now we'll go through some individual items questions, highlighting particularly interesting results.

## How do you use Dask?

For learning resources, almost every respondent uses the documentation.



![svg](/images/analyze_files/analyze_10_0.svg)


Most respondents use Dask at least occasionally. Fortunately we had a decent number of respondents who are just looking into Dask, yet still spent the time to take the survey.



![svg](/images/analyze_files/analyze_12_0.svg)


I'm curiuos about how learning resource usage changes as users become more experienced. We might expect those just looking into Dask to start with `examples.dask.org`, where they can try out Dask without installing anything.



![svg](/images/analyze_files/analyze_14_0.svg)


Overall, documentation is still the leader across user user groups.

The usage of the [Dask tutorial](https://github.com/dask/dask-tutorial) and the [dask examples](examples.dask.org) are relatively consistent across groups. The primary difference between regular and new users is that regular users are more likely to engage on GitHub.

From StackOverflow questions and GitHub issues, we have a vague idea about which parts of the library are used.
The survey shows that (for our respondents at least) DataFrame and Delayed are the most commonly used APIs.



![svg](/images/analyze_files/analyze_16_0.svg)



    About 65.49% of our respondests are using Dask on a Cluster.


But the majority of respondents *also* use Dask on their laptop.
This highlights the importance of Dask scaling down, either for
prototyping with a `LocalCluster`, or for out-of-core analysis
using `LocalCluster` or one of the single-machine schedulers.



![svg](/images/analyze_files/analyze_19_0.svg)


Most respondents use Dask interactively, at least some of the time.



![svg](/images/analyze_files/analyze_21_0.svg)


Most repondents thought that more documentation and examples would be the most valuable improvements to the project. This is especially pronounced among new users. But even among those using Dask everyday more people thought that "More examples" is more valuable than "New features" or "Performance improvements".





<style  type="text/css" >
    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row0_col0 {
          background:  #fff7fb;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row0_col1 {
          background:  #ece7f2;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row0_col2 {
          background:  #023858;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row0_col3 {
          background:  #04649e;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row0_col4 {
          background:  #04598c;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row1_col0 {
          background:  #fff7fb;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row1_col1 {
          background:  #ede8f3;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row1_col2 {
          background:  #023858;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row1_col3 {
          background:  #80aed2;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row1_col4 {
          background:  #d3d4e7;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row2_col0 {
          background:  #fff7fb;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row2_col1 {
          background:  #b1c2de;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row2_col2 {
          background:  #023858;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row2_col3 {
          background:  #f0eaf4;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87 row2_col4 {
          background:  #fbf4f9;
    }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col0 {
            background-color:  #fff7fb;
            color:  #000000;
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col1 {
            background-color:  #ece7f2;
            color:  #000000;
            background-color:  #ece7f2;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col3 {
            background-color:  #04649e;
            color:  #f1f1f1;
            background-color:  #04649e;
            color:  #f1f1f1;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col4 {
            background-color:  #04598c;
            color:  #f1f1f1;
            background-color:  #04598c;
            color:  #f1f1f1;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col0 {
            background-color:  #fff7fb;
            color:  #000000;
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col1 {
            background-color:  #ede8f3;
            color:  #000000;
            background-color:  #ede8f3;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col3 {
            background-color:  #80aed2;
            color:  #000000;
            background-color:  #80aed2;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col4 {
            background-color:  #d3d4e7;
            color:  #000000;
            background-color:  #d3d4e7;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col0 {
            background-color:  #fff7fb;
            color:  #000000;
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col1 {
            background-color:  #b1c2de;
            color:  #000000;
            background-color:  #b1c2de;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col3 {
            background-color:  #f0eaf4;
            color:  #000000;
            background-color:  #f0eaf4;
            color:  #000000;
        }    #T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col4 {
            background-color:  #fbf4f9;
            color:  #000000;
            background-color:  #fbf4f9;
            color:  #000000;
        }</style><table id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87" ><caption>Normalized by row. Darker means that a higher proporiton of users with that usage frequency prefer that priority.</caption><thead>    <tr>        <th class="index_name level0" >Which would help you most right now?</th>        <th class="col_heading level0 col0" >Bug fixes</th>        <th class="col_heading level0 col1" >More documentation</th>        <th class="col_heading level0 col2" >More examples in my field</th>        <th class="col_heading level0 col3" >New features</th>        <th class="col_heading level0 col4" >Performance improvements</th>    </tr>    <tr>        <th class="index_name level0" >How often do you use Dask?</th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>    </tr></thead><tbody>
                <tr>
                        <th id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87level0_row0" class="row_heading level0 row0" >Every day</th>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col0" class="data row0 col0" >9</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col1" class="data row0 col1" >11</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col2" class="data row0 col2" >25</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col3" class="data row0 col3" >22</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row0_col4" class="data row0 col4" >23</td>
            </tr>
            <tr>
                        <th id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87level0_row1" class="row_heading level0 row1" >Just looking for now</th>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col0" class="data row1 col0" >1</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col1" class="data row1 col1" >3</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col2" class="data row1 col2" >18</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col3" class="data row1 col3" >9</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row1_col4" class="data row1 col4" >5</td>
            </tr>
            <tr>
                        <th id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87level0_row2" class="row_heading level0 row2" >Occasionally</th>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col0" class="data row2 col0" >14</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col1" class="data row2 col1" >27</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col2" class="data row2 col2" >52</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col3" class="data row2 col3" >18</td>
                        <td id="T_a5fedb32_b3d6_11e9_b370_186590cd1c87row2_col4" class="data row2 col4" >15</td>
            </tr>
    </tbody></table>



Perhaps users of certain dask APIs feel differenlty from the group as a whole? We perform a similar analysis grouped by API use, rather than frequency of use.





<style  type="text/css" >
    #T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col1 {
            background-color:  #cacee5;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col3 {
            background-color:  #f1ebf4;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col4 {
            background-color:  #c4cbe3;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col1 {
            background-color:  #3b92c1;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col3 {
            background-color:  #62a2cb;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col4 {
            background-color:  #bdc8e1;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col1 {
            background-color:  #c2cbe2;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col3 {
            background-color:  #94b6d7;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col4 {
            background-color:  #e0dded;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col1 {
            background-color:  #e6e2ef;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col3 {
            background-color:  #ced0e6;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col4 {
            background-color:  #c5cce3;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col0 {
            background-color:  #dedcec;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col3 {
            background-color:  #1c7fb8;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col4 {
            background-color:  #73a9cf;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col1 {
            background-color:  #b4c4df;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col3 {
            background-color:  #b4c4df;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col4 {
            background-color:  #eee9f3;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col0 {
            background-color:  #faf2f8;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col1 {
            background-color:  #e7e3f0;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col3 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col4 {
            background-color:  #f4eef6;
            color:  #000000;
        }</style><table id="T_a605221c_b3d6_11e9_b370_186590cd1c87" ><caption>Normalized by row. Darker means that a higher proporiton of users of that API prefer that priority.</caption><thead>    <tr>        <th class="index_name level0" >Which would help you most right now?</th>        <th class="col_heading level0 col0" >Bug fixes</th>        <th class="col_heading level0 col1" >More documentation</th>        <th class="col_heading level0 col2" >More examples in my field</th>        <th class="col_heading level0 col3" >New features</th>        <th class="col_heading level0 col4" >Performance improvements</th>    </tr>    <tr>        <th class="index_name level0" >Dask APIs</th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>    </tr></thead><tbody>
                <tr>
                        <th id="T_a605221c_b3d6_11e9_b370_186590cd1c87level0_row0" class="row_heading level0 row0" >Array</th>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col0" class="data row0 col0" >10</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col1" class="data row0 col1" >24</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col2" class="data row0 col2" >62</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col3" class="data row0 col3" >15</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row0_col4" class="data row0 col4" >25</td>
            </tr>
            <tr>
                        <th id="T_a605221c_b3d6_11e9_b370_186590cd1c87level0_row1" class="row_heading level0 row1" >Bag</th>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col0" class="data row1 col0" >3</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col1" class="data row1 col1" >11</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col2" class="data row1 col2" >16</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col3" class="data row1 col3" >10</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row1_col4" class="data row1 col4" >7</td>
            </tr>
            <tr>
                        <th id="T_a605221c_b3d6_11e9_b370_186590cd1c87level0_row2" class="row_heading level0 row2" >DataFrame</th>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col0" class="data row2 col0" >16</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col1" class="data row2 col1" >32</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col2" class="data row2 col2" >71</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col3" class="data row2 col3" >39</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row2_col4" class="data row2 col4" >26</td>
            </tr>
            <tr>
                        <th id="T_a605221c_b3d6_11e9_b370_186590cd1c87level0_row3" class="row_heading level0 row3" >Delayed</th>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col0" class="data row3 col0" >16</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col1" class="data row3 col1" >22</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col2" class="data row3 col2" >55</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col3" class="data row3 col3" >26</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row3_col4" class="data row3 col4" >27</td>
            </tr>
            <tr>
                        <th id="T_a605221c_b3d6_11e9_b370_186590cd1c87level0_row4" class="row_heading level0 row4" >Futures</th>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col0" class="data row4 col0" >12</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col1" class="data row4 col1" >9</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col2" class="data row4 col2" >25</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col3" class="data row4 col3" >20</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row4_col4" class="data row4 col4" >17</td>
            </tr>
            <tr>
                        <th id="T_a605221c_b3d6_11e9_b370_186590cd1c87level0_row5" class="row_heading level0 row5" >ML</th>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col0" class="data row5 col0" >5</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col1" class="data row5 col1" >11</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col2" class="data row5 col2" >23</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col3" class="data row5 col3" >11</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row5_col4" class="data row5 col4" >7</td>
            </tr>
            <tr>
                        <th id="T_a605221c_b3d6_11e9_b370_186590cd1c87level0_row6" class="row_heading level0 row6" >Xarray</th>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col0" class="data row6 col0" >8</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col1" class="data row6 col1" >11</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col2" class="data row6 col2" >34</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col3" class="data row6 col3" >7</td>
                        <td id="T_a605221c_b3d6_11e9_b370_186590cd1c87row6_col4" class="data row6 col4" >9</td>
            </tr>
    </tbody></table>



Nothing really stands out. The "futures" users (who we expect to be relatively advanced) may prioritize features and performance over documentation. But everyone agrees that more examples are the highest priority.

## Common Feature Requests

For specific features, we made a list of things that we (as developers) thought might be important.





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Better Numpy/Pandas support</th>
      <th>Better Scikit-Learn/ML support</th>
      <th>Integrate with Deep Learning Frameworks</th>
      <th>Support for new libraries in my field</th>
      <th>Improve Scaling</th>
      <th>Dashboard / Diagnostics</th>
      <th>Ease of deployment</th>
      <th>Cloud integration</th>
      <th>Managing many users</th>
      <th>GPUs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Critical to me</td>
      <td>Not relevant for me</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Not relevant for me</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Critical to me</td>
      <td>Critical to me</td>
      <td>Not relevant for me</td>
      <td>Not relevant for me</td>
      <td>Critical to me</td>
      <td>Critical to me</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Critical to me</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Critical to me</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Critical to me</td>
      <td>Critical to me</td>
      <td>Critical to me</td>
      <td>Critical to me</td>
      <td>Somewhat useful</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Critical to me</td>
      <td>Critical to me</td>
      <td>Somewhat useful</td>
      <td>Critical to me</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
      <td>Somewhat useful</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Somewhat useful</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>Somewhat useful</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>Somewhat useful</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




The clearest standout is how many people thought "Better NumPy/Pandas support" was "most critical". In hindsight, it'd be good to have a followup fill-in field to undertand what each respondent meant by that. The parsimonious interpretion is "cover more of the NumPy / pandas API".

"Ease of deployment" had a high proportion of "critical to me". Again in hindsight, I notice a bit of ambiguity. Does this mean people want Dask to be easier to deploy? Or does this mean that Dask, which they currently find easy to deploy, is critically important? Regardless, we can prioritize simplicity in deployment.

Relatively few respondents care about things like "Managing many users", though we expect that this would be relatively popular among system administartors, who are a smaller population.

And of course, we have people pushing Dask to its limits for whom "Improving scaling" is critically important.

## What other systems do you use?

A relatively high proportion of respondents use Python 3 (97% compared to 84% in the most recent [Python Developers Survey](https://www.jetbrains.com/research/python-developers-survey-2018/)).


We were a bit surprised to see that SSH is the most popular "cluster resource manager".


How does cluster-resource manager compare with API usage?


HPC users are relatively heavy users of `dask.array` and xarray.

Somewhat surprisingly, Dask's heaviest users find dask stable enough. Perhaps they've pushed past the bugs and found workarounds (percentages are normalized by row).


## Takeaways

1. We should prioritize improving and expanding our documentation and examples. This may be
   accomplished by Dask maintainers seeking examples from the community. Many of the examples
   on https://examples.dask.org were developed by domain specialist who use Dask.
2. Improved scaling to larger problems is important, but we shouldn't
   sacrifice the single-machine usecase to get there.
3. Both interactive and batch workflows are important.
4. Dask's various sub-communities are more similar than they are different.

Thanks again to all the respondents. We look forward to repeating this process to identify trends over time.
