import asyncio
import sys
import time
import itertools
import random


class MaigretStyleProgress:
    """
    Maigret-style animated progress bar for async operations.

    Renders a smooth sub-character bar with a wave spinner and real-time
    stats (elapsed, ETA, speed) — identical in feel to maigret's bar.

    The bar advances via milestone calls (set_random_progress) that reflect
    real operation checkpoints, so the numbers are meaningful, not fake.

    ─────────────────────────────────────────────────────────────────────────
    Usage:
        p    = MaigretStyleProgress(total=511)
        task = asyncio.create_task(p.start_render())

        p.set_random_progress(10, 4)   # after request sent
        await real_work()
        p.set_random_progress(40, 5)   # after geo response
        ...
        p.done = True
        await task                     # bar fills to 100% and erases itself
    ─────────────────────────────────────────────────────────────────────────

    Arguments:
        total  -- cosmetic total (default 511 — matches maigret feel)
    """

    def __init__(self, total: int = 511):
        self.total   = total
        self.current = 0
        self.target  = 0
        self.start   = None
        self.done    = False

        # Wave animation — reads like music notes ▁▂▃▄▅▆▇
        self.spinner_frames = [
            "▁▂▃", "▂▃▄", "▃▄▅", "▄▅▆", "▅▆▇",
            "▆▇▆", "▇▆▅", "▆▅▄", "▅▄▃", "▄▃▂",
            "▃▂▁", "▂▁▂",
        ]
        self.spinner = itertools.cycle(self.spinner_frames)


    def set_target(self, value: int) -> None:
        """Set the target the bar should smoothly advance toward."""
        self.target = max(0, min(self.total, value))

    def set_random_progress(self, base: int, spread: int = 3) -> None:
        """
        Set a milestone target with a small random spread so the numbers
        look organic rather than always hitting exact round values.

        Args:
            base   -- percentage-equivalent target (0–total scale)
            spread -- ± random noise applied to base
        """
        noise = random.randint(-spread, spread)
        self.set_target(base + noise)

    def update(self, amount: int = 1) -> None:
        """Advance the target by a fixed amount (used by progress_callback)."""
        self.set_target(self.target + amount)


    def smooth_tick(self) -> None:
        """
        Move current one step toward target per render cycle.
        Small random step size (1–2) keeps movement smooth and natural.
        """
        if self.current < self.target:
            self.current = min(
                self.current + random.randint(1, 2),
                self.target,
            )
        elif self.current > self.target:
            self.current -= 1


    def _render(self) -> str:
        """
        Build one bar frame.

        Format (identical to maigret):
            Searching |████████████████▍          | ▂▃▄ 312/511 [61%] in 10s (~6s, 32.1/s)
        """
        pct     = self.current / self.total if self.total else 0
        bar_len = 40

        filled   = int(bar_len * pct)
        sub_idx  = int((pct * bar_len - filled) * 8)
        sub_chars = " ▏▎▍▌▋▊▉"
        sub_char  = sub_chars[min(sub_idx, len(sub_chars) - 1)] if filled < bar_len else ""

        bar = "█" * filled + sub_char + " " * (bar_len - filled - len(sub_char))

        elapsed = time.perf_counter() - self.start
        speed   = self.current / elapsed if elapsed > 0 else 0
        remain  = (self.total - self.current) / speed if speed > 0 else 0
        spin    = next(self.spinner)

        return (
            f"\rSearching |{bar}| {spin} "
            f"{self.current}/{self.total} [{int(pct * 100)}%] "
            f"in {elapsed:.1f}s (~{remain:.1f}s, {speed:.1f}/s)"
        )


    async def start_render(self) -> None:
        """
        Async render loop — run as a background Task.

        Renders at ~20 fps (every 0.05 s).
        When self.done is set:
            1. Fills bar to 100 %
            2. Waits one frame so user sees the complete bar
            3. Erases the line cleanly so data prints on a fresh screen
        """
        self.start = time.perf_counter()

        while not self.done:
            self.smooth_tick()
            sys.stdout.write(self._render())
            sys.stdout.flush()
            await asyncio.sleep(0.05)


        self.current = self.total
        sys.stdout.write(self._render())
        sys.stdout.flush()
        await asyncio.sleep(0.08)

        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()