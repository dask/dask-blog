---
layout: page
title: Dask Blog
---

{% include JB/setup %}

<div class="blog-header">
  <h1>Dask Blog</h1>
  <p class="blog-tagline">Working notes about scaling Python</p>
</div>

<div class="blog-meta-links">
  <a href="https://github.com/dask/dask-blog/blob/gh-pages/README.md" target="_blank">Contribute a Blog</a>
  <a href="{{ BASE_PATH }}/atom.xml">Atom Feed</a>
</div>

<ul class="posts-list">
  {% for post in site.posts %}
    {% if post.draft != true %}
    <li>
      <a href="{{ BASE_PATH }}{{ post.url }}" class="post-item-title">{{ post.title }}</a>
      <span class="post-item-date">{{ post.date | date: "%B %d, %Y" }}</span>
    </li>
    {% endif %}
  {% endfor %}
</ul>
