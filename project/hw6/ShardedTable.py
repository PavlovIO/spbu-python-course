from .HashTable_hw6 import HashTable
from typing import Optional, Any, Iterator, Callable
from multiprocessing import Queue, Process, cpu_count
from threading import Lock
from collections.abc import MutableMapping
import atexit


def request_handle(
    ht: HashTable, request: tuple[str, Any, Optional[Any], Optional[tuple[Any]]]
) -> Any:
    """
    Handles a single request to the hash table worker process.

    Args:
        ht: The local HashTable instance in the worker process.
        request: A tuple containing (operation, key, value, args).
                 - operation: The type of operation to perform (e.g., "get", "set", "atomic_upd").
                 - key: The key for the operation.
                 - value: The value for operations like "set" or the function for "atomic_upd".
                 - args: Additional arguments for the function in "atomic_upd".

    Returns:
        A tuple (status, result), where:
        - status: "ok" for success, "error" for failure.
        - result: The result of the operation on success, or an exception object on failure.
    """
    try:
        op, key, val, args = (
            request[0],
            request[1] if len(request) > 1 else None,
            request[2] if len(request) > 2 else None,
            request[3] if len(request) > 3 else None,
        )
        if op == "get":
            out = ht[key]
            return ("ok", out)
        elif op == "set":
            ht.insert(key, val)
            return ("ok", None)
        elif op == "del":
            ht.delete(key)
            return ("ok", None)
        elif op == "len":
            l = len(ht)
            return ("ok", l)
        elif op == "keys":
            keys = ht.keys()
            return ("ok", keys)
        elif op == "atomic_upd":
            if val is None or not callable(val):
                return ("error", ValueError("Atomic_upd requires func to be Callable"))
            assert val is not None
            current_value = ht[key]
            new_value = val(current_value, *args)
            ht[key] = new_value
            return ("ok", new_value)
        elif op == "max_size":
            ms = ht.max_size
            return ("ok", ms)
        else:
            return ("error", ValueError(f"Unknown operation: {op}"))
    except Exception as e:
        return ("error", e)


def sharded_worker(request_queue: Queue, response_queue: Queue):
    """
    Worker process function that handles requests for a single shard.

    Continuously reads requests from the request queue, processes them using
    the local HashTable instance, and sends the result to the response queue.

    Args:
        request_queue: Queue to receive requests from the main process.
        response_queue: Queue to send responses back to the main process.
    """
    ht = HashTable()
    while True:
        request = request_queue.get()
        if request[0] == "stop":
            break
        response = request_handle(ht, request)
        response_queue.put(response)


class ShardedHashTable(MutableMapping):
    """
    A thread-safe hash table implemented using sharding and multiprocessing.

    Data is distributed across multiple shards (sub-tables), each managed by a separate
    worker process. This allows for concurrent access while maintaining data integrity
    through atomic operations within each shard.
    """

    def __init__(self, shard_num: int = 0):
        """
        Initializes the ShardedHashTable.

        Args:
            shard_num: The number of shards to create, not more than number of CPU cores. If 0, uses the number of CPU cores.
        """
        max_shards = cpu_count()
        if shard_num == 0:
            self.shard_num = cpu_count()
        else:
            self.shard_num = max(max_shards, shard_num)

        self.locks: list[Lock] = [Lock() for _ in range(self.shard_num)]
        self.request_queue: list[Queue] = [Queue() for _ in range(self.shard_num)]
        self.response_queue: list[Queue] = [Queue() for _ in range(self.shard_num)]
        self.workers: list[Process] = []
        for i in range(self.shard_num):
            p = Process(
                target=sharded_worker,
                args=[self.request_queue[i], self.response_queue[i]],
            )
            p.start()
            self.workers.append(p)
        self.max_size = 0
        for i in range(self.shard_num):
            with self.locks[i]:
                self.request_queue[i].put(("max_size",))
                ms = self.response_queue[i].get()
                if ms[0] == "error":
                    raise ms[1]
                self.max_size += ms[1]

        atexit.register(self.close)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Sets the value for a given key in the hash table.

        Args:
            key: The key to set.
            value: The value to associate with the key.
        """
        shard_id = hash(key) % self.shard_num
        with self.locks[shard_id]:
            self.request_queue[shard_id].put(("set", key, value))
            response = self.response_queue[shard_id].get()
            if response[0] == "error":
                raise response[1]

    def __getitem__(self, key: Any) -> Any:
        """
        Gets the value for a given key from the hash table.

        Args:
            key: The key to retrieve the value for.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key is not found.
        """
        shard_id = hash(key) % self.shard_num
        with self.locks[shard_id]:
            self.request_queue[shard_id].put(("get", key))
            response = self.response_queue[shard_id].get()
            if response[0] == "ok":
                return response[1]
            else:
                raise response[1]

    def __delitem__(self, key: Any) -> None:
        """
        Removes a key-value pair from the hash table.

        Args:
            key: The key to remove.

        Raises:
            KeyError: If the key is not found.
        """
        shard_id = hash(key) % self.shard_num
        with self.locks[shard_id]:
            self.request_queue[shard_id].put(("del", key))
            response = self.response_queue[shard_id].get()
            if response[0] == "error":
                raise response[1]

    def __len__(self) -> int:
        """
        Returns the total number of key-value pairs in the hash table.

        Note: This operation acquires locks sequentially for each shard,
        which can be slow under high concurrency.

        Returns:
            The total number of items across all shards.
        """
        l = 0
        for i in range(self.shard_num):
            with self.locks[i]:
                self.request_queue[i].put(("len",))
                lq = self.response_queue[i].get()
                if lq[0] == "error":
                    raise lq[1]
                else:
                    l += lq[1]
        return l

    def __iter__(self) -> Iterator:
        """
        Iterates over all keys in the hash table.

        Note: This operation acquires locks sequentially for each shard,
        which can be slow under high concurrency.

        Yields:
            Keys from all shards.
        """
        for i in range(self.shard_num):
            with self.locks[i]:
                self.request_queue[i].put(("keys",))
                response = self.response_queue[i].get()
                if response[0] == "error":
                    raise response[1]
                yield from response[1]

    def close(self) -> None:
        """
        Closes the ShardedHashTable and terminates all worker processes.

        Sends a "stop" signal to each worker process and waits for them to finish.
        This method is called automatically when the object is garbage collected
        or when the program exits via atexit.
        """
        for q in self.request_queue:
            q.put(("stop",))
        for p in self.workers:
            p.join()

    def __enter__(self):
        """
        Context manager entry point.

        Returns:
            The ShardedHashTable instance itself.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.

        Ensures the ShardedHashTable is closed properly, even if an exception occurs.
        """
        try:
            self.close()
        except Exception as e:
            print(f"Exception was raised during context exit: {e}")

    def atomic_update(self, key: Any, func: Callable, *args) -> Any:
        """
        Atomically applies a function to the value associated with a key.

        This operation is performed entirely within a single shard worker process,
        ensuring atomicity. The function is applied as: new_value = func(current_value, *args).

        Args:
            key: The key whose value will be updated.
            func: A callable that takes the current value and optional arguments, and returns a new value.
                  Must be serializable (e.g., defined at module level).
            *args: Additional arguments to pass to the function.

        Returns:
            The new value after applying the function.

        Raises:
            Exception: If the function raises an exception or if the key is not found.
        """
        shard_id = hash(key) % self.shard_num
        with self.locks[shard_id]:
            self.request_queue[shard_id].put(("atomic_upd", key, func, args))
            response = self.response_queue[shard_id].get()
            if response[0] == "error":
                raise response[1]
            return response[1]
