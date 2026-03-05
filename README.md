# Dask Working Notes

A collection of working notes about [Dask](https://dask.org)

## Build Locally

This blog uses [Hugo](https://gohugo.io/). You will need Hugo (extended edition) installed to build locally.

Install Hugo following the [official instructions](https://gohugo.io/installation/), then run:

```
hugo server
```

The site will be available at `http://localhost:1313/` and will auto-reload on changes. Built pages are written to `public/`.

## Add a new page

Content lives in `content/posts/` as individual markdown files. These markdown files
have a few expectations on them.

1.  They should be named according to the date of publication like the
    following:

    ```
    YYYY-MM-DD-brief-title-url.md
    ```

    like

    ```
    2018-12-31-dask-in-the-new-year.md
    ```

2.  They should have the following front-matter

    ```
    ---
    title: Your Title
    date: YYYY-MM-DD
    author: Your Name
    tagline: an optional tagline
    tag: [A, list, of tags]
    ---
    ```

    You can copy-paste this from any existing post

3.  You can also optionally add the following element to the front-matter to
    avoid placing this article in the table of contents and on RSS feeds.

    ```
    draft: true
    ```

4.  Images should go in the `static/images/` directory and be referred to as
    `/images/my-image.svg` with normal HTML or markdown syntax like the
    following:

    ```html
    <img src="/images/my-image.svg" />
    ```

## Formatting

This project uses [prettier](https://prettier.io/) and [markdownlint](https://github.com/DavidAnson/markdownlint) to auto-format and lint files.

You can use [pre-commit](https://pre-commit.com/) to run this automatically:

```console
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Publish on Github Pages

The blog is built and deployed via GitHub Actions. Push to the `gh-pages` branch and the site will be built and deployed automatically.

The blog is also rebuilt nightly via a GitHub Actions cron job. This allows post authors to set the post date in the future for publishing later. Hugo will only build posts dated in the past. This should make scheduling a little easier.
