# pyright: reportAny=false, reportExplicitAny=false

from typing import TYPE_CHECKING

import pytest
from annotated_types import BaseMetadata, Ge, Gt

from aclaf._validation import ParameterValidatorRegistry
from aclaf.logging import NullLogger

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aclaf.types import ParameterValueType


class CustomMetadata(BaseMetadata):
    """Custom metadata for testing."""

    min_value: int

    def __init__(self, min_value: int) -> None:
        self.min_value = min_value


def custom_validator(
    value: "ParameterValueType | None",
    _other_parameters: "Mapping[str, ParameterValueType | None]",
    metadata: BaseMetadata,
) -> tuple[str, ...] | None:
    custom_meta = metadata if isinstance(metadata, CustomMetadata) else None
    if custom_meta is None:
        return ("invalid metadata type",)
    if not isinstance(value, int):
        return ("value must be an integer",)
    if value < custom_meta.min_value:
        return (f"value must be at least {custom_meta.min_value}",)
    return None


class TestParameterValidatorRegistry:
    def test_registry_initializes_with_default_validators(self):
        registry = ParameterValidatorRegistry()
        assert registry.has_validator(Gt)
        assert registry.has_validator(Ge)

    def test_registry_initializes_with_logger(self):
        logger = NullLogger()
        registry = ParameterValidatorRegistry(logger=logger)
        assert registry.logger is logger

    def test_registry_register_custom_validator_succeeds(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        empty_registry.register(CustomMetadata, custom_validator)
        assert empty_registry.has_validator(CustomMetadata)

    def test_registry_register_duplicate_key_raises_value_error(
        self,
        registry: ParameterValidatorRegistry,
    ):
        with pytest.raises(ValueError, match="already registered"):
            registry.register(Gt, custom_validator)

    def test_registry_unregister_existing_key_succeeds(
        self,
        registry: ParameterValidatorRegistry,
    ):
        registry.unregister(Gt)
        assert not registry.has_validator(Gt)

    def test_registry_unregister_nonexistent_key_raises_key_error(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        with pytest.raises(KeyError):
            empty_registry.unregister(CustomMetadata)

    def test_registry_get_validator_for_existing_key_returns_function(
        self,
        registry: ParameterValidatorRegistry,
    ):
        validator = registry.get_validator(Gt)
        assert validator is not None
        assert callable(validator)

    def test_registry_get_validator_for_nonexistent_key_returns_none(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        validator = empty_registry.get_validator(CustomMetadata)
        assert validator is None

    def test_registry_has_validator_for_existing_key_returns_true(
        self,
        registry: ParameterValidatorRegistry,
    ):
        assert registry.has_validator(Gt)

    def test_registry_has_validator_for_nonexistent_key_returns_false(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        assert not empty_registry.has_validator(CustomMetadata)

    def test_registry_validate_with_no_metadata_returns_none(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(42, {}, ())
        assert result is None

    def test_registry_validate_with_single_valid_metadata_returns_none(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(10, {}, (Gt(5),))
        assert result is None

    def test_registry_validate_with_single_invalid_metadata_returns_errors(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(3, {}, (Gt(5),))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 5" in result[0]

    def test_registry_validate_with_multiple_valid_metadata_returns_none(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(10, {}, (Gt(5), Ge(10)))
        assert result is None

    def test_registry_validate_with_multiple_metadata_some_invalid_returns_errors(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(10, {}, (Gt(5), Gt(15)))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 15" in result[0]

    def test_registry_validate_with_all_invalid_metadata_returns_all_errors(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(3, {}, (Gt(5), Ge(10)))
        assert result is not None
        assert len(result) == 2
        assert any("must be greater than 5" in err for err in result)
        assert any("must be greater than or equal to 10" in err for err in result)

    def test_registry_validate_skips_metadata_without_validator(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        result = empty_registry.validate(42, {}, (CustomMetadata(10),))
        assert result is None

    def test_registry_validate_with_custom_validator_succeeds(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        empty_registry.register(CustomMetadata, custom_validator)
        result = empty_registry.validate(15, {}, (CustomMetadata(10),))
        assert result is None

    def test_registry_validate_with_custom_validator_fails(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        empty_registry.register(CustomMetadata, custom_validator)
        result = empty_registry.validate(5, {}, (CustomMetadata(10),))
        assert result is not None
        assert len(result) == 1
        assert "value must be at least 10" in result[0]

    def test_registry_validate_passes_other_parameters_to_validator(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        other_params: dict[str, ParameterValueType | None] = {
            "param1": 10,
            "param2": "test",
        }
        captured_params: dict[str, ParameterValueType | None] = {}

        def capturing_validator(
            _value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            _metadata: BaseMetadata,
        ) -> tuple[str, ...] | None:
            captured_params.update(other_parameters)
            return None

        empty_registry.register(CustomMetadata, capturing_validator)
        _ = empty_registry.validate(42, other_params, (CustomMetadata(10),))

        assert captured_params == other_params

    def test_registry_validate_with_mixed_registered_and_unregistered_metadata(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(10, {}, (Gt(5), CustomMetadata(10)))
        assert result is None

    def test_registry_allows_reregistration_after_unregister(
        self,
        registry: ParameterValidatorRegistry,
    ):
        original_validator = registry.get_validator(Gt)
        registry.unregister(Gt)
        assert not registry.has_validator(Gt)

        def new_validator(
            _value: "ParameterValueType | None",
            _other_parameters: "Mapping[str, ParameterValueType | None]",
            _metadata: BaseMetadata,
        ) -> tuple[str, ...] | None:
            return ("always fails",)

        registry.register(Gt, new_validator)
        assert registry.has_validator(Gt)
        assert registry.get_validator(Gt) is not original_validator

        result = registry.validate(100, {}, (Gt(5),))
        assert result is not None
        assert len(result) == 1
        assert "always fails" in result[0]


class TestParameterValidatorRegistryEdgeCases:
    def test_registry_validate_with_empty_metadata_tuple_returns_none(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(42, {}, ())
        assert result is None

    def test_registry_validate_with_none_value_and_no_metadata_returns_none(
        self,
        registry: ParameterValidatorRegistry,
    ):
        result = registry.validate(None, {}, ())
        assert result is None

    def test_registry_validate_preserves_error_order(
        self,
        registry: ParameterValidatorRegistry,
    ):
        from annotated_types import Le, Lt  # noqa: PLC0415

        result = registry.validate(150, {}, (Gt(0), Lt(100), Le(50)))
        assert result is not None
        errors = list(result)
        # Errors should appear in order of metadata
        assert "must be less than 100" in errors[0]
        assert "must be less than or equal to 50" in errors[1]

    def test_registry_handles_validator_returning_empty_tuple(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        def empty_error_validator(
            _value: "ParameterValueType | None",
            _other_parameters: "Mapping[str, ParameterValueType | None]",
            _metadata: BaseMetadata,
        ) -> tuple[str, ...] | None:
            return ()

        empty_registry.register(CustomMetadata, empty_error_validator)
        result = empty_registry.validate(42, {}, (CustomMetadata(10),))
        # Empty tuple should be treated as no errors
        assert result is None

    def test_registry_handles_validator_returning_multiple_errors(
        self,
        empty_registry: ParameterValidatorRegistry,
    ):
        def multi_error_validator(
            _value: "ParameterValueType | None",
            _other_parameters: "Mapping[str, ParameterValueType | None]",
            _metadata: BaseMetadata,
        ) -> tuple[str, ...] | None:
            return ("error 1", "error 2", "error 3")

        empty_registry.register(CustomMetadata, multi_error_validator)
        result = empty_registry.validate(42, {}, (CustomMetadata(10),))
        assert result is not None
        assert len(result) == 3
        assert result[0] == "error 1"
        assert result[1] == "error 2"
        assert result[2] == "error 3"
