# Jekyll to Sphinx+ABlog Migration Plan — Dask Blog

## Context

The Dask blog (`blog.dask.org`) is a 158-post Jekyll blog using Jekyll-Bootstrap with a Bootstrap 3 "twitter" theme. It's deployed via GitHub Pages from the `gh-pages` branch. The goal is to migrate to **Sphinx + ABlog** with the **pydata-sphinx-theme** — the same theme family used by dask.org, pandas, numpy, and the broader PyData ecosystem. This keeps the blog aligned with the Dask documentation toolchain (all Python, all Sphinx) and provides built-in **light/dark theme** support with no custom theme code. MyST-Parser enables keeping all existing Markdown posts with minimal changes. Playwright is used during development to verify all content renders correctly (not a permanent CI fixture).

### Why Sphinx+ABlog over Hugo

- **Ecosystem alignment**: dask.org already uses Sphinx + pydata-sphinx-theme; the blog shares the same toolchain
- **All Python**: no Go dependency — everything is `pip install`-able
- **pydata-sphinx-theme has native ABlog support**: styled sidebar widgets, post cards, archive pages
- **Built-in light/dark toggle**: no custom JS needed — pydata-sphinx-theme handles it
- **MyST-Parser**: keeps existing Markdown posts with minimal front matter changes
- **Dollar math**: `myst_enable_extensions = ["dollarmath"]` handles existing `$...$` / `$$...$$` syntax natively

## Current State (Key Facts)

- **158 posts** in `_posts/` (2014–2024), **237+ images** in `images/`
- 150 posts contain `{% include JB/setup %}` (must be stripped)
- 8 draft posts (`draft: true`), 7 posts with `canonical_url`
- 2 posts use `layout: widepost`, 1 post uses `{% gist %}`
- 12 posts use MathJax (`$...$` / `$$...$$`), 26 posts contain `<iframe>`s, 50+ posts have inline HTML
- Permalink pattern: `/:year/:month/:day/:title` (no categories used)
- Disqus comments (short_name: `dask-blog`), GTM analytics (`GTM-P4GQM59`)
- Tag pages at `/tag/<name>/`, feeds at `atom.xml`, `feed.python.xml`, `feed.scipy.xml`, `feed.sympy.xml`

---

## Phase 1: Sphinx Project Setup

### 1.1 Branch strategy

- Continue on `sphinx-migration` branch (already created from `gh-pages`)
- `gh-pages` continues serving the live Jekyll site until cutover

### 1.2 Python dependencies (`requirements.txt`)

```
sphinx>=8.0
ablog>=0.11
pydata-sphinx-theme>=0.16
myst-parser>=4.0
```

### 1.3 Create `conf.py`

```python
# -- Project information
project = "Dask Blog"
author = "Dask Contributors"
copyright = "2014-2026, Dask Contributors"

# -- General configuration
extensions = [
    "ablog",
    "myst_parser",
    "sphinx.ext.mathjax",
    "sphinx.ext.githubpages",    # creates .nojekyll in output
]

# Source file handling
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

exclude_patterns = [
    "_build", "_website", ".doctrees",
    "node_modules", "public", ".github",
    "README.md", "CONTRIBUTING.md", "plans",
    "Gemfile", "Rakefile", "changelog.md",
    "drafts",
    # Legacy Jekyll files (until Phase 5 cleanup)
    "_posts", "_includes", "_layouts", "_plugins",
    "assets", "css", "scripts",
    "atom.xml", "feed.*.xml", "sitemap.txt",
    "tags.html", "404.html", "documentation.html",
]

# -- MyST-Parser configuration
myst_enable_extensions = [
    "dollarmath",       # $...$ and $$...$$ math (12 posts use this)
    "colon_fence",      # ::: directive syntax alternative
]
myst_update_mathjax = False   # Don't let MyST override MathJax config

# -- ABlog configuration
blog_baseurl = "https://blog.dask.org"
blog_title = "Dask Working Notes"
blog_path = "blog"                       # Archive pages at /blog/
blog_post_pattern = "posts/*/*/*/*"      # Match posts/YYYY/MM/DD/slug.md
post_date_format = "%b %d, %Y"          # e.g. "Jan 15, 2024"
post_date_format_short = "%b %d, %Y"
post_auto_excerpt = 1
post_show_prev_next = True
blog_feed_fulltext = True
blog_feed_archives = True                # Per-tag feeds
blog_feed_length = None                  # All posts in main feed
disqus_shortname = "dask-blog"

# ABlog builder
ablog_builder = "dirhtml"                # /post/ not /post.html
ablog_website = "_website"

# -- HTML output
html_theme = "pydata_sphinx_theme"
html_title = "Dask Working Notes"
html_favicon = "_static/favicon.ico"
html_static_path = ["_static"]
html_extra_path = [
    "images",           # Preserves /images/... URLs used in posts
    "storage",          # Preserves /storage/... URLs
    "CNAME",
    "extras",           # Redirect pages (atom.xml, feed.*.xml, etc.)
]
html_css_files = ["css/custom.css"]

html_theme_options = {
    "logo": {
        "image_light": "_static/dask-logo.svg",
        "image_dark": "_static/dask-logo-white.svg",
        "text": "Dask Blog",
    },
    "github_url": "https://github.com/dask/dask-blog",
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "external_links": [
        {"name": "dask.org", "url": "https://dask.org"},
        {"name": "Docs", "url": "https://docs.dask.org"},
    ],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/dask/dask-blog",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
    ],
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
    "footer_start": ["copyright"],
    "footer_end": ["last-updated"],
    "secondary_sidebar_items": [],       # No right sidebar on posts
}

html_sidebars = {
    "index": [],                                             # No sidebar on homepage
    "posts/*/*/*/*": ["ablog/postcard.html"],                # Post metadata sidebar
    "blog": ["ablog/tagcloud.html", "ablog/archives.html"], # Blog archive sidebar
    "blog/**": ["ablog/tagcloud.html", "ablog/archives.html"],
}

# -- MathJax
mathjax3_config = {
    "tex": {
        "inlineMath": [["$", "$"], ["\\(", "\\)"]],
        "displayMath": [["$$", "$$"], ["\\[", "\\]"]],
    },
}

# -- Analytics (injected via custom template override)
html_context = {
    "gtm_id": "GTM-P4GQM59",
}
```

### 1.4 Target directory structure

```
dask-blog/
  conf.py
  requirements.txt
  index.md                   # Homepage with postlist directive
  CNAME
  images/                    # Existing images (→ output root via html_extra_path)
  storage/                   # Existing storage files (→ output root)
  posts/                     # Blog posts organized by date
    2014/
      12/
        27/
          dask-part-1.md
    2015/
      ...
    ...
    2024/
      ...
  drafts/                    # Draft posts (excluded from build)
  extras/                    # Redirect HTML files for legacy URLs
    atom.xml                 # Redirect → /blog/atom.xml
    tag/                     # Redirect tag pages → /blog/tag/
    feed.python.xml          # Redirect → /blog/tag/Python/atom.xml
    feed.scipy.xml           # Redirect → /blog/tag/scipy/atom.xml
    feed.sympy.xml           # Redirect → /blog/tag/SymPy/atom.xml
    documentation.html       # Redirect → https://dask.org
  _static/
    css/
      custom.css             # Dask-branded CSS overrides
    dask-logo.svg
    dask-logo-white.svg
    favicon.ico
  _templates/
    analytics.html           # GTM script override
  playwright/                # Development testing (temporary)
  package.json
  .github/workflows/
```

---

## Phase 2: Theme & Styling

### 2.1 Design direction

Use **pydata-sphinx-theme** — the same theme family used by dask.org, pandas, numpy, xarray, and the broader PyData ecosystem. This provides out of the box:

- Built-in light/dark theme toggle (no custom JS needed)
- Responsive layout with Bootstrap 5
- ABlog-aware sidebar templates (post cards, tag clouds, archives)
- CSS custom properties for easy brand customization
- FontAwesome 6 support
- Pygments syntax highlighting with separate light/dark styles

### 2.2 Custom CSS (`_static/css/custom.css`)

Override pydata-sphinx-theme CSS variables to match dask.org branding:

```css
/* Dask brand colors */
html[data-theme="light"] {
  --pst-color-primary: #ffc11e; /* Dask gold */
  --pst-color-primary-text: #080815;
  --pst-color-link: #0088cc;
  --pst-color-link-hover: #005580;
  --pst-font-family-base: "Inter", sans-serif;
  --pst-font-family-heading: "Inter", sans-serif;
}

html[data-theme="dark"] {
  --pst-color-primary: #ffc11e; /* Dask gold */
  --pst-color-primary-text: #080815;
  --pst-color-link: #ffc11e;
  --pst-color-link-hover: #ffd561;
  --pst-font-family-base: "Inter", sans-serif;
  --pst-font-family-heading: "Inter", sans-serif;
}

/* Blog post listing style */
.postlist .postlist-date {
  color: var(--pst-color-text-muted);
  font-size: 0.9em;
}

/* Wide layout variant for widepost pages */
body.wide-post .bd-article {
  max-width: 100%;
}
```

### 2.3 Light/dark theme

Handled entirely by pydata-sphinx-theme — no custom implementation needed:

- Theme toggle button configured via `"navbar_end": ["theme-switcher"]`
- Follows system `prefers-color-scheme` preference by default
- Persists user choice to `localStorage`
- Syntax highlighting adapts via `pygments_light_style` / `pygments_dark_style`

### 2.4 Custom template: Analytics (`_templates/analytics.html`)

Override the pydata-sphinx-theme's analytics partial to inject Google Tag Manager:

```html
{% if gtm_id %}
<!-- Google Tag Manager -->
<script>
  (function (w, d, s, l, i) {
    w[l] = w[l] || [];
    w[l].push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
    var f = d.getElementsByTagName(s)[0],
      j = d.createElement(s),
      dl = l != "dataLayer" ? "&l=" + l : "";
    j.async = true;
    j.src = "https://www.googletagmanager.com/gtm.js?id=" + i + dl;
    f.parentNode.insertBefore(j, f);
  })(window, document, "script", "dataLayer", "{{ gtm_id }}");
</script>
{% endif %}
```

### 2.5 ABlog sidebar templates

pydata-sphinx-theme provides styled versions of ABlog sidebars:

| Template                 | Usage                                                          |
| ------------------------ | -------------------------------------------------------------- |
| `ablog/postcard.html`    | Post metadata (date, author, tags) — shown on individual posts |
| `ablog/tagcloud.html`    | Tag cloud — shown on archive pages                             |
| `ablog/archives.html`    | Year-based archive links — shown on archive pages              |
| `ablog/recentposts.html` | Recent posts list (optional)                                   |

Configured via `html_sidebars` in `conf.py` (see Phase 1.3).

---

## Phase 3: Content Migration

### 3.1 Write Python migration script (`migrate.py`)

Transforms all 158 posts from Jekyll format to Sphinx/ABlog/MyST format:

**File relocation:**

- `_posts/2024-01-15-my-post.md` → `posts/2024/01/15/my-post.md`
- Posts with `draft: true` (8 posts) → `drafts/original-slug.md`

**Front matter changes:**

- Remove: `layout: post`, `layout: widepost`, `theme: twitter`
- Keep as-is: `title`, `author`, `tags`
- Rename: `canonical_url` → `canonical_link` (ABlog's field name)
- Rename: `tagline` → `description` (or keep as custom metadata)
- Add: `blogpost: true` (explicit flag; `blog_post_pattern` also auto-detects)
- Add: `date` (extracted from filename, formatted as `"Jan 15, 2024"` matching `post_date_format`)
- Convert: `layout: widepost` → `layout_style: wide` (custom front matter, handled by CSS/template)

**Body changes:**

- Strip `{% include JB/setup %}` from all 150 posts
- Convert `{% gist USER/ID %}` → raw HTML `<script src="https://gist.github.com/USER/ID.js"></script>` (1 post)
- Move inline `<meta>` tag to front matter `description` (1 post)

**Example: before (Jekyll)**

```markdown
---
layout: post
title: My Awesome Post
author: Jane Doe
tags: [dask, python]
theme: twitter
canonical_url: https://example.com/original
---

{% include JB/setup %}

Post content here with $math$ and <iframe>s...
```

**Example: after (Sphinx/ABlog/MyST)**

```markdown
---
blogpost: true
date: Jan 15, 2024
title: My Awesome Post
author: Jane Doe
tags: dask, python
canonical_link: https://example.com/original
---

Post content here with $math$ and <iframe>s...
```

### 3.2 Raw HTML handling

MyST-Parser follows the CommonMark spec and passes through raw HTML blocks by default. The 50+ posts with inline HTML (`<iframe>`, `<table>`, `<div>`, etc.) should work without modification. This needs verification during testing — if any HTML is stripped, the affected blocks can be wrapped in MyST's raw directive:

````markdown
```{raw} html
<iframe src="https://example.com" width="100%" height="400"></iframe>
```
````

### 3.3 Static assets

```bash
# images/ and storage/ stay in place at the source root
# html_extra_path = ["images", "storage"] copies them to the output root
# This preserves all /images/... and /storage/... URLs used in posts
```

Download Dask logos and favicon to `_static/`:

- `_static/dask-logo.svg` (light mode logo)
- `_static/dask-logo-white.svg` (dark mode logo)
- `_static/favicon.ico`

### 3.4 Create homepage (`index.md`)

````markdown
---
myst:
  html_meta:
    description: "Dask Working Notes — Writing about Scaling Python"
---

# Dask Working Notes

```{postlist}
:format: "{title} — *{date}*"
:date: %b %d, %Y
:excerpts:
:expand: Read more...
```
````

```{toctree}
:hidden:
:glob:

posts/*/*/*/*
```

````

The hidden glob toctree ensures all posts are included in Sphinx's document tree without displaying a table of contents on the homepage.

### 3.5 Permalink preservation

Posts at `posts/YYYY/MM/DD/slug.md` with the `dirhtml` builder produce URLs at `/posts/:year/:month/:day/:slug/`.

**Important:** This adds a `/posts/` prefix that Jekyll does not have. The Jekyll URLs are `/:year/:month/:day/:title/`. Two options:

**Option A — Accept the URL change with redirects:**
- New URLs: `/posts/2024/01/15/my-post/`
- Create redirect HTML files at old URLs (`extras/2024/01/15/my-post/index.html`) via the migration script
- This is the simplest approach but creates ~150 redirect files

**Option B — Place year directories at source root:**
- Move posts to `2024/01/15/my-post.md` (at root, not under `posts/`)
- Set `blog_post_pattern = "20*/*/*/*"`
- URLs become `/:year/:month/:day/:slug/` — identical to Jekyll
- Trade-off: year directories at root make the source tree noisier

**Recommendation:** Option B for exact URL preservation. The year directories are clearly organized and the glob pattern cleanly identifies posts.

### 3.6 Tag URL preservation

ABlog generates tag archive pages at `{blog_path}/tag/<name>/`:
- With `blog_path = "blog"`: tag pages at `/blog/tag/<name>/` (differs from Jekyll's `/tag/<name>/`)
- With `blog_path = ""`: tag pages at `/tag/<name>/` (matches Jekyll)

If using `blog_path = "blog"`, create redirect HTML files in `extras/tag/<name>/index.html` pointing to `/blog/tag/<name>/`.

If using `blog_path = ""`, tag URLs match exactly. Note: `blog_path = ""` may cause the blog archive to conflict with the homepage — needs testing.

### 3.7 Feed URL preservation

ABlog generates Atom feeds (not RSS). With `blog_feed_archives = True`:
- Main feed: `{blog_path}/atom.xml`
- Per-tag feeds: `{blog_path}/tag/<name>/atom.xml`

The current Jekyll feeds are at root level:
- `atom.xml` → redirect to `/blog/atom.xml` (or matches if `blog_path = ""`)
- `feed.python.xml` → redirect to `/blog/tag/Python/atom.xml`
- `feed.scipy.xml` → redirect to `/blog/tag/scipy/atom.xml`
- `feed.sympy.xml` → redirect to `/blog/tag/SymPy/atom.xml`

Create redirect HTML files in `extras/` for the old feed URLs. The redirect files use meta-refresh:
```html
<!DOCTYPE html>
<html><head><meta http-equiv="refresh" content="0;url=/blog/tag/Python/atom.xml"></head>
<body>Redirecting...</body></html>
````

**Note:** Tag name casing in ABlog feed URLs needs verification. ABlog may lowercase tag slugs.

### 3.8 Documentation redirect

`extras/documentation.html` — meta-refresh redirect to `https://dask.org` (same as current).

### 3.9 404 page

Create `404.md` at the source root:

```markdown
---
orphan: true
nosearch: true
---

# Page Not Found

Sorry, this page does not exist. [Return to the homepage](/).
```

---

## Phase 4: Playwright Development Testing

Playwright is used during development to verify migration correctness, **not** as a permanent CI suite.

### 4.1 Setup

- `package.json` at root with `@playwright/test` devDependency
- `playwright/playwright.config.ts` with `webServer` pointing to `python -m http.server` serving `_website/`
- Or use `ablog serve` if it provides a suitable dev server

### 4.2 Test coverage (development verification)

- **Homepage**: loads, lists 150+ posts, has correct title
- **Every post URL**: returns 200 (iterate all post links from homepage)
- **Sample posts**: verify title, author, content renders
- **Images**: spot-check that `/images/` references load (sample 10 posts)
- **Syntax highlighting**: code blocks have Pygments-styled `<span>` elements
- **MathJax**: `mjx-container` elements appear on math-heavy posts
- **Navigation**: navbar links work, tag links work
- **Tag pages**: `/blog/tag/python/`, `/blog/tag/dask/` exist and list posts
- **Feeds**: `/blog/atom.xml` returns valid XML; per-tag feeds exist
- **Feed redirects**: `/atom.xml`, `/feed.python.xml` redirect correctly
- **Draft exclusion**: draft posts not on homepage, return 404
- **Canonical URLs**: posts with `canonical_link` have correct `<link rel="canonical">`
- **Wide layout**: widepost posts render with wide class
- **Responsive**: renders on mobile (375px), tablet (768px), desktop (1440px)
- **Light/dark theme**: toggle works, colors change, preference persists on reload
- **System preference**: `prefers-color-scheme: dark` emulation applies dark theme by default
- **Raw HTML**: iframes, tables, and inline HTML render correctly in sample posts
- **No console errors**: check sample posts for JS errors
- **Internal links**: spot-check that internal links resolve
- **Post URL redirects** (if Option A): old Jekyll URLs redirect to new URLs

---

## Phase 5: CI/CD & Cleanup

### 5.1 GitHub Actions: Sphinx build + deploy (`.github/workflows/build.yml`)

```yaml
name: Build & Deploy

on:
  push:
    branches: [gh-pages]
  pull_request:
    branches: [gh-pages]
  schedule:
    - cron: "0 3 * * *" # Nightly rebuild (replaces refresh.yml)
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Build site
        run: ablog build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: _website/

  deploy:
    if: github.event_name != 'pull_request'
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 5.2 Update pre-commit workflow

- Keep prettier + markdownlint, update action versions
- Update `.prettierignore` and `.gitignore` for Sphinx paths (`_build/`, `_website/`, `.doctrees/`, `node_modules/`)

### 5.3 Delete Jekyll artifacts

Remove: `_config.yml`, `_includes/`, `_layouts/`, `_plugins/`, `_posts/`, `assets/`, `css/`, `Gemfile`, `.ruby-version`, `Rakefile`, `atom.xml`, `feed.*.xml`, `sitemap.txt`, `index.md` (old Jekyll homepage — replaced by new `index.md`), `tags.html`, `documentation.html`, `404.html`, `changelog.md`, `scripts/`

Keep: `CNAME`, `.github/`, `README.md` (updated), `images/`, `storage/`

### 5.4 Delete refresh workflow

`.github/workflows/refresh.yml` is replaced by the `schedule` trigger in `build.yml`.

### 5.5 Update `.gitignore`

```gitignore
_build/
_website/
.doctrees/
node_modules/
public/
__pycache__/
*.pyc
```

---

## Implementation Order

1. Set up Sphinx skeleton (`conf.py`, `requirements.txt`, `.gitignore`, directory structure)
2. Configure pydata-sphinx-theme with dask branding (`_static/css/custom.css`, logos)
3. Create homepage (`index.md`) with postlist directive
4. Manually migrate 3–5 sample posts to verify the pipeline works
5. Write and run migration script (`migrate.py`) — transform all 158 posts
6. Create redirect files for legacy URLs (feeds, tag pages, documentation)
7. Verify with `ablog build && ablog serve` — manual spot-check
8. Set up Playwright and run tests — fix any rendering issues
9. Set up CI workflow for Sphinx builds
10. Remove all Jekyll files
11. Update `README.md` with new build instructions
12. Open PR against `gh-pages`, review, merge
13. Switch GitHub Pages source to "GitHub Actions"

## Key Risks & Mitigations

| Risk                                            | Mitigation                                                                                      |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Permalink mismatch (slug differences)           | Playwright tests check all 150+ post URLs return 200                                            |
| `/posts/` prefix in URLs (Option A)             | Use Option B (year dirs at root) for exact URL match; or create redirects                       |
| Raw HTML stripped by MyST-Parser                | CommonMark spec passes through HTML blocks; test 50+ posts; wrap in `{raw}` directive if needed |
| MathJax `$` conflicts with MyST                 | `dollarmath` extension + `myst_update_mathjax = False` configured; test 12 math posts           |
| Tag URL case sensitivity                        | ABlog may lowercase tag slugs; verify feed URLs match tag casing                                |
| Feed URL change (`atom.xml` → `/blog/atom.xml`) | Redirect files in `extras/`; or use `blog_path = ""` for root-level feeds                       |
| `blog_path = ""` conflicts with homepage        | Test thoroughly; fallback to `blog_path = "blog"` with redirects                                |
| Sphinx build speed (158 posts)                  | Acceptable for CI; use `sphinx -j auto` for parallel builds                                     |
| ABlog sidebar conflicts with theme              | pydata-sphinx-theme has native ABlog support since v0.16                                        |
| GitHub Pages deployment cutover                 | Build workflow + settings change coordinated; CNAME unchanged                                   |

## Open Questions

1. **`blog_path = ""` vs `blog_path = "blog"`** — Does empty blog_path work without conflicting with the homepage? Needs testing. If not, use `"blog"` and create redirects for `/tag/`, `/atom.xml`.
2. **Post URL structure** — Option A (`posts/YYYY/MM/DD/slug`) with `/posts/` prefix and redirects, or Option B (`YYYY/MM/DD/slug` at root) for exact URL preservation? Recommend Option B.
3. **Tag slug casing** — Do ABlog tag URLs preserve original casing (`Python` vs `python`)? Affects feed redirect targets.
4. **Raw HTML handling** — Does MyST-Parser pass through all 50+ posts' inline HTML without issues? Needs early testing with sample posts.

## Verification

After each phase, verify locally with:

```bash
pip install -r requirements.txt
ablog build
ablog serve
# → open http://localhost:8000
```

Full verification before merge:

```bash
cd playwright && npx playwright test
```
