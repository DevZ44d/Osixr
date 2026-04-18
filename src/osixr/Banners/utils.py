from .banners import banner
import random
import time
from .helper import Color

class BannerSplitLines:
    """
        Banner Animation & Styled Output Utility.

        This class is responsible for rendering animated banners and styled text
        output in the terminal using line-by-line animation.

        ------------------------------------------------------------------------

        Features:
            - Random banner selection
            - Line-by-line animation rendering
            - ANSI color support using colorama
            - Simple and reusable output formatting

        ------------------------------------------------------------------------

        Methods:
            random_banner():
                Returns a randomly selected banner string.

            show_banner(text: str) -> str:
                Animates and prints the given text line-by-line.

                Arguments:
                    text (str): The text (banner or content) to display.

                Returns:
                    str: The fully formatted (colored) output string.

        ------------------------------------------------------------------------

        Dependencies:
            - colorama
            - time
            - random
        """
    def __init__(self):
        self.ran = random.randint(0, len(banner) - 1)
        self.color = Color()

    def random_banner(self) -> str:
        return self.color.RED + banner[self.ran] + self.color.RESET

    def show_banner(self, result):
        lines = []

        for line in result.splitlines():
            #print(line)
            time.sleep(0.05)
            lines.append(line)

        return "\n".join(lines)


