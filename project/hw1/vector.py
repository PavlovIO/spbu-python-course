from math import sqrt, acos

# Operations for vectors


def dot_prod(v1: list[float], v2: list[float]) -> float:
    """Computes the dot product of two vectors.

    The dot product is defined as the sum of the pairwise products
    of the corresponding elements of the vectors.

    Args:
        v1 (list[float]): The first vector.
        v2 (list[float]): The second vector.

    Returns:
        float: The dot product of the vectors.

    Raises:
        ValueError: If the vectors have different lengths.

    Examples:
        >>> dot_prod([1, 2], [3, 4])
        11
        >>> dot_prod([1, 0], [0, 1])
        0
    """
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same length")
    return sum(a * b for a, b in zip(v1, v2))


def vec_len(v: list[float]) -> float:
    """Computes the Euclidean norm (length) of a vector.

    The length of a vector is defined as the square root of the sum of the squares of its components.

    Args:
        v (list[float]): The input vector.

    Returns:
        float: The length of the vector.

    Raises:
        ValueError: If the vector is empty.

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
    """Computes the angle between two vectors in radians.

    The angle is calculated using the formula:
        angle = arccos( (v1 · v2) / (|v1| * |v2|) )

    Args:
        v1 (list[float]): The first vector.
        v2 (list[float]): The second vector.

    Returns:
        float: The angle between the vectors in radians (in the range [0, π]).

    Raises:
        ValueError: If either vector is zero or empty.

    Examples:
        >>> import math
        >>> angle([1, 0], [0, 1])
        1.5707963267948966  # π/2
        >>> angle([1, 1], [5, 5])
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
