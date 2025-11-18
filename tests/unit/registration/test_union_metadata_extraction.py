from typing import Annotated

from annotated_types import Gt

from aclaf.registration._parameters import (
    _extract_union_metadata,  # pyright: ignore[reportPrivateUsage]
)


class TestUnionMetadataExtraction:
    def test_pipe_union_with_single_annotated_member(self):
        # Use eval to construct X | Y syntax at runtime
        annotation = eval(  # noqa: S307  # pyright: ignore[reportAny]
            "Annotated[int, Gt(0)] | None",
            {"Annotated": Annotated, "Gt": Gt, "int": int, "None": None},
        )
        metadata = _extract_union_metadata(annotation)

        assert len(metadata) == 1
        assert isinstance(metadata[0], Gt)
        assert metadata[0].gt == 0

    def test_pipe_union_with_multiple_annotated_members(self):
        # Use eval to construct X | Y syntax at runtime
        annotation = eval(  # noqa: S307  # pyright: ignore[reportAny]
            'Annotated[int, Gt(0)] | Annotated[str, "some_metadata"]',
            {"Annotated": Annotated, "Gt": Gt, "int": int, "str": str},
        )
        metadata = _extract_union_metadata(annotation)

        assert len(metadata) == 2
        assert isinstance(metadata[0], Gt)
        assert metadata[1] == "some_metadata"

    def test_pipe_union_with_three_annotated_members(self):
        # Use eval to construct X | Y syntax at runtime
        annotation = eval(  # noqa: S307  # pyright: ignore[reportAny]
            'Annotated[int, Gt(0)] | Annotated[str, "metadata"] | None',
            {
                "Annotated": Annotated,
                "Gt": Gt,
                "int": int,
                "str": str,
                "None": None,
            },
        )
        metadata = _extract_union_metadata(annotation)

        assert len(metadata) == 2
        assert isinstance(metadata[0], Gt)
        assert metadata[1] == "metadata"

    def test_non_union_returns_empty(self):
        annotation = Annotated[int, Gt(0)]
        metadata = _extract_union_metadata(annotation)

        assert metadata == []

    def test_union_without_annotated_returns_empty(self):
        annotation = int | str | None
        metadata = _extract_union_metadata(annotation)

        assert metadata == []
