import itertools
from typing import Any, Iterable, Iterator, Tuple

def create_chunks(iterable: Iterable[Any], batch_size: int) -> Iterator[Tuple[Any, ...]]:
    """
    A helper function to break an iterable into chunks of size batch_size.

    Args:
        iterable (Iterable[Any]): The iterable to be divided into chunks.
        batch_size (int): The size of each chunk.

    Returns:
        Iterator[Tuple[Any, ...]]: An iterator that yields tuples of elements
        from the iterable, where each tuple represents a chunk.

    Example:
        >>> numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> for chunk in create_chunks(numbers, 3):
        ...     print(chunk)
        (1, 2, 3)
        (4, 5, 6)
        (7, 8, 9)
        (10,)
    """
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))
