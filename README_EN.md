# MuseDigest

> 中文版（主）：[README.md](README.md)

Automatically collect the latest **photography / design / creative-industry** news, compile
**categorized image albums**, and analyze each image from **design & aesthetic** perspectives —
presented as a self-contained **interactive HTML gallery** (the UI is primarily in Chinese).

Built as a companion to the [ArtiMuse](../README.md) image-aesthetics model: the analysis uses
ArtiMuse's exact 8 expert dimensions (Composition & Design, Visual Elements & Structure, Technical
Execution, Originality & Creativity, Theme & Communication, Emotion & Viewer Response, Overall
Gestalt, Comprehensive Evaluation).

```
collect (RSS) → extract (images) → download (thumbnails) → categorize (genre)
              → analyze (aesthetic) → interactive gallery
```

## One-click (easiest, Windows)

In the `muse-digest/` folder, **double-click**:

- **`menu.bat`** — a Chinese menu: 1 collect / 2 ArtiMuse online / 3 login / 4 self-test /
  5 import local photos / 6 open last gallery / 7 clear.
- **`start.bat`** — zero setup: collect → build gallery → open browser (heuristic, no GPU/login).
- **`start-artimuse.bat`** — real scoring: opens system Edge for you to log in, then analyzes and
  opens a gallery with radar charts.
- **`import-photos.bat`** — **drag your own images/folder onto it** to analyze your own photos.

A console window shows progress (in Chinese); the browser opens when done. Append args like
`start.bat --limit 20`.

**Put them on the Desktop:** double-click **`make-shortcuts.bat`** to create three desktop
shortcuts. (The PowerShell menu is `start-menu.ps1`, launched by `menu.bat` with
`-ExecutionPolicy Bypass` so it runs even under restricted policy.)

## Quick start (command line)

```bash
# from the muse-digest/ folder, using the repo's .venv
pip install -r requirements.txt
python run.py --limit 12 --backend heuristic --open
```

This collects from the feeds in `config.yaml`, builds an album, and opens
`data/gallery/index.html`. The **heuristic** backend runs no vision model — it produces
genre-aware study prompts across the 8 dimensions (no fabricated score).

## Interactive gallery features

The generated `data/gallery/index.html` is a self-contained, offline app:

- **Overview stats** — image / category / source counts, average score, and a colored category-mix bar.
- **Album grid** — masonry layout with a per-image **score ring** and genre tag overlay.
- **Filter & sort** — category chips, a source dropdown, and sort by score / source.
- **Detail drawer** — full critique with a **radar chart** of the 8 aesthetic dimensions
  (lights up when a backend supplies per-dimension scores), per-dimension score chips, the
  "creative inspiration" takeaway, and **← / →** navigation between images.
- **Lightbox** — click the drawer image to view it large; arrow-key navigation.

## Import your own photos

Besides crawling the web, you can **import local images** for analysis (heuristic gives
per-image pixel analysis; ArtiMuse gives real aesthetic scores):

- Drag images/a folder onto **`import-photos.bat`**, or menu option **5**, or:
  ```bash
  python run.py --import "D:\photos"                  # a folder (recursive)
  python run.py --import a.jpg b.jpg --category Portrait
  python run.py --import "D:\photos" --backend artimuse_browser
  ```
  Supports jpg/png/webp/bmp/tiff/gif; content-deduplicated; source = "本地导入".

## Library management

The gallery is a **persistent, growing library**: every crawl/import is merged into
`data/library.json` (deduplicated by id) and the page shows the whole library. Manage it with the
category chips, source dropdown, and sort.

| Command / menu | Effect |
|---|---|
| `python run.py --rebuild` | Rebuild & open the page from the existing library, no re-analysis (menu 6). |
| `python run.py --fresh` | Clear the library, then run. |
| `python run.py --clear` | Clear the whole library (json + thumbnails) and exit (menu 7). |

Everything lives under `data/`: `library.json`, `images/`, `gallery/index.html`. Delete `data/` to
fully reset.

## Analyzer backends

Selected via `--backend` or `analyzer.backend` in `config.yaml`:

| Backend | What it does | Needs |
|---|---|---|
| `heuristic` | Genre-aware Chinese study prompts from source text + image properties. Always works. | nothing |
| `artimuse_browser` | Drives the **official demo** (artimuse.intern-ai.org.cn) in a logged-in browser and scrapes the real score + 8-dimension analysis. | `playwright`, a one-time manual login |
| `artimuse_local` | Runs **InternVL3-8B** locally in 4-bit (flash-attn off). Reproducible, fully local. | parent repo's heavy deps, a downloaded checkpoint, a CUDA GPU |

On any per-image failure, the pipeline **falls back to `heuristic`** for that image so a run
always completes. Fallbacks are flagged in the gallery.

### `artimuse_browser` (the "online" path)
There is **no public ArtiMuse API** and **no Hugging Face Space**; the demo is SSO-gated, so the
only faithful online option is browser automation.

It drives the **preinstalled system Edge** (`channel: msedge` in `config.yaml`), so **no chromium
download is needed**.

```bash
pip install playwright              # browser is system Edge; no chromium download
python tools/artimuse_login.py      # log in to intern-ai.org.cn once, press Enter
python tools/artimuse_selftest.py   # verify: prints the scraped score + 8 dimensions
python run.py --backend artimuse_browser --limit 3 --open   # or double-click start-artimuse.bat
```

To use playwright's bundled chromium instead, leave `channel` empty and run
`python -m playwright install chromium`.

**Demo DOM facts (from a no-login probe):** the page has exactly one `input[type="file"]` (upload
works), **no `<button>` elements** (div/span clickables; likely auto-runs on upload), and renders in
**Chinese** ("总分", "构图与设计"...). So result headings are matched by Chinese labels first
(`_heading_candidates`), English as fallback, mapped back to the English keys.

**First-run debugging:** the post-login result-page layout is **not yet verified** (login is yours
to do). Run `artimuse_selftest.py` first — it prints the scraped score + per-dimension text/scores.
If a dimension is empty or a score is None, adjust `SELECTORS` / `_heading_candidates` /
`_SCORE_RE`/`_SCORE_CN_RE` in `muse_digest/analyze/artimuse_browser.py`. Any per-image failure
**falls back to the Chinese heuristic** (flagged in the gallery), so a run never breaks.

> ⚠️ This automates a third-party UI: **fragile** (markup can change), **rate-limited**, for **small
> personal study batches**.

### `artimuse_local` (4-bit local)
Heavyweight and **VRAM-tight** on a 6 GB laptop GPU (slow: 8 attribute passes per image).

1. Install the parent repo's deps (from the repo root): `pip install -r ../requirements.txt`
2. Download a checkpoint into `../checkpoints/ArtiMuse`
   (from https://huggingface.co/Thunderbolt215215/ArtiMuse).
3. Run: `python run.py --backend artimuse_local --limit 1 --open`

Config under `analyzer.artimuse_local` controls `model_path`, `device`, `load_in_4bit`,
`use_flash_attn`, `max_new_tokens`.

## Configuration

Everything is in [`config.yaml`](config.yaml): `feeds`, the genre `categories` taxonomy,
`collection`/`download` limits, and `analyzer` settings. CLI flags (`--backend`, `--limit`) override
the corresponding config values.

Chinese UI labels live in [`muse_digest/labels.py`](muse_digest/labels.py) (dimension/category maps);
internal keys stay English so ArtiMuse's English prompts and English-feed keyword matching keep
working.

## Output

```
data/
  images/                # downloaded study thumbnails
  results/results.json   # full structured results (provenance + analysis)
  gallery/index.html     # the interactive, offline-portable gallery
```

## Responsible use

MuseDigest honors `robots.txt`, rate-limits per host, downloads **reduced-size study thumbnails**
(not full-res), and shows every image **with attribution linking back to its source**. It does not
re-host media. Respect each source's terms; for anything beyond personal study, seek permission from
the rights holder.
