# Setup - what Alex does himself

Everything below is a GitHub-side step. Nothing in this folder is public until step 1.
Never paste the token anywhere except the GitHub secrets page.

## 1. Create the profile repo - done 17 Nov 2026

The repo exists at https://github.com/AlexjComeau/AlexjComeau and the Snake workflow has run (branch `output`). Steps 2 to 4 are what remain, for the Metrics workflow only.

1. Open https://github.com/new
2. Repository name: `AlexjComeau` (must match the username exactly - that is what makes it a profile README).
3. Visibility: **Public**. Leave "Add a README" unchecked (this folder already has one).
4. Create, then push this folder:

```bash
cd ~/lovable/personal/github-profile
git remote add origin https://github.com/AlexjComeau/AlexjComeau.git
git push -u origin main
```

The README shows on https://github.com/AlexjComeau right away. The stats images stay broken until step 4 runs.

## 2. Create the token

1. GitHub, top right avatar, **Settings**, then **Developer settings** (bottom of the left menu).
2. **Personal access tokens**, then **Tokens (classic)**, then **Generate new token (classic)**.
3. Note: `metrics-profile`. Expiration: 1 year is fine (set a reminder).
4. Type matters: it must be a **classic** token. Fine-grained tokens are rejected by the action.
5. Scopes - pick one of the two:
   - **`public_repo` + `read:user`** (the minimum). Your public graph already shows all 9,803 contributions because "Include private contributions on my profile" is on, so the calendar, the commit count and the snake look full either way. Languages, lines and the habits charts will only see the 4 public repos.
   - **`repo` + `read:user`** (recommended for this profile). Lets the action read languages and lines across private repos and use private pushes for the habits charts. The workflow is configured so no private repo name is printed - only aggregate numbers and percentages.
6. Generate, copy the token once. It is shown only once.

## 3. Add the secret

1. Open https://github.com/AlexjComeau/AlexjComeau/settings/secrets/actions
2. **New repository secret**. Name: `METRICS_TOKEN`. Value: the token from step 2.

## 4. Run the workflows once

1. Open https://github.com/AlexjComeau/AlexjComeau/actions
2. Click **Metrics** in the left list, then **Run workflow** (keep branch `main`), then the green **Run workflow** button.
3. Snake already ran; it re-runs daily on its own.
4. Metrics takes about 3 to 8 minutes (four SVG renders; the languages step clones your repos). Snake takes about a minute.
5. Reload https://github.com/AlexjComeau. Hard-refresh once if an image is stale; GitHub caches images through its proxy for a few minutes.

After that both run daily on their own (Metrics 06:17 UTC, Snake 06:41 UTC) and on any manual run.

## Things that can bite

- **Scheduled workflows pause after 60 days without repo activity.** GitHub emails a warning first. Any push to the repo, or a manual run, re-enables them.
- **First Snake run.** The `output` branch does not exist until the Snake workflow has run once, so the snake image 404s before that. Same for the four `metrics-*.svg` files before the first Metrics run.
- **Token expiry.** When the classic token expires the Metrics run fails with a 401 in the Actions log. Make a new token and update the `METRICS_TOKEN` secret.
- **Rate limits.** The languages indepth step is the slow one. If a run times out, lower `plugin_languages_analysis_timeout` in `.github/workflows/metrics.yml` or drop `plugin_languages_indepth`.
- **Why the fork.** The workflow uses `gh-metrics/metrics@master`, the maintenance fork of `lowlighter/metrics`. Upstream has no commits since Dec 2023, and its achievements plugin fails on today's GitHub API. If the fork ever breaks, switch `uses:` back to `lowlighter/metrics@latest` and remove the three `plugin_achievements*` lines from each step.

## Change the look later

- `assets/header-light.svg` and `assets/header-dark.svg` - the animated banner. Hand-written SVG, edit the text in place.
- `.github/workflows/metrics.yml` - which plugins show in each column. Options are documented at https://github.com/gh-metrics/metrics (plugin READMEs under `source/plugins/`).
- `README.md` - the "What I build" cards and links.
- Preview locally before pushing: `python3 preview/render.py --serve` then open http://127.0.0.1:8787/preview/dark.html and `/preview/light.html`.

## Why these choices (research, 16 Nov 2026)

- **`gh-metrics/metrics@master`, not `lowlighter/metrics@latest`.** Upstream: last release v3.34 (Sep 2023), last commit Dec 2023, achievements plugin broken by the Projects (classic) sunset (lowlighter/metrics#1706, #1834), habits/activity crash on new event payloads. The fork: commits through Oct 2026, achievements migrated to Projects v2 (Mar + Jun 2026), habits and activity fixed, private-repo languages fix (#1579) included, prebuilt image `ghcr.io/gh-metrics/metrics:master` verified reachable.
- **Classic PAT only.** The action rejects fine-grained tokens (`source/app/action/index.mjs`) and `GITHUB_TOKEN` (no scope header). Checked in both upstream and fork.
- **Two SVGs per column, not one auto-dark SVG.** Neither the classic template nor the action has a theme option; `extras_css` with `!important` is the documented way to restyle. So: one light render, one dark render, swapped with `<picture>`, which GitHub documents (`data/reusables/getting-started/picture-element-example.md`). The `#gh-dark-mode-only` suffix still works but is undocumented since 2022.
- **Snake on branch `output`.** Platane/snk v3.5.0 (Apr 2026). Files on `raw.githubusercontent.com` are served with `max-age=300` and skip GitHub's camo proxy, so daily regenerations show within minutes. The metrics SVGs are committed to `main` for the same reason.
- **No github-readme-stats, streak or view-counter cards.** The public github-readme-stats instance returned 503 `DEPLOYMENT_PAUSED` on 16 Nov 2026 and both its author and DenverCoder1 now point people to Actions-based self-rendering. Glitch counters are gone (410). Everything on this profile is rendered by an Action and committed.
- **No badges, no skill icons.** The profiles that look designed in 2026 (adamalston, Platane, orhun, simonw) ship one or two owned SVGs plus self-updating data, not a shield wall. Inline `style=` is stripped by GitHub's sanitiser, so layout is `<table>`, `align` and `width` only.
- **Skipped on purpose.** `plugin_stars` (two of the six starred repos are work repos), `plugin_notable` (would print the employer org), `plugin_activity` and `plugin_lines_sections: repositories` (would print private repo names), WakaTime and Spotify (no accounts), the full-year 3D calendar (half-year fits the column; switch `plugin_isocalendar_duration` to `full-year` if wanted).
