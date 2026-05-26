"""Struct parsing and building.

No validation is done on incoming parameters.
"""

import collections.abc as col

import gmcodec.model as my_model
import gmcodec.stream as my_stream

VER_SPRITE = 800
VER_BACKGROUND = 710


def gmspr_extract_payload(
    payload: bytes,
) -> tuple[my_model.GmsprMeta, list[bytes]]:
    """Extract metadata and subimages from an uncompressed sprite payload.

    :param payload: Sprite payload.
    :return: (Metadata, subimages).
    """
    reader = my_stream.BinaryReader(payload)
    version = reader.read_int()

    origin_x = reader.read_int()
    origin_y = reader.read_int()
    subimage_count = reader.read_int()

    frames: list[bytes] = []
    master_w, master_h = 0, 0

    for i in range(subimage_count):
        _v = reader.read_int()
        w = reader.read_int()
        h = reader.read_int()
        size = reader.read_int()
        if i == 0:
            master_w, master_h = w, h
        frames.append(reader.read_bytes(size))

    meta = my_model.GmsprMeta(
        version=version,
        width=master_w,
        height=master_h,
        subimage_count=subimage_count,
        origin_x=origin_x,
        origin_y=origin_y,
        mask_kind=reader.read_int(),
        mask_tolerance=reader.read_int(),
        separate_masks=reader.read_int(),
        bbox_kind=reader.read_int(),
        bbox_left=reader.read_int(),
        bbox_right=reader.read_int(),
        bbox_bottom=reader.read_int(),
        bbox_top=reader.read_int(),
    )
    return meta, frames


def gmspr_build_payload(
    meta: my_model.GmsprMeta, frames: col.Iterable[bytes]
) -> bytes:
    """Construct an uncompressed sprite payload out of metadata and subimages.

    :param meta: Metadata.
    :param frames: Subimages (raw BGRA bytes).
    :return: Constructed payload.
    """
    writer = my_stream.BinaryWriter()
    writer.write_int(meta.version)
    writer.write_int(meta.origin_x)
    writer.write_int(meta.origin_y)
    writer.write_int(meta.subimage_count)

    for frame in frames:
        writer.write_int(VER_SPRITE)
        writer.write_int(meta.width)
        writer.write_int(meta.height)
        writer.write_int(len(frame))
        writer.write_bytes(frame)

    writer.write_int(meta.mask_kind)
    writer.write_int(meta.mask_tolerance)
    writer.write_int(meta.separate_masks)
    writer.write_int(meta.bbox_kind)
    writer.write_int(meta.bbox_left)
    writer.write_int(meta.bbox_right)
    writer.write_int(meta.bbox_bottom)
    writer.write_int(meta.bbox_top)

    return bytes(writer.data)


def gmbck_extract_payload(payload: bytes) -> tuple[my_model.GmbckMeta, bytes]:
    """Extract metadata and image from an uncompressed background payload.

    :param payload: Background payload.
    :return: (Metadata, image bytes).
    """
    reader = my_stream.BinaryReader(payload)
    bg_version = reader.read_int()

    use_as_tile = reader.read_int()
    tile_width = reader.read_int()
    tile_height = reader.read_int()
    h_offset = reader.read_int()
    v_offset = reader.read_int()
    h_sep = reader.read_int()
    v_sep = reader.read_int()

    image_version = reader.read_int()
    width = reader.read_int()
    height = reader.read_int()
    size = reader.read_int()

    pixels = reader.read_bytes(size)

    meta = my_model.GmbckMeta(
        version=bg_version,
        use_as_tile=use_as_tile,
        tile_width=tile_width,
        tile_height=tile_height,
        tile_h_offset=h_offset,
        tile_v_offset=v_offset,
        tile_h_sep=h_sep,
        tile_v_sep=v_sep,
        image_version=image_version,
        width=width,
        height=height,
    )
    return meta, pixels


def gmbck_build_payload(meta: my_model.GmbckMeta, pixels: bytes) -> bytes:
    """Construct an uncompressed background payload out of metadata and image.

    :param meta: Metadata.
    :param pixels: Image (raw BGRA bytes).
    :return: Constructed payload.
    """
    writer = my_stream.BinaryWriter()

    # Tile Metadata
    writer.write_int(meta.version)
    writer.write_int(meta.use_as_tile)
    writer.write_int(meta.tile_width)
    writer.write_int(meta.tile_height)
    writer.write_int(meta.tile_h_offset)
    writer.write_int(meta.tile_v_offset)
    writer.write_int(meta.tile_h_sep)
    writer.write_int(meta.tile_v_sep)

    # Image Struct
    writer.write_int(meta.image_version)
    writer.write_int(meta.width)
    writer.write_int(meta.height)
    writer.write_int(len(pixels))
    writer.write_bytes(pixels)

    return bytes(writer.data)
