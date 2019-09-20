---
layout: post
title: Better and faster hyperparameter optimization with Dask
author: <a href="http://stsievert.com">Scott Sievert</a>
tags: [machine-learning, dask-ml]
theme: twitter
---
{% include JB/setup %}

*Scott Sievert wrote this post. The original post lives at
[https://stsievert.com/blog/2019/09/19/dask-hyperparam-opt/][1] with better
styling. This work is supported by Anaconda, Inc.*

[1]:https://stsievert.com/blog/2019/09/19/dask-hyperparam-opt/

[Dask]'s machine learning package, [Dask-ML] now implements Hyperband, an
advanced "hyperparameter optimizaiton" algorithm that performs rather well.
This post will

* describe "hyperparameter optimization", a common problem in machine learning
* describe Hyperband's benefits and why it works
* show how to use Hyperband via an example, alongside performance comparisons
  for the same example

[Dask]:https://dask.org
[Dask-ML]:https://ml.dask.org/

In this post, I'll walk through a practical example and highlight key portions
of "[Better and faster hyperparameter optimization with Dask][scipy19]".

<!--More-->

## Problem

Any machine learning requires data, an untrained model or
model and "hyperparameters", parameters that are chosen before training begins that
help with cohesion between the model and data. The user needs to specify values
for these hyperparameters in order to use the model. A good example is
adapting ridge regression or LASSO to the amount of noise in the
data with the regularization parameter.[^alpha]

[^alpha]:Which amounts to choosing `alpha` in Scikit-learn's [Ridge](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html) or [LASSO](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html)

Model performance strongly depends on the hyperparameters provided.  A simple
example is tuning the regularization parameter in ridge regression or
LASSO.[^regularization] Another more complex example is a particular
visualization tool, [t-SNE]. This tool requires (at least) three
hyperparameters, and the first section in "[How to Use t-SNE
Effectively][tsne-study]" is titled "Those hyperparameters really matter".

[^regularization]:Performance comparison: Scikit-learn's visualization of tuning a Support Vector Machine's (SVM) regularization parameter: [Scaling the regularization parameter for SVCs][sklearn-reg]
[tsne-study]:https://distill.pub/2016/misread-tsne/
[sklearn-reg]:https://scikit-learn.org/stable/auto_examples/svm/plot_svm_scale_c.html
[t-SNE]:https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html

These hyperparameters need to be specified by the user. There are no good
heuristics for determining what the values should be.  Finding decent values
for these hyperparameters or "hyperparameter optimization" grows more complex
as the number of hyperparameters grow.

Finding good values for these hyperparameters is critical and has an entire
Scikit-Learn documentation page, "[Tuning the hyperparameters of an
estimator]." Briefly, finding the decent values of hyperparameters
is difficult and requires guessing or searching.

[Tuning the hyperparameters of an estimator]:http://scikit-learn.org/stable/modules/grid_search.html

**How can these hyperparameters be found quickly and efficiently with an
advanced task scheduler like Dask?** Parallelism will pose some challenges, but
the Dask architecture enables some advanced algorithms.

## Contributions

Dask-ML can quickly find high-performing hyperparameters.

I will back this
claim with intuition and experimental evidence. Specifically, Dask-ML now
implements an algorithm introduced by Li et. al. in "[Hyperband: A novel
bandit-based approach to hyperparameter optimization][hyperband-paper]".

[hyperband-paper]:https://arxiv.org/pdf/1603.06560.pdf

Pairing of Dask and Hyperband enables some exciting new performance opportunities.
Hyperband is fairly new,[^new] and this is the first implementation with an
advanced task scheduler like Dask that I'm aware of.[^other-work]

[^new]:By some metrics. It's been around since 2016 and some call that "old news."
[^other-work]:Including with [Ray-Tune's implementation][asha-ray] and "[Massively Parallel Hyperparameter Tuning][asha]".
[asha-ray]:https://ray.readthedocs.io/en/latest/tune-schedulers.html#asynchronous-hyperband
[asha]:https://arxiv.org/pdf/1810.05934.pdf

I'll highlight some key points of the corresponding paper,
"[Better and faster hyperparameter optimization with Dask][scipy19]".  Let's go
through the basics of Hyperband then illustrate its use and performance with
an example.

## Hyperband basics

The motivation for Hyperband is to find high performing hyperparameters with minimal
training. Given this goal, it makes sense to spend more time training high
performing models – why waste more time training time a model if it's done poorly in up until now?

One method to spend more time on high performing models is to initialize many
models, start training them, and then stop training low performing models
before training is finished. That's what Hyperband does. At the most basic
level, Hyperband is a principled early-stopping scheme for
[RandomizedSearchCV].

[RandomizedSearchCV]:https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html

Deciding when to stop the training of models depends on how strongly
the training data effects the score. There are two extremes:

1. when only the training data matter
    * i.e., when the hyperparameters don't influence the score at all
2. when only the hyperparameters matter
    * i.e., when the training data don't influence the score at all

Hyperband balances these two extremes by sweeping over how frequently
models are stopped. This sweep allows a mathematical proof that Hyperband
will find the best model possible with a minimal number of `partial_fit`
calls.[^qual]

[scipy19]:https://conference.scipy.org/proceedings/scipy2019/pdfs/scott_sievert.pdf
[^qual]:More accurately, Hyperband will find close to the best model possible with $N$ `partial_fit` calls in expected score with high probability, where "close" means "within log terms of the upper bound on score". For details, see corollary 1 of "[Better and faster hyperparameter optimization with Dask][hyperband-paper]".

That's the intuition for Hyperband, and a very informal description of the
paper's main result. But how well does it perform?

## Example

*Note: want to try `HyperbandSearchCV` out yourself? Dask has [an example use].
It can even be run in-browser!*

[an example use]:https://examples.dask.org/machine-learning/hyperparam-opt.html

I'll illustrate with a synthetic example. Let's build a dataset with 4 classes:

``` python
>>> from experiment import make_circles
>>> X, y = make_circles(n_classes=4, n_features=6, n_informative=2)
>>> scatter(X[:, :2], color=y)
```
<img src="/images/2019-hyperband/synthetic/dataset.png"
width="200px" />

*Note: this content is pulled from
[stsievert/dask-hyperband-comparison], or makes slight modifications.*

[stsievert/dask-hyperband-comparison]:https://github.com/stsievert/dask-hyperband-comparison

This is a pretty simple dataset. Let's build a fully connected neural net with
24 neurons to classify this dataset:

``` python
>>> from sklearn.neural_network import MLPClassifier
>>> model = MLPClassifier()
```

Building the neural net with PyTorch  is also possible,[^skorch] and what I used in development).

[^skorch]:Through the Scikit-learn API wrapper [skorch]

This neural net's behavior is dictated by a host of hyperparameters. There are
6 hyperparameters, and only one controls the model of the optimal architecture
(the number of neurons through `hidden_layer_sizes`). The rest control finding
the best model of that architecture. Details on the hyperparameters are in the
*[Appendix](#appendix)*.

``` python
>>> params = ...  # details in appendix
>>> params.keys()
dict_keys(['hidden_layer_sizes', 'alpha', 'batch_size', 'learning_rate'
           'learning_rate_init', 'power_t', 'momentum'])
>>> params["hidden_layer_sizes"]  # always 24 neurons
[(24, ), (12, 12), (6, 6, 6, 6), (4, 4, 4, 4, 4, 4), (12, 6, 3, 3)]
```

I choose these hyperparameters to have a complex search space that mimics the
searches performed for most neural networks. These searches typically involved
hyperparameters like "dropout", "learning rate", "momentum" and "weight
decay".[^user-facing]
End users don't care hyperparameters like these; they don't change the
model architecture, only finding the best model of a particular architecture.

[^user-facing]:There's less tuning for adaptive step size methods like [Adam] or [Adagrad]... and "[The Marginal Value of Adaptive Gradient Methods for Machine Learning][adamarginal]" shows that can underperform on test performance.

How can high performing hyperparameter values be found quickly?

[adamarginal]:https://arxiv.org/abs/1705.08292
[Adam]:https://arxiv.org/abs/1412.6980
[Adagrad]:http://jmlr.org/papers/v12/duchi11a.html

## Finding the best parameters

First, let's look at the parameters required for Dask-ML's implementation
of Hyperband (which is in the class `HyperbandSearchCV`).

### Hyperband parameters: rule-of-thumb
`HyperbandSearchCV` has two inputs:

1. `max_iter`, which determines how many times to call `partial_fit`
2. the chunk size of the Dask array, which determines how many data each
   `partial_fit` call receives.

These fall out pretty naturally once it's known how long to train the best
model and very approximately how many parameters to sample:

``` python
n_examples = 50 * len(X_train)  # 50 passes through dataset for best model
n_params = 299  # sample about 300 parameters

# inputs to hyperband
max_iter = n_params
chunk_size = n_examples // n_params
```

This rule-of-thumb requires are exactly the inputs the user cares about:

* `n_params`, a measure of how complex the search space is
* `n_examples`, how long to train the best model.

Notably, there's no tradeoff between `n_examples` and `n_params` like with
Scikit-learn's `RandomizedSearchCV` because `n_examples` is only for *some*
models, not for *all* models. There's more details on this
rule-of-thumb in the "Notes" section of the [`HyperbandSearchCV`
docs][hyperband-docstring].

[hyperband-docstring]:https://ml.dask.org/modules/generated/dask_ml.model_selection.HyperbandSearchCV.html#dask_ml.model_selection.HyperbandSearchCV

With these, a `HyperbandSearchCV` object can easily be created.

### Finding the best performing hyperparameters

This model selection algorithm Hyperband is implemented in the class
`HyperbandSearchCV`. Let's create an instance of that class:

``` python
>>> from dask_ml.model_selection import HyperbandSearchCV
>>>
>>> search = HyperbandSearchCV(
...     est, params, max_iter=max_iter, aggressiveness=4
... )
```

`aggressiveness` defaults to 3. `aggressiveness=4` is chosen because this is an
*initial* search; I know nothing about how this search space. Then, this search
should be more aggressive in culling off bad models.

Hyperband hides some details from the user (which enables the mathematical
guarantees), specifically the details on the amount of training and
the number of models created. These details are available in the `metadata`
attribute:

``` python
>>> search.metadata["n_models"]
378
>>> search.metadata["partial_fit_calls"]
5721
```

Now that we have some idea on how long the computation will take, let's ask it
to find the best set of hyperparameters:

``` python
>>> from dask_ml.model_selection import train_test_split
>>> X_train, y_train, X_test, y_test = train_test_split(X, y)
>>>
>>> X_train = X_train.rechunk(chunk_size)
>>> y_train = y_train.rechunk(chunk_size)
>>>
>>> search.fit(X_train, y_train)
```

The dashboard will be active during this time[^dashboard]:

[^dashboard]:But it probably won't be this fast: the video is sped up by a factor of 3.

<p>
<video width="600" autoplay loop controls class="center">
  <source src="/images/2019-hyperband/dashboard-compress.mp4" type="video/mp4" class="center">
  Your browser does not support the video tag.
</video>
</p>

How well do the hyperparameters found by this search perform?

``` python
>>> search.best_score_
0.9019221418447483
```

`HyperbandSearchCV` mirrors Scikit-Learn's API for [RandomizedSearchCV], so it
has access to all the expected attributes and methods:

``` python
>>> search.best_params_
{"batch_size": 64, "hidden_layer_sizes": [6, 6, 6, 6], ...}
>>> search.score(X_test, y_test)
0.8989070100111217
>>> search.best_model_
MLPClassifier(...)
```

Details on the attributes and methods are in the [HyperbandSearchCV
documentation][hyperband-docs].

[hyperband-docs]:https://ml.dask.org/modules/generated/dask_ml.model_selection.HyperbandSearchCV.html

## Performance

<!--
Plot 1: how well does it do?
Plot 2: how does this scale?
Plot 3: what opportunities does Dask enable?
-->

Let's run this on my personal laptop with 4 cores. I ran this 200 times, so
let's look at the distribution of final validation scores:

<img src="/images/2019-hyperband/synthetic/final-acc.svg"
 width="400px" class="center"/>

The "passive" comparison is really `RandomizedSearchCV` configured so it takes
an equal amount of work as `HyperbandSearchCV`. Let's see how this does over
time:

<img src="/images/2019-hyperband/synthetic/val-acc.svg"
 width="400px" class="center"/>

This graph shows the mean score over the 200 runs with the solid line, and the
shaded region represents the [interquartile range].

[interquartile range]:https://en.wikipedia.org/wiki/Interquartile_range

This graph shows that `HyperbandSearchCV` will find parameters 2–3 times
quicker than `RandomizedSearchCV`.  "Passes through the dataset" is a good
proxy for "time to solution" because there are only 4 workers. The dotted green
line indicates the data required to train 4 models to completion.

### Amenability to parallelism

These graphs are for serial environments, only 4 workers. How does
`HyperbandSearchCV` scale to more workers?

To do that, I ran a separate experiment, described more in the [corresponding
paper][scipy19]. The relevant difference is that a [PyTorch] neural network is used
through [skorch]. I ran the *same* experiment with a different number of Dask
workers.[^same] Here's how `HyperbandSearchCV` scales:

[skorch]:https://skorch.readthedocs.io/en/stable/
[PyTorch]:https://pytorch.org/

<img src="/images/2019-hyperband/image-denoising/scaling-patience.svg" width="400px" class="center" />

Training one model to completion requires 243 seconds (which is marked by the
white line). This is a comparison with `patience`, which stops training models
if their scores aren't increasing enough. Functionally, this is very useful
because the user might specify `n_examples` to be too large.

It looks like the speedups start to saturate somewhere
between 16 and 24 workers, at least for this example.
Of course, `patience` doesn't work as well for a large number of
workers.[^scale-worker]

[^scale-worker]:There's no time benefit to stopping jobs early if there are infinite workers; there's never a queue of jobs waiting to be run
[^same]:Everything is the same between different runs: the hyperparameters sampled, the model's internal random state, the data passed for fitting. Only the number of workers varies.


### Dask opportunities

Having a more workers influences the time required to reach a particular
validation score in different way. Hyperband is an advanced hyperparameter
optimization framework and Dask is an advanced task scheduler. What
opportunities does that combination create?

The most obvious opportunity involves job prioritization. Hyperband fits many
models in parallel (more than `n_params` models). Dask might not have that
number of workers available.

Of course, Dask can prioritize jobs, so it can prioritize which models get fit
soonest. Why not assign the model's most recent score to the priority? There's
some more info in Dask's documentation in [Prioritizing Work][dask-prior].

How does this prioritization scheme influence the score? Let's run another
experiment and only vary the prioritization scheme:

<img src="/images/2019-hyperband/synthetic/priority.svg"
     width="400px" class="center" />

This graph shows the "high scores" prioritization scheme above with the "fifo"
scheme, Dask's default. These two lines are the same in every way except for
the prioritization scheme. This run is one of the 200 runs mentioned in
*[Performance](#performance)*.

This graph is certainly helped by the fact that is run in a serial environment.
Job priority does not matter if every job can be run right away (there's
nothing to assign priority too!).

[dask-prior]:https://distributed.dask.org/en/latest/priority.html

*Note: core concepts in this section are illustrated by some code and images from a
notebook available at [stsievert/dask-hyperband-comparison].*

## Future work

One improvement is one making `HyperbandSearchCV` perform better for initial
searches. Some basic internals of Hyperband can be tweaked, which has
started in [dask/dask-ml #532].

[dask/dask-ml #532]:https://github.com/dask/dask-ml/pull/532

The biggest improvement I see is treating *dataset size* as the scarce resource
that needs to be preserved instead of *training time*. This would allow
Hyperband to work with any model, instead of only models that implement
`partial_fit`.

Serialization is an important part of the distributed Hyperband implementation
in `HyperbandSearchCV`. Scikit-learn and PyTorch can easily handle this because
they natively support the Pickle protocol[^pickle-post], but
Keras/Tensorflow/MXNet present challenges. The use of `HyperbandSearchCV` could
be increased by resolving this issue.

[^pickle-post]:"[Pickle isn't slow, it's a protocol][matt-pickle]" by Matthew Rocklin
[matt-pickle]:http://matthewrocklin.com/blog/work/2018/07/23/protocols-pickle

## Appendix

I choose to tune 7 hyperparameters, which are

* `hidden_layer_sizes`, which controls the activation function used at each
  neuron
* `alpha`, which controls the amount of regularization

More hyperparamaeters control finding the best neural network:

* `batch_size`, which controls the number of examples the `optimizer` uses to
  approximate the gradient
* `learning_rate`, `learning_rate_init`, `power_t`, which control some basic
  hyperparameters for the SGD optimizer I'll be using
* `momentum`, a more advanced hyperparameter for SGD with Nesterov's momentum.

