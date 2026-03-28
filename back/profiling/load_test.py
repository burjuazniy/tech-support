"""Latency benchmark for the Tech Support API.

Sends N sequential requests through the ASGI transport (in-process, no TCP
overhead) and prints percentile statistics.

Usage::

    cd back
    python profiling/load_test.py

The ASGI transport from httpx runs the full FastAPI/Starlette stack - including
all middleware - but skips OS networking, so the numbers reflect pure
application latency.
"""

import asyncio
import statistics
import sys
import time
from pathlib import Path

# Make src.back importable when running directly from back/
sys.path.insert(0, str(Path(__file__).parent.parent))

from httpx import ASGITransport, AsyncClient  # noqa: E402

# Silence application logs during profiling to avoid I/O skewing timings.
from src.back.logging_config import configure_logging  # noqa: E402

configure_logging("CRITICAL")

from src.back.main import app  # noqa: E402

WARMUP = 20
N = 500


async def _benchmark() -> list[float]:
    """Run WARMUP + N requests and return the latency of the N measured ones.

    Returns:
        list[float]: Latency in milliseconds for each measured request.
    """
    times: list[float] = []
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Warm-up: let Python JIT stabilise and caches fill.
        for _ in range(WARMUP):
            await client.get("/")

        for _ in range(N):
            t0 = time.perf_counter()
            await client.get("/")
            times.append((time.perf_counter() - t0) * 1000)

    return times


def _percentile(data: list[float], pct: float) -> float:
    idx = int(len(data) * pct / 100)
    return data[min(idx, len(data) - 1)]


def main() -> None:
    """Run the benchmark and print a latency summary table."""
    times = asyncio.run(_benchmark())
    times.sort()

    print(f"\n{'=' * 44}")
    print(f"  Latency benchmark  -  GET /  -  {N} reqs")
    print(f"{'=' * 44}")
    print(f"  Warmup requests : {WARMUP}")
    print(f"  Measured requests: {N}")
    print(f"{'-' * 44}")
    print(f"  Min  : {min(times):>8.3f} ms")
    print(f"  Mean : {statistics.mean(times):>8.3f} ms")
    print(f"  Median (p50): {_percentile(times, 50):>6.3f} ms")
    print(f"  p90  : {_percentile(times, 90):>8.3f} ms")
    print(f"  p95  : {_percentile(times, 95):>8.3f} ms")
    print(f"  p99  : {_percentile(times, 99):>8.3f} ms")
    print(f"  Max  : {max(times):>8.3f} ms")
    print(f"  Stdev: {statistics.stdev(times):>8.3f} ms")
    print(f"{'=' * 44}\n")


if __name__ == "__main__":
    main()
