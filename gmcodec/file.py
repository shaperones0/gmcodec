"""Handle GM's file wrapping."""

import zlib

import gmcodec.stream as my_stream

MAGIC = 1234321


def file_unpack(raw_bytes: bytes) -> bytes:
    """Strips the GameMaker magic header and decompresses the payload.

    :param raw_bytes: Raw bytes of ``.gmspr`` or ``.gmbck`` file.
    :return: Uncompressed payload.
    """
    reader = my_stream.BinaryReader(raw_bytes)
    magic = reader.read_int()

    if magic != MAGIC:
        # fallback in case magic number not found - find by zlib header
        zlib_start = raw_bytes.find(b'\x78\x9c')
        if zlib_start == -1:
            zlib_start = raw_bytes.find(b'\x78\xda')

        if zlib_start != -1:
            return zlib.decompress(raw_bytes[zlib_start:])

        raise ValueError(
            f'Invalid GameMaker external file. Magic number: {magic}'
        )

    zlib_size = reader.read_int()
    compressed = reader.read_bytes(zlib_size)

    return zlib.decompress(compressed)


def file_pack(payload_bytes: bytes, compression_level: int = 9) -> bytes:
    """Compresses a payload and wraps it in the GameMaker magic header.

    :param payload_bytes: The uncompressed struct payload (from ``core.py``).
    :param compression_level: Zlib compression level (0-9); GM usually uses 9.
    :return: Bytes ready to be written to disk.
    """
    compressed = zlib.compress(payload_bytes, level=compression_level)

    writer = my_stream.BinaryWriter()
    writer.write_int(MAGIC)
    writer.write_int(len(compressed))
    writer.write_bytes(compressed)

    return bytes(writer.data)
