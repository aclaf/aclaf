import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast
from typing_extensions import override

from annotated_types import BaseMetadata, GroupedMetadata

from aclaf.metadata import ParameterMetadata

if TYPE_CHECKING:
    from collections.abc import Iterator

    from aclaf.types import ParameterValueMappingType, ParameterValueType
    from aclaf.validation._registry import ValidatorMetadataType


@dataclass(slots=True, frozen=True)
class NotBlank(BaseMetadata):
    not_blank: bool = True

    @override
    def __hash__(self) -> int:
        return hash(self.not_blank)


def validate_not_blank(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    if not value.strip():
        return ("must not be blank.",)

    return None


@dataclass(slots=True, frozen=True)
class Pattern(ParameterMetadata):
    pattern: str


def validate_pattern(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    pattern_meta = cast("Pattern", metadata)

    if not re.match(pattern_meta.pattern, value):
        return (f"must match pattern '{pattern_meta.pattern}'.",)

    return None


@dataclass(slots=True, frozen=True)
class Choices(ParameterMetadata):
    choices: tuple[str, ...]


def validate_choices(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    choices_meta = cast("Choices", metadata)

    if value not in choices_meta.choices:
        return (f"must be one of {', '.join(repr(c) for c in choices_meta.choices)}.",)

    return None


@dataclass(slots=True, frozen=True)
class StartsWith(ParameterMetadata):
    prefix: str


def validate_starts_with(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    starts_meta = cast("StartsWith", metadata)

    if not value.startswith(starts_meta.prefix):
        return (f"must start with '{starts_meta.prefix}'.",)

    return None


@dataclass(slots=True, frozen=True)
class EndsWith(ParameterMetadata):
    suffix: str


def validate_ends_with(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    ends_meta = cast("EndsWith", metadata)

    if not value.endswith(ends_meta.suffix):
        return (f"must end with '{ends_meta.suffix}'.",)

    return None


@dataclass(slots=True, frozen=True)
class Contains(ParameterMetadata):
    substring: str


def validate_contains(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    contains_meta = cast("Contains", metadata)

    if contains_meta.substring not in value:
        return (f"must contain '{contains_meta.substring}'.",)

    return None


@dataclass(slots=True, frozen=True)
class Lowercase(ParameterMetadata):
    pass


def validate_lowercase(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    if not value.islower():
        return ("must be lowercase.",)

    return None


@dataclass(slots=True, frozen=True)
class Uppercase(ParameterMetadata):
    pass


def validate_uppercase(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    if not value.isupper():
        return ("must be uppercase.",)

    return None


@dataclass(slots=True, frozen=True)
class Alphanumeric(ParameterMetadata):
    pass


def validate_alphanumeric(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    if not value.isalnum():
        return ("must be alphanumeric (letters and numbers only).",)

    return None


@dataclass(slots=True, frozen=True)
class Alpha(ParameterMetadata):
    pass


def validate_alpha(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    if not value.isalpha():
        return ("must be alphabetic (letters only).",)

    return None


@dataclass(slots=True, frozen=True)
class Numeric(ParameterMetadata):
    pass


def validate_numeric(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    if not value.isnumeric():
        return ("must be numeric (numbers only).",)

    return None


@dataclass(slots=True, frozen=True)
class Printable(ParameterMetadata):
    pass


def validate_printable(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, str):
        return ("must be a string.",)

    if not value.isprintable():
        return ("must contain only printable characters.",)

    return None


@dataclass(slots=True, frozen=True)
class StringValidations(GroupedMetadata):
    not_blank: bool = False
    pattern: str | None = None
    choices: tuple[str, ...] | None = None
    starts_with: str | None = None
    ends_with: str | None = None
    contains: str | None = None
    lowercase: bool = False
    uppercase: bool = False
    alphanumeric: bool = False
    alpha: bool = False
    numeric: bool = False
    printable: bool = False

    @override
    def __iter__(self) -> "Iterator[BaseMetadata]":
        if self.not_blank:
            yield NotBlank()
        if self.pattern is not None:
            yield Pattern(pattern=self.pattern)
        if self.choices is not None:
            yield Choices(choices=self.choices)
        if self.starts_with is not None:
            yield StartsWith(prefix=self.starts_with)
        if self.ends_with is not None:
            yield EndsWith(suffix=self.ends_with)
        if self.contains is not None:
            yield Contains(substring=self.contains)
        if self.lowercase:
            yield Lowercase()
        if self.uppercase:
            yield Uppercase()
        if self.alphanumeric:
            yield Alphanumeric()
        if self.alpha:
            yield Alpha()
        if self.numeric:
            yield Numeric()
        if self.printable:
            yield Printable()
