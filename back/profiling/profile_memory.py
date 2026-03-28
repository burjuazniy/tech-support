"""Memory profiling script for the Tech Support API.

Uses Python's stdlib ``tracemalloc`` to measure heap allocations at three
checkpoints:

1. **Baseline** - after app import, before any request.
2. **After 1 request** - captures per-request allocation cost.
3. **After 100 requests** - checks for allocation growth (potential leaks).

Usage::

    cd back
    python profiling/profile_memory.py

Why tracemalloc?
    stdlib, zero dependencies, line-level granularity.  Alternative:
    ``memory_profiler`` (decorator-based, requires ``psutil``) or
    ``pympler`` (object-level tracking).
"""

import asyncio
import sys
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from httpx import ASGITransport, AsyncClient  # noqa: E402

from src.back.logging_config import configure_logging  # noqa: E402

configure_logging("CRITICAL")

from src.back.main import app  # noqa: E402

BATCH = 100


def _fmt(b: int) -> str:
    """Format bytes as KB with one decimal."""
    return f"{b / 1024:.1f} KB"


async def _measure() -> None:
    """Take three memory snapshots and print a diff report."""
    tracemalloc.start()

    # Snapshot 1: baseline (app imported, no requests yet) 
    snap_baseline = tracemalloc.take_snapshot()
    baseline_cur, baseline_peak = tracemalloc.get_traced_memory()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:

        # Snapshot 2: after first request (ASGI/middleware warm-up cost) 
        await client.get("/")
        snap_one = tracemalloc.take_snapshot()
        one_cur, one_peak = tracemalloc.get_traced_memory()

        # Snapshot 3: after BATCH requests (growth check) 
        for _ in range(BATCH - 1):
            await client.get("/")
        snap_batch = tracemalloc.take_snapshot()
        batch_cur, batch_peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    # Report 
    print(f"\n{'=' * 56}")
    print("  Memory Profile  –  tracemalloc")
    print(f"{'=' * 56}")
    print(f"  Checkpoint        Current      Peak")
    print(f"  {'' * 50}")
    print(f"  Baseline        {_fmt(baseline_cur):>10}  {_fmt(baseline_peak):>10}")
    print(f"  After 1 req     {_fmt(one_cur):>10}  {_fmt(one_peak):>10}")
    print(f"  After {BATCH} reqs  {_fmt(batch_cur):>10}  {_fmt(batch_peak):>10}")
    print(f"{'' * 56}")
    delta_1 = one_cur - baseline_cur
    delta_batch = batch_cur - one_cur
    print(f"  Alloc for 1st request    : {_fmt(delta_1)}")
    print(f"  Growth over {BATCH-1} more reqs : {_fmt(delta_batch)}")

    growth_per_req = delta_batch / (BATCH - 1) if BATCH > 1 else 0
    if abs(growth_per_req) < 512:
        verdict = "No significant per-request leak detected"
    else:
        verdict = f"WARNING: ~{_fmt(int(growth_per_req))}/req growth – investigate"
    print(f"  Verdict: {verdict}")
    print(f"{'=' * 56}")

    # Top allocations vs baseline
    top = snap_batch.compare_to(snap_baseline, "lineno")
    print("\n  Top 10 allocation sites (vs baseline):")
    print(f"  {'' * 70}")
    for stat in top[:10]:
        print(f"  {stat}")
    print()


if __name__ == "__main__":
    asyncio.run(_measure())
