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
        """Iteratively search for a node with the given key.
        Args:
            root: The root node to start searching from.
            key: The key to search for.
        Returns:
            The node containing the key, or None if not found.
        """
        node = root
        while node is not None:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return node

    def minimum(self, root: Optional[Node]) -> Optional[Node]:
        """Find the node with the smallest key in the subtree.
        Args:
            root: The root of the subtree to search.
        Returns:
            The node with the minimum key, or None if subtree is empty.
        """
        node = root
        if node is None:
            return None
        while node.left is not None:
            node = node.left
        return node

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
        node = root
        while True:
            if key == node.key:
                node.value = value
                break
            elif key < node.key:
                if node.left is None:
                    node.left = Node(key, value)
                    break
                else:
                    node = node.left
            else:
                if node.right is None:
                    node.right = Node(key, value)
                    break
                else:
                    node = node.right
        return root

    def delete(self, root: Optional[Node], key: Any) -> Optional[Node]:
        """Delete a node with the given key from the BST.
        Args:
            root: The root node of the current subtree.
            key: The key to delete.
        Returns:
            The root of the (possibly updated) subtree.
        """
        node = root
        prev = None
        #find node
        while node is not None:
            if key == node.key:
                break
            elif key < node.key:
                prev = node
                node = node.left
            else:
                prev = node
                node = node.right
        #case no node or root
        if node is None:
            return root
        #case node is root
        if prev is None:
            if node.left is None and node.right is None:# node is leaf - just delete
                return None
            elif node.left is not None or node.right is not None:# node is not leaf
                if node.left is None:# node have only right
                    return node.right
                elif node.right is None:# node have only left
                    return node.left
                else:# node have both left and right
                    suc = node.right
                    par = node
                    while suc.left is not None:
                        par = suc
                        suc = suc.left
                    n_key = suc.key
                    n_value = suc.value
                    if suc == node.right:
                        node.right = suc.right
                    else:
                        par.left = suc.right
                    node.key = n_key
                    node.value = n_value
                    return node
        #case node is no root
        else:
            if node.left is None and node.right is None:# node is leaf - just delete
                if node.key < prev.key:
                    prev.left = None
                else:
                    prev.right = None
            elif node.left is not None or node.right is not None:# node is not leaf
                if node.left is None:# node have only right
                    if node.key < prev.key:
                        prev.left = node.right
                    else:
                        prev.right = node.right
                elif node.right is None:# node have only left
                    if node.key < prev.key:
                        prev.left = node.left
                    else:
                        prev.right = node.left
                else:# node have both left and right
                    suc = node.right
                    par = node
                    while suc.left is not None:
                        par = suc
                        suc = suc.left
                    n_key = suc.key
                    n_value = suc.value
                    if suc == node.right:
                        node.right = suc.right
                    else:
                        par.left = suc.right
                    node.key = n_key
                    node.value = n_value
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
        self.size = 0
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
