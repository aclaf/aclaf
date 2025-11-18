from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from annotated_types import BaseMetadata

if TYPE_CHECKING:
    from aclaf.types import ParameterValueMappingType, ParameterValueType
    from aclaf.validation._registry import ValidatorMetadataType


@dataclass(slots=True, frozen=True)
class MutuallyExclusive(BaseMetadata):
    """At most one of specified parameters can be provided."""

    parameter_names: Sequence[str]


def validate_mutually_exclusive(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate at most one parameter is provided."""
    # Type guard - ensure value is a mapping
    if not isinstance(value, Mapping):
        return ("Command validators require parameter mapping.",)

    # Cast metadata to specific type
    meta = cast("MutuallyExclusive", metadata)

    # Check how many parameters are provided
    provided = [
        name
        for name in meta.parameter_names
        if name in value and value[name] is not None
    ]

    # Validate constraint
    errors: list[str] = []
    if len(provided) > 1:
        params_str = ", ".join(f"'{p}'" for p in provided)
        msg = (
            f"Parameters {params_str} are mutually exclusive - "
            f"only one can be provided."
        )
        errors.append(msg)

    if errors:
        return tuple(errors)
    return None


@dataclass(slots=True, frozen=True)
class ExactlyOneOf(BaseMetadata):
    """Exactly one of specified parameters must be provided."""

    parameter_names: Sequence[str]


def validate_exactly_one_of(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate exactly one parameter is provided."""
    # Type guard - ensure value is a mapping
    if not isinstance(value, Mapping):
        return ("Command validators require parameter mapping.",)

    # Cast metadata to specific type
    meta = cast("ExactlyOneOf", metadata)

    # Check how many parameters are provided
    provided = [
        name
        for name in meta.parameter_names
        if name in value and value[name] is not None
    ]

    # Validate constraint
    errors: list[str] = []
    if len(provided) == 0:
        params_str = ", ".join(f"'{p}'" for p in meta.parameter_names)
        errors.append(f"Exactly one of {params_str} must be provided.")
    elif len(provided) > 1:
        params_str = ", ".join(f"'{p}'" for p in provided)
        msg = (
            f"Exactly one parameter required, but {len(provided)} provided: "
            f"{params_str}."
        )
        errors.append(msg)

    if errors:
        return tuple(errors)
    return None


@dataclass(slots=True, frozen=True)
class AtLeastOneOf(BaseMetadata):
    """At least one of specified parameters must be provided."""

    parameter_names: Sequence[str]


def validate_at_least_one_of(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate at least one parameter is provided."""
    # Type guard - ensure value is a mapping
    if not isinstance(value, Mapping):
        return ("Command validators require parameter mapping.",)

    # Cast metadata to specific type
    meta = cast("AtLeastOneOf", metadata)

    # Check how many parameters are provided
    provided = [
        name
        for name in meta.parameter_names
        if name in value and value[name] is not None
    ]

    # Validate constraint
    errors: list[str] = []
    if len(provided) == 0:
        params_str = ", ".join(f"'{p}'" for p in meta.parameter_names)
        errors.append(f"At least one of {params_str} must be provided.")

    if errors:
        return tuple(errors)
    return None


@dataclass(slots=True, frozen=True)
class AtMostOneOf(BaseMetadata):
    """At most one of specified parameters can be provided."""

    parameter_names: Sequence[str]


def validate_at_most_one_of(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate at most one parameter is provided."""
    # Type guard - ensure value is a mapping
    if not isinstance(value, Mapping):
        return ("Command validators require parameter mapping.",)

    # Cast metadata to specific type
    meta = cast("AtMostOneOf", metadata)

    # Check how many parameters are provided
    provided = [
        name
        for name in meta.parameter_names
        if name in value and value[name] is not None
    ]

    # Validate constraint
    errors: list[str] = []
    if len(provided) > 1:
        params_str = ", ".join(f"'{p}'" for p in provided)
        msg = (
            f"At most one of {params_str} can be provided, "
            f"but {len(provided)} were provided."
        )
        errors.append(msg)

    if errors:
        return tuple(errors)
    return None
