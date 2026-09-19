# Animated GitHub profile — setup

## 1. Upload the complete profile

Extract the ZIP. In the public repository `mahidrahman375/mahidrahman375`, upload these at the repository root:

- `README.md`
- `assets/` (all images, including both snake SVG files)
- `scripts/` (both Python scripts)
- `.github/workflows/profile-animation.yml`

The header, cycling role text, pulsing network dots, moving dividers, toolkit accents, footer and snake all use local animated SVG files. They display without a badge or animation-hosting service. Your portrait remains the original photograph.

Do not upload the ZIP itself or nest its contents inside an extra folder. Copying only README.md will not upload the images.

The `.github` folder may be hidden on your computer. If you do not see it, use GitHub's **Add file → Create new file**, enter `.github/workflows/profile-animation.yml`, and paste the supplied YAML. Upload both scripts and all assets as well.

## 2. Run the snake workflow once

Open your repository's **Actions** tab. Enable workflows if GitHub asks. Select **Update profile animations → Run workflow** on your default branch.

The workflow generates a snake from your contribution graph, refreshes the public statistics and commits the SVG files into `assets/` on the default branch. After that, it runs daily at 03:23 UTC. GitHub may delay scheduled runs.

The normal repository-provided `GITHUB_TOKEN` is used; no personal token is required. The workflow requests `contents: write`. If repository or organisation policy blocks that permission, or branch protection blocks bot commits, the commit step will fail; adjust the relevant repository policy or use a branch-based publishing workflow. No workflow has been installed or run in your GitHub account by this delivery.

## 3. Preview

Open `PREVIEW.html` from the extracted folder in a browser. It includes GitHub-rendered Markdown with an approximate local dark stylesheet. Actual GitHub spacing can differ. All animation is inside SVG image files: there is no JavaScript or unsupported CSS embedded in README.md.

Animations include reduced-motion handling where provided by the artwork; browser settings can affect playback. An image viewer may show only a still frame. Use a web browser to view motion.

## What the initial snake shows

The included snake was fetched from your existing repository's `gh-pages/github-contribution-grid-snake.svg` and recoloured to match the profile. Its original generation date is unknown. It is an existing contribution snapshot, not an invented graph. The first workflow run replaces it with newly generated light and dark snake SVGs.

## Edit or rebuild

- Text and links: `README.md`
- Animated visuals: `scripts/build_animations.py`
- Base badge artwork and public statistics: `scripts/build_assets.py`
- Snake colours and refresh schedule: `.github/workflows/profile-animation.yml`

To rebuild locally with Python 3:

```bash
python3 scripts/build_assets.py
python3 scripts/build_animations.py
```

The first script fetches public GitHub information. The second requires no internet access. The contribution snake is refreshed by the GitHub Actions workflow, not by these Python commands.

Official snake generator documentation: https://github.com/Platane/snk
Official profile setup: https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
