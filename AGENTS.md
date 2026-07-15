# AGENTS.md — mochapulse

## What this repo IS

A GitHub special repository (profile README). The `README.md` renders on the GitHub profile page. `today.py` queries the GitHub GraphQL API and generates `dark_mode.svg` / `light_mode.svg` embedded in the README.

## Key files

- **`today.py`** — single-file Python script. No venv, no pyproject.toml, no poetry. The entire codebase.
- **`mochapulse-ascii-art.txt`** — INPUT file read by `today.py` to render ASCII art into the SVGs. Editable. Changes appear in both SVG outputs.
- **`dark_mode.svg` / `light_mode.svg`** — BUILT artifacts, never edit directly. Generated entirely by `_build_svg()` in `today.py` (no template files). SVGs are committed and referenced by the README via `raw.githubusercontent.com`.
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
