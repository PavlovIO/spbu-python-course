from typing import Optional, Any, Generator, Iterator
from collections.abc import MutableMapping


class Node:
    """A node in a binary search tree (BST).

    Attributes:
        key: The key used for ordering in the BST.
        value: The associated value stored with the key.
        left: Left child node (keys less than this node's key).
        right: Right child node (keys greater than this node's key).
    """

    def __init__(self, key: Any, value: Any) -> None:
        self.key = key
        self.value = value
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None


class BST:
    """A binary search tree (BST) implementation.

    Supports insertion, deletion, search, and in-order iteration.
    Keys must be comparable (support <, >, ==).
    """

    def __init__(self, root: Optional[Node] = None) -> None:
        self.root = root

    def find(self, root: Optional[Node], key: Any) -> Optional[Node]:
        """Recursively search for a node with the given key.
        Args:
            root: The root node to start searching from.
            key: The key to search for.
        Returns:
            The node containing the key, or None if not found.
        """
        if root is None or key == root.key:
            return root
        if key < root.key:
            return self.find(root.left, key)
        else:
            return self.find(root.right, key)

    def minimum(self, root: Optional[Node]) -> Optional[Node]:
        """Find the node with the smallest key in the subtree.
        Args:
            root: The root of the subtree to search.
        Returns:
            The node with the minimum key, or None if subtree is empty.
        """
        if root is None:
            return None
        if root.left is None:
            return root
        return self.minimum(root=root.left)

    def insert(self, root: Optional[Node], key: Any, value: Any) -> Node:
        """Insert a key-value pair into the BST.
        If the key already exists, its value is updated.
        Args:
            root: The root node of the current subtree.
            key: The key to insert (must be comparable).
            value: The value associated with the key.
        Returns:
            The root of the (possibly updated) subtree.
        """
        if root is None:
            return Node(key, value)
        elif key < root.key:
            root.left = self.insert(root.left, key, value)
        elif key > root.key:
            root.right = self.insert(root.right, key, value)
        else:
            root.value = value
        return root

    def delete(self, root: Optional[Node], key: Any) -> Optional[Node]:
        """Delete a node with the given key from the BST.
        Args:
            root: The root node of the current subtree.
            key: The key to delete.
        Returns:
            The root of the (possibly updated) subtree.
        """
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
        """Yield key-value pairs in ascending key order."""
        for key in self:
            yield (key, self[key])

    def _inorder(self, node: Optional[Node]) -> Generator:
        """In-order traversal generator (left, root, right)."""
        if node is not None:
            yield from self._inorder(node.left)
            yield node.key
            yield from self._inorder(node.right)

    def _rev_inorder(self, node: Optional[Node]) -> Generator:
        """Reverse in-order traversal generator (right, root, left)."""
        if node is not None:
            yield from self._rev_inorder(node.right)
            yield node.key
            yield from self._rev_inorder(node.left)

    def __iter__(self) -> Iterator:
        """Iterate over keys in ascending order."""
        return self._inorder(self.root)

    def __reversed__(self) -> Iterator:
        """Iterate over keys in descending order."""
        return self._rev_inorder(self.root)

    def __getitem__(self, key: Any) -> Any:
        """Get the value associated with the given key.
        Raises:
            KeyError: If the key is not found.
        """
        node = self.find(self.root, key)
        if node is not None:
            return node.value
        else:
            raise KeyError(key)

    def __contains__(self, key: Any) -> bool:
        """Check if the key exists in the BST."""
        return self.find(self.root, key) is not None


class HashTable(MutableMapping):
    """A hash table implementation using BSTs for collision resolution.

    Each bucket is a binary search tree, so keys must be both hashable and comparable.
    Automatically resizes when load factor exceeds 0.75.
    """

    def __init__(self, max_size: int = 16) -> None:
        self.max_size = max_size
        self.buckets: list = [None] * self.max_size
        self.size = 0

    def insert(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair.

        Resizes the table if the load factor exceeds 0.75.
        """
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

    def delete(self, key: Any) -> None:
        """Remove a key-value pair if it exists."""
        hash_key = hash(key) % self.max_size
        bucket = self.buckets[hash_key]
        if bucket is None or key not in bucket:
            return
        bucket.root = bucket.delete(bucket.root, key)
        self.size -= 1

    def reshape(self, new_size: Optional[int] = None):
        """Resize the hash table to a new size (default: double current size).

        Rehashes all existing key-value pairs into the new bucket array.
        """
        if new_size is None:
            new_size = self.max_size * 2
        new_buckets: list = [None] * new_size
        for key, value in self.items():
            hash_key = hash(key) % new_size
            bucket = new_buckets[hash_key]
            if bucket is None:
                new_buckets[hash_key] = BST()
                bucket = new_buckets[hash_key]
            bucket.root = bucket.insert(bucket.root, key, value)
        self.max_size = new_size
        self.buckets = new_buckets

    def __getitem__(self, key: Any) -> Any:
        """Get the value for the given key.

        Raises:
            KeyError: If the key is not found.
        """
        hash_key = hash(key) % self.max_size
        bucket = self.buckets[hash_key]
        if self.buckets[hash_key] is None:
            raise KeyError(key)
        node = bucket.find(bucket.root, key)
        if node is not None:
            return node.value
        else:
            raise KeyError(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair."""
        return self.insert(key, value)

    def __delitem__(self, key: Any) -> None:
        """Delete a key-value pair if it exists."""
        self.delete(key)

    def __len__(self) -> int:
        """Return the number of key-value pairs in the table."""
        return self.size

    def __iter__(self) -> Iterator:
        """Iterate over all keys in the hash table (no guaranteed order)."""
        for bucket in self.buckets:
            if bucket is not None:
                yield from bucket

    def __str__(self) -> str:
        """Return a string representation of the hash table (like a dict)."""
        out = "{"
        for tree in self.buckets:
            if tree is None:
                continue
            for key, value in tree.items():
                out += f"{key}: {value}, "
        return out[:-2] + "}" if out != "{" else "{}"
