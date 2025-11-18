from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, TypeAlias, runtime_checkable
from typing_extensions import override

from .console import Console, SupportsConsole

if TYPE_CHECKING:
    from .logging import Logger


@dataclass(slots=True, frozen=True)
class ResponseContext:
    console: Console
    logger: "Logger"


@runtime_checkable
class SupportsPrint(Protocol):
    @override
    def __str__(self) -> str: ...


SupportsResponseType: TypeAlias = SupportsPrint | SupportsConsole


SyncResponseType: TypeAlias = (
    SupportsResponseType
    | Generator[SupportsResponseType, None, SupportsResponseType | None]
)

AsyncResponseType: TypeAlias = (
    SupportsResponseType | AsyncGenerator[SupportsResponseType, None]
)

ResponseType: TypeAlias = SyncResponseType | AsyncResponseType
