"""GmCodec models."""

from dataclasses import dataclass
from typing import Self


# shoutouts to yal
@dataclass
class GmbckMeta:
    """Background metadata."""

    version: int
    use_as_tile: int
    tile_width: int
    tile_height: int
    tile_h_offset: int
    tile_v_offset: int
    tile_h_sep: int
    tile_v_sep: int
    image_version: int
    width: int
    height: int

    @classmethod
    def default(cls) -> Self:
        """Construct default ``GmbckMeta``.

        :return: ``GmbckMeta`` with default values for empty background.
        """
        return cls(
            version=710,
            use_as_tile=0,
            tile_width=16,
            tile_height=16,
            tile_h_offset=0,
            tile_v_offset=0,
            tile_h_sep=0,
            tile_v_sep=0,
            image_version=800,
            width=0,
            height=0,
        )


@dataclass
class GmsprMeta:
    """Sprite metadata."""

    version: int
    width: int
    height: int
    subimage_count: int
    origin_x: int
    origin_y: int

    # trailing data
    mask_kind: int  # 0: precise, 1: rect, 2: disk, 3: diamond
    mask_tolerance: int  # 0 to 255
    separate_masks: int  # boolean (but stored as 32-bit int)
    bbox_kind: int  # 0: automatic, 1: full, 2: manual
    bbox_left: int
    bbox_right: int
    bbox_bottom: int
    bbox_top: int

    @classmethod
    def default(cls) -> Self:
        """Construct default ``GmsprMeta``.

        :return: ``GmsprMeta`` with default values for empty sprite.
        """
        return cls(
            version=800,
            width=0,
            height=0,
            subimage_count=0,
            origin_x=0,
            origin_y=0,
            mask_kind=0,
            mask_tolerance=0,
            separate_masks=0,
            bbox_kind=0,
            bbox_left=0,
            bbox_right=0,
            bbox_bottom=0,
            bbox_top=0,
        )
