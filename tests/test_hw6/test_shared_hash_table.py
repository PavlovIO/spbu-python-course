import threading
import random
import pytest
from project.hw6 import BST
from project.hw6 import ShardedHashTable


def test_parallel_inserts_and_reads():
    NUM_THREADS = 16
    NUM_KEYS = 1_000

    with ShardedHashTable(4) as table:

        def writer(thread_id):
            for i in range(thread_id * NUM_KEYS, (thread_id + 1) * NUM_KEYS):
                table[i] = i

        def reader():
            for _ in range(NUM_KEYS * NUM_THREADS):
                key = random.randint(0, NUM_KEYS * NUM_THREADS - 1)
                try:
                    _ = table[key]
                except KeyError:
                    pass

        writers = [
            threading.Thread(target=writer, args=(t,)) for t in range(NUM_THREADS)
        ]
        readers = [threading.Thread(target=reader) for _ in range(NUM_THREADS)]

        for w in writers:
            w.start()
        for r in readers:
            r.start()

        for w in writers:
            w.join()
        for r in readers:
            r.join()

        for i in range(NUM_THREADS * NUM_KEYS):
            assert table[i] == i, f"Key {i} has incorrect value"


def test_concurrent_updates_do_not_corrupt_data():
    with ShardedHashTable(2) as table:
        key = "shared_key"
        table[key] = 0
        ITERATIONS = 1000
        THREADS = 8
        lock = threading.Lock()
        total_sum = 0

        def updater():
            nonlocal total_sum
            for _ in range(ITERATIONS):
                with lock:
                    value = table[key]
                    new_value = value + 1
                    table[key] = new_value
                    total_sum += 1

        threads = [threading.Thread(target=updater) for _ in range(THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        expected = ITERATIONS * THREADS
        assert (
            table[key] == expected
        ), f"Data corruption: expected {expected}, got {table[key]}"
        assert total_sum == expected


def test_concurrent_inserts_and_deletes():
    with ShardedHashTable(4) as table:
        for i in range(10_000):
            table[i] = i

        def inserter():
            for i in range(10_000, 20_000):
                table[i] = i

        def deleter():
            for i in range(0, 10_000):
                try:
                    del table[i]
                except KeyError:
                    pass

        t1 = threading.Thread(target=inserter)
        t2 = threading.Thread(target=deleter)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        deleted = [i for i in range(0, 10_000) if i in table]
        added = [i for i in range(10_000, 20_000) if i not in table]
        assert (
            len(deleted) == 0
        ), f"Некоторые старые ключи не были удалены: {deleted[:10]}"
        assert len(added) == 0, f"Некоторые новые ключи не были вставлены: {added[:10]}"


def increment(cur_val, delta):
    return cur_val + delta


def test_atomic_upd_func():
    with ShardedHashTable(4) as table:
        table[0] = 100
        assert table[0] == 100
        table.atomic_update(0, increment, 1)
        assert table[0] == 101


def test_locking_behavior_under_high_contention():
    with ShardedHashTable(4) as table:
        NUM_THREADS = 8
        KEYS = 2000

        for k in range(KEYS):
            table[k] = 0

        def task():
            for _ in range(2000):
                k = random.randint(0, KEYS - 1)
                table.atomic_update(k, increment, 1)

        threads = [threading.Thread(target=task) for _ in range(NUM_THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        total = sum(table[k] for k in range(KEYS))
        assert (
            total == NUM_THREADS * 2000
        ), "Несогласованные обновления — блокировки не работают!"
