from .HashTable_hw6 import HashTable
from typing import Optional, Any, Iterator
from multiprocessing import Queue, Process, cpu_count
from threading import Lock
from collections.abc import MutableMapping

def request_handle(ht: HashTable, request: tuple[str, Any, Optional[Any]]) -> Any:
    try:
        op, key, val = request[0], request[1], request[2] if len(request)>2 else None
        if op == "get":
            try:    
                out = ht[key]
                return ("ok", out)
            except KeyError as e:
                return ("error", e)
        elif op == "set":
            try:
                ht.insert(key, val)
                return ("ok", None)
            except Exception as e:
                return ("error", e)
        elif op == "del":
            try:
                ht.delete(key)
                return ("ok", None)
            except Exception as e:
                return ("error", e)
        elif op == "len":
            try:
                l = len(ht)
                return ("ok", l)
            except Exception as e:
                return ("error", e)
        elif op == "keys":
            try:
                keys = ht.keys()
                return ("ok", keys)
            except Exception as e:
                return ("error", e)
        else:
            return ("error", ValueError(f"Unknown operation: {op}"))
    except Exception as e:
        return ("error", e)
    
def sharded_worker(request_queue: Queue, response_queue: Queue):
    ht = HashTable()
    while True:
        request = request_queue.get()
        if request[0] == "stop":
            break
        response = request_handle(ht, request)
        response_queue.put(response)

class ShardedHashTable(MutableMapping):
    def __init__(self, shard_num: int = 0):
        if shard_num == 0:
            self.shard_num = cpu_count()
        else:
            self.shard_num = shard_num
        self.locks: list[Lock] = [Lock() for _ in range(self.shard_num)]
        self.request_queue: list[Queue] = [Queue() for _ in range(self.shard_num)]
        self.response_queue: list[Queue] = [Queue() for _ in range(self.shard_num)]
        self.workers = []
        for i in range(self.shard_num):
            p = Process(target=sharded_worker, args=[self.request_queue[i], self.response_queue[i]])
            p.start()
            self.workers.append(p)
    
    def __setitem__(self, key: Any, value: Any) -> None:
        shard_id = hash(key)%self.shard_num
        with self.locks[shard_id]:
            self.request_queue[shard_id].put(("set", key, value))
            response = self.response_queue[shard_id].get()
            if response[0] == "error":
                raise response[1]
    
    def __getitem__(self, key: Any) -> Any:
        shard_id = hash(key)%self.shard_num
        with self.locks[shard_id]:
            self.request_queue[shard_id].put(("get", key))
            response = self.response_queue[shard_id].get()
            if response[0] == "ok":
                return response[1]
            else:
                raise response[1]

    def __delitem__(self, key: Any) -> None:
        shard_id = hash(key)%self.shard_num
        with self.locks[shard_id]:
            self.request_queue[shard_id].put(("del", key))
            response = self.response_queue[shard_id].get()
            if response[0] == "error":
                raise response[1]

    def __len__(self) -> int:
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
        for i in range(self.shard_num):
            with self.locks[i]:
                self.request_queue[i].put(("keys",))
                response = self.response_queue[i].get()
                if response[0] == "error":
                    raise response[1]
                yield from response[1]

    def close(self) -> None:
        for q in self.request_queue:
            q.put(("stop",))
        for p in self.workers:
            p.join()
