# Test Data Edge-case Coverage Matrix

## Coverage map

| fixture | edge_case_tags | test modules |
| --- | --- | --- |
| `desktop_app/tests/fixtures/sample.pdf` | `layout_complexity:low`, `signature_position:center`, `field_density:low`, `rotation:0`, `occlusion:none` | `desktop_app/tests/test_pdf_field_detection.py`, `tests/test_integration_workflows.py` |
| `desktop_app/tests/fixtures/signed_output.pdf` | `layout_complexity:low`, `signature_position:center`, `field_density:low`, `rotation:0`, `occlusion:none` | `tests/test_integration_workflows.py`, `desktop_app/tests/test_pdf_bulk_field_detection.py` |
| `desktop_app/tests/fixtures/native_form_benchmark.pdf` | `layout_complexity:medium`, `signature_position:center`, `field_density:dense`, `rotation:0`, `occlusion:none` | `desktop_app/tests/test_pdf_field_detection.py`, `desktop_app/tests/test_pdf_bulk_field_detection.py` |
| `desktop_app/tests/fixtures/checkbox_heavy_benchmark.pdf` | `field_density:dense`, `layout_complexity:high`, `rotation:0`, `occlusion:none` | `desktop_app/tests/test_pdf_field_detection.py` |
| `desktop_app/tests/fixtures/mixed_layout_benchmark.pdf` | `layout_complexity:high`, `signature_position:offset`, `field_density:sparse`, `rotation:0`, `occlusion:none` | `desktop_app/tests/test_pdf_field_detection.py`, `tests/test_integration_workflows.py` |
| `desktop_app/tests/fixtures/scan_like_benchmark.pdf` | `scan_noise:high`, `layout_complexity:medium`, `signature_position:center`, `field_density:sparse`, `rotation:tilted`, `occlusion:partial` | `desktop_app/tests/test_pdf_bulk_field_detection.py`, `tests/test_integration_workflows.py` |
| `desktop_app/tests/fixtures/test_signature.png` | `signature_position:center`, `field_density:low`, `rotation:0`, `occlusion:none` | `desktop_app/tests/test_extractor.py`, `desktop_app/tests/test_pdf_field_detection.py` |
| `desktop_app/tests/fixtures/signature_edge_cases/blank_canvas.png` | `blank`, `background_only`, `negative_control` | `desktop_app/tests/test_signature_edge_cases.py` |
| `desktop_app/tests/fixtures/signature_edge_cases/low_contrast.png` | `contrast:low`, `background:gray` | `desktop_app/tests/test_signature_edge_cases.py` |
| `desktop_app/tests/fixtures/signature_edge_cases/rotated_tilted.png` | `rotation:tilted`, `background:white` | `desktop_app/tests/test_signature_edge_cases.py` |
| `desktop_app/tests/fixtures/signature_edge_cases/offset_noisy.png` | `signature_position:offset`, `scan_noise:high` | `desktop_app/tests/test_signature_edge_cases.py` |
| `desktop_app/tests/fixtures/signature_edge_cases/partial_occlusion.png` | `occlusion:partial`, `signature_position:center` | `desktop_app/tests/test_signature_edge_cases.py` |

## Gap scan

- If any test module does not consume a fixture tagged with its primary failure class, add the fixture or route the test to an existing closer match.
- Open gap currently tracked under `T-004` in [docs/test_data_audit.md].
