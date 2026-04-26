import asyncio
import os
import sys
import time
import itertools
import random
from rich.live  import Live
from rich.text  import Text
from rich.console import Console

def _is_android() -> bool:
    return bool(os.environ.get("ANDROID_ROOT") or os.environ.get("ANDROID_DATA"))


_BRAILLE = list("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")

_WAVE = [
    "▁▂▃", "▂▃▄", "▃▄▅", "▄▅▆", "▅▆▇",
    "▆▇▆", "▇▆▅", "▆▅▄", "▅▄▃", "▄▃▂",
    "▃▂▁", "▂▁▂",
]


class MaigretStyleProgress:

    def __init__(self, total: int = 511):
        self.total    = total
        self.current  = 0
        self.target   = 0
        self.start    = None
        self.done     = False
        self._android = _is_android()
        self._braille = itertools.cycle(_BRAILLE)
        self._wave    = itertools.cycle(_WAVE)

    def set_target(self, value: int) -> None:
        self.target = max(0, min(self.total, value))

    def set_random_progress(self, base: int, spread: int = 3) -> None:
        self.set_target(base + random.randint(-spread, spread))

    def update(self, amount: int = 1) -> None:
        self.set_target(self.target + amount)

    def smooth_tick(self) -> None:
        if self.current < self.target:
            self.current = min(self.current + random.randint(1, 2), self.target)
        elif self.current > self.target:
            self.current -= 1

    def _build_line(self) -> str:
        pct      = self.current / self.total if self.total else 0
        bar_len  = 40
        filled   = int(bar_len * pct)
        sub_chars = " ▏▎▍▌▋▊▉"
        sub_char  = sub_chars[min(int((pct * bar_len - filled) * 8), 7)] if filled < bar_len else ""
        bar      = "█" * filled + sub_char + " " * (bar_len - filled - len(sub_char))
        elapsed  = time.perf_counter() - self.start
        speed    = self.current / elapsed if elapsed > 0 else 0
        remain   = (self.total - self.current) / speed if speed > 0 else 0
        b = next(self._braille)
        w = next(self._wave)
        return (
            f"{b} Searching |{bar}| {w} "
            f"{self.current}/{self.total} [{int(pct * 100)}%] "
            f"in {elapsed:.1f}s (~{remain:.1f}s, {speed:.1f}/s)"
        )

    async def start_render(self) -> None:
        self.start = time.perf_counter()
        if self._android:
            await self._render_rich()
        else:
            await self._render_tty()

    async def _render_tty(self) -> None:
        while not self.done:
            self.smooth_tick()
            sys.stdout.write(f"\r\033[2K{self._build_line()}")
            sys.stdout.flush()
            await asyncio.sleep(0.05)
        self.current = self.total
        sys.stdout.write(f"\r\033[2K{self._build_line()}")
        sys.stdout.flush()
        await asyncio.sleep(0.08)
        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()

    async def _render_rich(self) -> None:

        console = Console()

        with Live(console=console, refresh_per_second=20) as live:
            while not self.done:
                self.smooth_tick()
                live.update(Text(self._build_line()))
                await asyncio.sleep(0.05)

            self.current = self.total
            live.update(Text(self._build_line()))
            await asyncio.sleep(0.08)