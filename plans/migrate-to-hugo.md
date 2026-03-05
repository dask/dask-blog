# Jekyll to Hugo Migration Plan — Dask Blog

## Context

The Dask blog (`blog.dask.org`) is a 158-post Jekyll blog using Jekyll-Bootstrap with a Bootstrap 3 "twitter" theme. It's deployed via GitHub Pages from the `gh-pages` branch. The goal is to migrate entirely to Hugo with a new custom theme **visually aligned with dask.org** (same Inter font, dark navbar/footer, gold `#FFC11E` accent color) and supporting both **light and dark themes**. Playwright is used during development to verify all content renders correctly (not a permanent CI fixture).

## Current State (Key Facts)

- **158 posts** in `_posts/` (2014-2024), **237+ images** in `images/`
- 150 posts contain `{% include JB/setup %}` (must be stripped)
- 8 draft posts (`draft: true`), 7 posts with `canonical_url`
- 2 posts use `layout: widepost`, 1 post uses `{% gist %}`
- 12 posts use MathJax (`$...$` / `$$...$$`), 26 posts contain `<iframe>`s
- Permalink pattern: `/:year/:month/:day/:title` (no categories used)
- Disqus comments (short_name: `dask-blog`), GTM analytics (`GTM-P4GQM59`)
- Tag pages at `/tag/<name>/`, feeds at `atom.xml`, `feed.python.xml`, `feed.scipy.xml`, `feed.sympy.xml`

---

## Phase 1: Hugo Project Setup

### 1.1 Branch strategy

- Create `hugo-migration` branch from `gh-pages`
- `gh-pages` continues serving the live Jekyll site until cutover

### 1.2 Create `hugo.toml`

```toml
baseURL = "https://blog.dask.org"
languageCode = "en-us"
title = "Dask Working Notes"
theme = "dask"

[permalinks]
  posts = "/:year/:month/:day/:title/"

[taxonomies]
  tag = "tag"   # preserves /tag/<name>/ URLs from Jekyll

buildFuture = false
buildDrafts = false
enableGitInfo = true

[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true  # Required: 50+ posts have inline HTML
    [markup.goldmark.extensions]
      [markup.goldmark.extensions.passthrough]
        enable = true
        [markup.goldmark.extensions.passthrough.delimiters]
          block = [["$$", "$$"], ["\\[", "\\]"]]
          inline = [["$", "$"], ["\\(", "\\)"]]
  [markup.highlight]
    style = "pygments"
    noClasses = false

[params]
  description = "Writing about Scaling Python"
  disqusShortname = "dask-blog"
  gtmID = "GTM-P4GQM59"

[outputFormats]
  [outputFormats.ATOM]
    mediaType = "application/atom+xml"
    baseName = "atom"
    isPlainText = true
  [outputFormats.PythonRSS]
    mediaType = "application/rss+xml"
    baseName = "feed.python"
    isPlainText = true
  [outputFormats.ScipyRSS]
    mediaType = "application/rss+xml"
    baseName = "feed.scipy"
    isPlainText = true
  [outputFormats.SympyRSS]
    mediaType = "application/rss+xml"
    baseName = "feed.sympy"
    isPlainText = true

[outputs]
  home = ["HTML", "ATOM", "PythonRSS", "ScipyRSS", "SympyRSS"]

[sitemap]
  filename = "sitemap.xml"
```

### 1.3 Target directory structure

```
dask-blog/
  hugo.toml
  CNAME
  content/
    posts/           # Migrated from _posts/
    _index.md        # Homepage
  static/
    images/          # Moved from images/
    storage/         # Moved from storage/
  themes/dask/       # New custom theme
    layouts/
    assets/css/
  playwright/        # Development testing (temporary)
  package.json
  .github/workflows/
```

---

## Phase 2: Theme Development (`themes/dask/`)

Design direction: **Aligned with dask.org** — the blog should feel like part of the dask.org ecosystem. Use the same font (Inter), color palette, and visual language. Support both **light and dark themes** via `prefers-color-scheme` with a manual toggle.

### 2.1 Design System (extracted from dask.org via Playwright)

**Typography:**

- Font family: `Inter, sans-serif` (dask.org uses Inter throughout)
- Body text: 16px base (modernized from current 13px), line-height 1.5
- H1: ~34px, weight 700
- H2: ~27px, weight 700
- Nav links: ~12px
- Monospace: `"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace`

**Color Palette (from dask.org):**

- Dark background: `#262326` (rgb(38,35,38)) — navbar, dark sections
- Near-black text: `#080815` (rgb(8,8,21)) — button text, dark UI text
- White: `#ffffff` — light backgrounds, text on dark
- Primary accent (gold/yellow): `#FFC11E` (rgb(255,193,30)) — CTA buttons, highlights
- Footer dark: `#33363D` (rgb(51,54,61))
- Body text on light: `#333333`
- Muted text: `#666666`
- Links on dark: `#ffffff` (no underline)
- Border radius: `4px` (buttons)
- Code block bg: dark with white text (on dark sections of dask.org)

**Light Theme (`prefers-color-scheme: light` / default):**

```css
:root {
  --color-bg: #ffffff;
  --color-bg-secondary: #f8f8f8;
  --color-text: #333333;
  --color-text-secondary: #666666;
  --color-link: #0088cc;
  --color-link-hover: #005580;
  --color-accent: #ffc11e; /* dask gold */
  --color-navbar-bg: #262326; /* dask dark */
  --color-navbar-text: #ffffff;
  --color-footer-bg: #33363d;
  --color-footer-text: #ffffff;
  --color-code-bg: #f5f5f5;
  --color-code-text: #333333;
  --color-border: #e0e0e0;
  --color-heading: #080815;
}
```

**Dark Theme (`prefers-color-scheme: dark`):**

```css
[data-theme="dark"],
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #1a1a2e;
    --color-bg-secondary: #262326;
    --color-text: #e0e0e0;
    --color-text-secondary: #999999;
    --color-link: #ffc11e; /* gold links on dark */
    --color-link-hover: #ffd561;
    --color-accent: #ffc11e;
    --color-navbar-bg: #080815;
    --color-navbar-text: #ffffff;
    --color-footer-bg: #080815;
    --color-footer-text: #cccccc;
    --color-code-bg: #2d2d3d;
    --color-code-text: #e0e0e0;
    --color-border: #444444;
    --color-heading: #ffffff;
  }
}
```

**Theme Toggle:**

- A sun/moon button in the navbar
- JavaScript: toggles `data-theme` attribute on `<html>`, persists choice to `localStorage`
- Default: follow system preference (`prefers-color-scheme`)
- Small inline `<script>` in `<head>` to apply saved preference before paint (avoids flash)

### 2.2 CSS: `themes/dask/assets/css/main.css`

- Vanilla CSS with custom properties as above
- Minimal reset, Inter font via Google Fonts or bundled
- All colors reference `var(--color-*)` tokens — entire theme switches by changing the custom properties
- Responsive layout: centered content (max-width ~740px), flex navbar
- Navbar: dark bg (`--color-navbar-bg`), Dask logo, nav links, theme toggle button
- Wide post variant (removes max-width constraint)
- Table, figure, code block, blockquote styling — all using theme tokens
- Footer: dark bg (`--color-footer-bg`) matching dask.org footer style

### 2.3 CSS: `themes/dask/assets/css/syntax.css`

- Two sets of syntax highlighting tokens: light and dark
- Light: port existing `css/pygments/pygments.css`
- Dark: inverted variant (light text on dark code bg)
- Controlled via `[data-theme="dark"] .highlight` selectors

### 2.3 Layouts

| File                     | Purpose                                                         |
| ------------------------ | --------------------------------------------------------------- |
| `_default/baseof.html`   | HTML shell: head partial, header, main block, footer, analytics |
| `posts/single.html`      | Single post: title, tagline, author, date, content, comments    |
| `posts/list.html`        | Post listing (section page for /posts/)                         |
| `index.html`             | Homepage: list all non-draft posts with links and dates         |
| `_default/taxonomy.html` | Individual tag page (e.g., `/tag/python/`)                      |
| `_default/terms.html`    | All tags overview (`/tag/`)                                     |
| `404.html`               | Custom 404 page                                                 |

### 2.5 Partials

| File                | Purpose                                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `head.html`         | Meta tags, CSS (fingerprinted), canonical URL, MathJax, feed link, **theme-init script** (reads localStorage, applies `data-theme` before paint) |
| `header.html`       | Dark navbar (`--color-navbar-bg`), Dask logo, nav links (Blog, Tags, Docs), **theme toggle button** (sun/moon icon)                              |
| `footer.html`       | Dark footer (`--color-footer-bg`) matching dask.org footer — copyright, Atom feed link, social links                                             |
| `comments.html`     | Disqus embed script (conditional on `disqusShortname`)                                                                                           |
| `analytics.html`    | Google Tag Manager script (conditional on `gtmID`)                                                                                               |
| `math.html`         | MathJax v3 configuration and script load                                                                                                         |
| `meta.html`         | SEO: description, canonical, og:url meta tags                                                                                                    |
| `theme-toggle.html` | JS for theme toggle: flip `data-theme`, persist to `localStorage`, update button icon                                                            |

### 2.5 Feed templates

- `index.atom.xml` — Main Atom feed (all non-draft posts)
- `index.feed.python.xml` — Posts tagged "Python"
- `index.feed.scipy.xml` — Posts tagged "scipy"
- `index.feed.sympy.xml` — Posts tagged "sympy"

### 2.6 Shortcodes

- `gist.html` — For the single `{% gist %}` usage (converts to `{{</* gist ID */>}}`)

---

## Phase 3: Content Migration

### 3.1 Write Python migration script (`migrate.py`)

Transforms all 158 posts from Jekyll to Hugo format:

**Front matter changes:**

- Remove: `layout: post`, `theme: twitter`
- Keep as-is: `title`, `author`, `tags`, `tagline`, `canonical_url`, `draft`
- Add: `date` field (extracted from filename `YYYY-MM-DD-slug.md`)
- Convert `layout: widepost` → `layout_style: wide` (custom param)

**Body changes:**

- Strip `{% include JB/setup %}` from all 150 posts
- Convert `{% gist ID %}` → `{{< gist ID >}}` (1 post)
- Move inline `<meta>` tag to front matter `description` (1 post)

### 3.2 Move static assets

```bash
mv images/ static/images/     # Preserves /images/ URL paths
mv storage/ static/storage/
```

### 3.3 Create homepage

`content/_index.md` with just front matter (title). The `index.html` template handles listing.

### 3.4 Documentation redirect

`static/documentation.html` — meta-refresh redirect to `https://dask.org`

### 3.5 Permalink preservation

Hugo config `posts = "/:year/:month/:day/:title/"` produces identical URLs to Jekyll's `/:categories/:year/:month/:day/:title` (since no posts use categories).

### 3.6 Tag URL preservation

Setting `[taxonomies] tag = "tag"` produces `/tag/<name>/` matching Jekyll's plugin output.

---

## Phase 4: Playwright Development Testing

Playwright is used during development to verify migration correctness, **not** as a permanent CI suite.

### 4.1 Setup

- `package.json` at root with `@playwright/test` devDependency
- `playwright/playwright.config.ts` with `webServer` pointing to `hugo server`

### 4.2 Test coverage (development verification)

- **Homepage**: loads, lists 150+ posts, has correct title
- **Every post URL**: returns 200 (iterate all posts from homepage links)
- **Sample posts**: verify title, author, content renders
- **Images**: spot-check that `/images/` references load (sample 10 posts)
- **Syntax highlighting**: code blocks have `.highlight` spans
- **MathJax**: `mjx-container` elements appear on math-heavy posts
- **Navigation**: navbar links work, tag links work
- **Tag pages**: `/tag/`, `/tag/python/`, `/tag/dask/` exist and list posts
- **Feeds**: `atom.xml`, `feed.python.xml`, `feed.scipy.xml`, `feed.sympy.xml` return valid XML
- **Draft exclusion**: draft posts not on homepage, return 404
- **Canonical URLs**: posts with `canonical_url` have correct `<link rel="canonical">`
- **Wide layout**: widepost posts render with wide class
- **Responsive**: renders on mobile (375px), tablet (768px), desktop (1440px)
- **Light/dark theme**: toggle works, colors change, preference persists on reload
- **System preference**: `prefers-color-scheme: dark` emulation applies dark theme by default
- **No console errors**: check sample posts for JS errors
- **Internal links**: spot-check that internal links resolve

---

## Phase 5: CI/CD & Cleanup

### 5.1 GitHub Actions: Hugo build + deploy (`.github/workflows/build.yml`)

- Trigger: push to `gh-pages`, PRs, nightly schedule, manual dispatch
- Steps: checkout (fetch-depth 0), setup Hugo, `hugo --minify`, deploy to GitHub Pages via Actions
- Requires: changing repo Settings → Pages → Source to "GitHub Actions"

### 5.2 Update pre-commit workflow

- Keep prettier + markdownlint, update versions
- Update `.prettierignore` and `.gitignore` for Hugo paths (`public/`, `resources/`, `node_modules/`)

### 5.3 Delete Jekyll artifacts

Remove: `_config.yml`, `_includes/`, `_layouts/`, `_plugins/`, `_posts/`, `assets/`, `css/`, `Gemfile`, `.ruby-version`, `Rakefile`, `atom.xml`, `feed.*.xml`, `sitemap.txt`, `index.md`, `tags.html`, `documentation.html`, `404.html`, `changelog.md`, `scripts/`

Keep: `CNAME`, `.github/`, `README.md` (updated)

### 5.4 Delete refresh workflow

`.github/workflows/refresh.yml` is replaced by the schedule trigger in `build.yml`.

---

## Implementation Order

1. Create `hugo-migration` branch
2. Set up Hugo skeleton (`hugo.toml`, directory structure, `.gitignore`)
3. Build theme (templates, partials, CSS) — test with a few sample posts
4. Write and run migration script — transform all 158 posts
5. Move static assets (`images/` → `static/images/`)
6. Create CNAME, documentation redirect, 404, homepage
7. Verify with `hugo server` — manual spot-check
8. Set up Playwright and run tests — fix any rendering issues
9. Set up CI workflow for Hugo builds
10. Remove all Jekyll files
11. Update `README.md` with new build instructions
12. Open PR against `gh-pages`, review, merge
13. Switch GitHub Pages source to "GitHub Actions"

## Key Risks & Mitigations

| Risk                                  | Mitigation                                                                |
| ------------------------------------- | ------------------------------------------------------------------------- |
| Permalink mismatch (slug differences) | Playwright tests check all 150+ post URLs return 200                      |
| Raw HTML breaks (iframes, tables)     | `unsafe = true` in Goldmark config; test posts with HTML                  |
| MathJax `$` conflicts with Goldmark   | Passthrough extension configured; test 12 math posts                      |
| Author field with HTML links          | Use `safeHTML` in template: `{{ .Params.author \| safeHTML }}`            |
| Tag URL case sensitivity              | Hugo lowercases by default; verify feed templates use lowercase keys      |
| Feed URL preservation                 | Custom output formats produce `atom.xml`, `feed.python.xml` at same paths |
| GitHub Pages deployment cutover       | Build workflow + settings change coordinated; CNAME unchanged             |

## Verification

After each phase, verify locally with:

```bash
hugo server --buildDrafts=false --disableFastRender
```

Full verification before merge:

```bash
cd playwright && npx playwright test
```
