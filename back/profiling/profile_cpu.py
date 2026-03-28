"""CPU profiling script for the Tech Support API.

Uses Python's stdlib ``cProfile`` to instrument N in-process ASGI requests
and report the top functions by cumulative CPU time.

Usage::

    cd back
    python profiling/profile_cpu.py

Outputs:
- Console table of top 25 functions by cumulative time.
- ``profiling/output/cpu_profile.prof`` - binary snapshot readable by
  ``pstats`` or the ``snakeviz`` visualiser::

      pip install snakeviz
      snakeviz profiling/output/cpu_profile.prof

Why cProfile?
    It is part of the Python stdlib (no install needed), low-overhead for
    most applications, and integrates with every Python IDE.  Alternatives:
    ``pyinstrument`` (wall-clock, friendlier output) and ``py-spy`` (sampling
    profiler that can attach to a running process without modifying code).
"""

import asyncio
import cProfile
import io
import pstats
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from httpx import ASGITransport, AsyncClient  # noqa: E402

from src.back.logging_config import configure_logging  # noqa: E402

configure_logging("CRITICAL")

from src.back.main import app  # noqa: E402

N = 1000
OUTPUT_FILE = Path(__file__).parent / "output" / "cpu_profile.prof"


async def _run() -> None:
    """Send N requests through the ASGI transport."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for _ in range(N):
            await client.get("/")


def main() -> None:
    """Profile N requests and print/save results."""
    profiler = cProfile.Profile()
    profiler.enable()
    asyncio.run(_run())
    profiler.disable()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    profiler.dump_stats(str(OUTPUT_FILE))

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(25)

    print(f"\n{'=' * 60}")
    print(f"  CPU Profile  –  GET /  –  {N} requests")
    print(f"{'=' * 60}")
    print(stream.getvalue())
    print(f"Full profile saved to: {OUTPUT_FILE}")
    print(f"Visualise with: snakeviz {OUTPUT_FILE}\n")


if __name__ == "__main__":
    main()
