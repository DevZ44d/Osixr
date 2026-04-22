from .IP.utails import AsyncFetchDict
from .IP.detector import FirewallSafeVPNDetector
from .Exif.core.photo_info import Exif
from .Banners.utils import BannerSplitLines, Color
from typing import Dict, Any
import asyncio, json


class IPlock(AsyncFetchDict):
    """
        High-level IP intelligence wrapper.

        Extends AsyncFetchDict — DO NOT override self.timeout after super().__init__()
        because the parent converts timeout (int) to aiohttp.ClientTimeout.

        Arguments:
            ip      -- Target IP address
            timeout -- Request timeout in seconds (default: 10)
    """

    def __init__(self, ip: str | None, timeout: int = 10) -> None:
        super().__init__(ip, timeout)   # sets ip, timeout (ClientTimeout), VPN, banners
        self.color = Color()

    async def get(self, banner: bool = True, void_firewall: bool = False) -> str:
        """
            Full pipeline:
                banner (animated, once)  →  Searching bar  →  bar erases  →  JSON

            get_all() handles everything internally:
                - prints the banner itself (if banner=True)
                - runs the progress bar
                - returns the formatted JSON string

            Args:
                banner        -- show ASCII art banner before the bar (default True)
                void_firewall -- bypass DNS/firewall via custom resolver

            Returns:
                str -- formatted JSON result
        """
        try:
            return await self.get_all(banner=banner, void_firewall=void_firewall)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)


class ExiF:
    """
        High-level EXIF metadata wrapper with animated banner output.

        Arguments:
            img -- Path to JPEG or TIFF image file
    """

    def __init__(self, img: str | None):
        self.obj    = BannerSplitLines()
        self.banner = self.obj.random_banner()
        self.info   = Exif(img)

    def to_dict(self, banner: bool = True) -> str | Any:
        """
            Return JSON metadata string, optionally with animated banner.

            Args:
                banner -- print animated banner before JSON (default True)

            Returns:
                str -- JSON metadata
        """
        data = json.dumps(self.info.to_dict(), indent=2, ensure_ascii=False)

        if banner:
            output = self.banner + "\n\n" + data
            return self.obj.show_banner(output)

        return data

    def print_all(self) -> str:
        """Print animated banner + full formatted metadata report."""
        report = self.banner + Color.RESET + "\n" + self.info.print_all()
        return self.obj.show_banner(report)

"""

async def _demo():
    scanner = IPlock(ip="8.8.8.8")
    result  = await scanner.get(banner=True)
    print(result)


async def _demo_exif():
    e = ExiF("MIN.jpg")
    #print(e.print_all())
    print(e.to_dict(banner=False))
    
if __name__ == "__main__":
    asyncio.run(_demo_exif())
"""



