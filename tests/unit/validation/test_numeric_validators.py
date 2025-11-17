# pyright: reportAny=false, reportExplicitAny=false

from annotated_types import Ge, Gt, Le, Lt, MultipleOf

from aclaf._validation import (
    ParameterValidatorRegistry,
    validate_ge,
    validate_gt,
    validate_le,
    validate_lt,
    validate_multiple_of,
)


class TestGreaterThanValidator:
    def test_validate_gt_with_value_greater_than_bound_succeeds(self):
        result = validate_gt(10, {}, Gt(5))
        assert result is None

    def test_validate_gt_with_value_equal_to_bound_fails(self):
        result = validate_gt(5, {}, Gt(5))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 5" in result[0]

    def test_validate_gt_with_value_less_than_bound_fails(self):
        result = validate_gt(3, {}, Gt(5))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 5" in result[0]

    def test_validate_gt_with_float_value_greater_than_bound_succeeds(self):
        result = validate_gt(5.5, {}, Gt(5.0))
        assert result is None

    def test_validate_gt_with_float_value_equal_to_bound_fails(self):
        result = validate_gt(5.0, {}, Gt(5.0))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 5.0" in result[0]

    def test_validate_gt_with_negative_values_succeeds_when_greater(self):
        result = validate_gt(-5, {}, Gt(-10))
        assert result is None

    def test_validate_gt_with_negative_values_fails_when_not_greater(self):
        result = validate_gt(-10, {}, Gt(-5))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than -5" in result[0]

    def test_validate_gt_with_zero_boundary_positive_value_succeeds(self):
        result = validate_gt(1, {}, Gt(0))
        assert result is None

    def test_validate_gt_with_zero_boundary_zero_value_fails(self):
        result = validate_gt(0, {}, Gt(0))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 0" in result[0]

    def test_validate_gt_with_incomparable_type_fails(self):
        result = validate_gt("string", {}, Gt(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be compared with 5" in result[0]

    def test_validate_gt_with_none_value_fails(self):
        result = validate_gt(None, {}, Gt(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be compared with 5" in result[0]

    def test_validate_gt_via_registry_with_valid_value_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(10, {}, (Gt(5),))
        assert result is None

    def test_validate_gt_via_registry_with_invalid_value_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(3, {}, (Gt(5),))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 5" in result[0]


class TestGreaterThanOrEqualValidator:
    def test_validate_ge_with_value_greater_than_bound_succeeds(self):
        result = validate_ge(10, {}, Ge(5))
        assert result is None

    def test_validate_ge_with_value_equal_to_bound_succeeds(self):
        result = validate_ge(5, {}, Ge(5))
        assert result is None

    def test_validate_ge_with_value_less_than_bound_fails(self):
        result = validate_ge(3, {}, Ge(5))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than or equal to 5" in result[0]

    def test_validate_ge_with_float_value_equal_to_bound_succeeds(self):
        result = validate_ge(5.0, {}, Ge(5.0))
        assert result is None

    def test_validate_ge_with_float_value_greater_than_bound_succeeds(self):
        result = validate_ge(5.5, {}, Ge(5.0))
        assert result is None

    def test_validate_ge_with_float_value_less_than_bound_fails(self):
        result = validate_ge(4.5, {}, Ge(5.0))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than or equal to 5.0" in result[0]

    def test_validate_ge_with_negative_values_succeeds_when_greater_or_equal(self):
        result = validate_ge(-5, {}, Ge(-5))
        assert result is None

    def test_validate_ge_with_negative_values_fails_when_less(self):
        result = validate_ge(-10, {}, Ge(-5))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than or equal to -5" in result[0]

    def test_validate_ge_with_zero_boundary_zero_value_succeeds(self):
        result = validate_ge(0, {}, Ge(0))
        assert result is None

    def test_validate_ge_with_zero_boundary_negative_value_fails(self):
        result = validate_ge(-1, {}, Ge(0))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than or equal to 0" in result[0]

    def test_validate_ge_with_incomparable_type_fails(self):
        result = validate_ge("string", {}, Ge(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be compared with 5" in result[0]

    def test_validate_ge_with_none_value_fails(self):
        result = validate_ge(None, {}, Ge(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be compared with 5" in result[0]

    def test_validate_ge_via_registry_with_valid_value_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(5, {}, (Ge(5),))
        assert result is None

    def test_validate_ge_via_registry_with_invalid_value_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(3, {}, (Ge(5),))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than or equal to 5" in result[0]


class TestLessThanValidator:
    def test_validate_lt_with_value_less_than_bound_succeeds(self):
        result = validate_lt(3, {}, Lt(5))
        assert result is None

    def test_validate_lt_with_value_equal_to_bound_fails(self):
        result = validate_lt(5, {}, Lt(5))
        assert result is not None
        assert len(result) == 1
        assert "must be less than 5" in result[0]

    def test_validate_lt_with_value_greater_than_bound_fails(self):
        result = validate_lt(10, {}, Lt(5))
        assert result is not None
        assert len(result) == 1
        assert "must be less than 5" in result[0]

    def test_validate_lt_with_float_value_less_than_bound_succeeds(self):
        result = validate_lt(4.5, {}, Lt(5.0))
        assert result is None

    def test_validate_lt_with_float_value_equal_to_bound_fails(self):
        result = validate_lt(5.0, {}, Lt(5.0))
        assert result is not None
        assert len(result) == 1
        assert "must be less than 5.0" in result[0]

    def test_validate_lt_with_negative_values_succeeds_when_less(self):
        result = validate_lt(-10, {}, Lt(-5))
        assert result is None

    def test_validate_lt_with_negative_values_fails_when_not_less(self):
        result = validate_lt(-5, {}, Lt(-10))
        assert result is not None
        assert len(result) == 1
        assert "must be less than -10" in result[0]

    def test_validate_lt_with_zero_boundary_negative_value_succeeds(self):
        result = validate_lt(-1, {}, Lt(0))
        assert result is None

    def test_validate_lt_with_zero_boundary_zero_value_fails(self):
        result = validate_lt(0, {}, Lt(0))
        assert result is not None
        assert len(result) == 1
        assert "must be less than 0" in result[0]

    def test_validate_lt_with_incomparable_type_fails(self):
        result = validate_lt("string", {}, Lt(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be compared with 5" in result[0]

    def test_validate_lt_with_none_value_fails(self):
        result = validate_lt(None, {}, Lt(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be compared with 5" in result[0]

    def test_validate_lt_via_registry_with_valid_value_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(3, {}, (Lt(5),))
        assert result is None

    def test_validate_lt_via_registry_with_invalid_value_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(10, {}, (Lt(5),))
        assert result is not None
        assert len(result) == 1
        assert "must be less than 5" in result[0]


class TestLessThanOrEqualValidator:
    def test_validate_le_with_value_less_than_bound_succeeds(self):
        result = validate_le(3, {}, Le(5))
        assert result is None

    def test_validate_le_with_value_equal_to_bound_succeeds(self):
        result = validate_le(5, {}, Le(5))
        assert result is None

    def test_validate_le_with_value_greater_than_bound_fails(self):
        result = validate_le(10, {}, Le(5))
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 5" in result[0]

    def test_validate_le_with_float_value_equal_to_bound_succeeds(self):
        result = validate_le(5.0, {}, Le(5.0))
        assert result is None

    def test_validate_le_with_float_value_less_than_bound_succeeds(self):
        result = validate_le(4.5, {}, Le(5.0))
        assert result is None

    def test_validate_le_with_float_value_greater_than_bound_fails(self):
        result = validate_le(5.5, {}, Le(5.0))
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 5.0" in result[0]

    def test_validate_le_with_negative_values_succeeds_when_less_or_equal(self):
        result = validate_le(-5, {}, Le(-5))
        assert result is None

    def test_validate_le_with_negative_values_fails_when_greater(self):
        result = validate_le(-5, {}, Le(-10))
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to -10" in result[0]

    def test_validate_le_with_zero_boundary_zero_value_succeeds(self):
        result = validate_le(0, {}, Le(0))
        assert result is None

    def test_validate_le_with_zero_boundary_positive_value_fails(self):
        result = validate_le(1, {}, Le(0))
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 0" in result[0]

    def test_validate_le_with_incomparable_type_fails(self):
        result = validate_le("string", {}, Le(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be compared with 5" in result[0]

    def test_validate_le_with_none_value_fails(self):
        result = validate_le(None, {}, Le(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be compared with 5" in result[0]

    def test_validate_le_via_registry_with_valid_value_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(5, {}, (Le(5),))
        assert result is None

    def test_validate_le_via_registry_with_invalid_value_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(10, {}, (Le(5),))
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 5" in result[0]


class TestMultipleOfValidator:
    def test_validate_multiple_of_with_exact_multiple_succeeds(self):
        result = validate_multiple_of(10, {}, MultipleOf(5))
        assert result is None

    def test_validate_multiple_of_with_zero_succeeds(self):
        result = validate_multiple_of(0, {}, MultipleOf(5))
        assert result is None

    def test_validate_multiple_of_with_non_multiple_fails(self):
        result = validate_multiple_of(7, {}, MultipleOf(5))
        assert result is not None
        assert len(result) == 1
        assert "must be a multiple of 5" in result[0]

    def test_validate_multiple_of_with_negative_multiple_succeeds(self):
        result = validate_multiple_of(-10, {}, MultipleOf(5))
        assert result is None

    def test_validate_multiple_of_with_negative_non_multiple_fails(self):
        result = validate_multiple_of(-7, {}, MultipleOf(5))
        assert result is not None
        assert len(result) == 1
        assert "must be a multiple of 5" in result[0]

    def test_validate_multiple_of_with_float_exact_multiple_succeeds(self):
        result = validate_multiple_of(1.5, {}, MultipleOf(0.5))
        assert result is None

    def test_validate_multiple_of_with_float_non_multiple_fails(self):
        result = validate_multiple_of(1.3, {}, MultipleOf(0.5))
        assert result is not None
        assert len(result) == 1
        assert "must be a multiple of 0.5" in result[0]

    def test_validate_multiple_of_with_one_returns_all_integers(self):
        result = validate_multiple_of(42, {}, MultipleOf(1))
        assert result is None

    def test_validate_multiple_of_with_same_value_succeeds(self):
        result = validate_multiple_of(5, {}, MultipleOf(5))
        assert result is None

    def test_validate_multiple_of_with_incompatible_type_fails(self):
        result = validate_multiple_of("string", {}, MultipleOf(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be divided by 5" in result[0]

    def test_validate_multiple_of_with_none_value_fails(self):
        result = validate_multiple_of(None, {}, MultipleOf(5))
        assert result is not None
        assert len(result) == 1
        assert "cannot be divided by 5" in result[0]

    def test_validate_multiple_of_via_registry_with_valid_value_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(10, {}, (MultipleOf(5),))
        assert result is None

    def test_validate_multiple_of_via_registry_with_invalid_value_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(7, {}, (MultipleOf(5),))
        assert result is not None
        assert len(result) == 1
        assert "must be a multiple of 5" in result[0]


class TestCombinedNumericValidators:
    def test_combined_gt_and_lt_with_value_in_range_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(50, {}, (Gt(0), Lt(100)))
        assert result is None

    def test_combined_gt_and_lt_with_value_below_range_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(-5, {}, (Gt(0), Lt(100)))
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 0" in result[0]

    def test_combined_gt_and_lt_with_value_above_range_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(150, {}, (Gt(0), Lt(100)))
        assert result is not None
        assert len(result) == 1
        assert "must be less than 100" in result[0]

    def test_combined_ge_and_le_with_value_at_lower_bound_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(0, {}, (Ge(0), Le(100)))
        assert result is None

    def test_combined_ge_and_le_with_value_at_upper_bound_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(100, {}, (Ge(0), Le(100)))
        assert result is None

    def test_combined_ge_le_and_multiple_of_all_satisfied_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(50, {}, (Ge(0), Le(100), MultipleOf(10)))
        assert result is None

    def test_combined_ge_le_and_multiple_of_multiple_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate(55, {}, (Ge(0), Le(100), MultipleOf(10)))
        assert result is not None
        assert len(result) == 1
        assert "must be a multiple of 10" in result[0]

    def test_multiple_validators_failing_returns_all_errors(self):
        registry = ParameterValidatorRegistry()
        # Value 151 fails both Lt(100) and MultipleOf(3)
        result = registry.validate(151, {}, (Gt(0), Lt(100), MultipleOf(3)))
        assert result is not None
        assert len(result) == 2
        assert any("must be less than 100" in err for err in result)
        assert any("must be a multiple of 3" in err for err in result)
