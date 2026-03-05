---
blogpost: true
date: Feb 13, 2023
title: Managing dask workloads with Flyte
author: Bernhard Stadlbauer
tags: Python, dask, Flyte, Kubernetes
---

It is now possible to manage `dask` workloads using [Flyte](https://flyte.org/) 🎉!

The major advantages are:

- Each [Flyte `task`](https://docs.flyte.org/projects/flytekit/en/latest/generated/flytekit.task.html) spins up its own ephemeral `dask` cluster using a Docker image tailored to the task, ensuring consistency in the Python environment across the client, scheduler, and workers.
- Flyte will use the existing [Kubernetes](https://kubernetes.io/) infrastructure to spin up `dask` clusters.
- Spot/Preemtible instances are natively supported.
- The whole `dask` task can be cached.
- Enabling `dask` support in an already running Flyte setup can be done in just a few minutes.

This is what a Flyte `task` backed by a `dask` cluster with four workers looks like:

```python
from typing import List

from distributed import Client
from flytekit import task, Resources
from flytekitplugins.dask import Dask, WorkerGroup, Scheduler


def inc(x):
    return x + 1


@task(
    task_config=Dask(
        scheduler=Scheduler(
            requests=Resources(cpu="2")
        ),
        workers=WorkerGroup(
            number_of_workers=4,
            limits=Resources(cpu="8", mem="32Gi")
        )
    )
)
def increment_numbers(list_length: int) -> List[int]:
    client = Client()
    futures = client.map(inc, range(list_length))
    return client.gather(futures)
```

This task can run locally using a standard `distributed.Client()` and can scale to arbitrary cluster sizes once [registered with Flyte](https://docs.flyte.org/projects/cookbook/en/latest/getting_started/package_register.html).

## What is Flyte?

[Flyte](https://flyte.org/) is a Kubernetes native workflow orchestration engine. Originally developed at [Lyft](https://www.lyft.com/), it is now an open-source ([Github](https://github.com/flyteorg/flyte)) and a graduate project under the Linux Foundation. It stands out among similar tools such as [Airflow](https://airflow.apache.org/) or [Argo](https://argoproj.github.io/) due to its key features, which include:

- Caching/Memoization of previously executed tasks for improved performance
- Kubernetes native
- Workflow definitions in Python, not e.g.,`YAML`
- Strong typing between tasks and workflows using `Protobuf`
- Dynamic generation of workflow DAGs at runtime
- Ability to run workflows locally

A simple workflow would look something like the following:

```python
from typing import List

import pandas as pd

from flytekit import task, workflow, Resources
from flytekitplugins.dask import Dask, WorkerGroup, Scheduler


@task(
    task_config=Dask(
        scheduler=Scheduler(
            requests=Resources(cpu="2")
        ),
        workers=WorkerGroup(
            number_of_workers=4,
            limits=Resources(cpu="8", mem="32Gi")
        )
    )
)
def expensive_data_preparation(input_files: List[str]) -> pd.DataFrame:
    # Expensive, highly parallel `dask` code
    ...
    return pd.DataFrame(...)  # Some large DataFrame, Flyte will handle serialization


@task
def train(input_data: pd.DataFrame) -> str:
    # Model training, can also use GPU, etc.
    ...
    return "s3://path-to-model"


@workflow
def train_model(input_files: List[str]) -> str:
    prepared_data = expensive_data_preparation(input_files=input_files)
    return train(input_data=prepared_data)
```

In the above, both `expensive_data_preparation()` as well as `train()` would be run in their own Pod(s) in Kubernetes, while the `train_model()` workflow is a DSL which creates a Directed Acyclic Graph (DAG) of the workflow. It will determine the order of tasks based on their inputs and outputs. Input and output types (based on the type hints) will be validated at registration time to avoid surprises at runtime.

After registration with Flyte, the workflow can be started from the UI:

<img src="/images/dask-flyte-workflow.png" alt="Dask workflow in the Flyte UI" style="max-width: 100%;" width="100%" />

## Why use the `dask` plugin for Flyte?

At first glance, Flyte and `dask` look similar in what they are trying to achieve, both capable of creating a DAG from user functions, managing inputs and outputs, etc. However, the major conceptual difference lies in their approach. While `dask` has long-lived workers to run tasks, a Flyte task is a designated Kubernetes Pod that creates a significant overhead in task-runtime.

While `dask` tasks incur an overhead of around one millisecond (refer to the [docs](https://distributed.dask.org/en/stable/efficiency.html#use-larger-tasks)), spinning up a new Kubernetes pod takes several seconds. The long-lived nature of the `dask` workers allows for optimization of the DAG, running tasks that operate on the same data on the same node, reducing the need for inter-worker data serialization (known as shuffling). With Flyte tasks being ephemeral, this optimization is not possible, and task outputs are serialized to a blob storage instead.

Given the limitations discussed above, why use Flyte? Flyte is not intended to replace tools such as dask or Apache Spark, but rather provides an orchestration layer on top. While workloads can be run directly in Flyte, such as training a single GPU model, Flyte offers [numerous integrations](https://flyte.org/integrations) with other popular data processing tools.

With Flyte managing the `dask` cluster lifecycle, each `dask` Flyte task will run on its own dedicated `dask` cluster made up of Kubernetes pods. When the Flyte task is triggered from the UI, Flyte will spin up a dask cluster tailored to the task, which will then be used to execute the user code. This enables the use of different Docker images with varying dependencies for different tasks, whilst always ensuring that the dependencies of the client, scheduler, and workers are consistent.

## What prerequisites are required to run `dask` tasks in Flyte?

- The Kubernetes cluster needs to have the [dask operator](https://kubernetes.dask.org/en/latest/operator.html) installed.
- Flyte version `1.3.0` or higher is required.
- The `dask` plugin needs to be enabled in the Flyte propeller config. (refer to the [docs](https://docs.flyte.org/en/latest/deployment/plugins/k8s/index.html#specify-plugin-configuration))
- The Docker image associated with the task must have the `flytekitplugins-dask` package installed in its Python environment.

## How do things work under the hood?

_Note: The following is for reference only and is not necessary for users who only use the plugin. However, it could be useful for easier debugging._

On a high-level overview, the following steps occur when a `dask` task is initiated in Flyte:

1. A `FlyteWorkflow` [Custom Resource (CR)](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) is created in Kubernetes.
2. Flyte Propeller, a [Kubernetes Operator](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)), detects the creation of the workflow.
3. The operator inspects the task's spec and identifies it as a `dask` task. It verifies if it has the required plugin associated with it and locates the `dask` plugin.
4. The `dask` plugin within Flyte Propeller picks up the task defintion and creates a [`DaskJob` Custom Resource](https://kubernetes.dask.org/en/latest/operator_resources.html#daskjob) using the [dask-k8s-operator-go-client](https://github.com/bstadlbauer/dask-k8s-operator-go-client/).
5. The [dask operator](https://kubernetes.dask.org/en/latest/operator.html) picks up the `DaskJob` resource and runs the job accordingly. It spins up a pod to run the client/job-runner, one for the scheduler, and additional worker pods as designated in the Flyte task decorator.
6. While the `dask` task is running, Flyte Propeller continuously monitors the `DaskJob` resource, waiting on it to report success or failure. Once the job has finished or the Flyte task has been terminated, all `dask` related resources will be cleaned up.

## Useful links

- [Flyte documentation](https://docs.flyte.org/en/latest/)
- [Flyte community](https://flyte.org/community)
- [flytekitplugins-dask user documentation](https://docs.flyte.org/projects/cookbook/en/latest/auto/integrations/kubernetes/k8s_dask/index.html)
- [flytekitplugins-dask deployment documentation](https://docs.flyte.org/en/latest/deployment/plugins/k8s/index.html)
- [dask-kubernetes documentation](https://kubernetes.dask.org/en/latest/)
- [Blog post on the dask kubernetes operator](http://blog.dask.org/2022/11/09/dask-kubernetes-operator)

In case there are any questions or concerns, don't hesitate to reach out. You can contact Bernhard Stadlbauer via the [Flyte Slack](https://slack.flyte.org/) or via [GitHub](https://github.com/bstadlbauer).

I would like to give shoutouts to [Jacob Tomlinson](https://jacobtomlinson.dev/) (Dask) and [Dan Rammer](https://github.com/hamersaw) (Flyte) for all of the help I've received. This would not have been possible without your support!
