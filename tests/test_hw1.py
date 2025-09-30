import pytest
from math import isclose, sqrt, pi
import project.hw1 as hw1

# vectors
def test_dot_prod():
    assert isclose(hw1.dot_prod([1, 2], [3, 4]), 11)
    assert isclose(hw1.dot_prod([0, 0], [1, 1]), 0)
    assert isclose(hw1.dot_prod([2.5, 1.5], [2, 2]), 8.0)


def test_dot_prod_different_lengths():
    with pytest.raises(ValueError, match="Vectors must have the same length"):
        hw1.dot_prod([1, 2, 3], [4, 5])


def test_dot_prod_non_numeric():
    with pytest.raises(TypeError):
        hw1.dot_prod([1, "a"], [2, 3])


def test_vec_len():
    assert isclose(hw1.vec_len([3, 4]), 5.0)
    assert isclose(hw1.vec_len([0, 0]), 0.0)
    assert isclose(hw1.vec_len([1, 1]), sqrt(2))


def test_vec_len_empty():
    with pytest.raises(ValueError, match="Vector must not be empty"):
        hw1.vec_len([])


def test_angle():
    assert isclose(hw1.angle([1, 0], [0, 1]), pi / 2)
    assert isclose(hw1.angle([1, 1], [2, 2]), 0.0)
    assert isclose(hw1.angle([1, 0], [-1, 0]), pi)


def test_angle_zero_vector():
    with pytest.raises(ValueError, match="Angle undefined for zero vector"):
        hw1.angle([0, 0], [1, 1])
    with pytest.raises(ValueError, match="Angle undefined for zero vector"):
        hw1.angle([1, 1], [0, 0])


# matrices
def test_mat_sum():
    m1 = [[1, 2], [3, 4]]
    m2 = [[5, 6], [7, 8]]
    expected = [[6, 8], [10, 12]]
    result = hw1.mat_sum(m1, m2)
    for row1, row2 in zip(result, expected):
        for a, b in zip(row1, row2):
            assert isclose(a, b)


def test_mat_sum_different_rows():
    with pytest.raises(ValueError, match="Matrices must have the same number of rows"):
        hw1.mat_sum([[1]], [[1], [2]])


def test_mat_sum_different_cols():
    with pytest.raises(
        ValueError, match="Matrices must have the same number of columns"
    ):
        hw1.mat_sum([[1, 2]], [[3]])


def test_mat_sum_empty():
    with pytest.raises(ValueError, match="Matrices must not be empty"):
        hw1.mat_sum([], [[1]])


def test_mat_prod():
    m1 = [[1, 2], [3, 4]]
    m2 = [[5, 6], [7, 8]]
    result = hw1.mat_prod(m1, m2)
    expected = [[19, 22], [43, 50]]
    for row1, row2 in zip(result, expected):
        for a, b in zip(row1, row2):
            assert isclose(a, b)


def test_mat_prod_incompatible_shapes():
    with pytest.raises(
        ValueError, match="Number of columns in m1 must equal number of rows in m2"
    ):
        hw1.mat_prod([[1, 2, 3]], [[4], [5]])


def test_transpose():
    m = [[1, 2, 3], [4, 5, 6]]
    result = hw1.transpose(m)
    expected = [[1, 4], [2, 5], [3, 6]]
    assert result == expected


def test_transpose_empty():
    assert hw1.transpose([]) == []


def test_transpose_single_row():
    assert hw1.transpose([[1, 2, 3]]) == [[1], [2], [3]]


def test_transpose_non_rectangular():
    with pytest.raises(ValueError, match="Matrix is not rectangular"):
        hw1.transpose([[1, 2], [3]])
