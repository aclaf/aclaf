import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from aclaf.metadata import ParameterMetadata

if TYPE_CHECKING:
    from collections.abc import Iterable

    from aclaf.types import ParameterValueMappingType, ParameterValueType
    from aclaf.validation._registry import ValidatorMetadataType


@dataclass(slots=True, frozen=True)
class PathExists(ParameterMetadata):
    pass


def validate_path_exists(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, (str, Path)):
        return ("must be a string or Path object.",)

    path = Path(value) if isinstance(value, str) else value

    if not path.exists():
        return (f"path '{value}' does not exist.",)

    return None


@dataclass(slots=True, frozen=True)
class IsFile(ParameterMetadata):
    pass


def validate_is_file(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, (str, Path)):
        return ("must be a string or Path object.",)

    path = Path(value) if isinstance(value, str) else value

    if not path.exists():
        return (f"path '{value}' does not exist.",)

    if not path.is_file():
        return (f"path '{value}' is not a file.",)

    return None


@dataclass(slots=True, frozen=True)
class IsDirectory(ParameterMetadata):
    pass


def validate_is_directory(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, (str, Path)):
        return ("must be a string or Path object.",)

    path = Path(value) if isinstance(value, str) else value

    if not path.exists():
        return (f"path '{value}' does not exist.",)

    if not path.is_dir():
        return (f"path '{value}' is not a directory.",)

    return None


@dataclass(slots=True, frozen=True)
class IsReadable(ParameterMetadata):
    pass


def validate_is_readable(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, (str, Path)):
        return ("must be a string or Path object.",)

    path = Path(value) if isinstance(value, str) else value

    if not path.exists():
        return (f"path '{value}' does not exist.",)

    if not os.access(path, os.R_OK):
        return (f"path '{value}' is not readable.",)

    return None


@dataclass(slots=True, frozen=True)
class IsWritable(ParameterMetadata):
    pass


def validate_is_writable(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, (str, Path)):
        return ("must be a string or Path object.",)

    path = Path(value) if isinstance(value, str) else value

    if not path.exists():
        return (f"path '{value}' does not exist.",)

    if not os.access(path, os.W_OK):
        return (f"path '{value}' is not writable.",)

    return None


@dataclass(slots=True, frozen=True)
class IsExecutable(ParameterMetadata):
    pass


def validate_is_executable(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, (str, Path)):
        return ("must be a string or Path object.",)

    path = Path(value) if isinstance(value, str) else value

    if not path.exists():
        return (f"path '{value}' does not exist.",)

    if not os.access(path, os.X_OK):
        return (f"path '{value}' is not executable.",)

    return None


@dataclass(slots=True, frozen=True)
class HasExtensions(ParameterMetadata):
    extensions: "str | Iterable[str]"


def validate_has_extensions(
    value: "ParameterValueType | ParameterValueMappingType | None",
    metadata: "ValidatorMetadataType",
) -> tuple[str, ...] | None:
    if value is None:
        return None

    if not isinstance(value, (str, Path)):
        return ("must be a string or Path object.",)

    path = Path(value) if isinstance(value, str) else value
    ext_meta = cast("HasExtensions", metadata)

    # Normalize extensions to a set
    if isinstance(ext_meta.extensions, str):
        allowed_extensions = {ext_meta.extensions}
    else:
        allowed_extensions = set(ext_meta.extensions)

    # Ensure all extensions start with a dot
    allowed_extensions = {
        ext if ext.startswith(".") else f".{ext}" for ext in allowed_extensions
    }

    # Check if the path name ends with any of the allowed extensions
    # This handles both simple extensions (.txt) and compound extensions (.tar.gz)
    path_str = str(path)
    if not any(path_str.endswith(ext) for ext in allowed_extensions):
        extensions_str = ", ".join(sorted(allowed_extensions))
        return (f"path '{value}' must have one of these extensions: {extensions_str}.",)

    return None
