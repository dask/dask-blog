# Read the Docs Deployment Plan

## Goal

Configure this Sphinx + ABlog blog project to build and host on Read the Docs.

## Background

This project uses Sphinx with ABlog and a custom `dask_blog_theme` (which inherits from `dask-sphinx-theme`). The Sphinx config (`conf.py`) uses `ablog_builder = "dirhtml"` for clean URLs. Dependencies are listed in `requirements.txt`.

## Approach: `build.jobs` with uv

RTD recommends [`build.jobs` over `build.commands`](https://about.readthedocs.com/blog/2025/01/override-build-process-with-build-jobs/) (announced January 2025). With `build.jobs`, we only override the environment creation and install steps, while letting RTD handle the Sphinx build and output placement automatically. This is simpler and less error-prone than `build.commands`.

Key advantages of `build.jobs`:

- RTD handles `sphinx-build` invocation and places output into `$READTHEDOCS_OUTPUT/html/` automatically
- The `sphinx` config key (builder, conf.py path) is still respected
- Less config to maintain; we don't need to manually manage output paths

## Configuration

### `.readthedocs.yaml`

Create this file in the repository root:

```yaml
# Read the Docs configuration file
# See https://docs.readthedocs.com/platform/stable/config-file/v2.html for details

version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.13"
  jobs:
    # Install uv via asdf (pre-installed in RTD build images)
    pre_create_environment:
      - asdf plugin add uv
      - asdf install uv latest
      - asdf global uv latest
    # Create venv with uv instead of the default virtualenv
    create_environment:
      - uv venv "${READTHEDOCS_VIRTUALENV_PATH}"
    # Install dependencies with uv (much faster than pip)
    install:
      - uv pip install --python "${READTHEDOCS_VIRTUALENV_PATH}/bin/python" -r requirements.txt

sphinx:
  configuration: conf.py
  builder: dirhtml
```

### Key details

- **`sphinx.builder: dirhtml`** must match `ablog_builder = "dirhtml"` in `conf.py` so URLs are consistent.
- **`sphinx.configuration: conf.py`** points RTD to our Sphinx config at the repo root.
- **Environment variables don't persist between commands**, so we use inline `--python` flag rather than setting `VIRTUAL_ENV`.
- **`asdf`** is pre-installed in RTD build images — it's the standard way to install tools like uv.

## Implementation Steps

1. **Create `.readthedocs.yaml`** in the repo root with the config above.
2. **Verify `conf.py` compatibility:**
   - `html_extra_path` references `CNAME` and `extras/` — ensure these exist or remove them if not needed on RTD (RTD handles custom domains separately, so `CNAME` is unnecessary).
   - `sphinx.ext.githubpages` creates a `.nojekyll` file — harmless on RTD but could be removed.
   - The `_themes/` directory with the local theme must be committed to the repo.
3. **Test the build** by pushing to the branch configured in RTD and checking the build logs.

## Gotchas

- **`ablog_website = "_website"`** in `conf.py` is only used by `ablog build` locally, not by `sphinx-build` which is what RTD runs. No changes needed.
- **`build.commands` would ignore the `sphinx` key entirely** — that's why we use `build.jobs` instead.
- Each command in `build.jobs` runs in a **fresh shell**, so env vars set in one command don't carry over to the next.

## References

- [RTD Config File v2 Reference](https://docs.readthedocs.com/platform/stable/config-file/v2.html)
- [RTD Build Customization](https://docs.readthedocs.com/platform/stable/build-customization.html)
- [RTD Environment Variables](https://docs.readthedocs.com/platform/stable/reference/environment-variables.html)
- [Override Build Process with build.jobs (Jan 2025)](https://about.readthedocs.com/blog/2025/01/override-build-process-with-build-jobs/)
