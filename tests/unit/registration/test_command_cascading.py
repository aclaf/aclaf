# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false, reportUnusedFunction=false, reportUnusedParameter=false, reportUnusedCallResult=false, reportUninitializedInstanceVariable=false, reportUnannotatedClassAttribute=false
# ruff: noqa: ARG001

from typing import TYPE_CHECKING

import pytest
from annotated_types import BaseMetadata

from aclaf import EMPTY_COMMAND_FUNCTION, Command
from aclaf.logging import MockLogger

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aclaf.logging import Logger
    from aclaf.types import ParameterValueType


class CascadeInt:
    """Custom type for cascading tests."""

    def __init__(self, value: int) -> None:
        self.value = value


class CascadeStr:
    """Custom type for cascading tests."""

    def __init__(self, value: str) -> None:
        self.value = value


class CascadeFloat:
    """Custom type for cascading tests."""

    def __init__(self, value: float) -> None:
        self.value = value


class CascadeMetadata1(BaseMetadata):
    """Custom metadata for cascading tests."""

    value: int


class CascadeMetadata2(BaseMetadata):
    """Custom metadata for cascading tests."""

    min_value: int


class CascadeMetadata3(BaseMetadata):
    """Custom metadata for cascading tests."""

    max_value: int


class TestConverterCascading:
    def test_mount_cascades_converters_to_child(self) -> None:
        parent = Command(name="parent")

        @parent.converter(CascadeInt)
        def parse_cascade_int(value, metadata):
            return CascadeInt(int(value) * 2)

        child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
        parent.mount(child)

        assert child.converters is parent.converters
        assert child.converters.has_converter(CascadeInt)

    def test_mount_overwrites_child_converter_registry(self) -> None:
        parent = Command(name="parent")

        @parent.converter(CascadeInt)
        def parent_converter(value, metadata):
            return CascadeInt(int(value) * 2)

        child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)

        @child.converter(CascadeStr)
        def child_converter(value, metadata):
            return CascadeStr(str(value).upper())

        # Child has its own registry before mounting
        assert child.converters is not parent.converters
        assert child.converters.has_converter(CascadeStr)

        # Mount overwrites child's registry with parent's
        parent.mount(child)

        assert child.converters is parent.converters
        assert child.converters.has_converter(CascadeInt)
        # Child's original converter is lost (overwritten)
        assert not child.converters.has_converter(CascadeStr)

    def test_command_decorator_inherits_converters(self) -> None:
        parent = Command(name="parent")

        @parent.converter(CascadeFloat)
        def parse_cascade_float(value, metadata):
            return CascadeFloat(float(value) * 1.5)

        @parent.command()
        def child():
            pass

        child_cmd = parent.subcommands["child"]
        assert child_cmd.converters is parent.converters
        assert child_cmd.converters.has_converter(CascadeFloat)


class TestValidatorCascading:
    def test_mount_cascades_validators_to_child(self) -> None:
        parent = Command(name="parent")

        @parent.validator(CascadeMetadata1)
        def validate_cascade1(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
        parent.mount(child)

        assert child.validators is parent.validators
        assert child.validators.has_validator(CascadeMetadata1)

    def test_mount_overwrites_child_validator_registry(self) -> None:
        parent = Command(name="parent")

        @parent.validator(CascadeMetadata1)
        def parent_validator(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)

        @child.validator(CascadeMetadata2)
        def child_validator(
            value: "ParameterValueType | None",
            other_parameters: "Mapping[str, ParameterValueType | None]",
            metadata,
        ):
            return None

        # Child has its own registry before mounting
        assert child.validators is not parent.validators
        assert child.validators.has_validator(CascadeMetadata2)

        # Mount overwrites child's registry with parent's
        parent.mount(child)

        assert child.validators is parent.validators
        assert child.validators.has_validator(CascadeMetadata1)
        # Child's original validator is lost (overwritten)
        assert not child.validators.has_validator(CascadeMetadata2)

    def test_command_decorator_inherits_validators(self) -> None:
        parent = Command(name="parent")

        @parent.validator(CascadeMetadata3)
        def validate_cascade3(
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
        assert child_cmd.validators.has_validator(CascadeMetadata3)


class TestLoggerCascading:
    def test_mount_cascades_logger_to_child(self, logger: "Logger") -> None:
        parent = Command(name="parent", logger=logger)

        child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
        parent.mount(child)

        assert child.logger is logger

    def test_mount_overwrites_child_logger(self, logger: "Logger") -> None:
        parent = Command(name="parent", logger=logger)

        child_logger = MockLogger()
        child = Command(
            name="child", run_func=EMPTY_COMMAND_FUNCTION, logger=child_logger
        )

        # Child has its own logger before mounting
        assert child.logger is child_logger
        assert child.logger is not parent.logger

        # Mount overwrites child's logger with parent's
        parent.mount(child)

        assert child.logger is logger
        assert child.logger is parent.logger

    def test_command_decorator_inherits_logger(self, logger: "Logger") -> None:
        parent = Command(name="parent", logger=logger)

        @parent.command()
        def child():
            pass

        child_cmd = parent.subcommands["child"]
        assert child_cmd.logger is logger


class TestDeepHierarchyCascading:
    def test_four_level_hierarchy_cascading(self, logger: "Logger") -> None:
        root = Command(name="root", logger=logger)

        @root.converter(CascadeInt)
        def parse_cascade_int(value, metadata):
            return CascadeInt(int(value) * 10)

        @root.validator(CascadeMetadata1)
        def validate_cascade1(
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

        level1_cmd = root.subcommands["level1"]
        level2_cmd = level1_cmd.subcommands["level2"]
        level3_cmd = level2_cmd.subcommands["level3"]

        # All levels share the same registries and logger
        assert level1_cmd.converters is root.converters
        assert level2_cmd.converters is root.converters
        assert level3_cmd.converters is root.converters

        assert level1_cmd.validators is root.validators
        assert level2_cmd.validators is root.validators
        assert level3_cmd.validators is root.validators

        assert level1_cmd.logger is logger
        assert level2_cmd.logger is logger
        assert level3_cmd.logger is logger

    def test_mount_chain_cascading(self, logger: "Logger") -> None:
        root = Command(name="root", logger=logger)

        @root.converter(CascadeFloat)
        def parse_cascade_float(value, metadata):
            return CascadeFloat(float(value))

        level1 = Command(name="level1", run_func=EMPTY_COMMAND_FUNCTION)
        level2 = Command(name="level2", run_func=EMPTY_COMMAND_FUNCTION)
        level3 = Command(name="level3", run_func=EMPTY_COMMAND_FUNCTION)

        root.mount(level1)
        level1.mount(level2)
        level2.mount(level3)

        # Each mount operation cascades parent's registries
        assert level1.converters is root.converters
        assert level1.logger is logger

        assert level2.converters is level1.converters
        assert level2.logger is level1.logger

        assert level3.converters is level2.converters
        assert level3.logger is level2.logger

        # All share the root's registries
        assert level3.converters is root.converters
        assert level3.logger is logger

    def test_root_command_accessible_from_all_levels(self) -> None:
        root = Command(name="root")

        @root.command()
        def level1():
            pass

        @root.subcommands["level1"].command()
        def level2():
            pass

        @root.subcommands["level1"].subcommands["level2"].command()
        def level3():
            pass

        level3_cmd = (
            root.subcommands["level1"]
            .subcommands["level2"]
            .subcommands["level3"]
        )
        assert level3_cmd.root_command is root

    @pytest.mark.skip(
        reason="TODO: Recursive cascading to nested subcommands not implemented"
    )
    def test_mount_cascades_to_nested_subcommands(self, logger: "Logger") -> None:
        parent = Command(name="parent", logger=logger)

        @parent.converter(CascadeInt)
        def parse_cascade_int(value, metadata):
            return CascadeInt(int(value))

        # Create a command with its own subcommand
        child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
        grandchild = Command(name="grandchild", run_func=EMPTY_COMMAND_FUNCTION)
        child.subcommands["grandchild"] = grandchild

        # Mount child (which has grandchild)
        parent.mount(child)

        # Both child and grandchild should inherit parent's converters
        assert child.converters is parent.converters
        # TODO(tony): This fails - grandchild still has its own registry
        assert grandchild.converters is parent.converters
        assert grandchild.logger is logger
