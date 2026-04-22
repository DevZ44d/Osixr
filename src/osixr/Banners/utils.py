from .banners import banner
import random
import time
from .helper import Color


class BannerSplitLines:
    """
    Banner Animation & Styled Output Utility.

    Renders animated banners and styled text output in the terminal
    using line-by-line animation.

    ─────────────────────────────────────────────────────────────────
    Methods:
        random_banner()          -> str   Returns a random colored banner string.
        show_banner(result: str) -> str   Prints text line-by-line with animation.
    ─────────────────────────────────────────────────────────────────

    Dependencies:
        - colorama
        - time
        - random
    """

    def __init__(self):
        self.ran   = random.randint(0, len(banner) - 1)
        self.color = Color()

    def random_banner(self) -> str:
        return self.color.RED + banner[self.ran] + self.color.RESET

    def show_banner(self, result: str) -> str:
        """
        Print text line-by-line with a short delay (animation effect).

        Args:
            result -- the full text to animate (banner or any content)

        Returns:
            str -- the fully formatted output string (same as input)
        """
        lines = []

        for line in result.splitlines():
            print(line)           # ← was commented out, causing banner to never show
            time.sleep(0.05)
            lines.append(line)

        return "\n".join(lines)