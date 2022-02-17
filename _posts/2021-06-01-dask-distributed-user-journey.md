---
layout: post
title: The evolution of a Dask Distributed user
tagline: The critical path to scaling from one machine to thousands
author: Jacob Tomlinson (NVIDIA)
tags: [Distributed, Tools, Organisations]
theme: twitter
---

{% include JB/setup %}

This week was the 2021 Dask Summit and [one of the workshops](https://summit.dask.org/schedule/presentation/20/deploying-dask/) that we ran covered many deployment options for Dask Distributed.

We covered local deployments, SSH, Hadoop, Kubernetes, the Cloud and managed services, but one question that came up a few times was "where do I start?".

I wanted to share the journey that I've seen many Dask users take in the hopes that you may recognize yourself as being somewhere along this path and it may inform you where to look next.

## In the beginning

As a user who is new to Dask you're likely working your way through [the documentation](https://docs.dask.org/en/latest/index.html) or perhaps [a tutorial](https://github.com/dask/dask-tutorial).

We often introduce the concept of the distributed scheduler early on, but you don't need it to get initial benefits from Dask. Switching from Pandas to Dask for larger than memory datasets is a common entry point and performs perfectly well using the default threaded scheduler.

```python
# Switching from this
import pandas as pd
df = pd.read_csv('/data/.../2018-*-*.csv')
df.groupby(df.account_id).balance.sum()

# To this
import dask.dataframe as dd
df = dd.read_csv('/data/.../2018-*-*.csv')
df.groupby(df.account_id).balance.sum().compute()
```

But by the time you're a few pages into the documentation you're already being encouraged to create `Client()` and `LocalCluster()` objects.

_**Note**: When you create a `Client()` with no arguments/config set Dask will launch a `LocalCluster()` object for you under the hood. So often `Client()` is equivalent to `Client(LocalCluster())`._

This is a common area for users to stick around in, launch a local distributed scheduler and do your work maximising the resources on your local machine.

```python
from dask.distributed import Client
import dask.dataframe as dd

client = Client()

df = dd.read_csv('/data/.../2018-*-*.csv')
df.groupby(df.account_id).balance.sum().compute()
```

## Breaking free from your machine

Once you get used to task graphs and work scheduling you may begin thinking about how you can expand your computation beyond your local machine.

Our code doesn't really need to change much, we are already connecting a client and doing Dask work, all we need are more networked machines with the same user environments, data, etc.

Personally I used to work in an organisation where every researcher was given a Linux desktop under their desk. These machines were on a LAN and had Active Directory and user home directories stored on a storage server. This meant you could sit down at any desk and log in and have a consistent experience. This also meant you could SSH to another machine on the network and your home directory would be there with all your files including your data and conda environments.

This is a common setup in many organisations and it can be tempting to SSH onto the machines of folks who may not be fully utilising their machine and run your work there. And I'm sure you ask first right!

Organisations may also have servers in racks designated for computational use and the setup will be similar. You can SSH onto them and home directories and data are available via network storage.

With Dask Distributed you can start to expand your workload onto these machines using `SSHCluster`. All you need is your SSH keys set up so you can log into those machines without a password.

```python
from dask.distributed import Client, SSHCluster
import dask.dataframe as dd

cluster = SSHCluster(
    [
        "localhost",
        "alices-desktop.lan",
        "bobs-desktop.lan",
        "team-server.lan",
    ]
)
client = Client(cluster)

df = dd.read_csv("/data/.../2018-*-*.csv")
df.groupby(df.account_id).balance.sum().compute()
```

Now the same workload can run on all of the CPUs in our little ad-hoc cluster, using all the memory and pulling data from the same shared storage.

## Moving to a compute platform

Using (and abusing) hardware like desktops and shared servers will get you reasonably far, but probably to the dismay of your IT team.

Organisations who have many users trying to perform large compute workloads will probably be thinking about or already have some kind of platform that is designated for running this work.

The platforms your organisation has will be the result of many somewhat arbitrary technology choices. What programming languages does your company use? What deals did vendors offer at the time of procurement? What skills do the current IT staff have? What did your CTO have for breakfast the day they chose a vendor?

I'm not saying these decisions are made thoughtlessly, but the criteria that are considered are often orthogonal to how the resource will ultimately be used by you. At Dask we support whatever platform decisions your organisations make. We try to build deployment tools for as many popular platforms as we can including:

- Hadoop via [dask-yarn](https://github.com/dask/dask-yarn)
- Kubernetes via [dask-kubernetes](https://github.com/dask/dask-kubernetes) and the [helm chart](https://github.com/dask/helm-chart)
- HPC (with schedulers like SLURM, PBS and SGE) via [dask-jobqueue](https://github.com/dask/dask-jobqueue)
- Cloud platforms (including AWS, Azure and GCP) with [dask-cloudprovider](https://github.com/dask/dask-cloudprovider)

As a user within an organisations you may have been onboarded to one of these platforms. You've probably been given some credentials and a little training on how to launch jobs on it.

The `dask-foo` tools listed above are designed to sit on top of those platforms and submit jobs on your behalf as if they were individual compute jobs. But instead of submitting a Python script to the platform we submit Dask schedulers and workers and then connect to them to leverage the provisioned resource. Clusters on top of clusters.

With this approach your IT team has full control over the compute resource. They can ensure folks get their fair share with quotas and queues. But you as a user gets the same Dask experience you are used to on your local machine.

Your data may be in a slightly different place on these platforms though. Perhaps you are on the cloud and your data is in object storage for example. Thankfully we have tools built on [fsspec](https://filesystem-spec.readthedocs.io/en/latest/) like [s3fs](https://github.com/dask/s3fs) or [adlfs](https://pypi.org/project/adlfs/) we can read this data in pretty much the same way. So still not much change to your workflow.

```python
from dask.distributed import Client
from dask_cloudprovider.azure import AzureVMCluster
import dask.dataframe as dd

cluster = AzureVMCluster(resource_group="<resource group>",
                         vnet="<vnet>",
                         security_group="<security group>",
                         n_workers=10)
client = Client(cluster)

df = dd.read_csv("adl://.../2018-*-*.csv")
df.groupby(df.account_id).balance.sum().compute()
```

## Centralizing your Dask resources

When your organisation gets enough folks adopting and using Dask it may be time for your IT team to step in and provide you with a managed service. Having many users submitting many ad-hoc clusters in a myriad of ways is likely to be less efficient than a centrally managed and more importantly ordained service from IT.

The motivation to move to a managed service is often driven at the organisational level rather than by individuals. Once you've reached this stage of Dask usage you're probably quite comfortable with your workflows and it may be inconvenient to change them. However the level of Dask deployment knowledge you've acquired to reach this stage is probably quite large, and as Dask usage at your organization grows it's not practical to expect everyone to reach the same level of competency.

At the end of the day being an expert in deploying distributed systems is probably not listed in your job description and you probably have something more important to be getting on with like data science, finance, physics, biology or whatever it is Dask is helping you do.

You may also be feeling some pressure from IT. You are running clusters on top of clusters and to them your Dask cluster is a black box and this can make them comfortable as they are the ones responsible for this hardware. It is common to feel constrained by your IT team, I know because I've been a sysadmin and used to constrain folks. But the motivations of your IT team are good ones, they are trying to save the organisation money, make best use of limited resources and ultimately get the IT out of your way so that you can get on with your job. So lean into this, engage with them, share your Dask knowledge and offer to become a pilot user for whatever solution they end up building.

One approach you could recommend they take is to deploy [Dask Gateway](https://gateway.dask.org/). This can be deployed by an administrator and provides a central hub which launches Dask clusters on behalf of users. It supports many types of authentication so it can hook into whatever your organisation uses and supports many of the same backend compute platforms that the standalone tools do, including Kubernetes, Hadoop and HPC.

This will allow them to ensure security settings are correct and consistent across clusters. If you are using containers they probably want you to use some official images which are regularly updated and vulnerability scanned. It may also give them more insight into what types of workloads folks are running and plan future systems more accurately. By using Dask Gateway this puts the control and responsibility of these things onto their side of the fence.

Users will need to authenticate with the gateway, but then can launch Dask clusters in a platform agnostic way.

```python
from dask.distributed import Client
from dask_gateway import Gateway
import dask.dataframe as dd

gateway = Gateway(
    address="http://daskgateway.myorg.com",
    auth="kerberos"
)
cluster = gateway.new_cluster()
client = Client(cluster)

df = dd.read_csv("/data/.../2018-*-*.csv")
df.groupby(df.account_id).balance.sum().compute()
```

Again reading your data requires some knowledge on how it is stored on the underlying compute platform you the gateway is using, but the changes required are minimal.

## Managed services

If your organisation is too small to have an IT team to manage this for you, or you just have a preference for managed services, there are startups popping up to provide this to you as a service including [Coiled](https://coiled.io/) and [Saturn Cloud](https://www.saturncloud.io/s/home/).

## Future platforms

Today the large cloud vendors have managed data science platforms including [AWS Sagemaker](https://aws.amazon.com/sagemaker/), [Azure Machine Learning](https://azure.microsoft.com/en-gb/services/machine-learning/) and [Google Cloud AI Platform](https://cloud.google.com/vertex-ai). But these do not include Dask as a service.

These cloud services are focussed on batch processing and machine learning today, but these clouds also have managed services for Spark and other compute cluster offerings. With Dask's increasing popularity it wouldn't surprise me if managed Dask services are released by these cloud vendors in the years to follow.

## Summary

One of the most powerful features of Dask is that your code can stay pretty much the same regardless of how big or complex the distributed compute cluster is. It scales from a single machine to thousands of servers with ease.

But scaling up requires both user and organisational growth and folks already seem to be treading a common path on that journey.

Hopefully this post will give you an idea of where you are on that path and where to jump to next. Whether you're new to the community and discovering the power of multi-core computing or an old hand who is trying to wrangle hundreds of users who all love Dask, good luck!
