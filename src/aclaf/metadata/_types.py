from types import MappingProxyType
from typing import TypeAlias

from annotated_types import BaseMetadata

MetadataType: TypeAlias = BaseMetadata | str | int

MetadataByType: TypeAlias = MappingProxyType[type[BaseMetadata], BaseMetadata]
