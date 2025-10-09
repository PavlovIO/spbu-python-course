import pytest
import project.hw3 as hw3


def test_cache_basic():
    """Test basic caching functionality."""
    call_count = 0

    @hw3.cache_func(maxsize=2)
    def add(x, y):
        nonlocal call_count
        call_count += 1
        return x + y

    assert add(1, 2) == 3
    assert call_count == 1
    assert add(1, 2) == 3  # cached
    assert call_count == 1
    assert add(3, 4) == 7
    assert call_count == 2


def test_cache_fifo_eviction():
    """Test FIFO eviction policy."""
    call_count = 0

    @hw3.cache_func(maxsize=2)
    def mul(x, y):
        nonlocal call_count
        call_count += 1
        return x * y

    assert mul(1, 2) == 2
    assert mul(3, 4) == 12
    assert mul(5, 6) == 30
    assert mul(1, 2) == 2
    assert call_count == 4


def test_cache_zero_maxsize():
    """Test that maxsize <= 0 disables caching."""
    call_count = 0

    @hw3.cache_func(maxsize=0)
    def f(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    assert f(5) == 10
    assert f(5) == 10
    assert call_count == 2


def test_cache_negative_maxsize():
    """Test that negative maxsize disables caching."""
    call_count = 0

    @hw3.cache_func(maxsize=-1)
    def f(x):
        nonlocal call_count
        call_count += 1
        return x

    assert f(1) == 1
    assert f(1) == 1
    assert call_count == 2


def test_cache_unhashable_args():
    """Test that unhashable arguments bypass caching."""
    call_count = 0

    @hw3.cache_func(maxsize=2)
    def process(lst):
        nonlocal call_count
        call_count += 1
        return sum(lst)

    assert process([1, 2, 3]) == 6
    assert process([1, 2, 3]) == 6
    assert call_count == 2


def test_isolated_keyword_only():
    """Test Isolated with keyword-only arguments (default behavior)."""

    @hw3.smart_args
    def modify_config(*, config=hw3.Isolated()):
        config["modified"] = True
        return config

    original = {"version": 1}
    result = modify_config(config=original)

    assert result["modified"] is True
    assert "modified" not in original  # original unchanged
    assert original == {"version": 1}


def test_isolated_positional_allowed():
    """Test Isolated with positional arguments when pos_args=True."""

    @hw3.smart_args(pos_args=True)
    def process_data(data=hw3.Isolated(), multiplier=2):
        data["result"] = data.get("value", 0) * multiplier
        return data

    original = {"value": 5}
    result = process_data(original)

    assert result["result"] == 10
    assert "result" not in original


def test_isolated_positional_not_allowed():
    """Test that Isolated raises AssertionError for positional args when pos_args=False."""
    with pytest.raises(AssertionError, match="Positioanal argument"):

        @hw3.smart_args(pos_args=False)
        def bad_func(data=hw3.Isolated()):
            return data


def test_evaluated_keyword_only():
    """Test Evaluated with keyword-only arguments."""
    import random

    random.seed(42)

    @hw3.smart_args
    def get_number(*, seed=hw3.Evaluated(lambda: random.randint(1, 100))):
        return seed

    num1 = get_number()
    num2 = get_number()

    assert isinstance(num1, int)
    assert isinstance(num2, int)


def test_evaluated_positional_allowed():
    """Test Evaluated with positional arguments when pos_args=True."""
    call_count = 0

    def counter():
        nonlocal call_count
        call_count += 1
        return call_count

    @hw3.smart_args(pos_args=True)
    def track_calls(value=hw3.Evaluated(counter)):
        return value

    val1 = track_calls()
    val2 = track_calls()

    assert val1 == 1
    assert val2 == 2


def test_evaluated_with_explicit_arg():
    """Test that Evaluated is not called when argument is provided explicitly."""
    call_count = 0

    def never_called():
        nonlocal call_count
        call_count += 1
        return 999

    @hw3.smart_args
    def use_default(*, x=hw3.Evaluated(never_called)):
        return x

    result = use_default(x=42)
    assert result == 42
    assert call_count == 0


def test_smart_args_no_special_defaults():
    """Test that functions without Isolated/Evaluated work normally."""

    @hw3.smart_args
    def normal_func(a, b=10):
        return a + b

    assert normal_func(5) == 15
    assert normal_func(5, 20) == 25


def test_deepcopy_nested_structures():
    """Test that Isolated performs deep copy on nested structures."""

    @hw3.smart_args
    def modify_nested(*, data=hw3.Isolated()):
        data["nested"]["value"] = 999
        return data

    original = {"nested": {"value": 1}}
    result = modify_nested(data=original)

    assert result["nested"]["value"] == 999
    assert original["nested"]["value"] == 1  # deep copy preserved original


def test_cache_and_smart_args_composition():
    """Test that cache_func and smart_args can be composed."""
    call_count = 0

    @hw3.cache_func(maxsize=2)
    @hw3.smart_args
    def cached_func(*, x=hw3.Evaluated(lambda: 42)):
        nonlocal call_count
        call_count += 1
        return x

    result1 = cached_func()
    result2 = cached_func()

    assert call_count == 1
    assert result1 == result2 == 42
