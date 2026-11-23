# AGENTS.md — mochapulse

## What this repo IS

A GitHub special repository (profile README). The `README.md` renders on the GitHub profile page. `python today.py` queries the GitHub GraphQL API and generates `dark_mode.svg` / `light_mode.svg` embedded in the README.

## Key files

- **`today.py`** — thin entry-point shim at the repo root. Only calls `mochapulse.build.run()`. Kept so `python today.py` still works for CI and the README. No venv, no pyproject.toml, no poetry.
- **`mochapulse/`** — the Python package with all logic. Modules: `config.py` (env/token, paths, color themes), `metrics.py` (API-call counter + timing), `github_api.py` (stateless GraphQL fetchers), `loc_cache.py` (LOC/commit fetching + on-disk cache), `age.py` (uptime string), `svg_card.py` (XML escaping, ASCII load, SVG build + stats injection), `build.py` (`run()` orchestrator).
- **`mochapulse-ascii-art.txt`** — INPUT file read by `svg_card.load_ascii_art()` to render ASCII art into the SVGs. Editable. Changes appear in both SVG outputs.
- **`dark_mode.svg` / `light_mode.svg`** — BUILT artifacts, never edit directly. Generated entirely by `svg_card.build_svg_document()` (no template files); the right-panel info rows live in `svg_card._info_entries()` — all text there is XML-escaped at render, so write `&`/`<`/`>` literally. SVGs are committed and referenced by the README via `raw.githubusercontent.com`.
- **`cache/requirements.txt`** — the only dependency declaration. Three deps: `requests`, `python-dateutil`, `lxml`.
- **`cache/<sha256>.txt`** — runtime GitHub API cache (SHA256 of USER_NAME). Gets committed by CI. Has a fixed-format comment header (7 lines). Do not delete, reformat, or change the comment header.
- **`cache/repository_archive.txt`** — manual cache for archived/deleted repos. Also has a fixed comment header. Editable manually to preserve stats for repos no longer on GitHub.
- **`.github/workflows/build.yaml`** — triggers on push to `main` + daily cron (4am UTC). Self-commits generated SVGs via `mochapulse-bot` (email: `actions@mochapulse.github.io`). Uses `git pull --rebase --autostash` before commit.
- **`.gitmodules`** — git submodule at `.agents/skills/ascii-art` pointing to `https://github.com/neethanwu/ascii-art.git`.

## How to run

```sh
pip install -r cache/requirements.txt
export ACCESS_TOKEN="ghp_..." USER_NAME="mochapulse"
python today.py
```

Without ACCESS_TOKEN, the script skips API queries and generates SVGs with placeholder zeros.

## Node.js project (SDD tooling)

The `.opencode/` directory is a separate Node.js project (`package.json`, `package-lock.json`, `node_modules/`). Dependencies: `@opencode-ai/plugin`. Leave `node_modules/` and `package-lock.json` alone unless explicitly asked.

## Conventions

- No tests, no linter, no formatter configured.
- OpenSpec SDD workflow enabled (`.opencode/skills/`, `openspec/config.yaml`).
- OpenSpec commands live under `.opencode/commands/` (`opsx-apply`, `opsx-propose`, etc.).
