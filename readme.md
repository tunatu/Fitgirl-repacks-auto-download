# FitGirl Scraper

A simple desktop app that scrapes download links from FitGirl Repacks and downloads them automatically — no more clicking through ads or copy-pasting links one by one.

---

## Download

Go to the [Releases](../../releases) page and download the latest `FitGirl.Scraper.exe`. No installation required — just run it.

---

## How to Use

1. **Open the app** by double-clicking `FitGirl.Scraper.exe`

2. **Paste a FitGirl Repacks link** into the text box at the top
   - Example: `https://fitgirl-repacks.site/ready-or-not/`

3. **Click "Scrape Links"** — the app will find all the download links on the page

4. **Pick a mirror** from the dropdown — the app supports both Datanodes and FuckingFast mirrors. Either works, pick whichever you prefer.

5. **Uncheck any files you don't want** — all files are checked by default. Uncheck any parts you don't need.

6. **Choose where to save** — click Browse to pick a folder. Defaults to your Downloads folder.

7. **Click "Download Selected"** — files will download one at a time. Progress is shown at the bottom.

---

## Requirements

If you're running the `.exe` — **nothing**. It's standalone.

If you want to run from source (for developers):

```bash
pip install requests beautifulsoup4 ttkbootstrap
python scraper.py
```

---

## Troubleshooting

**The app opens and immediately closes**
Right-click the exe and select "Run as administrator", or move it out of a protected folder like Desktop or Program Files.

**"Could not find any download sections"**
Make sure you're pasting a link to an actual game page on fitgirl-repacks.site, not the homepage.

**Download fails or gets stuck**
The file host may be temporarily down. Try switching to the other mirror in the dropdown and downloading again.

**My antivirus flagged the exe**
This is a false positive — PyInstaller-built executables commonly trigger antivirus heuristics because of how they're packaged. The source code is fully available in this repo for you to inspect. You can also run it directly from source if you prefer.

---

## Disclaimer

This tool is for personal use only. It does not bypass any paywalls or DRM. It simply automates clicking download links that are freely available on the page. Make sure you own the games you download.

---

## License

MIT — do whatever you want with it.