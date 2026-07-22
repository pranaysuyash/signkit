"""Tests for desktop_app/library/storage.py.

Focus: LibraryItem.tooltip_text must read cached dimensions from the JSON
metadata sidecar (written at save time) instead of re-opening every image
file with PIL on every library list refresh. Opening N files with PIL for
an N-item library was the largest measured UI-freeze contributor in the
2026-07-01 performance audit (see docs/research/performance_optimization.md).
"""

import os
import time

import pytest
from PIL import Image

from desktop_app.library import storage as lib


@pytest.fixture
def image_path(tmp_path):
    path = tmp_path / "sig.png"
    Image.new("RGBA", (321, 145), (0, 0, 0, 0)).save(str(path), format="PNG")
    return str(path)


def test_tooltip_uses_cached_metadata_without_opening_file(monkeypatch, image_path):
    """When metadata carries image_size, PIL.Image.open must not be called."""
    opened = []
    real_open = Image.open

    def spy_open(*args, **kwargs):
        opened.append(args)
        return real_open(*args, **kwargs)

    monkeypatch.setattr(Image, "open", spy_open)

    item = lib.LibraryItem(
        path=image_path,
        modified=time.time(),
        metadata={"image_size": {"width": 321, "height": 145}, "image_mode": "RGBA"},
    )
    text = item.tooltip_text

    assert "321 × 145" in text
    assert "RGBA" in text
    assert opened == []  # No PIL open triggered — dimensions came from metadata.


def test_tooltip_falls_back_to_pil_when_metadata_missing(image_path):
    """Legacy items saved without an image_size sidecar still show dimensions."""
    item = lib.LibraryItem(path=image_path, modified=time.time(), metadata=None)
    text = item.tooltip_text
    assert "321 × 145" in text


def test_tooltip_falls_back_when_metadata_present_but_no_image_size(image_path):
    item = lib.LibraryItem(
        path=image_path, modified=time.time(), metadata={"threshold": 128}
    )
    text = item.tooltip_text
    assert "321 × 145" in text
    assert "Threshold: 128" in text


def test_list_items_loads_cached_dimensions_end_to_end(tmp_path, monkeypatch):
    """save_image_to_library caches image_size; list_items + tooltip_text must
    round-trip that without any extra PIL open."""
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()
    monkeypatch.setattr(lib, "LIB_DIR", str(lib_dir))
    src = tmp_path / "source.png"
    Image.new("RGB", (64, 48), (255, 255, 255)).save(str(src), format="PNG")

    saved_path = lib.save_image_to_library(str(src))
    items = lib.list_items()
    assert len(items) == 1
    assert items[0].path == saved_path
    assert items[0].metadata["image_size"] == {"width": 64, "height": 48}

    opened = []
    real_open = Image.open

    def spy_open(*args, **kwargs):
        opened.append(args)
        return real_open(*args, **kwargs)

    monkeypatch.setattr(Image, "open", spy_open)
    assert "64 × 48" in items[0].tooltip_text
    assert opened == []


def test_list_items_only_parses_sidecars_for_returned_items(tmp_path, monkeypatch):
    """list_items(limit=N) must only JSON-parse the N sidecars it actually
    returns, not every sidecar in the directory. Previously it parsed every
    item's metadata before sorting and truncating — O(total files), not
    O(limit). Sorting must happen on cheap mtime stats first."""
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()
    monkeypatch.setattr(lib, "LIB_DIR", str(lib_dir))

    import time as time_module

    for i in range(20):
        path = lib_dir / f"sig_{i:02d}.png"
        Image.new("RGB", (10, 10)).save(str(path), format="PNG")
        (lib_dir / f"sig_{i:02d}.json").write_text(
            f'{{"image_size": {{"width": {i}, "height": {i}}}}}', encoding="utf-8"
        )
        # Force distinct, increasing mtimes so ordering is deterministic.
        stamp = time_module.time() + i
        os.utime(path, (stamp, stamp))

    opened_json = []
    real_open = open

    def counting_open(file, *args, **kwargs):
        if isinstance(file, str) and file.endswith(".json"):
            opened_json.append(file)
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr("builtins.open", counting_open)

    items = lib.list_items(limit=5)

    assert len(items) == 5
    assert len(opened_json) == 5, "expected exactly 5 sidecar reads for limit=5, not one per file in the directory"
    # Must be the 5 most recent (highest i, since mtime increased with i).
    assert {item.metadata["image_size"]["width"] for item in items} == {15, 16, 17, 18, 19}
