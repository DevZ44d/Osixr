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
        super().__init__(ip, timeout)   # handles ip, timeout, VPN, banners
        self.color = Color()
        self.banner = BannerSplitLines()

    async def get(self, banner: bool = True):
        re = self.banner.random_banner()
        try:
            if banner:
                return str(self.banner.show_banner(re)) + "\n" + json.dumps(
                    await self.analyze(), indent=2, ensure_ascii=False
                )
            else:
                return json.dumps(
                    await self.analyze(), indent=2, ensure_ascii=False
                )
        except Exception as e:
            return e




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
        """Print banner + JSON metadata to stdout."""

        if banner:
            output = self.banner + "\n\n" + json.dumps(
                self.info.to_dict(), indent=2, ensure_ascii=False
            )
            t = self.obj.show_banner(output)
            return t
        else:
            return json.dumps(
                self.info.to_dict(), indent=2, ensure_ascii=False
            )


    def print_all(self) -> None:
        """Print banner + full formatted metadata report."""
        report = self.banner + Color.RESET + "\n" + self.info.print_all()
        u = self.obj.show_banner(report)
        return u

"""
    async def _demo():
        scanner = IPlock(ip="8.8.8.8")
        #result  = await scanner.get()
        #all = await scanner.print_all()
        #clean   = scanner.clean_dict(result)
        #print(await scanner.silent_dict())
        print(await scanner.get(banner=True))
    
    async def demo():
        e = ExiF("WIN.jpg")
        print(e.print_all())
        print((e.to_dict(banner=False)))
    
    
    if __name__ == "__main__":
        asyncio.run(_demo())
        ##xxx()
    
    
    #if __name__ == "__main__":
        #xxx()
"""

