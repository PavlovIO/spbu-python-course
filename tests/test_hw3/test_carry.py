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

def test_curry_single_arg_at_a_time():
    """Test that curry_explicit functions accept only one argument at a time."""
    def f(a, b, c):
        return a + b + c
    
    curried = hw3.curry_explicit(f, 3)

    step1 = curried(1)
    step2 = step1(2)
    result = step2(3)
    assert result == 6   
    with pytest.raises(TypeError, match="takes 1 positional argument but"):
        curried(1, 2)
    with pytest.raises(TypeError, match="takes 1 positional argument but"):
        curried(1)(2, 3)

def test_curry_uncurry_roundtrip():
    """Test that uncurry(curry(f)) == f."""
    f = lambda a, b, c, d: a - b + c - d
    curried = hw3.curry_explicit(f, 4)
    uncurried = hw3.uncurry_explicit(curried, 4)

    args = (10, 2, 5, 1)
    assert uncurried(*args) == f(*args)
    assert curried(10)(2)(5)(1) == f(*args)

def test_uncurry_builtin_functions():
    """Test uncurrying with built-in functions."""
    curried_max = hw3.curry_explicit(max, 2)
    uncurried_max = hw3.uncurry_explicit(curried_max, 2)
    assert uncurried_max(10, 20) == 20
    
    curried_pow = hw3.curry_explicit(pow, 2)
    uncurried_pow = hw3.uncurry_explicit(curried_pow, 2)
    assert uncurried_pow(2, 3) == 8

def test_uncurry_arity_0():
    """Test uncurrying a zero-argument curried function."""

    def f():
        return "hello"

    curried = hw3.curry_explicit(f, 0)
    uncurried = hw3.uncurry_explicit(curried, 0)
    assert uncurried() == "hello"

def test_uncurry_arity_1():
    """Test uncurrying functions with arity = 1."""
    curried_abs = hw3.curry_explicit(abs, 1)
    uncurried_abs = hw3.uncurry_explicit(curried_abs, 1)
    assert uncurried_abs(-10) == 10

def test_uncurry_arbitrary_arity_function():
    """Test uncurrying with arbitrary-arity functions that were fixed to specific arity."""
    call_log = []
    
    def variadic(*args):
        call_log.append(args)
        return sum(args)
    
    # Fix to arity 3
    curried = hw3.curry_explicit(variadic, 3)
    uncurried = hw3.uncurry_explicit(curried, 3)
    
    result = uncurried(1, 2, 3)
    assert result == 6
    assert call_log == [(1, 2, 3)]

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

@pytest.mark.parametrize(
    "func, arity, arguments, expected_result",
    [
        (max, 2, (10, 20), 20),
        (min, 3, (5, 1, 9), 1),
        (pow, 2, (2, 3), 8),
        (sum, 1, ([1, 2, 3],), 6),
        (print, 2, (1, 2), None),
        (print, 1, ("hello",), None),
    ],
)
def test_curry_py_builtin(func, arity, arguments, expected_result):
    """Test currying various Python built-in functions."""
    
    curried = hw3.curry_explicit(func, arity)

    result = curried
    for arg in arguments:
        result = result(arg)

    assert result == expected_result

@pytest.mark.parametrize(
    "fixed_arity, test_args",
    [
        (1, ("single",)),
        (2, ("hello", "world")),
        (3, (1, 2, 3)),
        (4, ("a", "b", "c", "d")),
    ]
)
def test_curry_arbitrary_arity_parametrized(fixed_arity, test_args):
    """Test that curry_explicit fixes arbitrary arity to specified value."""
    captered = []
    
    def variadic(*args):
        captered.append(args)
        return sum(1 for _ in args)
    
    curried = hw3.curry_explicit(variadic, fixed_arity)

    result = curried
    for arg in test_args:
        result = result(arg)
    
    assert result == fixed_arity
    assert captered == [test_args]


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


def test_curry_arity_1():
    """Test currying functions with arity = 1."""
    curried_abs = hw3.curry_explicit(abs, 1)
    assert curried_abs(-5) == 5
    
    curried_len = hw3.curry_explicit(len, 1)
    assert curried_len([1, 2, 3]) == 3


def test_curry_high_arity():
    """Test currying with higher arity (5 arguments)."""
    f = lambda a, b, c, d, e: a * b + c * d - e
    curried = hw3.curry_explicit(f, 5)
    result = curried(2)(3)(4)(5)(6)
    assert result == 20
