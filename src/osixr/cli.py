import argparse
import asyncio
import json
import sys
from pathlib import Path
from .forward import help_m, check_for_update, versions


try:
    from colorama import init as _colorama_init
    _colorama_init(autoreset=True)
except ImportError:
    pass

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def banner_line(char="─", width=60) -> str:
    return DIM + char * width + RESET


def section(title: str, emoji: str = "") -> str:
    pad = max((58 - len(title)) // 2, 1)
    return f"\n{BOLD}{CYAN}{'─' * pad} {emoji}  {title}  {emoji} {'─' * pad}{RESET}\n"


def kv(key: str, val, key_width: int = 28) -> str:
    return f"  {CYAN}{key:<{key_width}}{RESET}: {BOLD}{val}{RESET}"


def _print_banner() -> None:
    try:
        from .Banners.utils import BannerSplitLines
        print(BannerSplitLines().random_banner())
    except Exception:
        pass


async def _run_ip(ip: str, timeout: int, output_json: bool, silent: bool, save: str | None):
    from .main import IPlock

    engine = IPlock(ip=ip, timeout=timeout)

    if not silent:
        _print_banner()

    result = await engine.analyze()
    clean  = engine.clean_dict(result)

    if output_json:
        out = json.dumps(clean, indent=2, ensure_ascii=False)
        print(out)
        if save:
            Path(save).write_text(out, encoding="utf-8")
            print(f"\n{GREEN}✔  Saved → {save}{RESET}")
        return

    print(section("IP INTELLIGENCE REPORT", "🌐"))

    groups = {
        "🔎  Identity": ["ip", "type", "hostname"],
        "🌍  Location": ["country", "country_code", "region", "city",
                         "postal", "latitude", "longitude", "timezone",
                         "GooGle Map"],
        "🏢  Network":  ["org", "isp", "asn", "domain"],
        "🔐  Security": ["VPN/PROXY", "proxy", "hosting", "mobile"],
        "⏱   Meta":     ["Takes"],
    }

    for group, keys in groups.items():
        rows = [(k, clean[k]) for k in keys if k in clean]
        if not rows:
            continue
        print(f"  {YELLOW}{BOLD}{group}{RESET}")
        print(f"  {DIM}{'─' * 54}{RESET}")
        for k, v in rows:
            label = k.replace("_", " ").title()
            if k == "VPN/PROXY":
                flag = (f"{RED}⚠  YES — suspicious{RESET}" if v
                        else f"{GREEN}✔  Clean{RESET}")
                print(f"  {CYAN}{'VPN / Proxy':<26}{RESET}: {flag}")
            else:
                print(kv(label, v))
        print()

    if save:
        Path(save).write_text(
            json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"{GREEN}✔  Saved → {save}{RESET}")

    print(banner_line())


async def _run_batch(ips: list[str], timeout: int, save: str | None):
    from .main import IPlock

    print(section("BATCH IP SCAN", "🔁"))
    print(f"  {DIM}Scanning {len(ips)} IPs concurrently …{RESET}\n")

    async def scan_one(ip: str):
        engine = IPlock(ip=ip.strip(), timeout=timeout)
        result = await engine.analyze()
        return ip.strip(), engine.clean_dict(result)

    results  = await asyncio.gather(*[scan_one(ip) for ip in ips])
    all_data: dict = {}

    for ip, data in results:
        vpn_flag = data.get("VPN/PROXY", False)
        flag_str = f"{RED}VPN/PROXY ⚠{RESET}" if vpn_flag else f"{GREEN}Clean ✔{RESET}"
        country  = data.get("country", "?")
        city     = data.get("city", "?")
        org      = data.get("org", data.get("isp", "?"))
        print(f"  {BOLD}{CYAN}{ip:<20}{RESET}  {country}, {city}  |  {org}  |  {flag_str}")
        all_data[ip] = data

    print()

    if save:
        Path(save).write_text(
            json.dumps(all_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"{GREEN}✔  Results saved → {save}{RESET}")

    print(banner_line())


def _run_vpn(ip: str) -> None:
    from .IP.detector import FirewallSafeVPNDetector

    print(f"\n  {DIM}Checking {ip} …{RESET}")
    det    = FirewallSafeVPNDetector()
    result = det.detect(ip)

    if result:
        print(f"\n  {RED}{BOLD}⚠   VPN / PROXY / HOSTING DETECTED{RESET}")
    else:
        print(f"\n  {GREEN}{BOLD}✔   Clean residential IP{RESET}")

    print(f"\n  {DIM}IP : {ip}{RESET}")
    print(banner_line())



SECTION_ALIASES = {
    "file":       "file_info",
    "camera":     "camera_info",
    "image":      "image_info",
    "capture":    "capture_settings",
    "datetime":   "datetime_info",
    "gps":        "gps_info",
    "lens":       "lens_info",
    "processing": "processing_info",
}

SECTION_META = {
    "file_info":        ("📁", "FILE INFORMATION"),
    "camera_info":      ("📷", "CAMERA & DEVICE"),
    "image_info":       ("🖼 ", "IMAGE PROPERTIES"),
    "capture_settings": ("⚙️ ", "CAPTURE SETTINGS"),
    "datetime_info":    ("📅", "DATE & TIME"),
    "gps_info":         ("📍", "GPS LOCATION"),
    "lens_info":        ("🔭", "LENS INFORMATION"),
    "processing_info":  ("🎨", "IMAGE PROCESSING"),
}


def _run_exif(filepath: str, output_json: bool, silent: bool,
              section_filter: str | None, save: str | None) -> None:
    from .Exif.core.photo_info import Exif

    if not Path(filepath).exists():
        print(f"{RED}✘  File not found: {filepath}{RESET}")
        sys.exit(1)

    try:
        info = Exif(filepath)
    except Exception as e:
        print(f"{RED}✘  Failed to parse EXIF: {e}{RESET}")
        sys.exit(1)

    if not silent:
        _print_banner()

    data = info.to_dict()

    if section_filter:
        key = SECTION_ALIASES.get(section_filter.lower(), section_filter)
        if key not in data:
            valid = ", ".join(SECTION_ALIASES.keys())
            print(f"{RED}✘  Unknown section '{section_filter}'. Valid: {valid}{RESET}")
            sys.exit(1)
        data = {key: data[key]}

    if output_json:
        out = json.dumps(data, indent=2, ensure_ascii=False)
        print(out)
        if save:
            Path(save).write_text(out, encoding="utf-8")
            print(f"\n{GREEN}✔  Saved → {save}{RESET}")
        return

    for key, content in data.items():
        if not content:
            continue
        emoji, title = SECTION_META.get(key, ("📌", key.upper()))
        print(section(title, emoji))
        max_klen = max((len(k) for k in content), default=20)
        for k, v in content.items():
            print(kv(k, v, max_klen + 2))
        print()

    has_gps = bool(data.get("gps_info"))
    has_cam = bool(data.get("camera_info"))
    total   = sum(len(v) for v in data.values())

    print(section("SUMMARY", "📊"))
    print(kv("EXIF Data",    "✅ Found" if total   else "❌ None"))
    print(kv("Camera Info",  "✅ Found" if has_cam else "❌ None"))
    print(kv("GPS Location", "✅ Found" if has_gps else "❌ None"))
    print(kv("Total Fields", total))
    print()

    if save:
        Path(save).write_text(
            json.dumps(info.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"{GREEN}✔  Saved → {save}{RESET}")

    print(banner_line())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="osixr",
        description=f"{BOLD}{CYAN}osixr{RESET} — OSINT toolkit: IP intelligence · EXIF metadata · VPN detection",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
        epilog=f"""
{BOLD}Examples:{RESET}

  {GREEN}# IP lookup{RESET}
  osixr ip 8.8.8.8
  osixr ip 8.8.8.8 --json
  osixr ip 8.8.8.8 --save result.json
  osixr ip 8.8.8.8 --silent --timeout 5

  {GREEN}# Batch IP scan{RESET}
  osixr batch 8.8.8.8 1.1.1.1 196.219.54.141
  osixr batch 8.8.8.8 1.1.1.1 --save batch.json

  {GREEN}# VPN/Proxy quick check{RESET}
  osixr vpn 192.168.1.1

  {GREEN}# EXIF metadata{RESET}
  osixr exif photo.jpg
  osixr exif photo.jpg --section gps
  osixr exif photo.jpg --json --save meta.json
  osixr exif photo.jpg --silent

  {GREEN}# Info flags{RESET}
  osixr -v
  osixr -c
  osixr -o
""",
    )


    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show osixr version and project info",
    )
    parser.add_argument(
        "-c", "--check",
        action="store_true",
        help="Check PyPI for a newer release",
    )
    parser.add_argument(
        "-o", "--osixr",
        action="store_true",
        help="Show full osixr help & usage guide",
    )
    # Manual help flag (replaces the disabled built-in -h)
    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show this help message",
    )

    sub = parser.add_subparsers(dest="command", metavar="command")

    # ip
    p_ip = sub.add_parser("ip", help="Full IP geo-lookup + VPN detection")
    p_ip.add_argument("ip",           help="Target IP address")
    p_ip.add_argument("--timeout",    type=int, default=10, metavar="SEC",
                      help="Request timeout in seconds (default: 10)")
    p_ip.add_argument("--json",       action="store_true", help="Output raw JSON")
    p_ip.add_argument("--silent",     action="store_true", help="Skip ASCII banner")
    p_ip.add_argument("--save",       metavar="FILE",      help="Save output to JSON file")

    # batch
    p_batch = sub.add_parser("batch", help="Scan multiple IPs concurrently")
    p_batch.add_argument("ips",       nargs="+", help="IP addresses to scan")
    p_batch.add_argument("--timeout", type=int, default=10, metavar="SEC",
                         help="Request timeout in seconds (default: 10)")
    p_batch.add_argument("--save",    metavar="FILE", help="Save results to JSON file")

    # vpn
    p_vpn = sub.add_parser("vpn", help="Quick VPN/Proxy detection only")
    p_vpn.add_argument("ip", help="Target IP address")

    # exif
    p_exif = sub.add_parser("exif", help="Extract EXIF metadata from image")
    p_exif.add_argument("file",       help="Path to JPEG or TIFF image")
    p_exif.add_argument("--section",  metavar="NAME",
                        help="Show one section only: "
                             "file | camera | image | capture | datetime | gps | lens | processing")
    p_exif.add_argument("--json",     action="store_true", help="Output raw JSON")
    p_exif.add_argument("--silent",   action="store_true", help="Skip ASCII banner")
    p_exif.add_argument("--save",     metavar="FILE",      help="Save metadata to JSON file")

    return parser



def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if args.version:
        print(versions())
        sys.exit(0)

    if args.check:
        check_for_update("osixr")
        sys.exit(0)

    if args.osixr:
        print(help_m())
        sys.exit(0)

    if args.help:
        parser.print_help()
        sys.exit(0)


    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "ip":
        asyncio.run(_run_ip(
            ip=args.ip,
            timeout=args.timeout,
            output_json=args.json,
            silent=args.silent,
            save=args.save,
        ))

    elif args.command == "batch":
        asyncio.run(_run_batch(
            ips=args.ips,
            timeout=args.timeout,
            save=args.save,
        ))

    elif args.command == "vpn":
        _run_vpn(args.ip)

    elif args.command == "exif":
        _run_exif(
            filepath=args.file,
            output_json=args.json,
            silent=args.silent,
            section_filter=args.section,
            save=args.save,
        )


if __name__ == "__main__":
    main()