import time, json, aiohttp
from typing import Dict, Optional
from aiohttp.resolver import AsyncResolver
from .detector import FirewallSafeVPNDetector
from ..Banners.utils import BannerSplitLines, Color


class AsyncFetchDict:
    """
        Async IP Intelligence & VPN Detection Engine.

        This module performs asynchronous IP analysis using external geo-IP APIs,
        combined with VPN/Proxy detection logic and formatted reporting utilities.

        It is designed for high-performance async environments using aiohttp.

        ------------------------------------------------------------------------

        Features:
            - Asynchronous HTTP requests (aiohttp)
            - Geo-IP lookup (latitude / longitude / country data)
            - VPN / Proxy detection integration
            - Google Maps link generation
            - Execution time tracking
            - Banner-based formatted output support

        ------------------------------------------------------------------------

        Keyword Arguments:
            ip                 -- (str) Target IP address to analyze.
            timeout            -- (int) Maximum request timeout in seconds.
                                  Default: 10 seconds.

        Dependencies:
            - aiohttp
            - FirewallSafeVPNDetector (custom module)
            - BannerSplitLines (custom UI/banner module)

        ------------------------------------------------------------------------

        Return Value (analyze):
        dict containing:
            latitude        -- IP latitude (if available)
            longitude       -- IP longitude (if available)
            VPN/PROXY       -- Boolean VPN/Proxy detection result
            Takes           -- Execution time of request
            GooGle Map      -- Google Maps link generated from coordinates
            message         -- Error message if IP is missing or request fails

        ------------------------------------------------------------------------

        Return Value (get_all):
        Formatted string output containing:
            - Random banner
            - JSON formatted cleaned IP analysis result
    """

    def __init__(self, ip: Optional[str] = None, timeout: int = 10) -> None:
        self.ip            = ip
        self.timeout       = aiohttp.ClientTimeout(total=timeout)
        self.VPN           = FirewallSafeVPNDetector()
        self.SplitBanners  = BannerSplitLines()
        self.color         = Color()

    async def fetch_json(self, session: aiohttp.ClientSession | None, url: str | None) -> Dict:
        """
            Perform asynchronous HTTP GET request and return JSON response.

            Args:
                session  -- aiohttp client session
                url      -- API endpoint URL

            Returns:
                dict:
                    Parsed JSON response OR error dictionary
        """
        try:
            async with session.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; osixr/1.0)",
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip",
                    },
            ) as r:
                if r.status != 200:
                    return {"[ERROR] HTTP": r.status}
                return await r.json(content_type=None)  # tolerate text/plain responses
        except aiohttp.ClientError as e:
            return {"[EXCEPTION]": str(e)}
        except Exception as e:
            return {"[EXCEPTION]": str(e)}

    def clean_dict(self, data: Dict | None) -> Dict:
        """
            Remove empty or null values from dictionary.

            Args:
                data -- raw dictionary

            Returns:
                dict -- cleaned dictionary
        """
        return {
            k: v
            for k, v in (data or {}).items()
            if v not in [None, "", [], {}]
        }

    async def analyze(self):
        """
            Run IP analysis and VPN detection pipeline.

            Flow:
                1. Validate IP
                2. Query geo-IP API
                3. Measure execution time
                4. Detect VPN/Proxy
                5. Generate Google Maps link

            Returns:
                dict -- enriched IP analysis result
        """
        if not self.ip:
            return {"message": "Add IP address"}

        start = time.perf_counter()

        try:
            url = self.VPN.API["is-who"] + self.ip
            #resolver = AsyncResolver(nameservers=["8.8.8.8", "1.1.1.1"])
            #connector = aiohttp.TCPConnector(resolver=resolver, ssl=False)

            async with aiohttp.ClientSession(
                    timeout=self.timeout
                    #connector=connector
            ) as session:
                result = await self.fetch_json(session, url)

                result["Takes"] = f"{(time.perf_counter() - start):.2f} s"
                result["VPN/PROXY"] = self.VPN.detect(self.ip)

                lat = result.get("latitude")
                lon = result.get("longitude")

                if lat and lon:
                    result["GooGle Map"] = f"https://www.google.com/maps?q={lat},{lon}"

            return result

        except aiohttp.ClientConnectorError as e:
            return {"message": str(e)}

    async def get_all(self):
        """
            Generate final formatted output.

            Returns:
                str -- banner + formatted JSON result
        """
        result = await self.analyze()

        random_banners = self.SplitBanners.random_banner()
        data = random_banners + "\n\n" + json.dumps(
            self.clean_dict(result),
            indent=2,
            ensure_ascii=False
        )

        return self.SplitBanners.show_banner(result=data)




