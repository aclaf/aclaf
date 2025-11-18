# Non-generic converter function type - accepts ParsedParameterValue | None and
# optional metadata, returns Any since we can't statically know the return
# type at the registry level
from collections.abc import Callable
from typing import Any

from annotated_types import BaseMetadata

from aclaf.types import ParsedParameterValue

ConverterFunctionType = Callable[
    [ParsedParameterValue | None, tuple[BaseMetadata, ...] | None], Any  # pyright: ignore[reportExplicitAny]
]
