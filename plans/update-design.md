# Update Blog Design to Match dask.org

## Goal

Update the Sphinx blog design to match the public Dask website (dask.org) so
that the blog feels like a seamless part of the Dask web presence.

## Reference Materials

- **dask.org/blog** — The target design we want to approximate:
  <https://www.dask.org/blog>
- **dask.org CSS** — Reference CSS created for a similar redesign. Download
  locally and use as a style reference (not a drop-in):
  <https://raw.githubusercontent.com/dask/dask.github.io/a1f5acf5ef038ed1f1208d36fd0641eb8557d2d9/_static/css/dask.css>
- **dask-sphinx-theme** — The official Dask Sphinx theme, checked out at
  `/Users/jtomlinson/Projects/dask/dask-sphinx-theme`. This is our base theme.

## Architecture Decisions

1. **Theme hierarchy**: `dask_blog_theme` (local) → `dask_sphinx_theme` →
   `sphinx_book_theme` → `pydata_sphinx_theme` → `basic`
2. **Local wrapper theme**: Create `_themes/dask_blog_theme/` in this repo that
   extends `dask_sphinx_theme` with blog-specific template overrides and CSS.
3. **Post listing**: Keep ABlog's `{postlist}` directive, style it with CSS to
   resemble card-style entries (not a full JS card/filter implementation).
4. **Dark mode**: Keep light/dark mode support via pydata-sphinx-theme's theme
   switcher. Style both themes with Dask brand colors.

## Steps

### 1. Set Up Local Blog Theme

Create `_themes/dask_blog_theme/` with:

- `theme.conf` — Inherits from `dask_sphinx_theme`, registers blog stylesheet.
- `static/css/blog.css` — Blog-specific styles (post listing cards, layout
  tweaks, footer styles). Replaces the current `_static/css/custom.css`.

Update `conf.py`:

- Switch `html_theme` from `pydata_sphinx_theme` to `dask_blog_theme`.
- Add `_themes` to the theme search path via
  `html_theme_path = ["_themes"]`.
- Update `requirements.txt` to add `dask-sphinx-theme` (and remove direct
  `pydata-sphinx-theme` dep since it comes transitively).
- Remove `html_css_files = ["css/custom.css"]` (the theme handles its own CSS).

### 2. Override Navbar to Match dask.org

Override the navbar template in `_themes/dask_blog_theme/layout.html` to
replace the documentation-focused links from dask-sphinx-theme with dask.org's
marketing nav:

- **Logo**: Dask logo linking to <https://www.dask.org>
- **Get Started**: <https://www.dask.org/get-started>
- **Community**: Dropdown with Demo Day, Get Help, Powered By, Mailing List
- **Blog**: <https://blog.dask.org> (this site — active state)
- **Docs**: <https://docs.dask.org/en/stable/>

The navbar should use the same dark background (`#262326`) and yellow hover
underline styling from dask-sphinx-theme. Keep mobile responsiveness.

### 3. Add dask.org-Style Footer

Create a footer template override with a multi-column layout matching dask.org:

- **Column 1 — Get Started**: Link to docs.dask.org
- **Column 2 — Community**: Get Help, Powered By, Demo Day
- **Column 3 — Blog**: Dask Blog, Contribute (GitHub)
- **Brand**: Brand Guidelines link
- **Social icons**: GitHub, Twitter, YouTube, Stack Overflow, Discourse
- **Copyright**: "Copyright © 2024 Dask core developers. New-BSD Licensed."

Style the footer using the reference CSS patterns (dark background, grid
columns, social icon links).

### 4. Style Post Listing as Cards

Style ABlog's `{postlist}` output to visually resemble dask.org/blog's card
layout using CSS only:

- Each post entry styled as a card with subtle border/shadow.
- Post title, date, and tags visible.
- "Read more..." link styled.
- Consistent spacing between cards.
- Responsive — single column on mobile, wider on desktop.

### 5. Refine Typography and Colors

Using the reference CSS and dask-sphinx-theme's existing variables as a guide:

- Font: Inter for body/headings, Inconsolata for code.
- Brand colors: gold `#ffc11e`, dark `#080815`, charcoal `#262326`.
- Link styling: yellow underline decoration on hover.
- Code blocks: salmon `#fc6e6b` for inline code, Dask Pygments style.
- Ensure dark mode counterparts are defined for all custom colors.

### 6. Update Sidebar Configuration

Adjust sidebar configuration for the new theme hierarchy:

- Index page: no sidebar (clean landing page).
- Individual posts: post metadata sidebar (date, author, tags).
- Archive pages (`/blog/`): tag cloud and archives sidebar.

### 7. Clean Up

- Remove `_static/css/custom.css` (replaced by theme CSS).
- Remove `_templates/analytics.html` (dask-sphinx-theme handles GTM via
  `theme_google_tag_manager_id`).
- Update `README.md` build instructions from Jekyll to Sphinx/ABlog:
  - `make serve` for development with auto-reload.
  - `make build` for static build.
  - Python + pip requirements instead of Ruby/Bundler.

## Verification

Use the `playwright-cli` skill to:

1. Take screenshots of <https://www.dask.org/blog> as the reference target.
2. Build the local site with `make serve`.
3. Take screenshots of the local build.
4. Compare and iterate on styling differences.

## Notes

- The reference CSS (`dask.css`) uses viewport-relative units (`vw`) and a
  custom grid system. Do NOT adopt these directly — they conflict with the
  pydata-sphinx-theme layout system. Instead, use them as visual reference and
  translate the design intent into pydata-sphinx-theme CSS variable overrides
  and targeted custom styles.
- ABlog's template integration flows through pydata-sphinx-theme. Verify that
  ABlog widgets (postcard, tagcloud, archives) render correctly with the new
  theme chain.
- The dask-sphinx-theme depends on `sphinx-book-theme>=1,<2`. Ensure this
  doesn't conflict with the ABlog version in use.
