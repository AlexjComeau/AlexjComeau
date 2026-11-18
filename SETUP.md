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
4. Metrics takes about 15 to 20 minutes; the languages step clones every repo. Snake takes about a minute.
5. Reload https://github.com/AlexjComeau. Hard-refresh once if an image is stale; GitHub caches images through its proxy for a few minutes.

After that both run daily on their own (Metrics 06:17 UTC, Snake 06:41 UTC) and on any manual run.

## Things that can bite

- **Scheduled runs are best effort.** None of the first night's slots fired (18 Nov 2026), with nothing misconfigured. Each workflow now has two slots a day, about 06:00 and 15:00 UTC, so one dropped run does not cost a day. If the page looks stale, run the workflow by hand from the Actions tab.
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
- **Two SVGs per column, not one auto-dark SVG.** Neither the classic template nor the action has a theme option. Each column is rendered once (the languages clone takes ~15 min), then the dark file is derived by injecting three `!important` colour rules into the SVG's `<style>`, and the pair is swapped with `<picture>`, which GitHub documents (`data/reusables/getting-started/picture-element-example.md`). The `#gh-dark-mode-only` suffix still works but is undocumented since 2022.
- **Snake on branch `output`.** Platane/snk v3.5.0 (Apr 2026). Files on `raw.githubusercontent.com` are served with `max-age=300` and skip GitHub's camo proxy, so daily regenerations show within minutes. The metrics SVGs are committed to `main` for the same reason.
- **No github-readme-stats, streak or view-counter cards.** The public github-readme-stats instance returned 503 `DEPLOYMENT_PAUSED` on 16 Nov 2026 and both its author and DenverCoder1 now point people to Actions-based self-rendering. Glitch counters are gone (410). Everything on this profile is rendered by an Action and committed.
- **No badges, no skill icons.** The profiles that look designed in 2026 (adamalston, Platane, orhun, simonw) ship one or two owned SVGs plus self-updating data, not a shield wall. Inline `style=` is stripped by GitHub's sanitiser, so layout is `<table>`, `align` and `width` only.
- **Skipped on purpose.** `plugin_stars` (two of the six starred repos are work repos), `plugin_notable` (would print the employer org), `plugin_activity` and `plugin_lines_sections: repositories` (would print private repo names), WakaTime and Spotify (no accounts).
- **Own skyline instead of the metrics calendar.** The metrics full-year calendar renders 480 by 310, so at full README width every label scales about 1.8 times. `assets/make_skyline.py` draws the year from the public contribution calendar at the right size, in both themes, in about 15 seconds.
- **Language scan capped at 40 minutes, not 15.** At 15 the scan sometimes stopped early and printed "partial results are displayed" onto the stats image.

## Added 18 Nov 2026

- **Skyline** (`.github/workflows/skyline.yml`, daily 06:05 UTC). `SKYLINE_WEEKS` in that file sets the window. It is `34`, which started at the first busy month when it was set (18 Nov 2026); `53` is the full year. Redraw by hand: `GH_TOKEN=$(gh auth token) python3 assets/make_skyline.py`.
- **Launch film teaser** (`assets/launch-film.gif`, 10 s, 3.7 MB). Two segments of the public launch cut, joined with ffmpeg: 0.3 to 3.3 s and 10.5 to 17.3 s, 848 px wide, 15 fps. It links to the film on YouTube.
- **Card images** (`assets/card-rou.jpg`, `assets/card-modmyclaude.png`). Each product site's own share image, trimmed to 2:1.
- **Share image** (`assets/social-preview.png`, 1280 by 640). Yours to upload, there is no API for it: https://github.com/AlexjComeau/AlexjComeau/settings then "Social preview", "Edit", "Upload an image". Regenerate with `python3 assets/make_header.py --stills` and a 1280 by 640 screenshot of `preview/social-preview.svg`.
- **Social links.** Also yours: https://github.com/settings/profile then "Social accounts". Up to four links.
- **Banner timeline.** Edit `TIMELINE` in `assets/make_header.py` (year, text), then run it. `PER` is seconds per entry; `SEED` changes the shuffle.


## Added 18 Nov 2026 (2): phone layout and two more cards

- **Phone layout.** On a phone GitHub shows the README about 293 px wide, so the banner's year line landed near 4.6 px and the stats near 3.5 px. Fixed without any GitHub feature that could change under us:
  - **Banner and skyline** carry a second layout inside the same file. An SVG's media queries see the size the image is drawn at, so under 560 px the big type shows and the small type hides. `LAYOUT` and `NARROW_BELOW` in `assets/make_header.py`, `NARROW_BELOW` in `assets/make_skyline.py`.
  - **Stats columns** are two images in a centred paragraph at `width="400"`, not a table. Two fit side by side from about a 1,240 px window up; below that they stack, and on a phone each fills the width.
  - **Card grid** stays a table (text cannot wrap around itself any other way here). The repo link has a zero-width space after the slash so the two columns stay close to even; GitHub strips `<wbr>`.
  - When testing sizes locally, give each test image its own URL (`?v=1`). A browser shares one copy of an SVG across every `<img>` with the same URL, and they all get the same layout.
- **Video and AI search cards** (`assets/card-video.svg`, `assets/card-search.svg`, from `python3 assets/make_cards.py`). Animated, dark only like the two site cards, a 10 s loop. They show how each system works and carry no figures; the pattern of green dots on the search card is drawn, not data. Labels hide under 240 px, where they would be specks.
- **Resting state.** The cards and the banner are drawn finished and the animation starts from nothing, so anything that shows the file without running it (a link preview, a still capture) gets the full picture and not an empty frame.
