"""Binary cursor for struct reading and writing."""

import struct


class BinaryReader:
    """Binary cursor for struct reading."""

    def __init__(self, data: bytes) -> None:
        """Binary cursor for struct reading and writing.

        :param data: Data to write.
        """
        self.data = data
        self.offset = 0

    def read_int(self) -> int:
        """Read signed i32.

        :return: Integer value read.
        """
        # signed i32 "<i"
        val = struct.unpack_from('<i', self.data, self.offset)[0]
        self.offset += 4
        return val

    def read_bytes(self, size: int) -> bytes:
        """Read next bytes.

        :param size: Number of bytes to read.
        :return: Bytes read.
        """
        val = self.data[self.offset : self.offset + size]
        self.offset += size
        return val


class BinaryWriter:
    """Binary cursor for struct writing."""

    def __init__(self) -> None:
        """Binary cursor for struct writing."""
        self.data = bytearray()

    def write_int(self, val: int) -> None:
        """Write signed i32.

        :param val: Value to write.
        """
        self.data.extend(struct.pack('<i', val))

    def write_bytes(self, val: bytes) -> None:
        """Write chunk of bytes.

        :param val: Bytes to write.
        """
        self.data.extend(val)
