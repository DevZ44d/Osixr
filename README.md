<div align="center">

<img src="https://github.com/user-attachments/assets/ca710e96-a798-4267-a7a6-bc63b3a7e44e" width="400">

**A Python toolkit for OSINT (IP intelligence & image EXIF metadata extraction & Etc-Soon)**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![aiohttp](https://img.shields.io/badge/aiohttp-async-orange?style=flat-square)](https://docs.aiohttp.org/)
[![colorama](https://img.shields.io/badge/colorama-terminal%20colors-yellow?style=flat-square)](https://pypi.org/project/colorama/)

[![Downloads](https://img.shields.io/pepy/dt/Osixr?style=flat-square&label=Downloads&color=8A2BE2)](https://pypi.org/project/osixr/)
[![Telegram Channel](https://img.shields.io/badge/Telegram-Channel-red.svg?style=flat-square&logo=telegram)](https://t.me/PyCodz)
[![Telegram Discuss](https://img.shields.io/badge/Telegram-Discuss-blue?style=flat-square&logo=telegram)](https://t.me/PyCodz_Chat)
</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Modules](#-modules)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [IP Module](#1-iplock-module--ip-intelligence--vpn-detection)
  - [ExiF Module](#2-exif-module--photo-metadata-extraction)
  - [CLI](#3-cli--command-line-interface)
- [Project Structure](#-project-structure)

---

## 🔍 Overview
- **Osixr** is a modular Python library designed for OSINT information gathering. It ships with two powerful engines:

| Engine | Description |
|--------|-------------|
| 🌐 **IP** | Async IP geo-lookup, VPN/Proxy detection, and Google Maps link generation |
| 📷 **ExiF** | Deep EXIF metadata extraction from JPEG/TIFF images — camera, GPS, lens, capture settings |

- Both modules output styled, animated terminal reports using random ASCII art banners.

---

## 📦 Modules
```
osixr/
├── IP/          → Async IP intelligence & VPN/Proxy detection
├── Exif/        → JPEG/TIFF EXIF metadata parser
└── Banners/     → ASCII art banners + colored terminal output
```

---

## ⚙️ Installation
- Via PyPi:
```bash
$ python -m pip install --upgrade osixr
```

- Via Git:
```bash
$ python -m pip install git+https://github.com/DevZ44d/Osixr.git
```

---

## 🚀 Quick Start
```python
import asyncio
from osixr import IPlock, ExiF

# IP Intelligence
async def run():
    scanner = IPlock(ip="8.8.8.8", timeout=8) 
    # Get clean JSON output (without banner: False)
    result = await scanner.get(banner=False, void_firewall=False)
    print(result)

asyncio.run(run())

# EXIF Metadata
async def _demo():
    e = ExiF("WIN.jpg")
    print(e.print_all())             # print banner and full-information .
    print((e.to_dict(banner=False))) # banner: bool = False -> Skip ASCII banner .


if __name__ == "__main__":
    asyncio.run(_demo())
```

---

## 📘 Usage

### 1. IPlock Module — IP Intelligence & VPN Detection
- The `IPlock` class is the high-level interface for async IP analysis.  
- It queries geo-IP APIs, detects VPN/Proxy usage, and generates a Google Maps link from the IP coordinates.

#### Basic Usage
```python
import asyncio
from osixr import IPlock

async def main():
    scanner = IPlock(ip="8.8.8.8", timeout=8)
    result = await scanner.get(banner=False, void_firewall=False)
    print(result)

asyncio.run(main())
```

#### `IPlock.__init__(ip, timeout)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ip` | `str \| None` | — | Target IP address to analyze |
| `timeout` | `int \| None` | `10` | Request timeout in seconds |

---

#### `await IPlock.get()` → `str`
- Runs the full async IP analysis pipeline and returns a formatted terminal output string including a random ASCII art banner.

```python
scanner = IPlock("1.1.1.1")
output = await scanner.get()
# Returns: banner + JSON result with geo data, VPN flag, Google Maps link
```

**Sample output fields:**
```json
{
  "ip": "8.8.8.8",
  "success": true,
  "type": "IPv4",
  "continent": "North America",
  "continent_code": "NA",
  "country": "United States",
  "country_code": "US",
  "region": "California",
  "region_code": "CA",
  "city": "Mountain View",
  "latitude": 37.3860517,
  "longitude": -122.0838511,
  "is_eu": false,
  "postal": "94039",
  "calling_code": "1",
  "capital": "Washington D.C.",
  "borders": "CA,MX",
  "flag": {
    "img": "https://cdn.ipwhois.io/flags/us.svg",
    "emoji": "🇺🇸",
    "emoji_unicode": "U+1F1FA U+1F1F8"
  },
  "connection": {
    "asn": 15169,
    "org": "Google LLC",
    "isp": "Google LLC",
    "domain": "google.com"
  },
  "timezone": {
    "id": "America/Los_Angeles",
    "abbr": "PDT",
    "is_dst": true,
    "offset": -25200,
    "utc": "-07:00"
  },
  "Takes": "2.22 s",
  "VPN/PROXY": true,
  "GooGle Map": "https://www.google.com/maps?q=37.3860517,-122.0838511"
}
```

---

#### Low-level: `AsyncFetchDict` (direct access)
```python
import asyncio
from osixr.IP.utails import AsyncFetchDict

async def main():
    engine = AsyncFetchDict(ip="8.8.8.8", timeout=10)

    # Full formatted output (banner + JSON)
    #takes one arg : void_firewall: bool | None = False
    output = await engine.get_all()
    print(output)

    # Raw analysis dict only
    data = await engine.analyze()
    print(data)

asyncio.run(main())
```

| Method | Returns | Description |
|--------|---------|-------------|
| `await analyze(void_firewall=False)` | `dict` | Raw IP analysis result with VPN flag, timing, map link |
| `await get_all(banner=True, void_firewall=False)` | `str` | Formatted terminal output with optional banner and firewall bypass support |
| `clean_dict(data)` | `dict` | Strips empty/null keys from any dictionary |

---

#### Low-level: `FirewallSafeVPNDetector` (synchronous)
```python
from osixr.IP.detector import FirewallSafeVPNDetector

vpn = FirewallSafeVPNDetector(timeout=6)

# Check if IP is VPN/Proxy/Hosting
is_vpn = vpn.detect("192.168.1.1")   # → True / False

# Get raw data from multiple APIs
raw_data = vpn.gather_data("8.8.8.8")  # → List[dict]
```

| Method | Returns | Description |
|--------|---------|-------------|
| `detect(ip)` | `bool` | `True` = VPN/Proxy/Hosting detected, `False` = Clean IP |
| `gather_data(ip)` | `List[dict]` | Raw responses from multiple geo-IP APIs |
| `is_vpn_isp(isp)` | `bool` | Checks ISP name against known cloud/hosting keywords |

**Detection scoring logic:**

| Signal | Score |
|--------|-------|
| ISP matches cloud/hosting keywords | +60 |
| API returns `proxy: true` flag | +40 |
| **Threshold to flag as VPN/Proxy** | **≥ 60** |

---

### 2. ExiF Module — Photo Metadata Extraction
- The `ExiF` class extracts and displays complete EXIF metadata from JPEG or TIFF images.

#### Basic Usage
```python
from osixr.main import ExiF

exif = ExiF("photo.jpg")
exif.print_all()   # Prints full report with animated banner to terminal
```

#### `ExiF.__init__(img)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `img` | `str` | Path to the image file (`.jpg`, `.jpeg`, `.tif`, `.tiff`) |

---

#### `ExiF.print_all()` → `None`
- Displays a full formatted metadata report in the terminal with an animated ASCII banner.

```python
exif = ExiF("photo.jpg")
exif.print_all()
```

#### `ExiF.to_dict` → `str | Any`
- Displays a full formatted metadata report in the terminal with or without an animated ASCII banner.

```python
exif = ExiF("photo.jpg")
exif.get(banner=False)    # without an animated ASCII banner, default is True .
```

---

#### Low-level: `Exif` (direct access)
- For programmatic access without terminal output:

```python
from osixr.Exif.core.photo_info import Exif

info = Exif("photo.jpg")

# Get full formatted text report
report = info.print_all()
print(report)

# Get structured dict (8 sections)
data = info.to_dict()
print(data["gps_info"])
print(data["camera_info"])
```

| Method | Returns | Description |
|--------|---------|-------------|
| `print_all()` | `str` | Full human-readable metadata report |
| `to_dict()` | `dict` | All metadata as structured nested dictionaries |

**`to_dict()` output structure:**

```json
{
  "file_info": {
    "File Name": "WIN.jpg",
    "File Path": "C:\\Users\\MF\\Desktop\\Osixr\\osixr\\src\\WIN.jpg",
    "File Size": "57.2 KB",
    "File Size (bytes)": "58,592",
    "File Extension": ".JPG",
    "File Modified": "2026-04-12 21:12:01",
    "File Created": "2026-04-12 23:32:42",
    "Dimensions (from header)": "1280 × 720 px"
  },
  "camera_info": {
    "Software": "Windows 11"
  },
  "image_info": {},
  "capture_settings": {},
  "datetime_info": {
    "Date/Time Original (Capture)": "Sunday, April 12, 2026 at 21:12:01"
  },
  "gps_info": {},
  "lens_info": {},
  "processing_info": {}
}
```

---

### 3. CLI — Command-Line Interface
- **osixr** ships with a full CLI so you can run every feature directly from the terminal — no Python code needed.
- Supports both `osixr` (after install) and `python -m osixr` (from source).

#### Installation check
```bash
$ osixr -c
```
 
---
 
#### Info Flags — `-v` `-c` `-o`
 
- Quick one-shot flags that don't require a subcommand.
 
| Flag | Long form | Description |
|------|-----------|-------------|
| `-v` | `--version` | Show osixr version, author, and project links |
| `-c` | `--check` | Check PyPI for a newer release |
| `-o` | `--osixr` | Show the full osixr help & usage guide |
| `-h` | `--help` | Show the argparse help message |
 
```bash
# Show version + author info
osixr -v
 
# Check if a new version is available on PyPI
osixr -c
 
# Show full help & usage guide
osixr -o
```

---
 
#### `ip` — Full IP Geo-Lookup + VPN Detection
 
```bash
osixr ip <IP> [--timeout SEC] [--json] [--silent] [--save FILE]
```
 
| Flag | Default | Description |
|------|---------|-------------|
| `ip` | — | Target IP address |
| `--timeout SEC` | `10` | Request timeout in seconds |
| `--json` | off | Print raw JSON output instead of styled report |
| `--silent` | off | Skip the ASCII art banner |
| `--save FILE` | — | Save output to a JSON file |
 
```bash
# Styled terminal report
osixr ip 8.8.8.8
 
# Raw JSON output
osixr ip 8.8.8.8 --json
 
# Save result to file
osixr ip 8.8.8.8 --save result.json
 
# Silent mode (no banner) with custom timeout
osixr ip 8.8.8.8 --silent --timeout 5
 
# Also works with python -m
python -m osixr ip 8.8.8.8 --silent
```
 
---
 
#### `batch` — Scan Multiple IPs Concurrently
 
```bash
osixr batch <IP> [<IP> ...] [--timeout SEC] [--save FILE]
```
 
| Flag | Default | Description |
|------|---------|-------------|
| `ips` | — | One or more IP addresses (space-separated) |
| `--timeout SEC` | `10` | Request timeout in seconds |
| `--save FILE` | — | Save all results to a JSON file |
 
```bash
# Scan three IPs at once
osixr batch 8.8.8.8 1.1.1.1 196.219.54.141
 
# Save batch results
osixr batch 8.8.8.8 1.1.1.1 --save batch.json
 
# Also works with python -m
python -m osixr batch 8.8.8.8 1.1.1.1 196.219.54.141
```
 
---
 
#### `vpn` — Quick VPN / Proxy Detection Only
 
```bash
osixr vpn <IP>
```
 
| Flag | Default | Description |
|------|---------|-------------|
| `ip` | — | Target IP address to check |
 
```bash
# Check a single IP
osixr vpn 192.168.1.1
 
# Also works with python -m
python -m osixr vpn 8.8.8.8
```
 
**Output:**
```
  ⚠   VPN / PROXY / HOSTING DETECTED     ← suspicious IP
  ✔   Clean residential IP               ← clean IP
```
 
---
 
#### `exif` — Extract EXIF Metadata from Image
 
```bash
osixr exif <FILE> [--section NAME] [--json] [--silent] [--save FILE]
```
 
| Flag | Default | Description |
|------|---------|-------------|
| `file` | — | Path to JPEG or TIFF image |
| `--section NAME` | — | Show one section only (see table below) |
| `--json` | off | Print raw JSON output instead of styled report |
| `--silent` | off | Skip the ASCII art banner |
| `--save FILE` | — | Save metadata to a JSON file |
 
**Available `--section` values:**
 
| Name | Description |
|------|-------------|
| `file` | File name, size, path, dimensions |
| `camera` | Camera make, model, software |
| `image` | Resolution, color space, orientation |
| `capture` | Shutter speed, aperture, ISO, flash |
| `datetime` | Original capture date & time |
| `gps` | GPS coordinates + Google Maps link |
| `lens` | Lens make, model, focal length |
| `processing` | White balance, contrast, saturation |
 
```bash
# Full metadata report
osixr exif photo.jpg
 
# GPS section only
osixr exif photo.jpg --section gps
 
# Camera info as JSON
osixr exif photo.jpg --section camera --json
 
# Save full metadata to file
osixr exif photo.jpg --save meta.json
 
# Silent mode (no banner)
osixr exif photo.jpg --silent
 
# Also works with python -m
python -m osixr exif photo.jpg --section gps --json
```
 
---

## 🗂 Project Structure
```
osixr/
│── pyproject.toml        ← Build system & project metadata (PEP 517/518)
│── README.md             ← Documentation & usage guide
│── LICENSE               ← Project license
│── src/
│   └── osixr/
│       │── forward.py    ← Version info, help message & update checker
│       │── __init__.py   ← Package initializer (public exports)
│       ├── main.py       ← High-level entry point (IPlock, ExiF classes)
│       │── cli.py        ← Command-line interface (argparse / user input handling)
│       │
│       ├── IP/
│       │   ├── __init__.py   ← IP module initializer
│       │   ├── detector.py   ← FirewallSafeVPNDetector (sync, multi-source VPN detection)
│       │   └── utails.py     ← AsyncFetchDict (async geo-IP fetching + formatting via aiohttp)
│       │
│       ├── Exif/
│       │   ├── __init__.py   ← Exif module initializer
│       │   ├── core/
│       │   │   ├── jpeg_reader.py  ← Low-level JPEG segment parser (APP markers extraction)
│       │   │   ├── tiff_parser.py  ← TIFF/EXIF binary decoder (endianness + tag parsing)
│       │   │   └── photo_info.py   ← High-level metadata engine (Exif class abstraction)
│       │   └── utils/
│       │       ├── tags.py     ← EXIF/GPS tag ID mappings (raw → readable names)
│       │       └── mapping.py  ← Value decoding maps (flash, orientation, exposure, etc.)
│       │
│       └── Banners/
│           │── __init__.py
│           ├── banners.py  ← ASCII art banner collection (15+ styles)
│           ├── utils.py    ← BannerSplitLines (animated / line-by-line rendering)
│           └── helper.py   ← Color constants wrapper (colorama abstraction)
```

---

<div align="center">

Made with AhMed — Pull requests welcome

</div>