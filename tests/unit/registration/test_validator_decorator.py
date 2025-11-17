# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportUnusedFunction=false, reportUnusedParameter=false, reportUnusedCallResult=false, reportUninitializedInstanceVariable=false
# ruff: noqa: ARG001

from typing import TYPE_CHECKING

from annotated_types import BaseMetadata

from aclaf import EMPTY_COMMAND_FUNCTION, Command

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aclaf.logging import Logger
    from aclaf.types import ParameterValueType


class CustomMetadata1(BaseMetadata):
    """Custom metadata for testing validators."""

    value: int


class CustomMetadata2(BaseMetadata):
    """Custom metadata for testing validators."""

    min_value: int


class CustomMetadata3(BaseMetadata):
    """Custom metadata for testing validators."""

    max_value: int


class TestValidatorRegistration:
    def test_validator_decorator_registers_validator(self) -> None:
        cmd = Command(name="test")

        @cmd.validator(CustomMetadata1)
        def validate_custom1(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        assert cmd.validators.has_validator(CustomMetadata1)
        assert cmd.validators.get_validator(CustomMetadata1) is validate_custom1

    def test_validator_decorator_returns_original_function(self) -> None:
        cmd = Command(name="test")

        def validate_custom1(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        result = cmd.validator(CustomMetadata1)(validate_custom1)

        assert result is validate_custom1

    def test_multiple_validators_for_different_metadata(self) -> None:
        cmd = Command(name="test")

        @cmd.validator(CustomMetadata1)
        def validate_custom1(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        @cmd.validator(CustomMetadata2)
        def validate_custom2(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        assert cmd.validators.has_validator(CustomMetadata1)
        assert cmd.validators.has_validator(CustomMetadata2)
        assert cmd.validators.get_validator(CustomMetadata1) is validate_custom1
        assert cmd.validators.get_validator(CustomMetadata2) is validate_custom2

    def test_validator_preserved_in_runtime_command(self) -> None:
        cmd = Command(name="test", run_func=EMPTY_COMMAND_FUNCTION)

        @cmd.validator(CustomMetadata3)
        def validate_custom3(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        runtime = cmd.to_runtime_command()

        assert runtime.validators is cmd.validators
        assert runtime.validators.has_validator(CustomMetadata3)


class TestValidatorInheritance:
    def test_command_decorator_inherits_parent_validators(self) -> None:
        parent = Command(name="parent")

        @parent.validator(CustomMetadata1)
        def validate_custom1(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        @parent.command()
        def child():
            pass

        child_cmd = parent.subcommands["child"]
        assert child_cmd.validators is parent.validators
        assert child_cmd.validators.has_validator(CustomMetadata1)
        assert child_cmd.validators.get_validator(CustomMetadata1) is validate_custom1

    def test_mount_inherits_parent_validators(self) -> None:
        parent = Command(name="parent")

        @parent.validator(CustomMetadata1)
        def validate_custom1(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
        parent.mount(child)

        assert child.validators is parent.validators
        assert child.validators.has_validator(CustomMetadata1)

    def test_validator_inheritance_transitive(self) -> None:
        root = Command(name="root")

        @root.validator(CustomMetadata2)
        def validate_custom2(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        @root.command()
        def mid():
            pass

        @root.subcommands["mid"].command()
        def leaf():
            pass

        leaf_cmd = root.subcommands["mid"].subcommands["leaf"]
        assert leaf_cmd.validators is root.validators
        assert leaf_cmd.validators.has_validator(CustomMetadata2)


class TestValidatorOverride:
    def test_child_cannot_override_parent_validator_via_decorator(self) -> None:
        parent = Command(name="parent")

        @parent.validator(CustomMetadata1)
        def parent_validator(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        @parent.command()
        def child():
            pass

        # Child inherits parent's validators registry (same object)
        # Therefore child cannot register a different validator for same key
        child_cmd = parent.subcommands["child"]
        assert child_cmd.validators is parent.validators


class TestValidatorCascading:
    def test_validator_cascades_through_mount(self, logger: "Logger") -> None:
        parent = Command(name="parent", logger=logger)

        @parent.validator(CustomMetadata3)
        def validate_custom3(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return ("Too long",)

        child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
        parent.mount(child)

        assert child.validators is parent.validators
        assert child.validators.get_validator(CustomMetadata3) is validate_custom3

    def test_validator_registry_shared_across_hierarchy(self) -> None:
        root = Command(name="root")

        @root.validator(CustomMetadata1)
        def validate_custom1(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        @root.command()
        def level1():
            pass

        @root.subcommands["level1"].command()
        def level2():
            pass

        @root.subcommands["level1"].subcommands["level2"].command()
        def level3():
            pass

        # All levels share the same registry
        level1_cmd = root.subcommands["level1"]
        level2_cmd = level1_cmd.subcommands["level2"]
        level3_cmd = level2_cmd.subcommands["level3"]

        assert level1_cmd.validators is root.validators
        assert level2_cmd.validators is root.validators
        assert level3_cmd.validators is root.validators
