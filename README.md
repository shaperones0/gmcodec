# gmcodec

Encoding, modifying and decoding GameMaker 8 external resource files:
- `.gmbck` done
- `.gmspr` done
- `.gmres` TODO

This readme also outlines **format specs** and library docs, examples, etc.

## TOC
- [Format](#format)
  - [GM Header](#gm-header)
  - [Frame](#frame)
  - [Sprite (`.gmspr`)](#sprite-gmspr)
  - [Background (`.gmbck`)](#background-gmbck)
- [Usage](#usage)
- [Reference](#reference)
  - [`gmcodec.file`](#gmcodecfile)
  - [`gmcodec.core`](#gmcodeccore)
  - [`gmcodec.model`](#gmcodecmodel)
  - [`gmcodec.stream`](#gmcodecstream)
  
## Format

General rules:
- Little-endian
- All integers are signed 32-bit
- In fact, every value (even bool) is a signed 32-bit, unless specified otherwise
- Pixels: Raw uncompressed BGRA bytes

### GM Header
All asset types have a common header:
- file signature (always `1234321`) (and yes, it's signed 32-bit)
- total byte size of the upcoming zlib stream

This is followed by Zlib compressed payload (Standard `78 9C` stream).

_Everything below refers to decompressed payload._

### Frame
Frames are used as subimages in sprites or the actual images in backgrounds.
- `i32` frame version (`800`)
- `i32` frame width
- `i32` frame height 
- `i32` frame pixel array size in bytes (`width * height * 4`)
- `bytes` raw BGRA pixel data


### Sprite (`.gmspr`)
- `i32` format version (`800`)
- `i32` origin x
- `i32` origin y
- `i32` subimage count (N)
  - N subimages, each is a `Frame` (dimensions must match across all frames)
- `i32` mask kind (0: precise, 1: rectangular, 2: disk, 3: diamond)
- `i32` mask tolerance (0 - 255)
- `i32` separate masks per frame (0: false, 1: true)
- `i32` bbox kind (0: automatic, 1: full image, 2: manual)
- `i32` bbox left 
- `i32` bbox right
- `i32` bbox bottom
- `i32` bbox top 

### Background (`.gmbck`)
- `i32` format version (should be `710`)
- `i32` use as tile set (0: false, 1: true)
- `i32` tile width
- `i32` tile height
- `i32` tile horizontal offset
- `i32` tile vertical offset
- `i32` tile horizontal separation
- `i32` tile vertical separation
- the rest is `Frame`

## Usage

I won't be posting this on PyPI. [Nooo](https://docs.astral.sh/uv/concepts/projects/dependencies/#git)

Otherwise, it's as weasy as that:

```python
from pathlib import Path
from gmcodec import file, core, stream, model
from PIL import Image, ImageEnhance

# read sprite
raw_bytes = Path("input/player.gmspr").read_bytes()
payload = file.file_unpack(raw_bytes)
meta, frames_bytes = core.gmspr_extract_payload(payload)

# modify metadata
meta.origin_x += 4
meta.origin_y -= 4

# motion trail effect :D
processed_frames = []
prev_frame: Image.Image | None = None

for i, bgra_bytes in enumerate(frames_bytes):
    # convert from BGRA to RGBA
    img = Image.frombytes("RGBA", (meta.width, meta.height), bgra_bytes, "raw", "BGRA")
    
    if prev_frame is not None:
        # ghost the previous frame and composite it beneath the current frame
        ghost = prev_frame.copy()
        ghost.putalpha(ImageEnhance.Brightness(ghost.split()[3]).enhance(0.4))
        img = Image.alpha_composite(ghost, img)
    
    prev_frame = img.copy()
    # don't forget to swap back to BGRA
    processed_frames.append(img.tobytes("raw", "BGRA"))

# save back to disk
new_payload = core.gmspr_build_payload(meta, processed_frames)
Path("output/sprPlayerGhost.gmspr").write_bytes(file.file_pack(new_payload))
```

## Reference
### `gmcodec.file`
Handles GM's file wrapping (`1234321` magic and zlib compression).
- `file_unpack(raw_bytes: bytes) -> bytes`: strip the header and decompress the payload; usually takes raw file bytes.
- `file_pack(payload_bytes: bytes, compression_level: int = 9) -> bytes`: compress the payload and wrap it into GM's header; outputs ready-to-be-written file bytes.

### `gmcodec.core`
Struct parsers. No validation is done on incoming parameters.
- `gmspr_extract_payload(payload: bytes) -> tuple[GmsprMeta, list[bytes]]`: parse uncompressed sprite payload into metadata and BGRA frame array.
- `gmspr_build_payload(meta: GmsprMeta, frames: Iterable[bytes]) -> bytes`: reconstruct an uncompressed sprite payload.
- `gmbck_extract_payload(payload: bytes) -> tuple[GmbckMeta, bytes]`: parse uncompressed background payload into metadata and BGRA frame.
- `gmbck_build_payload(meta: GmbckMeta, pixels: bytes) -> bytes`: reconstruct an uncompressed background payload.

### `gmcodec.model`
Metadata models; loosely follows internal format: [Format](#format).
- `GmsprMeta`
- `GmbckMeta`

Both provide `.default()` constructor with values for "empty" assets.

### `gmcodec.stream`
Encoded struct cursors `BinaryReader` and `BinaryWriter`. 
