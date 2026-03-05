# Migrate Dask Blog to Read the Docs

## Goal

Move the Dask blog from GitHub Pages to Read the Docs (RTD) for hosting and building.

## Background

- The blog is a Jekyll site using the `github-pages` gem
- Currently deployed from the `gh-pages` branch via GitHub Pages
- Local development uses a conda environment (`environment.yml`) to install Ruby, compilers, and make
- The Jekyll build outputs static HTML to `_site/`

## Key Finding: No Conda Needed on RTD

RTD provides Ruby as a first-class build tool via `build.tools.ruby` (added March 2024).
This means we do **not** need the conda environment on RTD — Ruby, `gem`, and `bundler` are
available natively. The existing `environment.yml` can remain for local development.

**Reference:** [Read the Docs Loves Ruby](https://about.readthedocs.com/blog/2024/03/read-the-docs-loves-ruby/)

## Implementation Steps

### 1. Create `.readthedocs.yaml`

RTD recommends `build.jobs` over `build.commands` because it is more structured, supports
`build.apt_packages`, and allows per-format build commands.

```yaml
# Read the Docs configuration file
# See https://docs.readthedocs.com/platform/stable/config-file/v2.html for details

version: 2

build:
  os: ubuntu-24.04
  tools:
    ruby: "3.3"
  jobs:
    install:
      - gem install bundler
      - bundle install
    build:
      html:
        - bundle exec jekyll build --destination $READTHEDOCS_OUTPUT/html
```

**Notes:**

- `ruby: "3.3"` — Pin to a specific version for reproducible builds (RTD also offers `3.4` and `latest`, but `latest` updates every 6 months and could break builds). The Gemfile uses `ruby RUBY_VERSION` so it dynamically adapts to whatever Ruby RTD provides.
- `$READTHEDOCS_OUTPUT/html/` — RTD requires built HTML in this directory. RTD sets the `$READTHEDOCS_OUTPUT` env var automatically.
- `bundle exec jekyll build` — Uses `bundle exec` to ensure we use the bundled Jekyll version, matching how we build locally.
- Each command runs in a fresh shell process, but `build.jobs` handles this correctly for sequential steps within each phase.

### 2. Handle `github: [metadata]` in `_config.yml`

The `_config.yml` contains `github: [metadata]` which causes the `jekyll-github-metadata` plugin
(included via the `github-pages` gem) to fetch repository metadata from the GitHub API. This will
likely fail or produce warnings on RTD since there's no GitHub token available.

**Options (pick one):**

- **Option A (simplest):** Set `PAGES_REPO_NWO` env var in RTD project settings to `dask/dask-blog` and add a `JEKYLL_GITHUB_TOKEN` if needed. This keeps the metadata plugin working.
- **Option B (cleaner):** Remove `github: [metadata]` from `_config.yml` if the site doesn't actually use `site.github` variables in templates. Check templates first.
- **Option C:** Add `--config _config.yml,_config_rtd.yml` to the build command with an override file that sets `github: false`.

### 3. Consider the `github-pages` Gem

The Gemfile uses `gem "github-pages"` which bundles Jekyll and ~30 GitHub-specific plugins. This
should still install and build on RTD, but it's heavier than needed. Consider whether to:

- **Keep it** — Simplest path, ensures the same build on GitHub Pages and RTD during migration.
- **Replace it** — Switch to `gem "jekyll"` directly with only the plugins we actually use. This
  is a separate task and can be done later.

### 4. Handle Custom Domain

- The repo has a `CNAME` file with `blog.dask.org`
- RTD has its own custom domain configuration in the project settings dashboard
- The `CNAME` file can remain (it won't affect RTD builds) but DNS will need to be updated to point to RTD instead of GitHub Pages
- Update `url` in `_config.yml` if RTD serves from a different base URL (likely fine as-is if custom domain is configured)

### 5. Update/Remove GitHub Actions Workflows

Once RTD is the primary host:

- **`.github/workflows/refresh.yml`** — This triggers daily GitHub Pages rebuilds for future-dated posts. RTD may have its own scheduling mechanism, or we can set up a webhook/cron to trigger RTD builds instead. **Remove or replace.**
- **`.github/workflows/pre-commit.yml`** — Keep this for PR linting, it's independent of hosting.

### 6. Set Up RTD Project

In the RTD dashboard:

1. Import the repository (`dask/dask-blog`)
2. Set the default branch (currently `gh-pages`, will need to decide on branch strategy)
3. Configure custom domain (`blog.dask.org`)
4. Set any required environment variables (see Step 2)
5. Trigger a test build and verify

## Potential Issues

| Issue                                                               | Mitigation                                              |
| ------------------------------------------------------------------- | ------------------------------------------------------- |
| `github-pages` gem tries to fetch GitHub metadata                   | Handle per Step 2                                       |
| Ruby version mismatch (Gemfile.lock pins 3.4.8, RTD offers 3.3/3.4) | Use `ruby: "3.4"` in RTD config, or update Gemfile.lock |
| `jekyll-gist` plugin needs network access                           | Should work — RTD builds have internet access           |
| Large image directory (~92MB in `_site/`) may slow builds           | RTD caches builds, should be manageable                 |
| Future-dated posts need daily rebuilds                              | Configure RTD build automation or external cron         |

## File Changes Summary

| File                            | Action                                                     |
| ------------------------------- | ---------------------------------------------------------- |
| `.readthedocs.yaml`             | **Create** — RTD build configuration                       |
| `_config.yml`                   | **Maybe modify** — Handle `github: [metadata]`             |
| `.github/workflows/refresh.yml` | **Remove or update** — No longer needed for GH Pages       |
| `CNAME`                         | **Keep** — Doesn't affect RTD, useful if we ever fall back |
| `environment.yml`               | **Keep** — Still useful for local development              |
