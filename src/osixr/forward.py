from importlib.metadata import version, PackageNotFoundError
from .Banners.utils import Color
import requests

c = Color()

def versions() -> str:
    try:
        pkg_version = version("osixr")
    except PackageNotFoundError:
        pkg_version = "unknown"

    return f"""
{c.RED}Osixr {c.WHITE}Version: {c.RED}{pkg_version}{c.WHITE}
Author: {c.RED}AhMed{c.WHITE} .

({c.RED}PyPI{c.WHITE})      : https://pypi.org/project/osixr .
({c.RED}GitHub{c.WHITE})    : https://github.com/DevZ44d/osixr.git .
({c.RED}Telegram{c.WHITE})  : https://t.me/PyCodz .
({c.RED}Portfolio{c.WHITE}) : https://deep.is-a.dev .
"""


def help_m() -> str:
    return f"""
{c.RED}Osixr{c.WHITE} - OSINT Toolkit: IP Intelligence & EXIF Metadata Extraction & Etc-Soon .
Usage:
        {c.RED}osixr {c.WHITE}[COMMAND] "[TARGET]" [OPTIONS]

{c.GREEN}Commands:{c.WHITE}
  {c.RED}ip{c.WHITE}              Full IP geo-lookup + VPN detection.
  {c.RED}batch{c.WHITE}           Scan multiple IPs concurrently.
  {c.RED}vpn{c.WHITE}             Quick VPN / Proxy detection only.
  {c.RED}exif{c.WHITE}            Extract EXIF metadata from image.

{c.GREEN}Options:{c.WHITE}
  {c.RED}--timeout SEC{c.WHITE}   Request timeout in seconds (default: 10).
  {c.RED}--json{c.WHITE}          Print raw JSON output.
  {c.RED}--silent{c.WHITE}        Skip ASCII art banner.
  {c.RED}--save FILE{c.WHITE}     Save output to a JSON file.
  {c.RED}--section NAME{c.WHITE}  Show one EXIF section only (exif command).
  {c.RED}-v, --version{c.WHITE}   Show osixr version.
  {c.RED}-h, --help{c.WHITE}      Show this help message.
"""


def check_for_update(package_name: str = "osixr") -> None:
    try:
        current_version = version(package_name)
        url = f"https://pypi.org/pypi/{package_name}/json"
        latest_version = requests.get(url, timeout=5).json()["info"]["version"]

        if current_version != latest_version:
            print(f"""{c.WHITE}
[{c.BLUE}notice{c.WHITE}] New release available: {c.RED}{current_version}{c.WHITE} → {c.GREEN}{latest_version}{c.WHITE}
[{c.BLUE}notice{c.WHITE}] Run: {c.GREEN}pip install -U {package_name}{c.WHITE}
""")
    except Exception:
        pass
