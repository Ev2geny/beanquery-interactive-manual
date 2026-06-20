---
name: update-beanquery-version
description: Update the project to the latest beanquery commit from GitHub. Use when the user asks to bump, upgrade, or refresh the beanquery version/commit. Updates the venv, pyproject.toml, the manual.py inline-script block, and the commit reference in section 1.1 of the manual.
---

# Update beanquery version

This project pins beanquery to a specific GitHub commit (the upstream repo ships
features ahead of its PyPI releases). The pinned commit appears in **four** places
that must all stay in sync:

1. The installed package in the virtual environment (`.venv`)
2. `pyproject.toml` — `dependencies` list
3. `manual.py` — the `# /// script` inline-metadata block at the top
4. `manual.py` — section 1.1, the sentence starting
   "Specifically the following beanquery commit was used"

The upstream repo is `https://github.com/beancount/beanquery.git` (default branch
`master`).

## Steps

### 1. Update the virtual environment to the latest beanquery

First make the dependency in `pyproject.toml` and `manual.py` point at the
unpinned branch tip so uv fetches the newest commit. In **both** files replace the
existing `beanquery @ git+...` line with the unpinned form:

```
beanquery @ git+https://github.com/beancount/beanquery.git
```

Then resolve and install:

```bash
uv sync
```

Read the `uv sync` output to capture the **full 40-character commit SHA** it
installed and the version string, e.g.:

```
Installed 1 package ... beanquery==0.3.0.dev0 (from git+...@62b6abba7f560e2d5e1dce231b55571b84fdf31f)
```

Record both the full SHA (for pinning) and the short 7-char prefix (for display).
If `uv sync` reports no change, beanquery is already at the latest commit — tell
the user and stop.

### 2. Pin pyproject.toml to the installed commit

In `pyproject.toml`, change the `beanquery` dependency to pin the exact SHA:

```
"beanquery @ git+https://github.com/beancount/beanquery.git@<FULL_SHA>",
```

### 3. Pin the manual.py inline-script block

In `manual.py`, the `# /// script` block near the top mirrors the dependency.
Pin it to the same SHA:

```
#     "beanquery @ git+https://github.com/beancount/beanquery.git@<FULL_SHA>",
```

### 4. Update the commit reference in section 1.1

Find the sentence in `manual.py` (around the section 1.1 markdown cell) that starts
with "Specifically the following beanquery commit was used" and update it to cite
the new commit as a markdown link to the GitHub commit page, with the version in
parentheses:

```
Specifically the following beanquery commit was used: [`<SHORT_SHA>`](https://github.com/beancount/beanquery/commit/<FULL_SHA>) (version <VERSION>).
```

Use the 7-char short SHA as the link text and the full SHA in the URL.

### 5. Re-lock and verify

Run `uv lock` to align `uv.lock` with the pinned commit, then confirm the lock
entry shows the new `?rev=<FULL_SHA>`:

```bash
uv lock
```

After updating, point out to the user that `docs/index.html` (the published static
output) has **not** been regenerated, and that a beanquery version bump can change
query rendering — recommend running the notebook and re-exporting before committing:

```bash
uv run marimo export html manual.py -o docs/index.html
```

## Notes

- Keep the SHA identical across all four locations. A mismatch between the
  inline-script block and `pyproject.toml` leads to different environments
  depending on how the notebook is launched.
- The short SHA is purely cosmetic (link text / display); the full SHA is what
  pins the dependency and lockfile.
