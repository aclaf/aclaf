import pytest

from aclaf._conversion import ConverterRegistry


@pytest.fixture
def registry() -> ConverterRegistry:
    return ConverterRegistry()


@pytest.fixture
def empty_registry() -> ConverterRegistry:
    reg = ConverterRegistry()
    # Clear builtin converters for isolated testing
    reg._converters.clear()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
    return reg
