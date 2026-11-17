# Setup - what Alex does himself

Everything below is a GitHub-side step. Nothing in this folder is public until step 1.
Never paste the token anywhere except the GitHub secrets page.

## 1. Create the profile repo

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
4. Scopes - pick one of the two:
   - **`public_repo` + `read:user`** (the minimum). Stats count public work only. Your public graph already shows all 9,803 contributions because "Include private contributions" is on, so the calendar and the snake look full either way. Activity, languages, habits and lines will only see the 4 public repos.
   - **`repo` + `read:user`** (recommended for this profile). Lets the action count the ~9,100 private commits in Activity, read languages and lines across private repos, and use private pushes for the habits charts. The workflow is configured so no private repo name is printed - only aggregate numbers and percentages.
5. Generate, copy the token once. It is shown only once.

## 3. Add the secret

1. Open https://github.com/AlexjComeau/AlexjComeau/settings/secrets/actions
2. **New repository secret**. Name: `METRICS_TOKEN`. Value: the token from step 2.

## 4. Run the workflows once

1. Open https://github.com/AlexjComeau/AlexjComeau/actions
2. Click **Metrics** in the left list, then **Run workflow** (keep branch `main`), then the green **Run workflow** button.
3. Do the same for **Snake**.
4. Metrics takes about 3 to 8 minutes (four SVG renders; the languages step clones your repos). Snake takes about a minute.
5. Reload https://github.com/AlexjComeau. Hard-refresh once if an image is stale; GitHub caches images through its proxy for a few minutes.

After that both run daily on their own (Metrics 06:17 UTC, Snake 06:41 UTC) and on any manual run.

## Things that can bite

- **Scheduled workflows pause after 60 days without repo activity.** GitHub emails a warning first. Any push to the repo, or a manual run, re-enables them.
- **First Snake run.** The `output` branch does not exist until the Snake workflow has run once, so the snake image 404s before that. Same for the four `metrics-*.svg` files before the first Metrics run.
- **Token expiry.** When the classic token expires the Metrics run fails with a 401 in the Actions log. Make a new token and update the `METRICS_TOKEN` secret.
- **Rate limits.** The languages indepth step is the slow one. If a run times out, lower `plugin_languages_analysis_timeout` in `.github/workflows/metrics.yml` or drop `plugin_languages_indepth`.

## Change the look later

- `assets/header-light.svg` and `assets/header-dark.svg` - the animated banner. Hand-written SVG, edit the text in place.
- `.github/workflows/metrics.yml` - which plugins show in each column. Options are documented at https://github.com/lowlighter/metrics (plugin READMEs under `source/plugins/`).
- `README.md` - the "What I build" cards and links.
- Preview locally before pushing: `python3 preview/render.py --serve` then open http://127.0.0.1:8787/preview/dark.html and `/preview/light.html`.
