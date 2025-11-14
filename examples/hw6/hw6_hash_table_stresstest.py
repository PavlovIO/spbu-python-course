import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from project.hw6 import HashTable

print("start")


def main() -> None:
    NUM_OPS = 5_000_000
    READ_RATIO = 0.8
    UNIQUE_KEYS = 10_000
    print("_1_")
    table = HashTable(40_000)
    for i in range(UNIQUE_KEYS):
        table[i] = i

    print("_2_")
    start = time.perf_counter()

    def worker():
        rng = random.Random(5)
        local_errors = 0
        for _ in range(NUM_OPS):
            op_type = "get" if rng.random() < READ_RATIO else rng.choice(("set","del"))
            key = rng.randint(0, UNIQUE_KEYS - 1)
            if op_type == "get":
                try:
                    _ = table[key]
                except KeyError:
                    pass
                except Exception:
                    local_errors += 1
            elif op_type == "set":
                try:
                    table[key] = rng.randint(0, 10_000_000)
                except Exception:
                    local_errors += 1
            else:
                try:
                    del table[key]
                except KeyError:
                    pass
                except Exception:
                    local_errors += 1
        return local_errors

    print("_3_")
    total_errors = worker()

    print("_4_")
    end = time.perf_counter()
    elapsed = end - start
    ops_per_sec = NUM_OPS / elapsed

    print(
        f"\nCompleted {NUM_OPS:,} operations in {elapsed:.2f}s "
        f"({ops_per_sec:,.0f} ops/sec)"
    )
    print(f"Total errors: {total_errors}")

    assert total_errors == 0, f"Encountered {total_errors} unexpected errors"


if __name__ == "__main__":
    main()
