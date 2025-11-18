from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from annotated_types import BaseMetadata

if TYPE_CHECKING:
    from aclaf.types import ParameterValueMappingType, ParameterValueType
    from aclaf.validation._registry import ValidatorMetadataType


@dataclass(slots=True, frozen=True)
class Requires(BaseMetadata):
    """If source parameter provided, required parameters must also be provided."""

    source: str
    required: tuple[str, ...]


def validate_requires(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate if source provided, required parameters must also be provided."""
    # Type guard - ensure value is a mapping
    if not isinstance(value, Mapping):
        return ("Command validators require parameter mapping.",)

    # Cast metadata to specific type
    meta = cast("Requires", metadata)

    # Check if source parameter is provided
    source_provided = meta.source in value and value[meta.source] is not None

    if not source_provided:
        return None  # No validation needed if source not provided

    # Source is provided - check required parameters
    missing = [
        name for name in meta.required if name not in value or value[name] is None
    ]

    # Validate constraint
    errors: list[str] = []
    if missing:
        missing_str = ", ".join(f"'{m}'" for m in missing)
        errors.append(f"Parameter '{meta.source}' requires: {missing_str}.")

    if errors:
        return tuple(errors)
    return None


@dataclass(slots=True, frozen=True)
class Forbids(BaseMetadata):
    """If source parameter provided, forbidden parameters must not be provided."""

    source: str
    forbidden: tuple[str, ...]


def validate_forbids(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate if source provided, forbidden parameters must not be provided."""
    # Type guard - ensure value is a mapping
    if not isinstance(value, Mapping):
        return ("Command validators require parameter mapping.",)

    # Cast metadata to specific type
    meta = cast("Forbids", metadata)

    # Check if source parameter is provided
    source_provided = meta.source in value and value[meta.source] is not None

    if not source_provided:
        return None  # No validation needed if source not provided

    # Source is provided - check forbidden parameters
    present = [
        name for name in meta.forbidden if name in value and value[name] is not None
    ]

    # Validate constraint
    errors: list[str] = []
    if present:
        present_str = ", ".join(f"'{p}'" for p in present)
        errors.append(f"Parameter '{meta.source}' forbids: {present_str}.")

    if errors:
        return tuple(errors)
    return None
