# Repair your existing GitHub profile

This archive matches the repository layout shown in your screenshot. It uses your existing animated portrait and contribution-snake workflows.

1. Extract the archive.
2. Open `mahidrahman375/mahidrahman375` at the repository root.
3. Choose **Add file → Upload files**.
4. Upload the extracted `README.md` file and the `Mahid_GitHub_Profile` folder together. GitHub should show `README.md` at the root and SVGs under `Mahid_GitHub_Profile/assets/`. Do not put README.md inside another folder.
5. Commit the changes. Open your GitHub profile.

Keep the existing `.github/workflows/dot-portrait.yml`, `.github/workflows/snake.yml`, `scripts/animate_dotify.py`, `assets/profile.png` and `assets/portrait-animation.gif`.

Do not install the previously supplied `profile-animation.yml`; your existing workflows already handle the portrait and snake. This repair adds no new workflow and does not change the existing ones.

The repaired root README uses:

- Animated portrait: `assets/portrait-animation.gif`
- Header, dividers, footer and toolkit: `Mahid_GitHub_Profile/assets/`
- Snake: `https://raw.githubusercontent.com/mahidrahman375/mahidrahman375/gh-pages/github-contribution-grid-snake.svg`

For a refreshed portrait, use **Actions → Generate Animated Dot Portrait → Run workflow**.
For a refreshed snake, use **Actions → Generate Snake → Run workflow**.

If you edit README.md by hand, paste its raw code into the editor, not copied text from its rendered preview. The previous root README had lost Markdown heading markers, table separators and links. Uploading the actual .md file preserves all formatting.

All existing assets and workflows remain in your GitHub repository. This is a repair package, so it intentionally does not include your existing portrait GIF, input photo or workflows. Repository writes have not been made for you.
