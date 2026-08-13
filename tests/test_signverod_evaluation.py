from tools.evaluate_signverod_corpus import _signature_boxes


def test_signverod_conversion_keeps_signature_boxes_and_converts_coco_geometry():
    objects = {
        "category": [1, 2, 1],
        "bbox": [[10, 20, 30, 40], [2, 3, 4, 5], [100, 110, 12, 14]],
    }

    assert _signature_boxes(objects, 200, 200) == [
        (10.0, 20.0, 40.0, 60.0),
        (100.0, 110.0, 112.0, 124.0),
    ]
