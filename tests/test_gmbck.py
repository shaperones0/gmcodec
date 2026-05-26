"""Tests for ``.gmbck`` loading and saving."""

from pathlib import Path

import pytest

from gmcodec.core import gmbck_build_payload, gmbck_extract_payload
from gmcodec.file import file_pack, file_unpack
from gmcodec.validate import gmbck_validate

DIR_DATA = Path(__file__).parent / 'data'
FILES_BG = list(DIR_DATA.glob('*.gmbck'))


@pytest.mark.parametrize('filepath', FILES_BG, ids=[f.name for f in FILES_BG])
def test_gmbck_roundtrip(filepath: Path) -> None:
    """Verify extraction and injection of a background symmetrical."""
    raw_file_bytes = filepath.read_bytes()
    original_payload = file_unpack(raw_file_bytes)
    meta, img = gmbck_extract_payload(original_payload)
    gmbck_validate(meta, img)
    reconstructed_payload = gmbck_build_payload(meta, img)
    assert original_payload == reconstructed_payload, (
        f'Struct mismatch for {filepath.name}'
    )


@pytest.mark.parametrize('filepath', FILES_BG, ids=[f.name for f in FILES_BG])
def test_gmbck_magic_header(filepath: Path) -> None:
    """Ensure the zlib wrapper functions correctly handle the header."""
    raw_file_bytes = filepath.read_bytes()

    original_payload = file_unpack(raw_file_bytes)
    repacked_file_bytes = file_pack(original_payload)
    second_payload = file_unpack(repacked_file_bytes)

    assert original_payload == second_payload, (
        f'Zlib compression wrapper failed for {filepath.name}'
    )
