# paper/

HTML summaries of Qiao Jin's papers. Each paper keeps its existing filename and URL. PDFs, cover PNGs and figures remain in `assets/papers/`, `assets/covers/` and `assets/figures/`.

`index.html` lists all paper pages alphabetically in compact single-line rows, with short names, venues and links to the HTML summary and PDF. Full titles appear on hover; venues are hidden on narrow screens to keep each paper on one line. Like `bio/`, the directory is marked `noindex`.

Run `python3 paper/build.py` after adding a paper or editing its title, venue or asset links. The script reads the existing paper pages and uses `bio/index.html` as the visual template. Edit the paper pages, not the generated index; optional short names are in `DISPLAY_NAMES` in `build.py`.

Before publishing, run `python3 tools/audit-decks.py` and check the directory's HTML and PDF links. Include the regenerated index and all referenced assets in the commit.
