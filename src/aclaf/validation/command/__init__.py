from annotated_types import Predicate

from aclaf.validation._registry import ValidatorRegistry
from aclaf.validation._shared import validate_predicate

from ._conflict import ConflictsWith, validate_conflicts_with
from ._constraint import (
    AtLeastOneOf,
    AtMostOneOf,
    ExactlyOneOf,
    MutuallyExclusive,
    validate_at_least_one_of,
    validate_at_most_one_of,
    validate_exactly_one_of,
    validate_mutually_exclusive,
)
from ._dependency import Forbids, Requires, validate_forbids, validate_requires

__all__ = [
    "AtLeastOneOf",
    "AtMostOneOf",
    "ConflictsWith",
    "ExactlyOneOf",
    "Forbids",
    "MutuallyExclusive",
    "Requires",
    "validate_at_least_one_of",
    "validate_at_most_one_of",
    "validate_conflicts_with",
    "validate_exactly_one_of",
    "validate_forbids",
    "validate_mutually_exclusive",
    "validate_requires",
]


def _create_default_command_validators() -> ValidatorRegistry:
    """Creates default command validator registry.

    This function is called once at module initialization to populate
    the default validator registry. The registry is cached at module level.
    """
    registry = ValidatorRegistry()

    # Shared validators
    registry.register(Predicate, validate_predicate)

    # Constraint validators
    registry.register(AtLeastOneOf, validate_at_least_one_of)
    registry.register(AtMostOneOf, validate_at_most_one_of)
    registry.register(ExactlyOneOf, validate_exactly_one_of)
    registry.register(MutuallyExclusive, validate_mutually_exclusive)

    # Dependency validators
    registry.register(Requires, validate_requires)
    registry.register(Forbids, validate_forbids)

    # Conflict validators
    registry.register(ConflictsWith, validate_conflicts_with)

    return registry


# Module-level singleton - initialized once at import time
_DEFAULT_COMMAND_VALIDATORS: ValidatorRegistry = _create_default_command_validators()


def default_command_validators() -> ValidatorRegistry:
    """Returns cached default command validator registry.

    Note: This registry is shared across all callers. Modifications to the
    returned registry will affect all subsequent calls. This is not thread-safe
    for concurrent modifications.
    """
    return _DEFAULT_COMMAND_VALIDATORS
