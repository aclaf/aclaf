"""Sequence domain validators for parameter-scoped validation.

This module provides validators for sequence (list/tuple/set) values:
- UniqueItems: All items must be unique (no duplicates)
- SequenceContains: Sequence must contain specific item(s)
- AllMatch: All items match predicate/pattern
- AnyMatch: At least one item matches predicate
- NoneMatch: No items match predicate/pattern
- ItemType: All items must be of specified type(s)
"""

# pyright: reportUnusedParameter=false

from collections.abc import Callable, Sequence as SequenceABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from annotated_types import BaseMetadata

if TYPE_CHECKING:
    from aclaf.types import ParameterValueMappingType, ParameterValueType
    from aclaf.validation._registry import ValidatorMetadataType

MAX_ERROR_DISPLAY_ITEMS = 5


@dataclass(slots=True, frozen=True)
class UniqueItems(BaseMetadata):
    """All items in sequence must be unique."""


@dataclass(slots=True, frozen=True)
class SequenceContains(BaseMetadata):
    """Sequence must contain specific item(s)."""

    items: tuple[object, ...]


@dataclass(slots=True, frozen=True)
class AllMatch(BaseMetadata):
    """All items match predicate/pattern."""

    predicate: Callable[[Any], bool]  # pyright: ignore[reportExplicitAny]


@dataclass(slots=True, frozen=True)
class AnyMatch(BaseMetadata):
    """At least one item matches predicate."""

    predicate: Callable[[Any], bool]  # pyright: ignore[reportExplicitAny]


@dataclass(slots=True, frozen=True)
class NoneMatch(BaseMetadata):
    """No items match predicate/pattern."""

    predicate: Callable[[Any], bool]  # pyright: ignore[reportExplicitAny]


@dataclass(slots=True, frozen=True)
class ItemType(BaseMetadata):
    """All items must be of specified type(s)."""

    types: tuple[type, ...]


def validate_unique_items(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate all items are unique."""
    if value is None:
        return None

    if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
        return ("must be a sequence (list, tuple, or set).",)

    # Pre-check if all items are hashable
    try:
        _ = {hash(item) for item in value}
    except TypeError:
        # Contains unhashable items - use slower comparison-based method
        return _validate_unique_items_unhashable(value)

    # All items are hashable - use fast set-based deduplication
    seen: set[object] = set()
    duplicates: set[object] = set()

    for item in value:
        if item in seen:
            duplicates.add(item)
        seen.add(item)

    if duplicates:
        # Sort duplicates for consistent output (may fail if items uncomparable)
        sorted_dups: list[object]
        try:
            sorted_dups = sorted(duplicates)  # pyright: ignore[reportArgumentType, reportUnknownVariableType]
        except TypeError:
            sorted_dups = list(duplicates)
        dup_str = ", ".join(repr(d) for d in sorted_dups)
        return (f"contains duplicate items: {dup_str}.",)

    return None


def _validate_unique_items_unhashable(
    value: "SequenceABC[object]",
) -> tuple[str, ...] | None:
    """Validate unique items for sequences with unhashable items."""
    seen: list[object] = []
    duplicates: list[object] = []

    for item in value:
        if item in seen and item not in duplicates:
            duplicates.append(item)
        elif item not in seen:
            seen.append(item)

    if duplicates:
        dup_str = ", ".join(repr(d) for d in duplicates)
        return (f"contains duplicate items: {dup_str}.",)

    return None


def validate_sequence_contains(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate sequence contains specific item(s)."""
    contains_meta = cast("SequenceContains", metadata)

    if value is None:
        return None

    if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
        return ("must be a sequence (list, tuple, or set).",)

    missing = [item for item in contains_meta.items if item not in value]

    if missing:
        missing_str = ", ".join(repr(m) for m in missing)
        return (f"must contain: {missing_str}.",)

    return None


def validate_all_match(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate all items match predicate."""
    all_match_meta = cast("AllMatch", metadata)

    if value is None:
        return None

    if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
        return ("must be a sequence (list, tuple, or set).",)

    failing_items = [item for item in value if not all_match_meta.predicate(item)]

    if failing_items:
        failing_str = ", ".join(
            repr(f) for f in failing_items[:MAX_ERROR_DISPLAY_ITEMS]
        )
        count = len(failing_items)
        if count > MAX_ERROR_DISPLAY_ITEMS:
            return (
                (f"{count} items do not match predicate. First 5: {failing_str}..."),
            )
        return (f"items do not match predicate: {failing_str}.",)

    return None


def validate_any_match(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate at least one item matches predicate."""
    any_match_meta = cast("AnyMatch", metadata)

    if value is None:
        return None

    if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
        return ("must be a sequence (list, tuple, or set).",)

    if not any(any_match_meta.predicate(item) for item in value):
        return ("at least one item must match predicate.",)

    return None


def validate_none_match(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate no items match predicate."""
    none_match_meta = cast("NoneMatch", metadata)

    if value is None:
        return None

    if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
        return ("must be a sequence (list, tuple, or set).",)

    matching_items = [item for item in value if none_match_meta.predicate(item)]

    if matching_items:
        matching_str = ", ".join(
            repr(m) for m in matching_items[:MAX_ERROR_DISPLAY_ITEMS]
        )
        count = len(matching_items)
        if count > MAX_ERROR_DISPLAY_ITEMS:
            return (
                (
                    f"{count} items match predicate (none should). "
                    f"First 5: {matching_str}..."
                ),
            )
        return (f"items must not match predicate: {matching_str}.",)

    return None


def validate_item_type(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    """Validate all items are of specified type(s)."""
    item_type_meta = cast("ItemType", metadata)

    if value is None:
        return None

    if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
        return ("must be a sequence (list, tuple, or set).",)

    invalid_items = [
        item for item in value if not isinstance(item, item_type_meta.types)
    ]

    if invalid_items:
        type_names = ", ".join(t.__name__ for t in item_type_meta.types)
        invalid_str = ", ".join(
            f"{item!r} ({type(item).__name__})"
            for item in invalid_items[:MAX_ERROR_DISPLAY_ITEMS]
        )
        count = len(invalid_items)
        if count > MAX_ERROR_DISPLAY_ITEMS:
            return (
                (
                    f"{count} items are not of type {type_names}. "
                    f"First 5: {invalid_str}..."
                ),
            )
        return (f"all items must be of type {type_names}. Invalid: {invalid_str}.",)

    return None
