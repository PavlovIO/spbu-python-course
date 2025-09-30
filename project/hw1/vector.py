from math import sqrt, acos

# Operations for vectors


def dot_prod(v1: list[float], v2: list[float]) -> float:
    """Вычисляет скалярное произведение двух векторов.

    Скалярное произведение определяется как сумма попарных произведений
    соответствующих элементов векторов.

    Args:
        v1 (list[float]): Первый вектор.
        v2 (list[float]): Второй вектор.

    Returns:
        float: Скалярное произведение векторов.

    Raises:
        ValueError: Если векторы имеют разную длину.
        TypeError: Если элементы векторов не являются числами.

    Examples:
        >>> dot_prod([1, 2], [3, 4])
        11.0
        >>> dot_prod([1, 0], [0, 1])
        0.0
    """
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same length")
    return sum(a * b for a, b in zip(v1, v2))


def vec_len(v: list[float]) -> float:
    """Вычисляет длину (евклидову норму) вектора.

    Длина вектора определяется как квадратный корень из суммы квадратов его компонент.

    Args:
        v (list[float]): Вектор.

    Returns:
        float: Длина вектора.

    Raises:
        ValueError: Если вектор пуст.
        TypeError: Если элементы вектора не являются числами.

    Examples:
        >>> vec_len([3, 4])
        5.0
        >>> vec_len([0, 0])
        0.0
    """
    if not v:
        raise ValueError("Vector must not be empty")
    return sqrt(sum(ai**2 for ai in v))


def angle(v1: list[float], v2: list[float]) -> float:
    """Вычисляет угол между двумя векторами в радианах.

    Угол вычисляется по формуле:
        angle = arccos( (v1 · v2) / (|v1| * |v2|) )

    Args:
        v1 (list[float]): Первый вектор.
        v2 (list[float]): Второй вектор.

    Returns:
        float: Угол между векторами в радианах (от 0 до π).

    Raises:
        ValueError: Если хотя бы один из векторов нулевой или пустой.
        TypeError: Если элементы векторов не являются числами.

    Examples:
        >>> import math
        >>> angle([1, 0], [0, 1])
        1.5707963267948966
        >>> angle([1,1],[5,5])
        0.0
    """
    l1 = vec_len(v1)
    l2 = vec_len(v2)
    if (l1 == 0) or (l2 == 0):
        raise ValueError("Angle undefined for zero vector")
    cos_angle = dot_prod(v1, v2) / (l1 * l2)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    if abs(1 - cos_angle) < 1.0e-15:
        cos_angle = 1
    return acos(cos_angle)
