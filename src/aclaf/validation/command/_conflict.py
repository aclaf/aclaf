from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from annotated_types import BaseMetadata

if TYPE_CHECKING:
    from aclaf.types import ParameterValueMappingType, ParameterValueType
    from aclaf.validation._registry import ValidatorMetadataType


@dataclass(slots=True, frozen=True)
class ConflictsWith(BaseMetadata):
    """Parameters cannot be provided together."""

    parameter_names: Sequence[str]


def validate_conflicts_with(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate parameters cannot be provided together."""
    # Type guard - ensure value is a mapping
    if not isinstance(value, Mapping):
        return ("Command validators require parameter mapping.",)

    # Cast metadata to specific type
    meta = cast("ConflictsWith", metadata)

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
            f"Parameters {params_str} conflict with each other and "
            f"cannot be provided together."
        )
        errors.append(msg)

    if errors:
        return tuple(errors)
    return None
