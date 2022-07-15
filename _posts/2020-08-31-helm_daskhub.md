---
layout: post
title: Announcing the DaskHub Helm Chart
tagline: DaskHub
tags: [Helm, Dask Gateway, Deployment]
theme: twitter
author: Tom Augspurger
---

Today we're announcing the release of the
[`daskhub`](https://github.com/dask/helm-chart/blob/master/daskhub/README.md)
helm chart. This is a [Helm](https://helm.sh/) chart to easily install
[JupyterHub](https://jupyter.org/hub) and Dask for multiple users on a
Kubernetes Cluster. If you're managing deployment for many people that needs
interactive, scalable computing (say for a class of students, a data science
team, or a research lab) then `dask/daskhub` might be right for you.

You can install `dask/daskhub` on a Kubernetes cluster today with

```console
helm repo add dask https://helm.dask.org/
helm repo update
helm upgrade --install dhub dask/daskhub
```

## History

The `dask/daskhub` helm chart is an evolution of the [Pangeo](http://pangeo.io/)
helm chart, which came out of that community's attempts to do big data
geoscience on the cloud. We're very grateful to have years of experience using
Dask and JupyterHub together. Pangeo was always aware that there wasn't anything
geoscience-specific to their Helm chart and so were eager to contribute it to
Dask to share the maintenance burden. In the process of moving it over to Dask's
chart repository we took the opportunity to clean up a few rough edges.

It's interesting to read the [original
announcement](https://blog.dask.org/2018/01/22/pangeo-2) of Pangeo's JupyterHub
deployment. A lot has improved, and we hope that this helm chart assists more
groups in deploying JupyterHubs capable of scalable computations with Dask.

## Details

Internally, the DaskHub helm chart is relatively simple combination of the
[JupyterHub](https://github.com/jupyterhub/zero-to-jupyterhub-k8s) and [Dask
Gateway](https://github.com/dask/dask-gateway/) helm charts. The only additional
magic is some configuration to

1. Register Dask Gateway as a [JupyterHub
   service](https://jupyterhub.readthedocs.io/en/stable/reference/services.html).
2. Set environment variables to make using Dask Gateway easy for your users.

With the default configuration, your users will be able to create and connect to
Dask Clusters, including their dashboards, with a simple

```python
>>> from dask_gateway import GatewayCluster
>>> cluster = GatewayCluster()
>>> client = cluster.get_client()
```

Check out the
[documentation](https://docs.dask.org/en/latest/setup/kubernetes-helm.html) for
details and let us know if you run into any difficulties.
