# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An interactive tutorial/manual for [beanquery](https://github.com/beancount/beanquery) — a SQL-like query tool for Beancount ledger data — implemented as a single [marimo](https://marimo.io/) notebook. The compiled static HTML is published to GitHub Pages.

## Commands

```bash
# Run as interactive read-only notebook
uv run marimo run manual.py

# Run in editable (development) mode
uv run marimo edit manual.py

# Compile to static HTML (published output)
uv run marimo export html manual.py -o docs/index.html
```

There is no automated test suite. Validation is done by running the notebook and verifying live query outputs render correctly.

## Architecture

**`manual.py`** is the entire application (~3200 lines). It is a marimo notebook where each section is one or more `@app.cell`-decorated functions. The file ends with `if __name__ == "__main__": app.run()`.

Key helper functions defined near the top of `manual.py`:
- `get_beanquery_output(ledger_text, query, narrow)` — runs a beanquery query against an in-memory ledger string and returns formatted text output
- `query_output(ledger_text, query, narrow)` — wraps the above in a marimo UI element
- `ledger_editor(default_text, label)` — marimo widget for an editable Beancount ledger
- `query_editor(default_text, label)` — marimo SQL code editor widget

The interactive cells wire together `ledger_editor` + `query_editor` outputs into `query_output`, so edits to the ledger or query automatically re-run and display results.

**`custom.css`** provides notebook styling (blue headings, compact margins) and is referenced in the marimo app config.

**`docs/index.html`** is the compiled static output — regenerate it with the export command above before committing changes intended for GitHub Pages.

## Branching

- `develop` — active development
- `main` — stable/published releases; PRs merge here
