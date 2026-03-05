# Dask Blog Design Update Plan

## Goal

Update the design of this Hugo blog to visually match the public Dask website (dask.org), while keeping it blog-focused and functional.

## Reference Material

- **Design reference CSS**: https://raw.githubusercontent.com/dask/dask.github.io/a1f5acf5ef038ed1f1208d36fd0641eb8557d2d9/_static/css/dask.css
- **Visual target**: https://www.dask.org/blog (index page layout and overall feel)
- **Current site theme**: `themes/dask/` (Hugo custom theme)

## Design Decisions

| Decision             | Choice                                                            |
| -------------------- | ----------------------------------------------------------------- |
| Dark mode            | **Keep** the light/dark toggle                                    |
| Index page filtering | **No** interactive tag filtering or sorting — keep simple list    |
| Navbar links         | Blog-focused: Blog, Tags, Docs + theme toggle (restyled visually) |
| Redesign scope       | **Full** — index, single posts, tag pages, navbar, footer         |
| Typography units     | **rem/px** (standard, not viewport-width units)                   |
| Content max-width    | **~900px** (widen from current 740px)                             |

## Color Palette (from dask.css reference)

Use these CSS custom properties, adapted for light and dark themes:

- **Primary dark**: `#080815` (headings, navbar dark bg)
- **Charcoal**: `#262326` (current navbar bg — keep)
- **Accent gold**: `#FFC11E` (keep — already in use)
- **Accent red**: `#EF1561` (for hover states or highlights, optional)
- **Blue link**: `#1F5AFF` (consider for light-mode links instead of current `#0088cc`)
- **Light grey bg**: `#F6F6F6` (secondary backgrounds)
- **Medium grey**: `#EBEAEE` (borders)

## Phase 1: Navbar Redesign

**Files**: `themes/dask/layouts/partials/header.html`, `main.css`

- Restyle navbar to match dask.org's visual design (clean, modern feel)
- Keep existing links: Blog (home), Tags, Docs
- Keep the dark mode toggle button
- Add the Dask logo (already present, ensure it matches dask.org's logo styling)
- Wider inner container to match new ~900px content width (or match dask.org's navbar width)
- Clean font styling: Inter, slightly larger nav link text

## Phase 2: Footer Redesign

**Files**: `themes/dask/layouts/partials/footer.html`, `main.css`

- Match dask.org footer structure: Dask logo, quick links, social icons, copyright
- Add social links: GitHub, Twitter/X, YouTube, Stack Overflow, Discourse
- Update copyright text to match dask.org: "Copyright © 2025 Dask core developers. New-BSD Licensed"
- Multi-column layout with logo on left, link groups, social icons
- Dark background (keep current `#33363D` or align with dask.org)

## Phase 3: Index Page Redesign

**Files**: `themes/dask/layouts/index.html`, `main.css`

- Update content max-width to ~900px
- Each post entry should show: **title**, **date** (formatted like "May 30, 2024"), **tags** (as small pills/badges)
- Keep the simple chronological list layout (newest first)
- Add subtle separators or spacing between entries for visual clarity
- Style the page title and description to match dask.org's blog header

## Phase 4: Single Post Page Redesign

**Files**: `themes/dask/layouts/posts/single.html`, `main.css`

- Update post header styling (title, author, date, tags)
- Content area widened to ~900px (matching index)
- Ensure code blocks, images, tables, and blockquotes look polished
- Tag pills should match the style used on the index page
- Review and update the Disqus comments section styling

## Phase 5: Tag Pages

**Files**: `themes/dask/layouts/_default/taxonomy.html`, `themes/dask/layouts/_default/terms.html`, `main.css`

- Style the "all tags" overview page with tag pills matching the index page style
- Style individual tag pages (e.g., `/tag/python/`) to show filtered post lists

## Phase 6: Global Polish

**Files**: `main.css`, `syntax.css`, various templates

- Update the responsive breakpoints if needed (current: 600px)
- Verify dark mode looks good with all the new styles
- Test syntax highlighting in both light and dark modes
- Verify all pages render correctly: index, single posts, tag pages, 404

## Implementation Notes

- Use the **playwright-cli** skill to visually compare our build against dask.org/blog
- Build locally with `hugo server` (see README.md for instructions)
- All styling changes go in `themes/dask/assets/css/main.css` unless a new CSS file is warranted
- Cherry-pick styles/patterns from the reference dask.css — do NOT import it wholesale (it uses vw units and is built for a different site structure)
- Font stays as **Inter** (already matches dask.org)
