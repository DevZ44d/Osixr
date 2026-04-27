# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x.x   | ✅ Active support |
| 1.x.x   | ❌ No longer supported |

## Reporting a Vulnerability

If you discover a security vulnerability in **Osixr**, please report it
**privately** — do not open a public GitHub issue.

**Contact:**

| Channel | Address |
|---------|---------|
| Email | alexcrow221@gmail.com |
| Telegram | https://t.me/PyCodz_Chat |

Please include the following in your report:

- A clear description of the vulnerability
- Steps to reproduce the issue
- Potential impact (what an attacker could achieve)
- Your suggested fix (optional but appreciated)

You will receive a response within **72 hours**.
If the vulnerability is confirmed, a patched release will be published
as soon as possible and you will be credited in the changelog.

## Scope

The following are **in scope** for security reports:

- Arbitrary code execution via crafted API responses
- Credential or token leakage
- Unsafe deserialization of external data
- Dependency vulnerabilities with direct impact on Osixr users
- DNS / network request hijacking via `void_firewall` mode
- Path traversal or arbitrary file read via the EXIF module
- Maliciously crafted JPEG/TIFF files causing crashes or code execution
  in the EXIF parser (`jpeg_reader.py`, `tiff_parser.py`)
- GPS coordinate or sensitive EXIF data leakage to unintended destinations

The following are **out of scope:**

- Vulnerabilities in third-party APIs (ipwho.is, ip-api.com, etc.)
- Issues requiring physical access to the user's machine
- Social engineering attacks
- Bugs without a realistic security impact

## Modules & Attack Surface

### IP Intelligence (`IP/`)

Osixr queries the following external services at runtime:

| Service | Purpose |
|---------|---------|
| `ipwho.is` | Geo-IP lookup |
| `ip-api.com` | VPN / Proxy detection |
| `ipinfo.io` | VPN / Proxy detection |
| `geojs.io` | VPN / Proxy detection |
| `api.ipify.org` + others | Public IP resolution (`me` keyword) |

Osixr does **not** authenticate to these services and sends only the target
IP address. No personal data is stored or transmitted beyond what is required
for each lookup.

### EXIF Metadata (`Exif/`)

The EXIF module reads and parses binary data from local JPEG and TIFF files.

**Privacy notice:**
EXIF metadata can contain highly sensitive personal data including:

- 📍 GPS coordinates (precise location where the photo was taken)
- 📅 Exact date and time of capture
- 📷 Device make, model, and serial number
- 🔧 Software version and OS information

Users are responsible for ensuring they have the right to process EXIF data
from any image file. Do not extract or share EXIF data from images without
the explicit consent of the image owner.

**Security note:**
Maliciously crafted image files could potentially trigger parser bugs.
Only parse images from trusted sources. If you discover a parser
vulnerability, please report it privately using the contact details above.

## Dependency Security

To check for known vulnerabilities in Osixr's dependencies:

```bash
pip install pip-audit
pip-audit
```

## Disclosure Policy

We follow **Responsible Disclosure**:

1. Reporter submits vulnerability privately
2. Maintainer confirms receipt within **72 hours**
3. Maintainer investigates and develops a fix
4. Patched version is released
5. Vulnerability is publicly disclosed after users have had time to update

---

<div align="center">
  <sub>Osixr — Made with ❤️ by AhMed (DevZ44d)</sub>
</div>
