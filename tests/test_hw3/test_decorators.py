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
        config["modified"] = "changed"
        return config

    original = {"version": 1}
    result = modify_config(config=original)

    assert result["modified"] == "changed"
    assert "modified" not in original
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
        def bad_func(data=hw3.Isolated(), /):
            return data


def test_evaluated_keyword_only():
    """Test Evaluated with keyword-only arguments."""
    call_count = 0

    def get_counter():
        nonlocal call_count
        call_count += 1
        return call_count

    @hw3.smart_args
    def get_number(*, x=get_counter(), seed=hw3.Evaluated(get_counter)):
        return (x, seed)

    num1 = get_number()
    num2 = get_number()

    assert num1 == (1, 2)
    assert num2 == (1, 3)


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
    """Test that cache_func and smart_args work together correctly.

    This test verifies that:
    1. smart_args evaluates the dynamic default (Evaluated) on first call
    2. cache_func caches the result of the first call
    3. On second call, cache_func returns cached result WITHOUT calling the function again
    4. Therefore, Evaluated is only evaluated once, not twice
    """
    call_count = 0
    eval_count = 0

    def dynamic_value():
        nonlocal eval_count
        eval_count += 1
        return 100 + eval_count

    @hw3.cache_func(maxsize=2)
    @hw3.smart_args
    def composed_func(*, x=hw3.Evaluated(dynamic_value)):
        nonlocal call_count
        call_count += 1
        return x

    # First call:
    # - smart_args calls dynamic_value() → returns 101
    # - function body executes → call_count = 1
    # - cache_func stores result 101
    result1 = composed_func()

    # Second call:
    # - smart_args would normally call dynamic_value(), BUT...
    # - cache_func sees same arguments and returns cached result
    # - function body is NOT executed → call_count remains 1
    # - dynamic_value is NOT called again → eval_count remains 1
    result2 = composed_func()

    assert result1 == 101
    assert result2 == 101
    assert call_count == 1
    assert eval_count == 1

    # Third call with different argument (bypasses cache)
    result3 = composed_func(x=999)
    assert result3 == 999
    assert call_count == 2
    assert eval_count == 1


def test_smart_args_isolated_and_evaluated_together():
    """Test simultaneous use of Isolated and Evaluated on different arguments."""
    eval_count = 0

    def get_timestamp():
        nonlocal eval_count
        eval_count += 1
        return f"time_{eval_count}"

    @hw3.smart_args
    def process_data(data=hw3.Isolated(), timestamp=hw3.Evaluated(get_timestamp)):
        data["processed"] = "True"
        data["timestamp"] = timestamp
        return data

    original_data = {"id": 123, "value": "test"}

    result1 = process_data(data=original_data)
    result2 = process_data(data=original_data)

    assert "processed" not in original_data
    assert result1["processed"] == "True"
    assert result2["processed"] == "True"

    assert result1["timestamp"] == "time_1"
    assert result2["timestamp"] == "time_2"
    assert eval_count == 2


def test_smart_args_isolated_evaluated_keyword_args():
    """Test Isolated and Evaluated with regular keyword arguments (no *)."""
    call_count = 0

    def get_default_value():
        nonlocal call_count
        call_count += 1
        return call_count

    @hw3.smart_args
    def configure(
        config=hw3.Isolated(), timeout=hw3.Evaluated(get_default_value), retries=3
    ):
        config["timeout"] = timeout
        config["retries"] = retries
        return config

    original_config = {"name": "service", "enabled": True}

    result1 = configure(config=original_config, retries=2)
    result2 = configure(config=original_config, timeout=999)

    assert "timeout" not in original_config
    assert "retries" not in original_config
    assert original_config == {"name": "service", "enabled": True}

    assert result1["timeout"] == 1
    assert result2["timeout"] == 999
    assert call_count == 1

    assert result1["retries"] == 2
    assert result2["retries"] == 3
