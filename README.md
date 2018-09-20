Dask Working Notes
==================

A collection of working notes about [Dask](https://dask.org)


Build Locally
-------------

This blog uses Jekyll, which is built on Ruby.  You will need Ruby to build
locally.

Do this once on your machine (assuming you have `ruby` and `gem`, Ruby's
package manager)

```
gen install bundler
bundle install
```

Then do this whenever you want to build-and-host your docs

```
bundle exec jekyll serve
```

That should also watch for changes and rebuild automatically.  Built pages live
in `_site`.



Add a new page
--------------

Content lives in `_posts` as individual markdown files.  These markdown files
have a few expectations on them.

1.  They should be named according to the date of publication
2.  They should have the following front-matter

    ```
    layout: post
    title: Your Title
    tagline: an optional tagline
    tags: [A, list, of tags]
    theme: twitter
    ---

    {% include JB/setup %}
    ```

    You can copy-paste this from any existing post
3.  You can also optionally add the following element to the front-matter to
    avoid placing this article in the table of contents and on RSS feeds.

    ```
    draft: true
    ```


Publish on Github Pages
-----------------------

Github runs Jekyll by default.  No additional work is needed for deployment,
just push to the `gh-pages` branch and things should be up in a few minutes.
