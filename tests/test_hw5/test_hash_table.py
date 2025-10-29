import pytest
from project.hw5 import HashTable, BST

# BST tests
@pytest.mark.parametrize(
    "key, value", [(5, "five"), ("age", 19), ("stats", (("age", 19), ("health", 21)))]
)
def test_BST_single_insertion(key, value):
    tree = BST()
    tree.root = tree.insert(tree.root, key, value)
    assert tree.root.key == key
    assert tree.root.value == value


@pytest.mark.parametrize(
    "key, value, new_value",
    [
        (5, "five", "FIVE"),
        ("age", 19, 20),
        ("stats", (("age", 19), ("health", 21)), "No Info"),
    ],
)
def test_BST_rewrite_insertion(key, value, new_value):
    tree = BST()
    tree.root = tree.insert(tree.root, key, value)
    assert tree.root.key == key
    assert tree.root.value == value

    tree.root = tree.insert(tree.root, key, new_value)
    assert tree.root.value == new_value


@pytest.mark.parametrize("key, value", [("key_10", 10), ("a", 125), ("key5", 5)])
def test_BST_search(key, value):
    tree = BST()
    for i in [5, 3, 7, 1, 6, 9, 8, 4, 0, 2]:
        tree.root = tree.insert(tree.root, f"key_{i}", i)
    tree.root = tree.insert(tree.root, key, value)
    node_key_4 = tree.find(tree.root, "key_4")
    new_node = tree.find(tree.root, key)
    # find tests
    assert node_key_4.value == 4
    assert new_node.value == value
    # __contains__ tests
    assert "key_5" in tree
    assert key in tree
    assert "non-existing_key" not in tree
    # __getitems__ tests
    assert tree["key_3"] == 3
    assert tree[key] == value
    with pytest.raises(KeyError):
        _ = tree["non-existing_key"]


@pytest.mark.parametrize(
    "key",
    [
        "key_5",  # delete root
        "key_1",  # delete leaf
        "key_3",  # delete node with 1 leafs
        "key_9",  # delete node with 1 leaf and 1 node
        "key_7",  # delete node with 2 leafs
    ],
)
def test_BST_deletion(key):
    tree = BST()
    for i in [5, 3, 7, 1, 6, 9, 8, 10]:
        tree.root = tree.insert(tree.root, f"key_{i}", i)
    assert key in tree
    tree.root = tree.delete(tree.root, key)
    assert key not in tree


def test_BST_delete_empty():
    tree = BST()
    tree.root = tree.delete(tree.root, "missing")
    assert tree.root is None


def test_BST_delete_nonexistent():
    tree = BST()
    tree.root = tree.insert(tree.root, "a", 1)
    tree.root = tree.delete(tree.root, "b")  # Should not crash
    assert "a" in tree


def test_BST_traversal():
    tree = BST()
    for i in [5, 3, 7, 1, 6, 9, 8, 4, 0, 2]:
        tree.root = tree.insert(tree.root, i, i)
    assert list(tree) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(reversed(tree)) == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]


def test_BST_minimum():
    tree = BST()
    assert tree.minimum(tree.root) == None
    for i in [5, 3, 7, 1, 6, 9, 8, 4, 0, 2]:
        tree.root = tree.insert(tree.root, i, i)
    assert tree.minimum(tree.root).key == 0
    assert tree.minimum(tree.root.right).key == 6


def test_BST_items():
    tree = BST()
    for k, v in [(2, "two"), (1, "one"), (3, "three")]:
        tree.root = tree.insert(tree.root, k, v)
    assert dict(tree.items()) == {1: "one", 2: "two", 3: "three"}


# HashTable tests
@pytest.mark.parametrize(
    "key, value", [(5, "five"), ("age", 19), ("stats", (("age", 19), ("health", 21)))]
)
def test_Hash_single_insertion(key, value):
    ht = HashTable()
    assert len(ht) == 0
    ht.insert(key, value)
    assert ht[key] == value
    assert len(ht) == 1


@pytest.mark.parametrize(
    "key, value, new_value",
    [
        (5, "five", "FIVE"),
        ("age", 19, 20),
        ("stats", (("age", 19), ("health", 21)), "No Info"),
    ],
)
def test_Hash_rewrite_insertion(key, value, new_value):
    ht = HashTable()
    ht[key] = value
    assert ht[key] == value
    ht[key] = new_value
    assert ht[key] == new_value


def test_Hash_basic_operators():
    ht = HashTable()
    for i in range(10):
        ht[f"key_{i}"] = i  # using __setitem__
    assert len(ht) == 10
    # __getitem__ tests
    assert ht["key_5"] == 5
    with pytest.raises(KeyError, match="definitely_missing"):
        _ = ht["definitely_missing"]
    # __contains__ tests
    assert "key_7" in ht
    assert "key_11" not in ht
    # __delitem__ tests
    del ht["key_9"]
    assert "key_9" not in ht
    assert len(ht) == 9


def test_Hash_None_insertion():
    ht = HashTable()
    ht[1] = None
    assert ht[1] is None


def test_Hash_delete_missing():
    ht = HashTable()
    ht["a"] = 1
    del ht["b"]
    assert len(ht) == 1


def test_Hash_resize():
    ht = HashTable(2)  # small to trigger
    ht[1] = "one"
    assert ht.max_size == 2
    ht[2] = "two"  # reshape triggered
    ht[3] = "three"
    assert ht.max_size == 4
    assert len(ht) == 3
    assert ht[1] == "one"
    assert ht[2] == "two"
    assert ht[3] == "three"


def test_Hash_collision_handling():
    ht = HashTable(4)
    ht[1] = "one"
    ht[5] = "four"
    bucket = ht.buckets[1]
    assert len(ht) == 2
    assert 1 in bucket
    assert 5 in bucket
    assert ht[1] == "one"
    assert ht[5] == "four"


def test_Hash_get():
    ht = HashTable()
    ht["1"] = "one"
    assert ht.get("1") == "one"
    assert ht.get("missing") is None
    assert ht.get("missing", "default") == "default"
