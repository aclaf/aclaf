from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from annotated_types import Predicate

    from aclaf.types import ParameterValueMappingType, ParameterValueType
    from aclaf.validation._registry import ValidatorMetadataType


def validate_predicate(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate value against a predicate function.

    The predicate function is called with the value and must return True
    for the validation to pass. If the predicate returns False or raises
    an exception, validation fails.

    Args:
        value: The value to validate
        metadata: Predicate metadata containing the validation function

    Returns:
        Tuple of error messages if validation fails, None if validation passes
    """
    predicate_meta = cast("Predicate", metadata)

    # None values pass through without validation
    if value is None:
        return None

    # Call the predicate function with the value
    try:
        result = predicate_meta.func(value)
    except Exception as e:  # noqa: BLE001
        # User-provided predicates can raise any exception type (AttributeError,
        # TypeError, ValueError, etc.) - broad exception handling is necessary
        return (f"predicate validation failed: {e!s}",)

    # Check if predicate returned True
    if not result:
        return ("does not satisfy the required predicate condition.",)

    return None
