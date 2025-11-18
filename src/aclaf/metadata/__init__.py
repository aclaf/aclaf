from ._command import CommandMetadata
from ._metadata import flatten_metadata, get_all_metadata, get_metadata, has_metadata
from ._parameter import (
    Arg,
    AtLeastOne,
    AtMostOne,
    Collect,
    Count,
    Default,
    ErrorOnDuplicate,
    ExactlyOne,
    FirstWins,
    Flag,
    LastWins,
    Opt,
    ParameterMetadata,
    ZeroOrMore,
)
from ._types import MetadataByType, MetadataType

__all__ = [
    "Arg",
    "AtLeastOne",
    "AtMostOne",
    "Collect",
    "CommandMetadata",
    "Count",
    "Default",
    "ErrorOnDuplicate",
    "ExactlyOne",
    "FirstWins",
    "Flag",
    "LastWins",
    "MetadataByType",
    "MetadataType",
    "Opt",
    "ParameterMetadata",
    "ZeroOrMore",
    "flatten_metadata",
    "get_all_metadata",
    "get_metadata",
    "has_metadata",
]
