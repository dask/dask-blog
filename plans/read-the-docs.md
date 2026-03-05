# Migrate Dask Blog to Read the Docs

## Goal

Update this project to build and host on Read the Docs instead of GitHub Pages.

## Background

- This is a Hugo static site (theme: `dask`, committed in `themes/dask/`)
- No SCSS — Hugo Extended is **not** required
- `enableGitInfo = true` in `hugo.toml` — requires full git history (RTD clones the repo with git, so this works by default)
- Currently deployed via GitHub Actions to GitHub Pages

## Approach

Read the Docs supports any static site generator via `build.jobs`. We'll use asdf (which is pre-installed on RTD build images) to install Hugo, then build the site outputting to `$READTHEDOCS_OUTPUT/html/` where RTD expects it.

We'll use `build.jobs` (not `build.commands`) because:

- It's the recommended approach per [RTD docs](https://about.readthedocs.com/blog/2025/01/override-build-process-with-build-jobs/)
- More structured — allows format-specific build steps
- Supports `build.apt_packages` if we ever need system deps

## Steps

### 1. Create `.readthedocs.yaml`

```yaml
# Read the Docs configuration file
# See https://docs.readthedocs.com/platform/stable/config-file/v2.html for details

version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.13"
  jobs:
    create_environment:
      - asdf plugin add hugo
      - asdf install hugo latest
      - asdf global hugo latest
    build:
      html:
        - hugo --minify --destination $READTHEDOCS_OUTPUT/html/
```

Key details:

- **`python: "3.13"`** — at least one tool is required in `build.tools`
- **`asdf`** — pre-installed on RTD build images, used by RTD's own docs examples for installing tools like `uv` and `pixi`
- **`create_environment`** — used for tool setup (following RTD's own examples)
- **`asdf plugin add hugo` / `asdf install hugo latest`** — installs Hugo via the [asdf-hugo plugin](https://github.com/NeoHsu/asdf-hugo)
- **`--minify`** — matches the existing GitHub Actions build
- **`--destination $READTHEDOCS_OUTPUT/html/`** — writes output directly where RTD expects it (resolves to `_readthedocs/html/`)

### 2. Configure the project on Read the Docs

- Go to [readthedocs.org](https://readthedocs.org) and import the repository
- Set the default branch to match the production branch
- Configure the custom domain `blog.dask.org` in RTD project settings
- Set up DNS (CNAME from `blog.dask.org` to the RTD domain)

### 3. Update GitHub Actions

- Remove the GitHub Pages deploy workflow (`.github/workflows/build.yml`) or repurpose it for PR preview builds only
- Keep the pre-commit linting workflow (`.github/workflows/pre-commit.yml`)

### 4. Clean up GitHub Pages artifacts

- Remove the `CNAME` file (used for GitHub Pages custom domain)
- Update `hugo.toml` `baseURL` if RTD uses a different URL pattern (likely stays `https://blog.dask.org`)

## Alternative: Hugo Extended (if needed later)

If SCSS is ever added to the theme, install the extended version via asdf by prefixing the version with `extended_`:

```yaml
create_environment:
  - asdf plugin add hugo
  - asdf install hugo extended_0.147.0
  - asdf global hugo extended_0.147.0
```

Or download a prebuilt binary directly:

```yaml
install:
  - wget -q https://github.com/gohugoio/hugo/releases/download/v0.147.0/hugo_extended_0.147.0_linux-amd64.tar.gz
  - tar -xzf hugo_extended_0.147.0_linux-amd64.tar.gz
  - mv hugo $READTHEDOCS_VIRTUALENV_PATH/bin/
```

## Key RTD Environment Variables

| Variable                       | Description                                            |
| ------------------------------ | ------------------------------------------------------ |
| `$READTHEDOCS_OUTPUT`          | Base output path (append `/html/`)                     |
| `$READTHEDOCS_VIRTUALENV_PATH` | Python venv path (useful for placing binaries on PATH) |
| `$READTHEDOCS_VERSION`         | Version slug (`latest`, branch name, etc.)             |
| `$READTHEDOCS_CANONICAL_URL`   | Canonical base URL                                     |

## References

- [RTD Config File v2](https://docs.readthedocs.com/platform/stable/config-file/v2.html)
- [RTD Build Customization](https://docs.readthedocs.com/platform/stable/build-customization.html)
- [RTD Environment Variables](https://docs.readthedocs.com/platform/stable/reference/environment-variables.html)
- [RTD build.jobs blog post](https://about.readthedocs.com/blog/2025/01/override-build-process-with-build-jobs/)
