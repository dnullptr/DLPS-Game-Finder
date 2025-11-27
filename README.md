# DLPS Game FW Finder

Small command-line utility (dlps.py)
 to locate, identify and optionally verify firmware/game files for DLPS-based projects.

## Features
- Scan a directory (or single file) for firmware/game files related to DLPS.
- Identify candidate files by filename patterns and binary headers.
- Optional checksum verification (MD5/SHA1/SHA256).
- Export results as JSON or CSV.
- Optional recursive scanning and simple metadata extraction (size, timestamps, hashes).
- Optional remote lookups against the DLPS website to determine which console firmware versions each game supports, including known backports to lower firmware versions.

## DLPS site and compatibility
This project can (optionally) query the publicly-available DLPS site (a community-uploaded game dump repository) to find metadata about uploaded images, including the range of console firmware versions that a given dump is known to work with. The script can detect when a game has been backported to earlier firmware and will surface that information.

For privacy and compliance:
- Remote lookups are optional and require the `requests` package.
- The tool should be used responsibly and in accordance with the DLPS site's terms of service and robots.txt.

You can also tell the script your console firmware version so it can report compatibility specific to your device (see options below).

## Requirements
- **Python:** 3.8 or newer.
- **Runtime packages:** listed in `requirements.txt` (recommended install via `pip install -r requirements.txt`). The script depends on these packages:
    - `selenium` (>=4.8.0)
    - `undetected-chromedriver` (>=3.2.0)
    - `webdriver-manager` (>=3.8.6)
    - `fake-useragent` (>=0.1.11)
    - `requests` (>=2.28.0) — optional; used only if you extend the script to perform remote lookups.
- **Browser:** Google Chrome must be installed on the system. `webdriver-manager` / `undetected-chromedriver` will automatically manage the matching driver.

Installation (PowerShell):
```
python -m venv .venv
; .\.venv\Scripts\Activate.ps1
; pip install -r requirements.txt
```

Notes:
- The script uses a headless Chrome instance by default. If you encounter problems, try running without `--headless` (edit `dlps.py` options) to see the browser during scraping.
- Keep the packages up-to-date if the target site changes frequently; `undetected-chromedriver` and `selenium` can be sensitive to Chrome version mismatches.

## Installation
Place `dlps.py` in a directory on your PATH or run it directly:
```
python dlps.py [options]
```

## Usage
This repository contains `dlps.py`, a small scraper that visits the DLPS category page (by default `https://dlpsgame.com/category/ps5`), extracts the "Working"/compatibility text from posts, and — if provided a firmware version — records entries compatible with that firmware.

Running the script
- Run without arguments to perform a full scrape and print progress to stdout:
```
python dlps.py
```
- Optionally provide a firmware version as the first argument (simple positional argument). When provided, the script will test compatibility against the supplied firmware major version and append compatible game titles and versions to `dlps_compatible.txt`:
```
python dlps.py 6.xx
```

What the script does
- Visits each page in the configured category (`CATEGORY_URL` in `dlps.py`).
- Extracts post links and looks for a spoiler/compatibility span (configured by `SPOILER_SELECTOR`).
- Searches the extracted text for a "Working" range and optional "Backport" info.
- If a firmware argument was provided and a compatible version is found, appends `"<title>: <versions>"` to `dlps_compatible.txt` and prints a compatibility notice.


Output files
- `dlps_compatible.txt`: appended lines of compatible entries when a firmware argument is supplied.

## Exit codes
- 0: Success (no issues)
- 1: General error (invalid args, IO error)
- 2: No candidates found (scan completed)

## Contributing
PRs and issues welcome. Keep changes minimal and test with Python 3.8+.

