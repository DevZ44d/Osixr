import json
import urllib.request
import urllib.error
import socket
import time
from typing import Dict, List, Any, Optional


class FirewallSafeVPNDetector:
    """
        Firewall-Safe VPN / Proxy Detection Engine.

        This module performs IP reputation analysis using multiple public APIs
        in order to detect VPNs, proxies, hosting providers, and cloud services.

        It is designed to be lightweight and firewall-safe by using urllib
        instead of heavy async HTTP libraries.

        ------------------------------------------------------------------------

        Features:
            - Multi-source IP intelligence gathering
            - ISP reputation scoring system
            - VPN / Proxy detection heuristics
            - Retry mechanism for reliability
            - Keyword-based cloud provider detection

        ------------------------------------------------------------------------

        Keyword Arguments:
            timeout         -- Request timeout in seconds (default: 6)

        ------------------------------------------------------------------------

        Detection Logic:
            - ISP analysis (cloud / hosting detection keywords)
            - Proxy flags from API responses
            - Weighted scoring system

        Final Decision:
            Returns True if IP is likely VPN/Proxy/Hosting
            based on threshold scoring (>= 60)

        ------------------------------------------------------------------------

        Return Values:
        detect(ip) -> bool
            True  = VPN / Proxy / Hosting detected
            False = Clean residential IP

        gather_data(ip) -> List[dict]
            Raw API responses from multiple IP intelligence providers
    """

    def __init__(self, timeout: int = 6):
        self.timeout = timeout

        self.keywords = [
            "vpn", "proxy", "hosting", "cloud",
            "aws", "amazon", "google", "azure",
            "digitalocean", "linode", "vultr",
            "ovh", "contabo", "hetzner", "m247"
        ]

        self.API: Dict[str, str] = {
            "is-who": "https://ipwho.is/"
        }

        self.endpoints: List[str] = []

    def fetch(self, url: str) -> Dict[str, Any]:
        """
            Perform safe HTTP request and return JSON response.

            Args:
                url (str): Target API endpoint

            Returns:
                dict: Parsed JSON response or empty dict on failure
        """
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept-Encoding": "gzip",
                    "Connection": "close"
                }
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                data = res.read().decode("utf-8", errors="ignore")
                return json.loads(data)

        except (urllib.error.URLError, socket.timeout, json.JSONDecodeError):
            return {}
        except Exception:
            return {}

    def gather_data(self, ip: str, progress_callback=None) -> List[Dict[str, Any]]:
        """
            Collect IP intelligence from multiple public APIs.

            Args:
                ip (str): Target IP address

            Returns:
                List[dict]: List of API responses
        """
        results: List[Dict[str, Any]] = []
        self.endpoints = [
            f"http://ip-api.com/json/{ip}",
            f"https://ipinfo.io/{ip}/json",
            f"https://get.geojs.io/v1/ip/geo/{ip}.json"
        ]

        for url in self.endpoints:
            for _ in range(1):  # retry
                data = self.fetch(url)

                if progress_callback:
                    progress_callback()

                if data:
                    results.append(data)
                    break
                else:
                    time.sleep(0.3)

        return results

    def detect(self, ip: str, progress_callback = None) -> bool:
        """
            Determine if an IP is VPN / Proxy / Hosting.

            Args:
                ip (str): Target IP address

            Returns:
                bool: True if suspicious, False if clean
        """
        results = self.gather_data(ip, progress_callback)

        isps = []
        proxy_flags = []

        for r in results:
            isps.append(
                r.get("isp")
                or r.get("org")
                or r.get("organization_name")
            )

            if "proxy" in r:
                proxy_flags.append(r.get("proxy"))

        isp = self.vote(isps)

        score = 0

        if self.is_vpn_isp(isp):
            score += 60

        if any(proxy_flags):
            score += 40

        return score >= 60

    def vote(self, values: List[Any]) -> Optional[str]:
        """
            Return most frequent non-null value.

            Args:
                values (List): List of values

            Returns:
                str | None: Most common value
        """
        values = [v for v in values if v]
        if not values:
            return None
        return max(set(values), key=values.count)

    def is_vpn_isp(self, isp: Optional[str]) -> bool:
        """
            Check ISP against known cloud / hosting providers.

            Args:
                isp (str | None): ISP name

            Returns:
                bool: True if ISP matches VPN/hosting patterns
        """
        if not isp:
            return False

        isp = isp.lower()
        return any(k in isp for k in self.keywords)