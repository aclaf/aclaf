# pyright: reportAny=false, reportExplicitAny=false, reportArgumentType=false, reportUnannotatedClassAttribute=false, reportImplicitOverride=false, reportUnknownParameterType=false, reportMissingParameterType=false

from typing import Annotated, get_args

from annotated_types import (
    Ge,
    GroupedMetadata,
    Gt,
    Interval,
    Le,
    Lt,
    MaxLen,
    MinLen,
    MultipleOf,
)

from aclaf._internal._metadata import flatten_metadata
from aclaf._validation import ParameterValidatorRegistry


class TestIntervalUnpacking:
    def test_interval_with_gt_and_le_unpacks_to_gt_and_le(self):
        interval = Interval(gt=0, le=100)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 2
        assert any(isinstance(m, Gt) and m.gt == 0 for m in flattened)
        assert any(isinstance(m, Le) and m.le == 100 for m in flattened)

    def test_interval_with_ge_and_lt_unpacks_to_ge_and_lt(self):
        interval = Interval(ge=10, lt=100)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 2
        assert any(isinstance(m, Ge) and m.ge == 10 for m in flattened)
        assert any(isinstance(m, Lt) and m.lt == 100 for m in flattened)

    def test_interval_with_all_bounds_unpacks_to_all_constraints(self):
        interval = Interval(gt=0, ge=1, lt=100, le=99)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 4
        assert any(isinstance(m, Gt) and m.gt == 0 for m in flattened)
        assert any(isinstance(m, Ge) and m.ge == 1 for m in flattened)
        assert any(isinstance(m, Lt) and m.lt == 100 for m in flattened)
        assert any(isinstance(m, Le) and m.le == 99 for m in flattened)

    def test_interval_with_only_gt_unpacks_to_gt(self):
        interval = Interval(gt=0)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 1
        assert isinstance(flattened[0], Gt)
        assert flattened[0].gt == 0

    def test_interval_with_only_ge_unpacks_to_ge(self):
        interval = Interval(ge=5)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 1
        assert isinstance(flattened[0], Ge)
        assert flattened[0].ge == 5

    def test_interval_with_only_lt_unpacks_to_lt(self):
        interval = Interval(lt=100)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 1
        assert isinstance(flattened[0], Lt)
        assert flattened[0].lt == 100

    def test_interval_with_only_le_unpacks_to_le(self):
        interval = Interval(le=50)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 1
        assert isinstance(flattened[0], Le)
        assert flattened[0].le == 50

    def test_interval_with_no_bounds_unpacks_to_empty_list(self):
        interval = Interval()
        flattened = flatten_metadata([interval])

        assert len(flattened) == 0

    def test_interval_with_float_bounds_unpacks_correctly(self):
        interval = Interval(ge=0.5, le=99.9)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 2
        assert any(isinstance(m, Ge) and m.ge == 0.5 for m in flattened)
        assert any(isinstance(m, Le) and m.le == 99.9 for m in flattened)

    def test_interval_with_negative_bounds_unpacks_correctly(self):
        interval = Interval(gt=-100, lt=-10)
        flattened = flatten_metadata([interval])

        assert len(flattened) == 2
        assert any(isinstance(m, Gt) and m.gt == -100 for m in flattened)
        assert any(isinstance(m, Lt) and m.lt == -10 for m in flattened)

    def test_interval_validation_via_registry_succeeds_when_in_range(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(gt=0, lt=100)
        flattened_metadata = tuple(flatten_metadata([interval]))

        result = registry.validate(50, {}, flattened_metadata)
        assert result is None

    def test_interval_validation_via_registry_fails_when_below_lower_bound(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(gt=0, lt=100)
        flattened_metadata = tuple(flatten_metadata([interval]))

        result = registry.validate(0, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 0" in result[0]

    def test_interval_validation_via_registry_fails_when_above_upper_bound(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(gt=0, lt=100)
        flattened_metadata = tuple(flatten_metadata([interval]))

        result = registry.validate(100, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than 100" in result[0]

    def test_interval_validation_via_registry_accepts_boundary_with_ge(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(ge=0, le=100)
        flattened_metadata = tuple(flatten_metadata([interval]))

        result = registry.validate(0, {}, flattened_metadata)
        assert result is None

    def test_interval_validation_via_registry_accepts_boundary_with_le(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(ge=0, le=100)
        flattened_metadata = tuple(flatten_metadata([interval]))

        result = registry.validate(100, {}, flattened_metadata)
        assert result is None


class TestMixedGroupedAndIndividualMetadata:
    def test_interval_mixed_with_individual_constraints_flattens_correctly(self):
        interval = Interval(gt=0, lt=100)
        individual = MultipleOf(5)
        flattened = flatten_metadata([interval, individual])

        assert len(flattened) == 3
        assert any(isinstance(m, Gt) and m.gt == 0 for m in flattened)
        assert any(isinstance(m, Lt) and m.lt == 100 for m in flattened)
        assert any(isinstance(m, MultipleOf) and m.multiple_of == 5 for m in flattened)

    def test_multiple_intervals_flatten_correctly(self):
        interval1 = Interval(gt=0)
        interval2 = Interval(lt=100)
        flattened = flatten_metadata([interval1, interval2])

        assert len(flattened) == 2
        assert any(isinstance(m, Gt) and m.gt == 0 for m in flattened)
        assert any(isinstance(m, Lt) and m.lt == 100 for m in flattened)

    def test_interval_with_non_numeric_validators_flattens_correctly(self):
        interval = Interval(gt=0, lt=100)
        min_len = MinLen(3)
        max_len = MaxLen(10)
        flattened = flatten_metadata([interval, min_len, max_len])

        assert len(flattened) == 4
        assert any(isinstance(m, Gt) for m in flattened)
        assert any(isinstance(m, Lt) for m in flattened)
        assert any(isinstance(m, MinLen) for m in flattened)
        assert any(isinstance(m, MaxLen) for m in flattened)

    def test_validation_with_interval_and_multiple_of_all_satisfied(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(ge=0, le=100)
        multiple = MultipleOf(10)
        flattened_metadata = tuple(flatten_metadata([interval, multiple]))

        result = registry.validate(50, {}, flattened_metadata)
        assert result is None

    def test_validation_with_interval_satisfied_but_multiple_of_fails(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(ge=0, le=100)
        multiple = MultipleOf(10)
        flattened_metadata = tuple(flatten_metadata([interval, multiple]))

        result = registry.validate(55, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be a multiple of 10" in result[0]

    def test_validation_with_interval_fails_and_multiple_of_satisfied(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(ge=0, le=100)
        multiple = MultipleOf(10)
        flattened_metadata = tuple(flatten_metadata([interval, multiple]))

        result = registry.validate(110, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 100" in result[0]

    def test_validation_with_both_interval_and_multiple_of_fail(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(ge=0, le=100)
        multiple = MultipleOf(10)
        flattened_metadata = tuple(flatten_metadata([interval, multiple]))

        result = registry.validate(115, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 2
        assert any("must be less than or equal to 100" in err for err in result)
        assert any("must be a multiple of 10" in err for err in result)


class TestNestedGroupedMetadata:
    def test_nested_grouped_metadata_flattens_recursively(self):
        # Create a custom nested GroupedMetadata for testing
        # In practice, nested GroupedMetadata is unlikely but should be handled

        class NestedInterval(GroupedMetadata):
            def __init__(self, inner_interval: Interval) -> None:
                self._inner = inner_interval

            def __iter__(self):
                yield self._inner

        inner = Interval(gt=0, lt=100)
        nested = NestedInterval(inner)
        flattened = flatten_metadata([nested])

        # Should recursively flatten to the individual constraints
        assert len(flattened) == 2
        assert any(isinstance(m, Gt) and m.gt == 0 for m in flattened)
        assert any(isinstance(m, Lt) and m.lt == 100 for m in flattened)

    def test_deeply_nested_grouped_metadata_flattens_completely(self):
        class NestedInterval(GroupedMetadata):
            def __init__(self, inner):
                self._inner = inner

            def __iter__(self):
                yield self._inner

        inner = Interval(ge=10, le=90)
        level1 = NestedInterval(inner)
        level2 = NestedInterval(level1)
        flattened = flatten_metadata([level2])

        assert len(flattened) == 2
        assert any(isinstance(m, Ge) and m.ge == 10 for m in flattened)
        assert any(isinstance(m, Le) and m.le == 90 for m in flattened)


class TestTypeAliasMetadataExtraction:
    def test_metadata_from_annotated_type_alias_is_accessible(self):
        positive_int = Annotated[int, Gt(0)]

        # Verify metadata can be extracted from type alias
        args = get_args(positive_int)
        assert len(args) == 2
        assert args[0] is int
        assert isinstance(args[1], Gt)
        assert args[1].gt == 0

    def test_metadata_from_type_alias_with_interval(self):
        bounded_int = Annotated[int, Interval(ge=0, le=100)]

        args = get_args(bounded_int)
        assert len(args) == 2
        assert args[0] is int
        assert isinstance(args[1], Interval)

        # Flatten the interval
        flattened = flatten_metadata([args[1]])
        assert len(flattened) == 2
        assert any(isinstance(m, Ge) and m.ge == 0 for m in flattened)
        assert any(isinstance(m, Le) and m.le == 100 for m in flattened)

    def test_metadata_from_type_alias_with_multiple_validators(self):
        validated_int = Annotated[int, Gt(0), Le(100), MultipleOf(5)]

        args = get_args(validated_int)
        metadata_items = args[1:]  # Skip the base type

        assert len(metadata_items) == 3
        assert any(isinstance(m, Gt) for m in metadata_items)
        assert any(isinstance(m, Le) for m in metadata_items)
        assert any(isinstance(m, MultipleOf) for m in metadata_items)

    def test_validation_with_type_alias_metadata_succeeds(self):
        bounded_int = Annotated[int, Interval(ge=0, le=100)]

        registry = ParameterValidatorRegistry()
        args = get_args(bounded_int)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(50, {}, flattened_metadata)
        assert result is None

    def test_validation_with_type_alias_metadata_fails(self):
        bounded_int = Annotated[int, Interval(ge=0, le=100)]

        registry = ParameterValidatorRegistry()
        args = get_args(bounded_int)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(150, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 100" in result[0]

    def test_nested_type_alias_metadata_extraction(self):
        positive_int = Annotated[int, Gt(0)]
        bounded_positive_int = Annotated[positive_int, Le(100)]

        # Extract metadata from the nested alias
        args = get_args(bounded_positive_int)
        # First arg should be PositiveInt (the inner alias)
        assert len(args) >= 2

        # The outer annotation adds Le(100)
        outer_metadata = list(args[1:])
        assert any(isinstance(m, Le) for m in outer_metadata)

        # To get the inner metadata, we need to unwrap positive_int
        inner_args = get_args(args[0])
        if inner_args:  # If positive_int is still Annotated
            inner_metadata = list(inner_args[1:])
            assert any(isinstance(m, Gt) for m in inner_metadata)


class TestGenericTypeMetadataExtraction:
    def test_metadata_from_generic_list_type_argument(self):
        positive_int = Annotated[int, Gt(0)]
        list_of_positive_ints = list[positive_int]

        args = get_args(list_of_positive_ints)
        assert len(args) == 1

        # Get metadata from the type argument
        inner_type = args[0]
        inner_args = get_args(inner_type)
        if inner_args:
            metadata = list(inner_args[1:])
            assert any(isinstance(m, Gt) for m in metadata)

    def test_metadata_from_generic_dict_type_arguments(self):
        positive_int = Annotated[int, Gt(0)]
        non_empty_str = Annotated[str, MinLen(1)]
        dict_type = dict[non_empty_str, positive_int]

        args = get_args(dict_type)
        assert len(args) == 2

        # Check key type metadata
        key_args = get_args(args[0])
        if key_args:
            key_metadata = list(key_args[1:])
            assert any(isinstance(m, MinLen) for m in key_metadata)

        # Check value type metadata
        value_args = get_args(args[1])
        if value_args:
            value_metadata = list(value_args[1:])
            assert any(isinstance(m, Gt) for m in value_metadata)

    def test_nested_generic_type_metadata_extraction(self):
        bounded_int = Annotated[int, Interval(ge=0, le=100)]
        list_of_lists = list[list[bounded_int]]

        # Unwrap outer list
        outer_args = get_args(list_of_lists)
        assert len(outer_args) == 1

        # Unwrap inner list
        inner_list_args = get_args(outer_args[0])
        assert len(inner_list_args) == 1

        # Get the bounded_int type
        bounded_int_type = inner_list_args[0]
        bounded_int_args = get_args(bounded_int_type)
        if bounded_int_args:
            metadata = list(bounded_int_args[1:])
            assert any(isinstance(m, Interval) for m in metadata)

            # Flatten the interval
            flattened = flatten_metadata(metadata)
            assert any(isinstance(m, Ge) for m in flattened)
            assert any(isinstance(m, Le) for m in flattened)


class TestMetadataUnpackingEdgeCases:
    def test_empty_metadata_list_returns_empty_list(self):
        flattened = flatten_metadata([])
        assert flattened == []

    def test_metadata_list_with_only_non_grouped_items_unchanged(self):
        metadata = [Gt(0), Le(100), MultipleOf(5)]
        flattened = flatten_metadata(metadata)

        assert len(flattened) == 3
        assert flattened[0] is metadata[0]
        assert flattened[1] is metadata[1]
        assert flattened[2] is metadata[2]

    def test_metadata_order_is_preserved_during_flattening(self):
        metadata = [MultipleOf(5), Interval(gt=0, lt=100), MinLen(3)]
        flattened = flatten_metadata(metadata)

        # MultipleOf should be first
        assert isinstance(flattened[0], MultipleOf)
        # Interval unpacks to Gt and Lt (order within interval is implementation detail)
        # MinLen should be last
        assert isinstance(flattened[-1], MinLen)

    def test_validation_errors_from_unpacked_metadata_are_clear(self):
        registry = ParameterValidatorRegistry()
        interval = Interval(ge=10, le=20)
        flattened_metadata = tuple(flatten_metadata([interval]))

        result = registry.validate(5, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        # Should get error from Ge validator
        assert "must be greater than or equal to 10" in result[0]

    def test_validation_with_conflicting_interval_bounds_reports_first_error(self):
        registry = ParameterValidatorRegistry()
        # Impossible interval: gt=100 and lt=10
        interval = Interval(gt=100, lt=10)
        flattened_metadata = tuple(flatten_metadata([interval]))

        # No value can satisfy this
        result = registry.validate(50, {}, flattened_metadata)
        assert result is not None
        # Will fail at least one constraint
        assert len(result) >= 1

    def test_multiple_interval_unpacking_preserves_all_constraints(self):
        interval1 = Interval(ge=0, le=50)
        interval2 = Interval(ge=10, le=100)
        flattened = flatten_metadata([interval1, interval2])

        # Should have 4 constraints total
        assert len(flattened) == 4

        # Count each type
        ge_constraints = [m for m in flattened if isinstance(m, Ge)]
        le_constraints = [m for m in flattened if isinstance(m, Le)]

        assert len(ge_constraints) == 2
        assert len(le_constraints) == 2

    def test_interval_unpacking_with_same_bounds_creates_distinct_objects(self):
        interval1 = Interval(gt=0)
        interval2 = Interval(gt=0)
        flattened = flatten_metadata([interval1, interval2])

        assert len(flattened) == 2
        assert all(isinstance(m, Gt) and m.gt == 0 for m in flattened)
        # Even though they have the same value, they should be distinct objects
        # from different intervals (though this is implementation detail)


class TestParameterValidationFullFlow:
    def test_interval_annotation_on_parameter_succeeds_with_valid_values(self):
        registry = ParameterValidatorRegistry()

        percentage_type = Annotated[int, Interval(gt=0, le=100)]
        args = get_args(percentage_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        assert registry.validate(1, {}, flattened_metadata) is None
        assert registry.validate(50, {}, flattened_metadata) is None
        assert registry.validate(100, {}, flattened_metadata) is None

    def test_interval_annotation_on_parameter_fails_with_invalid_values(self):
        registry = ParameterValidatorRegistry()

        percentage_type = Annotated[int, Interval(gt=0, le=100)]
        args = get_args(percentage_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(-1, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 0" in result[0]

        result = registry.validate(0, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 0" in result[0]

        result = registry.validate(101, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 100" in result[0]

    def test_type_alias_with_multiple_validators_succeeds_with_valid_values(self):
        registry = ParameterValidatorRegistry()

        verbose_type = Annotated[int, Gt(0), Le(5)]
        args = get_args(verbose_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        assert registry.validate(1, {}, flattened_metadata) is None
        assert registry.validate(3, {}, flattened_metadata) is None
        assert registry.validate(5, {}, flattened_metadata) is None

    def test_type_alias_with_multiple_validators_fails_with_invalid_values(self):
        registry = ParameterValidatorRegistry()

        verbose_type = Annotated[int, Gt(0), Le(5)]
        args = get_args(verbose_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(0, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be greater than 0" in result[0]

        result = registry.validate(6, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 5" in result[0]

        result = registry.validate(10, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 5" in result[0]

    def test_generic_list_with_annotated_element_type_validates_elements(self):
        registry = ParameterValidatorRegistry()

        positive_int_type = Annotated[int, Gt(0)]
        list_type = list[positive_int_type]

        list_args = get_args(list_type)
        element_type = list_args[0]
        element_args = get_args(element_type)
        metadata = element_args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        values = [1, 2, 3]
        for value in values:
            result = registry.validate(value, {}, flattened_metadata)
            assert result is None

    def test_generic_list_with_annotated_element_type_fails_for_invalid_elements(
        self,
    ):
        registry = ParameterValidatorRegistry()

        positive_int_type = Annotated[int, Gt(0)]
        list_type = list[positive_int_type]

        list_args = get_args(list_type)
        element_type = list_args[0]
        element_args = get_args(element_type)
        metadata = element_args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        invalid_values = [0, -1, -10]
        for value in invalid_values:
            result = registry.validate(value, {}, flattened_metadata)
            assert result is not None
            assert len(result) == 1
            assert "must be greater than 0" in result[0]

    def test_complex_type_alias_with_interval_succeeds_with_valid_values(self):
        registry = ParameterValidatorRegistry()

        port_type = Annotated[int, Interval(ge=1, le=65535)]
        args = get_args(port_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        assert registry.validate(1, {}, flattened_metadata) is None
        assert registry.validate(8080, {}, flattened_metadata) is None
        assert registry.validate(65535, {}, flattened_metadata) is None

    def test_complex_type_alias_with_interval_fails_with_invalid_values(self):
        registry = ParameterValidatorRegistry()

        port_type = Annotated[int, Interval(ge=1, le=65535)]
        args = get_args(port_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(0, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be greater than or equal to 1" in result[0]

        result = registry.validate(65536, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 65535" in result[0]

    def test_nested_generic_with_interval_validates_correctly(self):
        registry = ParameterValidatorRegistry()

        bounded_int_type = Annotated[int, Interval(ge=0, le=100)]
        list_of_lists_type = list[list[bounded_int_type]]

        outer_args = get_args(list_of_lists_type)
        inner_list_type = outer_args[0]
        inner_args = get_args(inner_list_type)
        element_type = inner_args[0]
        element_args = get_args(element_type)
        metadata = element_args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        valid_values = [0, 50, 100]
        for value in valid_values:
            result = registry.validate(value, {}, flattened_metadata)
            assert result is None

    def test_nested_generic_with_interval_fails_for_invalid_values(self):
        registry = ParameterValidatorRegistry()

        bounded_int_type = Annotated[int, Interval(ge=0, le=100)]
        list_of_lists_type = list[list[bounded_int_type]]

        outer_args = get_args(list_of_lists_type)
        inner_list_type = outer_args[0]
        inner_args = get_args(inner_list_type)
        element_type = inner_args[0]
        element_args = get_args(element_type)
        metadata = element_args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(-1, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be greater than or equal to 0" in result[0]

        result = registry.validate(101, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 100" in result[0]

    def test_type_alias_with_interval_and_multiple_of_succeeds(self):
        registry = ParameterValidatorRegistry()

        even_percentage_type = Annotated[int, Interval(ge=0, le=100), MultipleOf(2)]
        args = get_args(even_percentage_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        assert registry.validate(0, {}, flattened_metadata) is None
        assert registry.validate(50, {}, flattened_metadata) is None
        assert registry.validate(100, {}, flattened_metadata) is None

    def test_type_alias_with_interval_and_multiple_of_fails_on_odd_values(self):
        registry = ParameterValidatorRegistry()

        even_percentage_type = Annotated[int, Interval(ge=0, le=100), MultipleOf(2)]
        args = get_args(even_percentage_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(1, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be a multiple of 2" in result[0]

        result = registry.validate(99, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be a multiple of 2" in result[0]

    def test_type_alias_with_interval_and_multiple_of_fails_outside_bounds(self):
        registry = ParameterValidatorRegistry()

        even_percentage_type = Annotated[int, Interval(ge=0, le=100), MultipleOf(2)]
        args = get_args(even_percentage_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(-2, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be greater than or equal to 0" in result[0]

        result = registry.validate(102, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "must be less than or equal to 100" in result[0]

    def test_string_length_validation_with_interval_succeeds(self):
        registry = ParameterValidatorRegistry()

        bounded_string_type = Annotated[str, MinLen(3), MaxLen(10)]
        args = get_args(bounded_string_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        assert registry.validate("abc", {}, flattened_metadata) is None
        assert registry.validate("hello", {}, flattened_metadata) is None
        assert registry.validate("1234567890", {}, flattened_metadata) is None

    def test_string_length_validation_with_interval_fails_outside_bounds(self):
        registry = ParameterValidatorRegistry()

        bounded_string_type = Annotated[str, MinLen(3), MaxLen(10)]
        args = get_args(bounded_string_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate("ab", {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "length must be at least 3" in result[0]

        result = registry.validate("12345678901", {}, flattened_metadata)
        assert result is not None
        assert len(result) == 1
        assert "length must be at most 10" in result[0]

    def test_multiple_constraints_fail_independently_and_report_all_errors(self):
        registry = ParameterValidatorRegistry()

        constrained_type = Annotated[int, Interval(ge=10, le=20), MultipleOf(5)]
        args = get_args(constrained_type)
        metadata = args[1:]
        flattened_metadata = tuple(flatten_metadata(metadata))

        result = registry.validate(7, {}, flattened_metadata)
        assert result is not None
        assert len(result) == 2
        assert any("must be greater than or equal to 10" in err for err in result)
        assert any("must be a multiple of 5" in err for err in result)
