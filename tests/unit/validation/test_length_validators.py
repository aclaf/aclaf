# pyright: reportAny=false, reportExplicitAny=false, reportArgumentType=false

from annotated_types import MaxLen, MinLen

from aclaf._validation import (
    ParameterValidatorRegistry,
    validate_max_len,
    validate_min_len,
)


class TestMinLenValidator:
    def test_validate_min_len_with_string_exceeding_minimum_succeeds(self):
        result = validate_min_len("hello", {}, MinLen(3))
        assert result is None

    def test_validate_min_len_with_string_equal_to_minimum_succeeds(self):
        result = validate_min_len("abc", {}, MinLen(3))
        assert result is None

    def test_validate_min_len_with_string_below_minimum_fails(self):
        result = validate_min_len("ab", {}, MinLen(3))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 3" in result[0]

    def test_validate_min_len_with_empty_string_and_zero_minimum_succeeds(self):
        result = validate_min_len("", {}, MinLen(0))
        assert result is None

    def test_validate_min_len_with_empty_string_and_positive_minimum_fails(self):
        result = validate_min_len("", {}, MinLen(1))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 1" in result[0]

    def test_validate_min_len_with_list_exceeding_minimum_succeeds(self):
        result = validate_min_len([1, 2, 3, 4], {}, MinLen(3))
        assert result is None

    def test_validate_min_len_with_list_equal_to_minimum_succeeds(self):
        result = validate_min_len([1, 2, 3], {}, MinLen(3))
        assert result is None

    def test_validate_min_len_with_list_below_minimum_fails(self):
        result = validate_min_len([1, 2], {}, MinLen(3))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 3" in result[0]

    def test_validate_min_len_with_empty_list_and_zero_minimum_succeeds(self):
        empty_list: list[int] = []
        result = validate_min_len(empty_list, {}, MinLen(0))
        assert result is None

    def test_validate_min_len_with_empty_list_and_positive_minimum_fails(self):
        empty_list: list[int] = []
        result = validate_min_len(empty_list, {}, MinLen(1))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 1" in result[0]

    def test_validate_min_len_with_tuple_exceeding_minimum_succeeds(self):
        result = validate_min_len((1, 2, 3, 4), {}, MinLen(3))
        assert result is None

    def test_validate_min_len_with_tuple_below_minimum_fails(self):
        result = validate_min_len((1, 2), {}, MinLen(3))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 3" in result[0]

    def test_validate_min_len_with_dict_exceeding_minimum_succeeds(self):
        result = validate_min_len({"a": 1, "b": 2, "c": 3}, {}, MinLen(2))
        assert result is None

    def test_validate_min_len_with_dict_below_minimum_fails(self):
        result = validate_min_len({"a": 1}, {}, MinLen(2))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 2" in result[0]

    def test_validate_min_len_with_unicode_string_counts_characters(self):
        result = validate_min_len("café", {}, MinLen(4))
        assert result is None

    def test_validate_min_len_with_unicode_string_below_minimum_fails(self):
        result = validate_min_len("café", {}, MinLen(5))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 5" in result[0]

    def test_validate_min_len_with_type_without_len_fails(self):
        result = validate_min_len(42, {}, MinLen(3))
        assert result is not None
        assert len(result) == 1
        assert "length cannot be determined" in result[0]

    def test_validate_min_len_with_none_value_fails(self):
        result = validate_min_len(None, {}, MinLen(3))
        assert result is not None
        assert len(result) == 1
        assert "length cannot be determined" in result[0]

    def test_validate_min_len_via_registry_with_valid_value_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("hello", {}, (MinLen(3),))
        assert result is None

    def test_validate_min_len_via_registry_with_invalid_value_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("ab", {}, (MinLen(3),))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 3" in result[0]


class TestMaxLenValidator:
    def test_validate_max_len_with_string_below_maximum_succeeds(self):
        result = validate_max_len("ab", {}, MaxLen(5))
        assert result is None

    def test_validate_max_len_with_string_equal_to_maximum_succeeds(self):
        result = validate_max_len("hello", {}, MaxLen(5))
        assert result is None

    def test_validate_max_len_with_string_exceeding_maximum_fails(self):
        result = validate_max_len("hello world", {}, MaxLen(5))
        assert result is not None
        assert len(result) == 1
        assert "length must be at most 5" in result[0]

    def test_validate_max_len_with_empty_string_succeeds(self):
        result = validate_max_len("", {}, MaxLen(5))
        assert result is None

    def test_validate_max_len_with_empty_string_and_zero_maximum_succeeds(self):
        result = validate_max_len("", {}, MaxLen(0))
        assert result is None

    def test_validate_max_len_with_list_below_maximum_succeeds(self):
        result = validate_max_len([1, 2], {}, MaxLen(5))
        assert result is None

    def test_validate_max_len_with_list_equal_to_maximum_succeeds(self):
        result = validate_max_len([1, 2, 3, 4, 5], {}, MaxLen(5))
        assert result is None

    def test_validate_max_len_with_list_exceeding_maximum_fails(self):
        result = validate_max_len([1, 2, 3, 4, 5, 6], {}, MaxLen(5))
        assert result is not None
        assert len(result) == 1
        assert "length must be at most 5" in result[0]

    def test_validate_max_len_with_empty_list_succeeds(self):
        empty_list: list[int] = []
        result = validate_max_len(empty_list, {}, MaxLen(5))
        assert result is None

    def test_validate_max_len_with_tuple_below_maximum_succeeds(self):
        result = validate_max_len((1, 2), {}, MaxLen(5))
        assert result is None

    def test_validate_max_len_with_tuple_exceeding_maximum_fails(self):
        result = validate_max_len((1, 2, 3, 4, 5, 6), {}, MaxLen(5))
        assert result is not None
        assert len(result) == 1
        assert "length must be at most 5" in result[0]

    def test_validate_max_len_with_dict_below_maximum_succeeds(self):
        result = validate_max_len({"a": 1}, {}, MaxLen(5))
        assert result is None

    def test_validate_max_len_with_dict_exceeding_maximum_fails(self):
        test_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6}
        result = validate_max_len(test_dict, {}, MaxLen(5))
        assert result is not None
        assert len(result) == 1
        assert "length must be at most 5" in result[0]

    def test_validate_max_len_with_unicode_string_counts_characters(self):
        result = validate_max_len("café", {}, MaxLen(4))
        assert result is None

    def test_validate_max_len_with_unicode_string_exceeding_maximum_fails(self):
        result = validate_max_len("café", {}, MaxLen(3))
        assert result is not None
        assert len(result) == 1
        assert "length must be at most 3" in result[0]

    def test_validate_max_len_with_type_without_len_fails(self):
        result = validate_max_len(42, {}, MaxLen(5))
        assert result is not None
        assert len(result) == 1
        assert "length cannot be determined" in result[0]

    def test_validate_max_len_with_none_value_fails(self):
        result = validate_max_len(None, {}, MaxLen(5))
        assert result is not None
        assert len(result) == 1
        assert "length cannot be determined" in result[0]

    def test_validate_max_len_via_registry_with_valid_value_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("hello", {}, (MaxLen(5),))
        assert result is None

    def test_validate_max_len_via_registry_with_invalid_value_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("hello world", {}, (MaxLen(5),))
        assert result is not None
        assert len(result) == 1
        assert "length must be at most 5" in result[0]


class TestCombinedLengthValidators:
    def test_combined_min_len_and_max_len_with_value_in_range_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("hello", {}, (MinLen(3), MaxLen(10)))
        assert result is None

    def test_combined_min_len_and_max_len_at_lower_bound_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("abc", {}, (MinLen(3), MaxLen(10)))
        assert result is None

    def test_combined_min_len_and_max_len_at_upper_bound_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("abcdefghij", {}, (MinLen(3), MaxLen(10)))
        assert result is None

    def test_combined_min_len_and_max_len_below_range_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("ab", {}, (MinLen(3), MaxLen(10)))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 3" in result[0]

    def test_combined_min_len_and_max_len_above_range_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("hello world!", {}, (MinLen(3), MaxLen(10)))
        assert result is not None
        assert len(result) == 1
        assert "length must be at most 10" in result[0]

    def test_combined_min_len_and_max_len_with_exact_length_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate("exact", {}, (MinLen(5), MaxLen(5)))
        assert result is None

    def test_combined_min_len_and_max_len_with_list_in_range_succeeds(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate([1, 2, 3, 4], {}, (MinLen(3), MaxLen(10)))
        assert result is None

    def test_combined_min_len_and_max_len_with_list_below_range_fails(self):
        registry = ParameterValidatorRegistry()
        result = registry.validate([1, 2], {}, (MinLen(3), MaxLen(10)))
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 3" in result[0]
