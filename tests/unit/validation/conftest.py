import pytest

from aclaf._validation import ParameterValidatorRegistry


@pytest.fixture
def registry() -> ParameterValidatorRegistry:
    return ParameterValidatorRegistry()


@pytest.fixture
def empty_registry() -> ParameterValidatorRegistry:
    reg = ParameterValidatorRegistry()
    # Clear built-in validators for isolated testing
    reg._validators.clear()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
    return reg
