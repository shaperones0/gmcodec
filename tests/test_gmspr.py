"""Tests for ``.gmspr`` loading and saving."""

from pathlib import Path

import pytest

from gmcodec.core import gmspr_build_payload, gmspr_extract_payload
from gmcodec.file import file_pack, file_unpack
from gmcodec.validate import gmspr_validate

DIR_DATA = Path(__file__).parent / 'data'
FILES_SPRITE = list(DIR_DATA.glob('*.gmspr'))


@pytest.mark.parametrize(
    'filepath', FILES_SPRITE, ids=[f.name for f in FILES_SPRITE]
)
def test_gmspr_roundtrip(filepath: Path) -> None:
    """Verify extraction and injection of a sprite are symmetrical."""
    raw_file_bytes = filepath.read_bytes()
    original_payload = file_unpack(raw_file_bytes)
    meta, frames = gmspr_extract_payload(original_payload)
    gmspr_validate(meta, frames)
    reconstructed_payload = gmspr_build_payload(meta, frames)
    assert original_payload == reconstructed_payload, (
        f'Struct mismatch for {filepath.name}'
    )


@pytest.mark.parametrize(
    'filepath', FILES_SPRITE, ids=[f.name for f in FILES_SPRITE]
)
def test_gmspr_magic_header(filepath: Path) -> None:
    """Ensure the zlib wrapper functions correctly handle the header."""
    raw_file_bytes = filepath.read_bytes()

    original_payload = file_unpack(raw_file_bytes)
    repacked_file_bytes = file_pack(original_payload)
    second_payload = file_unpack(repacked_file_bytes)

    assert original_payload == second_payload, (
        f'Zlib compression wrapper failed for {filepath.name}'
    )
