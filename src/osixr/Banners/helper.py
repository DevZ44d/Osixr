from colorama import Fore
from typing import Any


class Color:
    """
        Terminal Color Constants Wrapper.

        This class provides a simple abstraction over ANSI color codes
        using the `colorama` library for coloring terminal output.

        It is designed to improve readability and maintainability when
        working with colored CLI outputs.

        ------------------------------------------------------------------------

        Features:
            - Predefined ANSI color constants
            - Simplified access to common terminal colors
            - Easy integration with CLI tools and animations

        ------------------------------------------------------------------------

        Attributes:
            RED (Any):
                ANSI code for red colored text.

            WHITE (Any):
                ANSI code for white colored text.

            RESET (Any):
                Resets terminal color back to default.

        ------------------------------------------------------------------------

        Dependencies:
            - colorama (Fore, Style)

        ------------------------------------------------------------------------

        Example:

            from colorama import Fore

            color = Color()
            print(color.RED + "Error message" + color.RESET)
        """
    RED: Any= Fore.RED
    WHITE: Any = Fore.WHITE
    RESET: Any = Fore.RESET
    BLUE: Any  = Fore.BLUE
    GREEN: Any = Fore.GREEN