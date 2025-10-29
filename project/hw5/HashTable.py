from typing import Optional, Any, Generator, Iterator


class Node:
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None


class BST:
    def __init__(self, root: Optional[Node] = None) -> None:
        self.root = root

    def find(self, root: Optional[Node], key) -> Optional[Node]:
        if root is None or key == root.key:
            return root
        if key < root.key:
            return self.find(root.left, key)
        else:
            return self.find(root.right, key)

    def minimum(self, root: Optional[Node]) -> Optional[Node]:
        if root is None:
            return None
        if root.left is None:
            return root
        return self.minimum(root=root.left)

    def insert(self, root: Optional[Node], key, value) -> Node:
        if root is None:
            return Node(key, value)
        elif key < root.key:
            root.left = self.insert(root.left, key, value)
        elif key > root.key:
            root.right = self.insert(root.right, key, value)
        else:
            root.value = value
        return root

    def delete(self, root: Optional[Node], key) -> Optional[Node]:
        if root is None:
            return root
        if key < root.key:
            root.left = self.delete(root.left, key)
        elif key > root.key:
            root.right = self.delete(root.right, key)
        elif root.left is not None and root.right is not None:
            suc = self.minimum(root.right)
            assert suc is not None
            root.key = suc.key
            root.value = suc.value
            root.right = self.delete(root.right, root.key)
        else:
            if root.left is not None:
                root = root.left
            elif root.right is not None:
                root = root.right
            else:
                root = None
        return root

    def items(self) -> Generator:
        for key in self:
            yield (key, self[key])

    def _inorder(self, node) -> Generator:
        if node is not None:
            yield from self._inorder(node.left)
            yield node.key
            yield from self._inorder(node.right)

    def _rev_inorder(self, node) -> Generator:
        if node is not None:
            yield from self._rev_inorder(node.right)
            yield node.key
            yield from self._rev_inorder(node.left)

    def __iter__(self) -> Iterator:
        return self._inorder(self.root)

    def __reversed__(self) -> Iterator:
        return self._rev_inorder(self.root)

    def __getitem__(self, key) -> Any:
        node = self.find(self.root, key)
        if node is not None:
            return node.value
        else:
            raise KeyError(key)

    def __contains__(self, key) -> bool:
        return self.find(self.root, key) is not None


class HashTable:
    def __init__(self, max_size=16) -> None:
        self.max_size = max_size
        self.buckets: list = [None] * self.max_size
        self.size = 0

    def insert(self, key, value) -> None:
        if self.size >= self.max_size * 0.75:
            self.reshape()
        hash_key = hash(key) % self.max_size
        bucket = self.buckets[hash_key]
        if bucket is None:
            self.buckets[hash_key] = BST()
            bucket = self.buckets[hash_key]
        if key not in bucket:
            self.size += 1
        bucket.root = bucket.insert(bucket.root, key, value)

    def delete(self, key) -> None:
        hash_key = hash(key) % self.max_size
        bucket = self.buckets[hash_key]
        if bucket is None or key not in bucket:
            return
        bucket.root = bucket.delete(bucket.root, key)
        self.size -= 1

    def get(self, key, default=None) -> Any:
        hash_key = hash(key) % self.max_size
        bucket = self.buckets[hash_key]
        if bucket is None:
            return default
        node = bucket.find(bucket.root, key)
        if node is not None:
            return node.value
        else:
            return default

    def items(self) -> Generator:
        for tree in self.buckets:
            if tree is not None:
                for key, value in tree.items():
                    yield (key, value)

    def reshape(self, new_size: int | None = None):
        if new_size is None:
            new_size = self.max_size * 2
        self.max_size = new_size
        new_buckets: list = [None] * self.max_size
        for (key, value) in self.items():
            hash_key = hash(key) % self.max_size
            bucket = new_buckets[hash_key]
            if bucket is None:
                new_buckets[hash_key] = BST()
                bucket = new_buckets[hash_key]
            bucket.root = bucket.insert(bucket.root, key, value)
        self.buckets = new_buckets

    def __getitem__(self, key) -> Any:
        hash_key = hash(key) % self.max_size
        bucket = self.buckets[hash_key]
        if self.buckets[hash_key] is None:
            raise KeyError(key)
        node = bucket.find(bucket.root, key)
        if node is not None:
            return node.value
        else:
            raise KeyError(key)

    def __setitem__(self, key, value) -> None:
        return self.insert(key, value)

    def __delitem__(self, key) -> None:
        self.delete(key)

    def __len__(self) -> int:
        return self.size

    def __contains__(self, key) -> bool:
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __str__(self) -> str:
        out = "{"
        for tree in self.buckets:
            if tree is None:
                continue
            for key, value in tree.items():
                out += f"{key}: {value}, "
        return out[:-2] + "}" if out != "{" else "{}"
