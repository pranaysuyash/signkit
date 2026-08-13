from PIL import Image, ImageDraw
import os
import shutil
import sys
import tempfile
from pathlib import Path


SAMPLE_SIGNATURE_NAME = "signature_template_synthetic_512.jpg"


def _canonical_sample_path() -> Path | None:
    """Locate the checked-in sample in source and packaged app layouts."""

    source_root = Path(__file__).resolve().parents[2]
    candidates = [
        Path(__file__).resolve().with_name(SAMPLE_SIGNATURE_NAME),
        source_root / "desktop_app" / "resources" / SAMPLE_SIGNATURE_NAME,
    ]
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        bundle = Path(bundle_root)
        candidates.extend(
            [
                bundle / "desktop_app" / "resources" / SAMPLE_SIGNATURE_NAME,
            ]
        )

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def generate_sample_signature() -> str:
    """Return a temporary copy of the canonical real signature sample.

    The synthetic drawing remains as a source-tree fallback for development
    layouts that do not include the checked-in asset yet.
    """

    canonical_path = _canonical_sample_path()
    if canonical_path is not None:
        fd, path = tempfile.mkstemp(suffix=canonical_path.suffix)
        os.close(fd)
        shutil.copy2(canonical_path, path)
        return path

    img = Image.new("RGB", (800, 400), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    ink = "#1a1a2e"

    # J
    j_points = [
        (120, 80), (120, 100), (120, 130), (120, 160), (120, 190),
        (118, 215), (112, 235), (100, 250), (85, 255), (72, 248),
        (65, 235), (68, 220), (80, 215)
    ]
    draw.line(j_points, fill=ink, width=3)

    # o
    o_start_x = 130
    o_start_y = 175
    o_top = [
        (o_start_x, o_start_y), (138, 158), (152, 148), (170, 148),
        (185, 155), (192, 168), (190, 182), (182, 195), (168, 202),
        (152, 202), (140, 195), (133, 182), (o_start_x, o_start_y)
    ]
    draw.line(o_top, fill=ink, width=2)

    # h
    h_points = [
        (195, 120), (195, 155), (195, 185), (195, 200),
        (198, 215), (210, 225), (225, 225), (238, 215),
        (242, 200), (240, 185), (235, 175), (232, 180),
        (240, 185), (248, 195), (252, 210), (250, 225),
        (245, 240), (238, 248)
    ]
    draw.line(h_points, fill=ink, width=2)

    # n
    n_points = [
        (260, 180), (262, 195), (268, 210), (280, 220),
        (295, 220), (308, 210), (312, 195), (310, 182),
        (305, 178), (300, 185), (305, 195), (312, 208),
        (322, 218), (332, 218), (338, 210), (340, 198),
        (338, 185)
    ]
    draw.line(n_points, fill=ink, width=2)

    # D
    d_points = [
        (390, 130), (390, 155), (390, 180), (390, 205),
        (390, 230), (392, 245),
        (405, 252), (425, 255), (450, 248), (470, 232),
        (480, 210), (482, 185), (480, 162), (470, 145),
        (452, 135), (430, 132), (410, 132), (398, 135)
    ]
    draw.line(d_points, fill=ink, width=3)

    # o (in Doe)
    do_start_x = 495
    do_start_y = 180
    do_points = [
        (do_start_x, do_start_y), (502, 162), (518, 152), (536, 152),
        (552, 160), (558, 175), (555, 190), (545, 202),
        (530, 208), (512, 208), (500, 200), (494, 188),
        (do_start_x, do_start_y)
    ]
    draw.line(do_points, fill=ink, width=2)

    # e
    e_points = [
        (568, 180), (575, 162), (592, 152), (612, 155),
        (625, 165), (628, 182), (620, 198), (605, 208),
        (585, 210), (570, 202), (565, 190), (568, 180),
        (575, 178), (595, 178), (615, 182)
    ]
    draw.line(e_points, fill=ink, width=2)

    # Signature underline
    draw.line(
        [(100, 275), (140, 278), (200, 280), (280, 282),
         (360, 280), (440, 278), (520, 280), (600, 283),
         (660, 282), (710, 278)],
        fill=ink, width=2
    )

    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img.save(path)
    return path
