from functools import wraps
import inspect
import copy
from collections import deque
from typing import Any, Callable

# ---Cache Decorator---
def cache_keys(args: tuple, kwargs: dict[str, Any]) -> tuple:
    """
    Generate a hashable cache key from function arguments.

    This function constructs a canonical, hashable representation of the given
    positional and keyword arguments, suitable for use as a key in a dictionary-
    based cache (e.g., for memoization). The resulting key is a flat tuple that
    combines the positional arguments and sorted keyword argument items.

    Parameters
    ----------
    args : tuple
        A tuple of positional arguments. All elements must be hashable.
    kwargs : dict[str, Any]
        A dictionary of keyword arguments. All keys must be strings (as per type hint),
        and all values must be hashable.

    Returns
    -------
    tuple
        A hashable tuple representing the combined arguments, structured as:
        ``(args,) + tuple(sorted(kwargs.items()))``.
        This format ensures consistent ordering of keyword arguments and
        preserves the structure of positional arguments.

    Raises
    ------
    TypeError
        If any element in `args` or any value in `kwargs` is unhashable
        (e.g., `list`, `dict`, `set`, or other mutable types). The error
        message includes details about the unhashable type.

    Examples
    --------
    >>> cache_keys((1, 2), {'x': 'a', 'y': 3})
    ((1, 2), ('x', 'a'), ('y', 3))

    >>> cache_keys((), {'flag': True})
    ((), ('flag', True))

    >>> cache_keys(([1, 2],), {})  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    TypeError: Arguments must be hashable: unhashable type: 'list'

    Notes
    -----
    - Keyword arguments are sorted by key to ensure consistent ordering,
      making the cache key independent of the insertion order in `kwargs`.
    - Only hashable types (e.g., `int`, `str`, `tuple`, `frozenset`, etc.)
      are allowed. Mutable containers like `list` or `dict` will cause a
      `TypeError`.
    - This function assumes `kwargs` keys are strings, as indicated by the
      type annotation, which guarantees they are hashable and sortable.
    """
    try:
        key = (args,) + tuple(sorted(kwargs.items()))
        hash(key)
        return key
    except TypeError as e:
        raise TypeError(f"Arguments must be hashable: {e}")


def cache_func(func: Callable | None = None, *, maxsize: int = 0) -> Callable:
    """Caches the results of function calls using a FIFO (first-in, first-out) strategy.

    This decorator stores up to `maxsize` most recent call results.
    If `maxsize` is zero or negative, caching is disabled and the original
    function is returned unchanged.

    The cache key is built from all positional and keyword arguments.
    Only hashable arguments are supported; non-hashable arguments bypass caching.

    Examples:
        >>> @cache_func(maxsize=2)
        ... def add(x, y):
        ...     print(f"Computing {x} + {y}")
        ...     return x + y
        ...
        >>> add(1, 2)
        Computing 1 + 2
        3
        >>> add(1, 2)  # cached
        3
        >>> add(3, 4)
        Computing 3 + 4
        7
        >>> add(5, 6)  # evicts (1, 2)
        Computing 5 + 6
        11
        >>> add(1, 2)  # recomputed (no longer cached)
        Computing 1 + 2
        3

    Args:
        func: The function to decorate. If not provided (e.g., used as
              @cache_func(maxsize=5)), returns a decorator.
        maxsize: Maximum number of cached results to keep. Must be a non-negative
                 integer. If <= 0, caching is disabled.

    Returns:
        A wrapped function with caching enabled (or the original function if
        caching is disabled).

    Note:
        - Arguments must be hashable (e.g., int, str, tuple of hashables).
        - Non-hashable arguments (e.g., list, dict) skip caching silently.
        - Keyword arguments are normalized by sorting keys, so
          f(a=1, b=2) and f(b=2, a=1) produce the same cache key.
    """
    if func is None:
        return lambda f: cache_func(f, maxsize=maxsize)
    if maxsize <= 0:
        return func

    cache: dict[tuple, Any] = {}
    key_ord: deque[tuple] = deque()

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            key = cache_keys(args, kwargs)
        except TypeError as e:
            return func(*args, **kwargs)

        if key in cache:
            return cache[key]

        result = func(*args, **kwargs)
        cache[key] = result
        key_ord.append(key)

        if len(cache) > maxsize:
            pop_key = key_ord.popleft()
            del cache[pop_key]

        return result

    return wrapper


# -------------------------------

# ---Smart Arguments Decorator---
class Isolated:
    """Sentinel class to mark arguments that should be deep-copied upon function call.

    When used as a default value for a parameter, indicates that any provided
    argument for this parameter must be deep-copied before being passed to the
    function body. This prevents accidental mutation of the original object.
    """

    pass


class Evaluated:
    """Wrapper for callables that should be evaluated at call time for default values.

    When used as a default value for a parameter, the wrapped callable (which must
    take no arguments) is invoked each time the function is called and the parameter
    is not explicitly provided. This allows dynamic default values (e.g., timestamps,
    random numbers, or fresh mutable objects).

    Args:
        func: A callable with no arguments that returns a value.
    """

    def __init__(self, func: Callable[[], Any]) -> None:
        if func is None:
            raise ValueError("Evaluated requires a callable as argument")
        self.func = func


def smart_args(func: Callable | None = None, pos_args: bool = False) -> Callable:
    """Decorator that enhances function arguments with smart default behaviors.

    Supports two special default value markers:
      - `Isolated()`: Ensures the passed argument is deep-copied before use.
      - `Evaluated(func)`: Evaluates `func()` at call time if the argument is omitted.

    By default, these markers are only allowed for keyword-only arguments.
    Set `pos_args=True` to also allow them for positional arguments.

    The decorator analyzes the function signature once at decoration time and
    applies the appropriate transformations on every function call.

    Args:
        func: The function to decorate. If not provided (e.g., used as
              @smart_args(pos_args=True)), returns a decorator.
        pos_args: If True, allow `Isolated` and `Evaluated` for positional
                  arguments.
                  Default is False.

    Returns:
        A wrapped function with enhanced argument handling.

    Raises:
        ValueError: If a parameter uses both `Isolated` and `Evaluated`,
                    or if `Evaluated` is given a non-callable.

    Examples:
        # Isolation for keyword-only args (default)
        >>> @smart_args
        ... def update_config(*, config=Isolated()):
        ...     config['updated'] = True
        ...     return config
        ...
        >>> orig = {'version': 1}
        >>> new = update_config(config=orig)
        >>> orig
        {'version': 1}  # unchanged

        # Dynamic defaults with Evaluated
        >>> from datetime import datetime
        >>> @smart_args
        ... def log_event(*, timestamp=Evaluated(datetime.now)):
        ...     return timestamp
        ...
        >>> t1 = log_event()
        >>> t2 = log_event()
        >>> t1 < t2  # True — fresh timestamp each time

        # Support for positional args (opt-in)
        >>> @smart_args(pos_args=True)
        ... def process(data=Isolated(), mode='default'):
        ...     data['mode'] = mode
        ...     return data
        ...
        >>> result = process({'input': 42})  # data is isolated
    """
    if func is None:
        return lambda f: smart_args(f, pos_args=pos_args)

    # not using getfullargspec() as it is outdated
    sig = inspect.signature(func)

    isolated = set()
    evaluated: dict[str, Any] = {}

    for name, param in sig.parameters.items():
        is_kwarg = param.kind in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        # check whether positional argument allowed to take Isolated or Evaluated as default
        is_pos_allowed = pos_args and param.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD
        )

        is_iso = isinstance(param.default, Isolated)
        is_eva = isinstance(param.default, Evaluated)

        assert (is_kwarg or is_pos_allowed) or not (
            is_iso or is_eva
        ), f"Positioanal argument {name} can't use Isolated or Evaluated if flag pos_args is False"
        """if not ( (is_kwarg or is_pos_allowed) or not (is_iso or is_eva) ):
            raise ValueError(f"Positioanal argument {name} can't use Isolated or Evaluated if flag pos_args is False")"""

        assert not (
            is_iso and is_eva
        ), f"Argument {name} can't use Isolated and Evaluated together"
        """if is_iso and is_eva:
            raise ValueError(f"Argument {name} can't use Isolated and Evaluated together ")"""

        if is_iso:
            isolated.add(name)
        elif is_eva:
            evaluated[name] = param.default.func

    @wraps(func)
    def wrapper(*args, **kwargs):
        # making BoundArgument variable arguments where arguments.arguments - dict[arg_name, arg_value]
        arguments = sig.bind(*args, **kwargs)
        arguments.apply_defaults()  # adds arguments that doesnt get value and dont have default value

        for name in isolated:
            if name in arguments.arguments:
                arguments.arguments[name] = copy.deepcopy(arguments.arguments[name])

        for name, ev_func in evaluated.items():
            if arguments.arguments[name] == sig.parameters[name].default:
                arguments.arguments[name] = ev_func()

        return func(*arguments.args, **arguments.kwargs)

    return wrapper
