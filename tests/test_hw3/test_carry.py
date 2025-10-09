import pytest
import project.hw3 as hw3

@pytest.mark.parametrize(
    "func, arity, arguments, expected",
    [
        (lambda: 42, 0, (), 42),
        (lambda x: x * 2, 1, (5,), 10),
        (lambda x, y, z: x + y * z, 3, (2, 3, 4), 14),
    ],
)
def test_curry_diffrent_arity(func, arity, arguments, expected):
    curried = hw3.curry_explicit(func, arity)
    result = curried
    if arity == 0:
        result = result()
    for i in arguments:
        result = result(i)
    assert result == expected

def test_curry_uncurry_roundtrip():
    """Test that uncurry(curry(f)) == f."""
    f = lambda a, b, c, d: a - b + c - d
    curried = hw3.curry_explicit(f, 4)
    uncurried = hw3.uncurry_explicit(curried, 4)
    
    args = (10, 2, 5, 1)
    assert uncurried(*args) == f(*args)
    assert curried(10)(2)(5)(1) == f(*args)


def test_uncurry_arity_0():
    """Test uncurrying a zero-argument curried function."""
    def f():
        return "hello"
    curried = hw3.curry_explicit(f, 0)
    uncurried = hw3.uncurry_explicit(curried, 0)
    assert uncurried() == "hello"


def test_uncurry_arity_mismatch():
    """Test that uncurry raises TypeError on wrong number of arguments."""
    f = lambda x, y: x + y
    curried = hw3.curry_explicit(f, 2)
    uncurried = hw3.uncurry_explicit(curried, 2)
    
    with pytest.raises(TypeError, match="Expected 2 arguments"):
        uncurried(1)  # too few
    
    with pytest.raises(TypeError, match="Expected 2 arguments"):
        uncurried(1, 2, 3)  # too many


def test_negative_arity():
    """Test that negative arity raises ValueError."""
    f = lambda x: x
    
    with pytest.raises(ValueError, match="Arity can be negative"):
        hw3.curry_explicit(f, -1)
    
    with pytest.raises(ValueError, match="Arity can be negative"):
        hw3.uncurry_explicit(f, -1)


def test_curry_with_builtin():
    """Test currying a built-in function with fixed arity."""
    def my_sum(a, b):
        return a + b
    
    curried = hw3.curry_explicit(my_sum, 2)
    assert curried(10)(20) == 30


def test_curry_arbitrary_arity_function():
    """Test that curry fixes the arity for arbitrary-arity functions."""
    captured = []
    def fake_print(*args):
        captured.append(args)
        return None
    
    curried_print = hw3.curry_explicit(fake_print, 2)
    result = curried_print("hello")("world")
    
    assert result is None
    assert captured == [("hello", "world")]
    


def test_curry_arity_0_returns_callable():
    """Ensure curry_explicit(f, 0) returns a callable, not f() result."""
    called = False
    def f():
        nonlocal called
        called = True
        return 999
    
    curried = hw3.curry_explicit(f, 0)
    assert not called
    assert callable(curried)
    result = curried()
    assert called
    assert result == 999


def test_uncurry_arity_0_returns_callable():
    """Ensure uncurry_explicit(curried, 0) returns a callable."""
    def f():
        return "test"
    
    curried = hw3.curry_explicit(f, 0)
    uncurried = hw3.uncurry_explicit(curried, 0)
    
    assert callable(uncurried)
    assert uncurried() == "test"


def test_curry_identity():
    """Test currying the identity function."""
    identity = lambda x: x
    curried = hw3.curry_explicit(identity, 1)
    assert curried(42) == 42


def test_curry_high_arity():
    """Test currying with higher arity (5 arguments)."""
    f = lambda a, b, c, d, e: a * b + c * d - e
    curried = hw3.curry_explicit(f, 5)
    result = curried(2)(3)(4)(5)(6)
    assert result == 20