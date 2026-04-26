import time
import json
import asyncio
import urllib.request
from typing import Dict, Optional

import aiohttp
from aiohttp.resolver import AsyncResolver
from ..Banners.banners import banner as BANNERS
import random

from .detector import FirewallSafeVPNDetector
from ..Banners.utils import BannerSplitLines, Color
from osixr.src.osixr.IP.progress import MaigretStyleProgress


def resolve_my_ip(timeout: int = 5) -> str:
    apis = [
        "https://api.ipify.org",
        "https://ipinfo.io/ip",
        "https://checkip.amazonaws.com",
        "https://api4.my-ip.io/ip",
        "https://ipecho.net/plain",
    ]
    for url in apis:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; osixr/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as res:
                ip = res.read().decode("utf-8", errors="ignore").strip()
                if ip:
                    return ip
        except Exception:
            continue
    return "0.0.0.0"


class AsyncFetchDict:

    _BAR_TOTAL = 100

    def __init__(self, ip: Optional[str] = None, timeout: int = 10) -> None:
        self.ip           = ip
        self.timeout      = aiohttp.ClientTimeout(total=timeout)
        self.VPN          = FirewallSafeVPNDetector()
        self.SplitBanners = BannerSplitLines()
        self.color        = Color()

    def _resolve_ip(self) -> Optional[str]:
        if self.ip and self.ip.strip().lower() == "me":
            return resolve_my_ip()
        return self.ip

    async def fetch_json(self, session: aiohttp.ClientSession, url: str) -> Dict:
        try:
            async with session.get(
                url,
                headers={
                    "User-Agent":      "Mozilla/5.0 (compatible; osixr/1.0)",
                    "Accept":          "application/json",
                    "Accept-Encoding": "gzip",
                },
            ) as r:
                if r.status != 200:
                    return {"[ERROR] HTTP": r.status}
                return await r.json(content_type=None)
        except aiohttp.ClientError as e:
            return {"[EXCEPTION]": str(e)}
        except Exception as e:
            return {"[EXCEPTION]": str(e)}

    def clean_dict(self, data: Optional[Dict]) -> Dict:
        return {
            k: v for k, v in (data or {}).items()
            if v not in (None, "", [], {})
        }

    async def analyze(
        self,
        void_firewall: bool = False,
        progress: Optional[MaigretStyleProgress] = None,
    ) -> Dict:
        target_ip = self._resolve_ip()

        if not target_ip or target_ip == "0.0.0.0":
            return {"message": "Could not resolve public IP" if self.ip == "me" else "No IP address provided"}

        start = time.perf_counter()
        url   = self.VPN.API["is-who"] + target_ip

        try:
            connector = None
            if void_firewall:
                resolver  = AsyncResolver(nameservers=["8.8.8.8", "1.1.1.1"])
                connector = aiohttp.TCPConnector(resolver=resolver, ssl=False)

            async with aiohttp.ClientSession(
                timeout   = self.timeout,
                connector = connector,
            ) as session:
                if progress:
                    progress.set_random_progress(10, 4)
                result = await self.fetch_json(session, url)
                if progress:
                    progress.set_random_progress(40, 5)

            if not isinstance(result, dict):
                return {"message": "Invalid API response"}

            if any(k.startswith("[ERROR]") or k.startswith("[EXCEPTION]") for k in result):
                return result

            _milestones = iter([55, 70, 85])

            def _vpn_cb():
                if progress:
                    progress.set_random_progress(next(_milestones, 85), 4)

            result["VPN/PROXY"] = await asyncio.to_thread(
                self.VPN.detect,
                target_ip,
                _vpn_cb,
            )

            lat = result.get("latitude")
            lon = result.get("longitude")
            if lat and lon:
                result["GooGle Map"] = f"https://www.google.com/maps?q={lat},{lon}"

            result["Takes"] = f"{(time.perf_counter() - start):.2f} s"

            if progress:
                progress.set_random_progress(100, 1)

            return result

        except aiohttp.ClientConnectorError as e:
            return {"message": f"Connection failed: {e}"}
        except Exception as e:
            return {"message": f"Unexpected error: {e}"}

    async def get_all(
        self,
        banner:        bool = True,
        void_firewall: bool = False,
    ) -> str:
        if banner:
            ran         = random.randint(0, len(BANNERS) - 1)
            banner_text = f"\033[91m{BANNERS[ran]}\033[0m"
            self.SplitBanners.show_banner(result=banner_text)

        progress      = MaigretStyleProgress(total=self._BAR_TOTAL)
        progress_task = asyncio.create_task(progress.start_render())

        result = await self.analyze(
            void_firewall = void_firewall,
            progress      = progress,
        )

        progress.done = True
        await progress_task

        cleaned = (
            self.clean_dict(result)
            if isinstance(result, dict)
            else {"message": "Invalid result"}
        )

        return json.dumps(cleaned, indent=2, ensure_ascii=False)