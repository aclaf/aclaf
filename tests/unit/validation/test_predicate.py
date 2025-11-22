"""Unit tests for predicate validator."""

from annotated_types import Predicate

from aclaf.validation._shared import validate_predicate


class TestValidatePredicate:
    def test_validates_passing_predicate(self):
        metadata = Predicate(lambda x: x > 0)
        value = 5

        result = validate_predicate(value, metadata)

        assert result is None

    def test_rejects_failing_predicate(self):
        metadata = Predicate(lambda x: x > 0)
        value = -5

        result = validate_predicate(value, metadata)

        assert result is not None
        assert len(result) == 1
        assert "does not satisfy the required predicate condition" in result[0]

    def test_validates_string_predicate(self):
        metadata = Predicate(lambda s: len(s) >= 3)
        value = "hello"

        result = validate_predicate(value, metadata)

        assert result is None

    def test_rejects_string_failing_predicate(self):
        metadata = Predicate(lambda s: len(s) >= 3)
        value = "hi"

        result = validate_predicate(value, metadata)

        assert result is not None
        assert "does not satisfy the required predicate condition" in result[0]

    def test_validates_complex_predicate(self):
        def is_even_and_positive(x: int) -> bool:
            return x > 0 and x % 2 == 0

        metadata = Predicate(is_even_and_positive)
        value = 4

        result = validate_predicate(value, metadata)

        assert result is None

    def test_rejects_complex_predicate_failure(self):
        def is_even_and_positive(x: int) -> bool:
            return x > 0 and x % 2 == 0

        metadata = Predicate(is_even_and_positive)
        value = 3

        result = validate_predicate(value, metadata)

        assert result is not None

    def test_validates_none_value(self):
        metadata = Predicate(lambda x: x > 0)
        value = None

        result = validate_predicate(value, metadata)

        assert result is None

    def test_handles_predicate_exception(self):
        def raises_error(x: int) -> bool:
            msg = "Something went wrong"
            raise ValueError(msg)

        metadata = Predicate(raises_error)
        value = 42

        result = validate_predicate(value, metadata)

        assert result is not None
        assert len(result) == 1
        assert "predicate validation failed" in result[0]
        assert "Something went wrong" in result[0]

    def test_validates_list_predicate(self):
        metadata = Predicate(lambda lst: len(lst) > 0 and all(x > 0 for x in lst))
        value: list[int] = [1, 2, 3]

        result = validate_predicate(value, metadata)

        assert result is None

    def test_rejects_empty_list_predicate(self):
        metadata = Predicate(lambda lst: len(lst) > 0)
        value: list[int] = []

        result = validate_predicate(value, metadata)

        assert result is not None

    def test_validates_dict_predicate(self):
        metadata = Predicate(lambda d: "required_key" in d)
        value = {"required_key": "value", "other": 123}

        result = validate_predicate(value, metadata)

        assert result is None

    def test_rejects_dict_missing_key(self):
        metadata = Predicate(lambda d: "required_key" in d)
        value = {"other": 123}

        result = validate_predicate(value, metadata)

        assert result is not None

    def test_validates_boolean_true_result(self):
        metadata = Predicate(lambda _: True)
        value = "anything"

        result = validate_predicate(value, metadata)

        assert result is None

    def test_rejects_boolean_false_result(self):
        metadata = Predicate(lambda _: False)
        value = "anything"

        result = validate_predicate(value, metadata)

        assert result is not None

    def test_validates_type_check_predicate(self):
        metadata = Predicate(lambda x: isinstance(x, int) and x > 0)
        value = 42

        result = validate_predicate(value, metadata)

        assert result is None

    def test_rejects_wrong_type_predicate(self):
        metadata = Predicate(lambda x: isinstance(x, int))
        value = "not an int"

        result = validate_predicate(value, metadata)

        assert result is not None

    def test_handles_attribute_error_in_predicate(self):
        metadata = Predicate(lambda x: x.nonexistent_attribute > 0)
        value = 42

        result = validate_predicate(value, metadata)

        assert result is not None
        assert "predicate validation failed" in result[0]
        assert "AttributeError" in result[0] or "attribute" in result[0].lower()

    def test_validates_range_check_predicate(self):
        metadata = Predicate(lambda x: 0 <= x <= 100)
        value = 50

        result = validate_predicate(value, metadata)

        assert result is None

    def test_rejects_out_of_range_predicate(self):
        metadata = Predicate(lambda x: 0 <= x <= 100)
        value = 150

        result = validate_predicate(value, metadata)

        assert result is not None
