# Operations for matrices


def mat_sum(m1: list[list[float]], m2: list[list[float]]) -> list[list[float]]:
    """Adds two matrices of the same size.

    Args:
        m1 (list[list[float]]): The first matrix.
        m2 (list[list[float]]): The second matrix.

    Returns:
        list[list[float]]: The resulting matrix where each element is the sum
        of the corresponding elements from the input matrices.

    Raises:
        ValueError: If either matrix is empty or if the matrices have different dimensions.

    Examples:
        >>> mat_sum([[1, 2]], [[3, 4]])
        [[4, 6]]
    """
    if not m1 or not m1[0] or not m2 or not m2[0]:
        raise ValueError("Matrices must not be empty")
    if len(m1) != len(m2):
        raise ValueError("Matrices must have the same number of rows")
    if any(len(row1) != len(row2) for row1, row2 in zip(m1, m2)):
        raise ValueError("Matrices must have the same number of columns")

    return [[a + b for a, b in zip(row1, row2)] for row1, row2 in zip(m1, m2)]


def mat_prod(m1: list[list[float]], m2: list[list[float]]) -> list[list[float]]:
    """Multiplies two matrices.

    Args:
        m1 (list[list[float]]): The first matrix of size n x m.
        m2 (list[list[float]]): The second matrix of size m x k.

    Returns:
        list[list[float]]: The resulting matrix of size n x k, where the element at (i, j)
        is the dot product of the i-th row of the first matrix and the j-th column of the second matrix.

    Raises:
        ValueError: If either matrix is empty or if the number of columns in m1
        does not match the number of rows in m2.

    Examples:
        >>> mat_prod([[1, 2]], [[3], [4]])
        [[11]]
        >>> mat_prod([[1, 2], [3, 4]], [[3, 5], [4, 6]])
        [[11, 17], [25, 39]]
    """
    if not m1 or not m1[0] or not m2 or not m2[0]:
        raise ValueError("Matrices must not be empty")
    if len(m1[0]) != len(m2):
        raise ValueError("Number of columns in m1 must equal number of rows in m2")
    if any(len(row) != len(m1[0]) for row in m1):
        raise ValueError("Matrix m1 is not rectangular")
    if any(len(row) != len(m2[0]) for row in m2):
        raise ValueError("Matrix m2 is not rectangular")

    return [[sum(a * b for a, b in zip(row, col)) for col in zip(*m2)] for row in m1]


def transpose(m: list[list[float]]) -> list[list[float]]:
    """Transposes a matrix.

    Args:
        m (list[list[float]]): The input matrix of size n x m.

    Returns:
        list[list[float]]: The transposed matrix of size m x n.

    Raises:
        ValueError: If the input matrix is not rectangular.

    Examples:
        >>> transpose([[1, 2, 3]])
        [[1], [2], [3]]
        >>> transpose([[1, 2], [3, 4]])
        [[1, 3], [2, 4]]
    """
    if not m:
        return []
    if not all(len(row) == len(m[0]) for row in m):
        raise ValueError("Matrix is not rectangular")
    return [list(col) for col in zip(*m)]
