from functools import reduce
from typing import \
    Iterable, \
    Generator, \
    Any, \
    Callable, \
    Optional
    
def squared_number_gen(start: int, finish: int) -> Generator[int, None, None]:
    """
    Generate squares of integers in the inclusive range [start, finish].
    
    Args:
        start (int): The starting integer (inclusive).
        finish (int): The ending integer (inclusive).
        
    Yields:
        int: The square of the next integer in the range.
        
    Examples:
        >>> list(squared_number_gen(1, 3))
        [1, 4, 9]
    """
    for i in range(start, finish + 1):
        yield i**2

def as_func(operator: Callable, 
            *args, \
            func: Optional[Callable] = None, \
            pred: Optional[Callable] = None, \
             **kwargs,
            ) -> Callable[[Iterable], Iterable]:
    """
    Create a lazy processing wrapper for iterable data streams.
    
    Supports built-in operators: map, filter, zip, and reduce.
    For custom operators, the iterable is passed as the first argument,
    and `func`/`pred` are injected via keyword arguments if provided.
    
    Args:
        operator: The processing function (e.g., map, filter, or a custom callable).
        *args: Additional positional arguments (e.g., initializer for reduce).
        func: Transformation function (for map) or predicate (alternative to `pred`).
        pred: Filtering predicate (alternative to `func`).
        **kwargs: Extra keyword arguments for custom operators.
        
    Returns:
        Callable[[Iterable], Iterable]: A function that takes an iterable and
        returns a generator yielding processed elements.
        
    Raises:
        ValueError: If required functions are missing for map/filter,
                    or if too many arguments are passed to reduce.
                    
    Examples:
        >>> double = as_func(map, func=lambda x: x * 2)
        >>> positive = as_func(filter, pred=lambda x: x > 0)
        >>> list(double([1, 2, 3]))
        [2, 4, 6]
    """
    if operator is map:
        if func is None:
            raise ValueError("map requires 'func'")
        def wrapper(items: Iterable) -> Iterable:
            for item in items:
                yield func(item)
        return wrapper
    
    if operator is filter:
        predicate = func or pred
        if predicate is None: 
            raise ValueError("filter requires 'func' or 'pred'")
        def wrapper(items: Iterable) -> Iterable:
            for item in items:
                if predicate(item): 
                    yield item
        return wrapper
    
    if operator is zip:
        def wrapper(items: Iterable) -> Iterable:
            for item in zip(*items):
                yield item
        return wrapper
    
    if operator is reduce:
        if func is None:
            raise ValueError("reduce requires 'func'")
        if len(args) > 1:
            raise ValueError("reduce requires at most one initializer")
        def wrapper(items: Iterable) -> Iterable:
            initializer = args[0] if args else None
            result = reduce(func, items, initializer) if args else reduce(func, items)
            yield result  
        return wrapper

    extra_kwargs = {}
    if func is not None:
        extra_kwargs['func'] = func
    if pred is not None:
        extra_kwargs['pred'] = pred
    def wrapper(items: Iterable) -> Iterable:
        comb_kwargs = {**extra_kwargs, **kwargs}
        result = operator(items, *args, **comb_kwargs)
        yield from result
    return wrapper
    

def pipe(streams: Iterable[Any], operators: list[Callable]) -> Generator[Any, None, None]:
    """
    Apply a sequence of operators to a data stream in a lazy pipeline.
    
    Each operator must be a function (typically created by `as_func`)
    that accepts an iterable and returns an iterable.
    
    Args:
        stream: The input data sequence.
        operators: A list of processing operators to apply sequentially.
        
    Yields:
        Elements of the resulting sequence after all transformations.
        
    Raises:
        ValueError: If the operators list is empty.
        
    Examples:
        >>> double = as_func(map, func=lambda x: x * 2)
        >>> positive = as_func(filter, pred=lambda x: x > 0)
        >>> result = pipe([-2, -1, 0, 1, 2], [positive, double])
        >>> collect(result)
        [2, 4]
    """
    if operators == []:
        raise ValueError("'operators' must not be empty")
    
    result = streams
    for op in operators:
        result = op(result)
    yield from result

def collect(gen: Iterable[Any]) -> list[Any]:
    """
    Collect all elements from an iterable into a list.

    Args:
        it: Any iterable (generator, map, filter, range, etc.).
        
    Returns:
        list: A list containing all elements from the input iterable.
        
    Examples:
        >>> collect(range(3))
        [0, 1, 2]
        >>> collect((x for x in [1, 2, 3] if x > 1))
        [2, 3]
    """
    return list(gen)
