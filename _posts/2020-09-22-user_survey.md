---
layout: post
title: 2020 Dask User Survey
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

table tr:hover td {
    background: none;
}

</style>

This post presents the results of the 2020 Dask User Survey,
which ran earlier this summer. Thanks to everyone who took the time to fill out the survey!
These results help us better understand the Dask community and will guide future development efforts.

The raw data, as well as the start of an analysis, can be found in this binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dask/dask-examples/main?urlpath=%2Ftree%2Fsurveys%2F2020.ipynb)

Let us know if you find anything in the data.

## Highlights

- We had 240 responses to the survey (slightly fewer than last year, which had about 260).
- Overall, results look mostly similar to last year's.
- Our documentation has probably improved relative to last year
- Respondents care more about performance relative to last year.

## New Questions

Most of the questions are the same as in 2019. We added a couple questions about deployment and dashboard usage. Let's look at those first.

Among respondents who use a Dask package to deploy a cluster (about 53% of respondents), there's a wide spread of methods.

<img src="/images/2020_survey/2020_3_0.png">

Most people access the dashboard through a web browser. Those not using the dashboard are likely (hopefully) just using Dask on a single machine with the threaded scheduler (though the dashboard works fine on a single machine as well).

<img src="/images/2020_survey/2020_5_0.png">

## Learning Resources

Respondents' learning material usage is farily similar to last year. The most notable differences are from
our survey form providing more options (our [YouTube channel](https://www.youtube.com/channel/UCj9eavqmvwaCyKhIlu2GaoA) and "Gitter chat"). Other than that, [examples.dask.org](https://examples.dask.org) might be relatively more popular.

<img src="/images/2020_survey/2020_7_0.png">

Just like last year, we'll look at resource usage grouped by how often they use Dask.

<img src="/images/2020_survey/2020_10_0.png">

A few observations

- GitHub issues are becoming relatively less popular, which perhaps reflects better documentation or stability (assuming people go to the issue tracker when they can't find the answer in the docs or they hit a bug).
- <https://examples.dask.org> is notably now more popular among occasinal users.
- In response to last year's survey, we invested time in making <https://tutorial.dask.org> better, which we previously felt was lacking. Its usage is still about the same as last year's (pretty popular), so it's unclear whether we should dedicate additional focus there.

## How do you use Dask?

API usage remains about the same as last year (recall that about 20 fewer people took the survey and people can select multiple, so relative differences are most interesting). We added new choices for RAPIDS, Prefect, and XGBoost, each of which are somewhat popular (in the neighborhood of `dask.Bag`).

<img src="/images/2020_survey/2020_12_0.png">

About 65% of our users are using Dask on a cluster at least some of the time, which is similar to last year.

## How can Dask improve?

Respondents continue to say that more documentation and examples would be the most valuable improvements to the project.

One interesting change comes from looking at "Which would help you most right now?" split by API group (`dask.dataframe`, `dask.array`, etc.). Last year showed that "More examples" in my field was the most important for all API groups (first table below). But in 2020 there are some differences (second table below).

<style  type="text/css" >
    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col1 {
            background-color:  #cacee5;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col3 {
            background-color:  #f1ebf4;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col4 {
            background-color:  #c4cbe3;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col1 {
            background-color:  #3b92c1;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col3 {
            background-color:  #62a2cb;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col4 {
            background-color:  #bdc8e1;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col1 {
            background-color:  #c2cbe2;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col3 {
            background-color:  #94b6d7;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col4 {
            background-color:  #e0dded;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col1 {
            background-color:  #e6e2ef;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col3 {
            background-color:  #ced0e6;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col4 {
            background-color:  #c5cce3;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col0 {
            background-color:  #dedcec;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col3 {
            background-color:  #1c7fb8;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col4 {
            background-color:  #73a9cf;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col1 {
            background-color:  #b4c4df;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col3 {
            background-color:  #b4c4df;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col4 {
            background-color:  #eee9f3;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col0 {
            background-color:  #faf2f8;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col1 {
            background-color:  #e7e3f0;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col3 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col4 {
            background-color:  #f4eef6;
            color:  #000000;
        }</style><table id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87" ><caption>2019 normalized by row. Darker means that a higher proporiton of users of that API prefer that priority.</caption><thead>    <tr>        <th class="index_name level0" >Which would help you most right now?</th>        <th class="col_heading level0 col0" >Bug fixes</th>        <th class="col_heading level0 col1" >More documentation</th>        <th class="col_heading level0 col2" >More examples in my field</th>        <th class="col_heading level0 col3" >New features</th>        <th class="col_heading level0 col4" >Performance improvements</th>    </tr>    <tr>        <th class="index_name level0" >Dask APIs</th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>    </tr></thead><tbody>

                <tr>
                        <th id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87level0_row0" class="row_heading level0 row0" >Array</th>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col0" class="data row0 col0" >10</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col1" class="data row0 col1" >24</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col2" class="data row0 col2" >62</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col3" class="data row0 col3" >15</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row0_col4" class="data row0 col4" >25</td>
            </tr>
            <tr>
                        <th id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87level0_row1" class="row_heading level0 row1" >Bag</th>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col0" class="data row1 col0" >3</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col1" class="data row1 col1" >11</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col2" class="data row1 col2" >16</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col3" class="data row1 col3" >10</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row1_col4" class="data row1 col4" >7</td>
            </tr>
            <tr>
                        <th id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87level0_row2" class="row_heading level0 row2" >DataFrame</th>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col0" class="data row2 col0" >16</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col1" class="data row2 col1" >32</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col2" class="data row2 col2" >71</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col3" class="data row2 col3" >39</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row2_col4" class="data row2 col4" >26</td>
            </tr>
            <tr>
                        <th id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87level0_row3" class="row_heading level0 row3" >Delayed</th>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col0" class="data row3 col0" >16</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col1" class="data row3 col1" >22</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col2" class="data row3 col2" >55</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col3" class="data row3 col3" >26</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row3_col4" class="data row3 col4" >27</td>
            </tr>
            <tr>
                        <th id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87level0_row4" class="row_heading level0 row4" >Futures</th>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col0" class="data row4 col0" >12</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col1" class="data row4 col1" >9</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col2" class="data row4 col2" >25</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col3" class="data row4 col3" >20</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row4_col4" class="data row4 col4" >17</td>
            </tr>
            <tr>
                        <th id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87level0_row5" class="row_heading level0 row5" >ML</th>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col0" class="data row5 col0" >5</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col1" class="data row5 col1" >11</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col2" class="data row5 col2" >23</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col3" class="data row5 col3" >11</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row5_col4" class="data row5 col4" >7</td>
            </tr>
            <tr>
                        <th id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87level0_row6" class="row_heading level0 row6" >Xarray</th>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col0" class="data row6 col0" >8</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col1" class="data row6 col1" >11</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col2" class="data row6 col2" >34</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col3" class="data row6 col3" >7</td>
                        <td id="T_0a8701b8_e96b_11ea_9e95_186590cd1c87row6_col4" class="data row6 col4" >9</td>
            </tr>
    </tbody></table>

<style  type="text/css" >
    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col1 {
            background-color:  #f1ebf5;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col3 {
            background-color:  #f5eef6;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col4 {
            background-color:  #d0d1e6;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col0 {
            background-color:  #f0eaf4;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col3 {
            background-color:  #f0eaf4;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col4 {
            background-color:  #4c99c5;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col0 {
            background-color:  #f5eff6;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col3 {
            background-color:  #fcf4fa;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col4 {
            background-color:  #8eb3d5;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col1 {
            background-color:  #ebe6f2;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col3 {
            background-color:  #f5eff6;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col4 {
            background-color:  #3d93c2;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col1 {
            background-color:  #f5eef6;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col2 {
            background-color:  #0567a2;
            color:  #f1f1f1;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col3 {
            background-color:  #cacee5;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col4 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col0 {
            background-color:  #ede8f3;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col1 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col3 {
            background-color:  #c1cae2;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col4 {
            background-color:  #80aed2;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col0 {
            background-color:  #fff7fb;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col1 {
            background-color:  #f8f1f8;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col2 {
            background-color:  #023858;
            color:  #f1f1f1;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col3 {
            background-color:  #c9cee4;
            color:  #000000;
        }    #T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col4 {
            background-color:  #86b0d3;
            color:  #000000;
        }</style><table id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87" ><caption>2020 normalized by row. Darker means that a higher proporiton of users of that API prefer that priority.</caption><thead>    <tr>        <th class="index_name level0" >Which would help you most right now?</th>        <th class="col_heading level0 col0" >Bug fixes</th>        <th class="col_heading level0 col1" >More documentation</th>        <th class="col_heading level0 col2" >More examples in my field</th>        <th class="col_heading level0 col3" >New features</th>        <th class="col_heading level0 col4" >Performance improvements</th>    </tr>    <tr>        <th class="index_name level0" >Dask APIs</th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>        <th class="blank" ></th>    </tr></thead><tbody>

                <tr>
                        <th id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87level0_row0" class="row_heading level0 row0" >Array</th>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col0" class="data row0 col0" >12</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col1" class="data row0 col1" >16</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col2" class="data row0 col2" >56</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col3" class="data row0 col3" >15</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row0_col4" class="data row0 col4" >23</td>
            </tr>
            <tr>
                        <th id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87level0_row1" class="row_heading level0 row1" >Bag</th>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col0" class="data row1 col0" >7</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col1" class="data row1 col1" >5</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col2" class="data row1 col2" >24</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col3" class="data row1 col3" >7</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row1_col4" class="data row1 col4" >16</td>
            </tr>
            <tr>
                        <th id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87level0_row2" class="row_heading level0 row2" >DataFrame</th>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col0" class="data row2 col0" >24</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col1" class="data row2 col1" >21</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col2" class="data row2 col2" >67</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col3" class="data row2 col3" >22</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row2_col4" class="data row2 col4" >41</td>
            </tr>
            <tr>
                        <th id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87level0_row3" class="row_heading level0 row3" >Delayed</th>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col0" class="data row3 col0" >15</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col1" class="data row3 col1" >19</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col2" class="data row3 col2" >46</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col3" class="data row3 col3" >17</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row3_col4" class="data row3 col4" >34</td>
            </tr>
            <tr>
                        <th id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87level0_row4" class="row_heading level0 row4" >Futures</th>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col0" class="data row4 col0" >9</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col1" class="data row4 col1" >10</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col2" class="data row4 col2" >21</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col3" class="data row4 col3" >13</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row4_col4" class="data row4 col4" >24</td>
            </tr>
            <tr>
                        <th id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87level0_row5" class="row_heading level0 row5" >ML</th>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col0" class="data row5 col0" >6</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col1" class="data row5 col1" >4</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col2" class="data row5 col2" >21</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col3" class="data row5 col3" >9</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row5_col4" class="data row5 col4" >12</td>
            </tr>
            <tr>
                        <th id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87level0_row6" class="row_heading level0 row6" >Xarray</th>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col0" class="data row6 col0" >3</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col1" class="data row6 col1" >4</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col2" class="data row6 col2" >25</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col3" class="data row6 col3" >9</td>
                        <td id="T_0a8d3eac_e96b_11ea_9e95_186590cd1c87row6_col4" class="data row6 col4" >13</td>
            </tr>
    </tbody></table>

Examples are again the most important (for all API groups except `Futures`). But "Performance improvements" is now the second-most important improvement (except for `Futures` where it's most important). How should we interpret this? A charitable interpretation is that Dask's users are scaling to larger problems and are running into new scaling challenges. A less charitable interpretation is that our user's workflows are the same but Dask is getting slower!

## What other systems do you use?

SSH continues to be the most popular "cluster resource mananger". This was the big surprise last year, so we put in some work to make it nicer. Aside from that, not much has changed.

<img src="/images/2020_survey/2020_25_0.png">

And Dask users are about as happy with its stability as last year.

<img src="/images/2020_survey/2020_27_0.png">

## Takeaways

1. Overall, most things are similar to last year.
2. Documentation, especially domain-specific examples, continues to be important. That said, our documentation is probably better than it was last year.
3. More users are pushing Dask further. Investing in performance is likely to be valuable.

Thanks again to all the respondents!
