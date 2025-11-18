from dataclasses import dataclass
from typing import TYPE_CHECKING

from aclaf.metadata import ParameterMetadata

if TYPE_CHECKING:
    from ._types import ConverterFunctionType


@dataclass(slots=True, frozen=True)
class Convert(ParameterMetadata):
    func: "ConverterFunctionType"
