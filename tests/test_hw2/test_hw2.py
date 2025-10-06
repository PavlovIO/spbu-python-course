import pytest
import project.hw2 as hw2
from functools import reduce

# Tests for input data generator


def test_squared_number_gen():
    gen = hw2.squared_number_gen(1, 3)
    assert list(gen) == [1, 4, 9]

    gen = hw2.squared_number_gen(0, 0)
    assert list(gen) == [0]

    gen = hw2.squared_number_gen(2, 1)  # empty range
    assert list(gen) == []


# Tests for functions as_func with different opperators


@pytest.mark.parametrize(
    "input_data,func,expected",
    [
        ([1, 2, 3], lambda x: x * 2, [2, 4, 6]),
        ([1, 2, 3], lambda x: x**2, [1, 4, 9]),
        ([], lambda x: x, []),
    ],
)
def test_as_func_map(input_data, func, expected):
    mapper = hw2.as_func(map, func=func)
    result = hw2.collect(mapper(input_data))
    assert result == expected


@pytest.mark.parametrize(
    "input_data,pred,expected",
    [
        ([1, -2, 3, -4, 5], lambda x: x > 0, [1, 3, 5]),
        ([1, 2, 3], lambda x: x % 2 == 0, [2]),
        ([], lambda x: True, []),
    ],
)
def test_as_func_filter(input_data, pred, expected):
    filtr = hw2.as_func(filter, pred=pred)
    result = hw2.collect(filtr(input_data))
    assert result == expected


def test_as_func_filter_with_func():
    filtr = hw2.as_func(filter, func=lambda x: x > 0)
    result = hw2.collect(filtr([-1, 0, 1, 2]))
    assert result == [1, 2]


def test_as_func_zip():
    zipper = hw2.as_func(zip)
    input_data = [[1, 2, 3], ["a", "b", "c"]]
    result = hw2.collect(zipper(input_data))
    assert result == [(1, "a"), (2, "b"), (3, "c")]


@pytest.mark.parametrize(
    "input_data,func,initializer,expected",
    [
        ([1, 2, 3], lambda a, b: a + b, None, 6),
        ([1, 2, 3], lambda a, b: a * b, None, 6),
        ([], lambda a, b: a + b, 0, 0),
        ([1, 2], lambda a, b: a + b, 10, 13),
    ],
)
def test_as_func_reduce(input_data, func, initializer, expected):
    args = (initializer,) if initializer is not None else ()
    reducer = hw2.as_func(reduce, *args, func=func)
    result = hw2.collect(reducer(input_data))
    assert result == [expected]


def test_as_func_reduce_no_func_raises():
    with pytest.raises(ValueError, match="reduce requires 'func'"):
        hw2.as_func(reduce)


def test_as_func_reduce_too_many_args_raises():
    with pytest.raises(ValueError, match="reduce requires at most one initializer"):
        hw2.as_func(reduce, 1, 2, func=lambda a, b: a + b)


# Test for custom fucntions


def custom_take_while(iterable, pred):
    for x in iterable:
        if not pred(x):
            break
        yield x


def test_as_func_custom_operator():
    take_positive = hw2.as_func(custom_take_while, pred=lambda x: x > 0)
    result = hw2.collect(take_positive([1, 2, -1, 3, 4]))
    assert result == [1, 2]


# Tests for pipe function


def test_pipe_simple():
    double = hw2.as_func(map, func=lambda x: x * 2)
    positive = hw2.as_func(filter, pred=lambda x: x > 0)

    data = [-2, -1, 0, 1, 2, 3]
    result = hw2.collect(hw2.pipe(data, [positive, double]))
    assert result == [2, 4, 6]


def test_pipe_single_operator():
    double = hw2.as_func(map, func=lambda x: x * 2)
    result = hw2.collect(hw2.pipe([1, 2, 3], [double]))
    assert result == [2, 4, 6]


def test_pipe_empty_operators_raises():
    with pytest.raises(ValueError, match="'operators' must not be empty"):
        hw2.collect(hw2.pipe([1, 2, 3], []))


# Test for collect


@pytest.mark.parametrize(
    "input_data,expected",
    [
        ([1, 2, 3], [1, 2, 3]),
        ((x for x in range(3)), [0, 1, 2]),
        (map(str, [1, 2]), ["1", "2"]),
        ([], []),
    ],
)
def test_collect(input_data, expected):
    assert hw2.collect(input_data) == expected


# Integration test: generate → filter → map → reduce → collect."


def test_full_pipeline():

    gen = hw2.squared_number_gen(1, 5)

    even = hw2.as_func(filter, pred=lambda x: x % 2 == 0)

    double = hw2.as_func(map, func=lambda x: x * 2)

    summer = hw2.as_func(reduce, func=lambda a, b: a + b)

    result = hw2.collect(hw2.pipe(gen, [even, double, summer]))
    assert result == [40]
