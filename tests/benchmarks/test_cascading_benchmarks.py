# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownArgumentType=false

from dataclasses import dataclass

from annotated_types import BaseMetadata

from aclaf import EMPTY_COMMAND_FUNCTION, Command
from aclaf._conversion import ConverterRegistry
from aclaf.logging import MockLogger
from aclaf.validation import ValidatorRegistry


class TestCascadingPerformance:
    def test_mount_single_command_no_subcommands(self, benchmark):
        """Baseline: mounting a command with no subcommands."""

        def setup():
            parent = Command(name="parent", logger=MockLogger())
            child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
            return (parent, child), {}

        def mount_command(parent, child):
            parent.mount(child)

        benchmark.pedantic(mount_command, setup=setup, rounds=1000)

    def test_mount_command_with_one_subcommand(self, benchmark):
        """Mount a command with 1 level of subcommands."""

        def setup():
            parent = Command(name="parent", logger=MockLogger())
            child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
            grandchild = Command(name="grandchild", run_func=EMPTY_COMMAND_FUNCTION)
            child.subcommands["grandchild"] = grandchild
            return (parent, child), {}

        def mount_command(parent, child):
            parent.mount(child)

        benchmark.pedantic(mount_command, setup=setup, rounds=1000)

    def test_mount_command_with_5_level_hierarchy(self, benchmark):
        """Mount a command with 5 levels of subcommands."""

        def setup():
            parent = Command(name="parent", logger=MockLogger())
            level1 = Command(name="level1", run_func=EMPTY_COMMAND_FUNCTION)
            level2 = Command(name="level2", run_func=EMPTY_COMMAND_FUNCTION)
            level3 = Command(name="level3", run_func=EMPTY_COMMAND_FUNCTION)
            level4 = Command(name="level4", run_func=EMPTY_COMMAND_FUNCTION)
            level5 = Command(name="level5", run_func=EMPTY_COMMAND_FUNCTION)

            level1.subcommands["level2"] = level2
            level2.subcommands["level3"] = level3
            level3.subcommands["level4"] = level4
            level4.subcommands["level5"] = level5

            return (parent, level1), {}

        def mount_command(parent, level1):
            parent.mount(level1)

        benchmark.pedantic(mount_command, setup=setup, rounds=1000)

    def test_mount_command_with_10_level_hierarchy(self, benchmark):
        """Mount a command with 10 levels of subcommands."""

        def setup():
            parent = Command(name="parent", logger=MockLogger())
            commands = [
                Command(name=f"level{i}", run_func=EMPTY_COMMAND_FUNCTION)
                for i in range(1, 11)
            ]

            for i in range(len(commands) - 1):
                commands[i].subcommands[f"level{i+2}"] = commands[i + 1]

            return (parent, commands[0]), {}

        def mount_command(parent, level1):
            parent.mount(level1)

        benchmark.pedantic(mount_command, setup=setup, rounds=1000)

    def test_mount_command_with_wide_tree(self, benchmark):
        """Mount a command with 10 direct subcommands."""

        def setup():
            parent = Command(name="parent", logger=MockLogger())
            root_child = Command(name="root_child", run_func=EMPTY_COMMAND_FUNCTION)

            for i in range(10):
                child = Command(name=f"child{i}", run_func=EMPTY_COMMAND_FUNCTION)
                root_child.subcommands[f"child{i}"] = child

            return (parent, root_child), {}

        def mount_command(parent, root_child):
            parent.mount(root_child)

        benchmark.pedantic(mount_command, setup=setup, rounds=1000)

    def test_mount_command_with_balanced_tree(self, benchmark):
        """Mount a command with a balanced tree (3 levels, 3 children per level)."""

        def setup():
            parent = Command(name="parent", logger=MockLogger())
            root = Command(name="root", run_func=EMPTY_COMMAND_FUNCTION)

            # Level 1: 3 children
            for i in range(3):
                level1 = Command(name=f"l1_{i}", run_func=EMPTY_COMMAND_FUNCTION)
                root.subcommands[f"l1_{i}"] = level1

                # Level 2: 3 children each
                for j in range(3):
                    level2 = Command(
                        name=f"l2_{i}_{j}", run_func=EMPTY_COMMAND_FUNCTION
                    )
                    level1.subcommands[f"l2_{i}_{j}"] = level2

                    # Level 3: 3 children each
                    for k in range(3):
                        level3 = Command(
                            name=f"l3_{i}_{j}_{k}", run_func=EMPTY_COMMAND_FUNCTION
                        )
                        level2.subcommands[f"l3_{i}_{j}_{k}"] = level3

            return (parent, root), {}

        def mount_command(parent, root):
            parent.mount(root)

        benchmark.pedantic(mount_command, setup=setup, rounds=100)

    def test_mount_with_all_config_populated(self, benchmark):
        """Mount with all configuration options populated."""

        @dataclass(slots=True, frozen=True)
        class BenchMetadata(BaseMetadata):
            value: int = 0

        class BenchType:
            def __init__(self, value: int) -> None:
                self.value = value

        def setup():
            # Create fresh registries for each run to avoid conflicts
            converter_registry = ConverterRegistry()
            param_validator_registry = ValidatorRegistry()
            cmd_validator_registry = ValidatorRegistry()

            parent = Command(
                name="parent",
                logger=MockLogger(),
                converters=converter_registry,
                parameter_validators=param_validator_registry,
                command_validators=cmd_validator_registry,
            )

            @parent.converter(BenchType)
            def parse_bench_type(value, _metadata):
                return BenchType(int(value))

            @parent.parameter_validator(BenchMetadata)
            def validate_bench(value, metadata):
                return None

            @parent.command_validator(BenchMetadata)
            def validate_command(value, metadata):
                return None

            child = Command(name="child", run_func=EMPTY_COMMAND_FUNCTION)
            grandchild = Command(name="grandchild", run_func=EMPTY_COMMAND_FUNCTION)
            child.subcommands["grandchild"] = grandchild

            return (parent, child), {}

        def mount_command(parent, child):
            parent.mount(child)

        benchmark.pedantic(mount_command, setup=setup, rounds=1000)
