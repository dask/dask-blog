# Dask Blog Redesign Plan

## Goal

Update the design of this Jekyll blog (blog.dask.org) to match the look and feel of the public Dask website (dask.org). The blog should feel like a seamless part of the main site.

## Reference Materials

- **Target design**: https://www.dask.org/blog — the index page styling we're matching
- **Reference CSS**: https://raw.githubusercontent.com/dask/dask.github.io/a1f5acf5ef038ed1f1208d36fd0641eb8557d2d9/_static/css/dask.css — foundation CSS from a prior redesign with the same goals
- **Local build instructions**: See `README.md` — use `bundle exec jekyll serve` in the conda environment

## Design Decisions

### CSS Strategy

- **Drop Bootstrap 3.3.7** — replace with the reference `dask.css` as the base stylesheet
- Add blog-specific styles on top of the reference CSS
- **Convert vw units to rem/px** — the reference CSS uses viewport-relative units extensively; convert these to rem/px with media queries for better long-form reading

### Typography

- **Use Inter** as the primary sans-serif font (loaded from Google Fonts CDN), matching dask.org

### Color Scheme

- **Dark nav and footer** matching dask.org (primary dark: `#080815`, accents: yellow `#ffc11e`, red `#ef1561`)
- **Light/white content area** for blog readability
- Dask accent colors for links, buttons, and interactive elements

### Index Page

- **Styled list** — keep the list-based post layout but restyle it to match dask.org aesthetics (colors, fonts, spacing, visual hierarchy)
- No JavaScript-powered filtering or sorting

### Navigation & Footer

- **Full dask.org navigation bar** — replicate the header nav (Get Started, Community, Blog, Docs, social icons) so the blog feels integrated with the main site
- **Full dask.org footer** — replicate the comprehensive footer with links, branding, and social media

### Post Pages

- **Redesign post pages** — update with new typography, colors, header styling, and consistent nav/footer

### Tags Page

- **Restyle tags page** (`/tags.html`) to be consistent with the new design system

## Scope of Changes

### Files to Modify

- `_includes/themes/twitter/default.html` — main HTML wrapper (nav, footer, head assets)
- `_includes/themes/twitter/post.html` — post layout template
- `_includes/themes/twitter/page.html` — page layout template
- `_includes/themes/twitter/widepost.html` — wide post variant
- `index.md` — homepage post listing
- `tags.html` — tags page
- `_config.yml` — may need updates for new asset paths

### Files to Add

- New CSS file(s) based on the reference `dask.css`, adapted for blog use
- Possibly new include files for the updated nav/footer components

### Files to Remove/Deprecate

- `assets/themes/twitter/bootstrap/` — Bootstrap CSS files (replaced by new CSS)
- `assets/themes/twitter/css/style.css` — old custom styles (merged into new CSS)

## Implementation Approach

Use the playwright-cli skill to view the site we are mirroring along with the build preview of this site. Use the local build instructions from `README.md` to make a local build.

1. **Set up reference CSS** — download and adapt `dask.css`, converting vw units to rem/px and adding blog-specific styles
2. **Update the HTML wrapper** (`default.html`) — replace the Bootstrap navbar and footer with dask.org-matching nav/footer markup, swap out Bootstrap CSS references for the new stylesheet, add Inter font loading
3. **Restyle the index page** — update `index.md` markup/styling for the new list design
4. **Restyle post pages** — update post/page/widepost templates with new typography and layout
5. **Restyle the tags page** — update `tags.html` to match the new design
6. **Test and iterate** — build locally, compare with dask.org/blog, refine
