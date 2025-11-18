"""Numeric domain validators for parameter-scoped validation.

This module provides validators for numeric values including:
- MultipleOf: Value must be divisible by specified value
- Interval: Value must be within range (inclusive/exclusive bounds)
- IsInteger: Value must be whole number
- IsPositive: Value must be > 0
- IsNegative: Value must be < 0
- IsNonNegative: Value must be >= 0
- IsNonPositive: Value must be <= 0
- Precision: Decimal precision constraint
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, cast

from annotated_types import BaseMetadata

if TYPE_CHECKING:
    from annotated_types import Interval, MultipleOf

    from aclaf.types import ParameterValueMappingType, ParameterValueType
    from aclaf.validation._registry import ValidatorMetadataType


@dataclass(slots=True, frozen=True)
class IsInteger(BaseMetadata):
    """Value must be a whole number (validates float is .0)."""


@dataclass(slots=True, frozen=True)
class IsPositive(BaseMetadata):
    """Value must be > 0."""


@dataclass(slots=True, frozen=True)
class IsNegative(BaseMetadata):
    """Value must be < 0."""


@dataclass(slots=True, frozen=True)
class IsNonNegative(BaseMetadata):
    """Value must be >= 0 (common for counts)."""


@dataclass(slots=True, frozen=True)
class IsNonPositive(BaseMetadata):
    """Value must be <= 0."""


@dataclass(slots=True, frozen=True)
class Precision(BaseMetadata):
    """Decimal precision constraint (max decimal places)."""

    max_decimals: int


def validate_multiple_of(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate value is divisible by specified multiple."""
    multiple_meta = cast("MultipleOf", metadata)
    errors: list[str] = []
    try:
        if (value % multiple_meta.multiple_of) != 0:  # pyright: ignore[reportOperatorIssue]
            errors.append(f"must be a multiple of {multiple_meta.multiple_of}.")
    except TypeError:
        errors.append(f"cannot be divided by {multiple_meta.multiple_of}.")

    if errors:
        return tuple(errors)
    return None


def _check_lower_bound(
    value: float, interval_meta: "Interval", errors: list[str]
) -> None:
    """Check lower bound of interval."""
    if interval_meta.gt is not None:
        try:
            if not value > interval_meta.gt:  # pyright: ignore[reportOperatorIssue]
                errors.append(f"must be greater than {interval_meta.gt}.")
        except TypeError:
            errors.append(f"cannot be compared with {interval_meta.gt}.")
    elif interval_meta.ge is not None:
        try:
            if not value >= interval_meta.ge:  # pyright: ignore[reportOperatorIssue]
                errors.append(f"must be greater than or equal to {interval_meta.ge}.")
        except TypeError:
            errors.append(f"cannot be compared with {interval_meta.ge}.")


def _check_upper_bound(
    value: float, interval_meta: "Interval", errors: list[str]
) -> None:
    """Check upper bound of interval."""
    if interval_meta.lt is not None:
        try:
            if not value < interval_meta.lt:  # pyright: ignore[reportOperatorIssue]
                errors.append(f"must be less than {interval_meta.lt}.")
        except TypeError:
            errors.append(f"cannot be compared with {interval_meta.lt}.")
    elif interval_meta.le is not None:
        try:
            if not value <= interval_meta.le:  # pyright: ignore[reportOperatorIssue]
                errors.append(f"must be less than or equal to {interval_meta.le}.")
        except TypeError:
            errors.append(f"cannot be compared with {interval_meta.le}.")


def validate_interval(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate value is within range with inclusive/exclusive bounds."""
    interval_meta = cast("Interval", metadata)
    errors: list[str] = []

    if value is None:
        return None

    if not isinstance(value, (int, float)):
        errors.append("must be a number.")
        return tuple(errors)

    _check_lower_bound(value, interval_meta, errors)
    _check_upper_bound(value, interval_meta, errors)

    if errors:
        return tuple(errors)
    return None


def validate_is_integer(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate value is whole number."""
    if value is None:
        return None

    if isinstance(value, int):
        return None  # Already an integer

    if isinstance(value, float):
        if value.is_integer():
            return None
        return ("must be a whole number (no decimal part).",)

    return ("must be a number.",)


def validate_is_positive(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate value is > 0."""
    if value is None:
        return None

    if not isinstance(value, (int, float)):
        return ("must be a number.",)

    if not value > 0:
        return (f"must be greater than 0, got {value}.",)

    return None


def validate_is_negative(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate value is < 0."""
    if value is None:
        return None

    if not isinstance(value, (int, float)):
        return ("must be a number.",)

    if not value < 0:
        return (f"must be less than 0, got {value}.",)

    return None


def validate_is_non_negative(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate value is >= 0."""
    if value is None:
        return None

    if not isinstance(value, (int, float)):
        return ("must be a number.",)

    if not value >= 0:
        return (f"must be greater than or equal to 0, got {value}.",)

    return None


def validate_is_non_positive(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate value is <= 0."""
    if value is None:
        return None

    if not isinstance(value, (int, float)):
        return ("must be a number.",)

    if not value <= 0:
        return (f"must be less than or equal to 0, got {value}.",)

    return None


def validate_precision(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate decimal precision constraint."""
    precision_meta = cast("Precision", metadata)

    if value is None:
        return None

    if isinstance(value, int):
        return None  # Integers have no decimal places

    if isinstance(value, float):
        # Convert to Decimal for precise decimal place counting
        decimal_value = Decimal(str(value))
        tuple_exp = decimal_value.as_tuple().exponent
        # exponent is int for normal numbers, 'n'/'N'/'F' for special values
        if not isinstance(tuple_exp, int):
            return ("cannot determine decimal places for special value.",)

        decimal_places = abs(tuple_exp)

        if decimal_places > precision_meta.max_decimals:
            return (
                (
                    f"must have at most {precision_meta.max_decimals} decimal places, "
                    f"got {decimal_places}."
                ),
            )
        return None

    return ("must be a number.",)
