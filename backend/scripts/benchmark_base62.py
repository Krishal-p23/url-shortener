"""Run a small local benchmark for the Base62 utility."""

import time

from app.utils.base62 import encode_base62


def main() -> None:
    iterations = 100_000
    started = time.perf_counter()
    for value in range(iterations):
        encode_base62(value)
    elapsed = time.perf_counter() - started
    operations_per_second = iterations / elapsed
    print(f"Base62 encode: {operations_per_second:,.0f} operations/second")
    print(f"Iterations: {iterations:,}; elapsed: {elapsed:.4f}s")


if __name__ == "__main__":
    main()