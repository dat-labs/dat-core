
import itertools
from typing import Any, Iterable, Iterator, Tuple

def create_chunks(iterable: Iterable[Any], batch_size: int) -> Iterator[Tuple[Any, ...]]:
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))
