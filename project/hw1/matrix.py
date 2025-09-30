# Operations for matrices


def mat_sum(m1: list[list[float]], m2: list[list[float]]) -> list[list[float]]:
    """Складывает две матрицы одинакового размера.

    Args:
        m1 (list[list[float]]): Первая матрица.
        m2 (list[list[float]]): Вторая матрица.

    Returns:
        list[list[float]]: Результирующая матрица, где каждый элемент — сумма
        соответствующих элементов входных матриц.

    Raises:
        ValueError: Если матрицы пусты или имеют разные размеры.

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
    """Перемножает две матрицы одинакового размера.

    Args:
        m1 (list[list[float]]): Первая матрица n x m.
        m2 (list[list[float]]): Вторая матрица m x k.

    Returns:
        list[list[float]]: Результирующая матрица n x k, где i,j элемент — произведение i-ой строки первой матрицы на
        j-ый столбей второй матрицы.

    Raises:
        ValueError: Если матрицы пусты или имеют разные размеры.

    Examples:
        >>> mat_prod([[1, 2]], [[3], [4]])
        [[11]]
        >>> mat_prod([[1, 2], [3, 4]], [[3, 5],[4, 6]])
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
    """Транспонирование матрицы.

    Args:
        m1 (list[list[float]]): Исходная матрица n x m.

    Returns:
        list[list[float]]: Результирующая транспонированая матрица m x n.

    Raises:
        ValueError: Если матрица не прямоугольная.

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
