import time
import json
import asyncio
from typing import Dict, Optional

import aiohttp
from aiohttp.resolver import AsyncResolver

from .detector import FirewallSafeVPNDetector
from ..Banners.utils import BannerSplitLines, Color
from .progress import MaigretStyleProgress


class AsyncFetchDict:
    """
    Async IP Intelligence & VPN Detection Engine.

    Full pipeline when analyze() / get_all() is called:

        1. Print the random ASCII art banner (animated, line-by-line)
        2. Start the Searching bar (MaigretStyleProgress) as a background Task
        3. Advance bar to ~10 %  →  send geo-IP request (aiohttp)
        4. Advance bar to ~40 %  →  geo response received
        5. Advance bar per VPN endpoint  →  3 endpoints → ~55 / 70 / 85 %
        6. Advance bar to ~100 % →  mark done, bar fills and erases itself
        7. Return enriched result dict  →  caller prints the data

    ─────────────────────────────────────────────────────────────────────────
    Arguments:
        ip      -- Target IP address (str or None)
        timeout -- Request timeout in seconds (default: 10)

    Methods:
        analyze(void_firewall, progress)  -> dict
        get_all(banner, void_firewall)    -> str
        clean_dict(data)                  -> dict
    ─────────────────────────────────────────────────────────────────────────
    """

    def __init__(self, ip: Optional[str] = None, timeout: int = 10) -> None:
        self.ip           = ip
        self.timeout      = aiohttp.ClientTimeout(total=timeout)
        self.VPN          = FirewallSafeVPNDetector()
        self.SplitBanners = BannerSplitLines()
        self.color        = Color()

    # ── low-level fetch ───────────────────────────────────────────────────────

    async def fetch_json(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """
        Async HTTP GET → parsed JSON dict.
        Returns error dict on non-200 status or any exception.
        """
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

    # ── utility ───────────────────────────────────────────────────────────────

    def clean_dict(self, data: Optional[Dict]) -> Dict:
        """Strip None / empty-string / empty-list / empty-dict values."""
        return {
            k: v for k, v in (data or {}).items()
            if v not in (None, "", [], {})
        }

    # ── main pipeline ─────────────────────────────────────────────────────────

    async def analyze(
        self,
        void_firewall: bool = False,
        progress: Optional[MaigretStyleProgress] = None,
    ) -> Dict:
        """
        Run full IP analysis with milestone-driven progress updates.

        Milestones:
            ~10 %  — request about to be sent
            ~40 %  — geo-IP response received
            ~55 %  — VPN endpoint 1 done
            ~70 %  — VPN endpoint 2 done
            ~85 %  — VPN endpoint 3 done + score computed
            ~100 % — all done

        Args:
            void_firewall -- bypass DNS via Google / Cloudflare resolver
            progress      -- MaigretStyleProgress instance (optional)

        Returns:
            dict -- enriched result
        """
        if not self.ip:
            return {"message": "Add IP address"}

        start = time.perf_counter()
        url   = self.VPN.API["is-who"] + self.ip

        try:
            connector = None
            if void_firewall:
                resolver  = AsyncResolver(nameservers=["8.8.8.8", "1.1.1.1"])
                connector = aiohttp.TCPConnector(resolver=resolver, ssl=False)

            async with aiohttp.ClientSession(
                timeout   = self.timeout,
                connector = connector,
            ) as session:

                # Milestone 1: request sent
                if progress:
                    progress.set_random_progress(10, 4)

                result = await self.fetch_json(session, url)

                # Milestone 2: geo response received
                if progress:
                    progress.set_random_progress(40, 5)

            if not isinstance(result, dict):
                return {"message": "Invalid API response"}

            if any(k.startswith("[ERROR]") or k.startswith("[EXCEPTION]") for k in result):
                return result

            # VPN detection — 3 endpoints, each advances the bar
            # Progress callback: called once per API endpoint inside gather_data
            _milestones = iter([55, 70, 85])

            def _vpn_progress_cb():
                if progress:
                    target = next(_milestones, 85)
                    progress.set_random_progress(target, 4)

            result["VPN/PROXY"] = await asyncio.to_thread(
                self.VPN.detect,
                self.ip,
                _vpn_progress_cb,
            )

            # Enrich result
            lat = result.get("latitude")
            lon = result.get("longitude")
            if lat and lon:
                result["GooGle Map"] = f"https://www.google.com/maps?q={lat},{lon}"

            result["Takes"] = f"{(time.perf_counter() - start):.2f} s"

            # Milestone final: all done
            if progress:
                progress.set_random_progress(100, 1)

            return result

        except aiohttp.ClientConnectorError as e:
            return {"message": f"Connection failed: {e}"}
        except Exception as e:
            return {"message": f"Unexpected error: {e}"}

    # ── formatted output ──────────────────────────────────────────────────────

    async def get_all(
        self,
        banner:        bool = True,
        void_firewall: bool = False,
    ) -> str:
        """
        Full pipeline:
            1. Print animated banner (once, line-by-line)
            2. Start Searching bar
            3. Run analyze() with milestone progress updates
            4. Bar fills to 100 % and erases itself
            5. Return formatted JSON string

        Args:
            banner        -- show ASCII art banner before the bar (default True)
            void_firewall -- bypass firewall/DNS via custom resolver

        Returns:
            str -- formatted JSON string (NOT printed here — caller decides)
        """
        if banner:
            banner_text = self.SplitBanners.random_banner()
            self.SplitBanners.show_banner(result=banner_text)


        progress      = MaigretStyleProgress(total=100)
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