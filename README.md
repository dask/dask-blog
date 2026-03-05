# Dask Working Notes

A collection of working notes about [Dask](https://dask.org)

## Build Locally

This blog uses [Sphinx](https://www.sphinx-doc.org/) with
[ABlog](https://ablog.readthedocs.io/) and requires Python 3.10+.

Start the development server with auto-reload:

```console
uv run sphinx-autobuild -b dirhtml . _build/dirhtml
```

This opens the site at <http://localhost:8000> and watches for changes.

To build a static copy:

```console
uv run sphinx-build -b dirhtml . _build/dirhtml
```

Built pages live in `_build/dirhtml/`.

## Add a new post

Posts live in year-based directories as individual Markdown files:

```
YYYY/MM/DD/brief-title-url.md
```

For example:

```
2024/05/30/dask-is-fast.md
```

Each post needs the following front matter:

```yaml
---
blogpost: true
date: May 30, 2024
title: Your Title
author: Your Name
tags: dask, topic1, topic2
---
```

Images should go in the `images/` directory and be referenced as
`/images/my-image.svg`.

## Formatting

This project uses [prettier](https://prettier.io/) and
[markdownlint](https://github.com/DavidAnson/markdownlint) to auto-format and
lint files.

You can use [pre-commit](https://pre-commit.com/) to run this automatically:

```console
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Deployment

The site is deployed to GitHub Pages via GitHub Actions. Push to the `gh-pages`
branch and deployment happens automatically. A nightly cron job rebuilds the
site, so posts with future dates will appear when their date arrives.
