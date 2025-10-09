from typing import Callable, Any


def curry_explicit(func: Callable[..., Any], arity: int) -> Callable:
    """Transforms a function of fixed arity into its curried form.

    Given a function `func` that takes `arity` positional arguments,
    returns a new function that accepts arguments one at a time.
    Each call returns a new function accepting the next argument,
    until all `arity` arguments are provided, at which point `func`
    is called with all collected arguments.

    Examples:
        >>> f = lambda x, y, z: x + y + z
        >>> curried = curry_explicit(f, 3)
        >>> curried(1)(2)(3)
        6
        >>> zero_arg = curry_explicit(lambda: 42, 0)
        >>> zero_arg()
        42

    Args:
        func: A callable that accepts exactly `arity` positional arguments.
        arity: The number of positional arguments `func` expects.
               Must be a non-negative integer.

    Returns:
        A curried version of `func`. For arity N > 0, the result is a chain
        of N nested functions, each taking one argument. For arity 0,
        returns a zero-argument function that calls `func()`.

    Raises:
        ValueError: If `arity` is negative.
    """
    if arity < 0:
        raise ValueError("Arity can be negative")
    if arity == 0:
        return func

    def curry(args: list[Any]) -> Callable:
        if len(args) == arity:
            return func(*args)
        else:
            return lambda x: curry(args + [x])

    return curry([])


def uncurry_explicit(func: Callable[..., Any], arity: int) -> Callable:
    """Transforms a curried function back into a function of fixed arity.

    Given a curried function `func` (produced by `curry_explicit`) that
    accepts arguments one by one over `arity` calls, returns a new function
    that accepts all `arity` arguments at once and applies them sequentially
    to `func`.

    Examples:
        >>> f = lambda x, y, z: x * y * z
        >>> curried = curry_explicit(f, 3)
        >>> uncurried = uncurry_explicit(curried, 3)
        >>> uncurried(2, 3, 4)
        24
        >>> const = curry_explicit(lambda: 'ok', 0)
        >>> uncurried_zero = uncurry_explicit(const, 0)
        >>> uncurried_zero()
        'ok'

    Args:
        func: A curried function that can be called `arity` times,
              each time with one argument.
        arity: The expected number of arguments (i.e., the depth of currying).
               Must be a non-negative integer.

    Returns:
        A function that takes exactly `arity` positional arguments and
        returns the same result as calling `func(arg1)(arg2)...(argN)`.

    Raises:
        ValueError: If `arity` is negative.
        TypeError: If the returned function is called with a number of
                   arguments different from `arity`.
    """
    if arity < 0:
        raise ValueError("Arity can be negative")
    if arity == 0:
        return func

    def uncurry(*args: Any) -> Any:
        if len(args) != arity:
            raise TypeError(f"Expected {arity} arguments, got {len(args)}")
        result = func
        for arg in args:
            result = result(arg)
        return result

    return uncurry
