# Parser Baseline Comparison

Date: 2026-06-21

This matrix compares the current local baseline against the benchmark corpus generated for the parser exploration branch.

## Current Availability

- LiteParse adapter seam: available, package unavailable in this environment
- Managed parser adapter seam: available, opt-in only
- Current local baseline: `pypdf` + `pikepdf` + `pypdfium2` + `PyMuPDF` opt-in

## Matrix

| file | pages | text_pages | widget_count | images | signature_candidates | acroform_candidates | heuristic_candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| demo_document.pdf | 6 | 6 | 0 | 0 | 9 | 0 | 9 |
| sample.pdf | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| signed_output.pdf | 2 | 0 | 0 | 2 | 2 | 0 | 2 |
| native_form_benchmark.pdf | 1 | 1 | 5 | 0 | 7 | 5 | 3 |
| checkbox_heavy_benchmark.pdf | 1 | 1 | 5 | 0 | 8 | 5 | 3 |
| mixed_layout_benchmark.pdf | 1 | 1 | 0 | 0 | 3 | 0 | 3 |
| scan_like_benchmark.pdf | 1 | 0 | 0 | 1 | 3 | 0 | 3 |

## Readout

1. Native widget detection is now real and reproducible on the AcroForm benchmarks.
2. Heuristic suggestions stay bounded to a small page-level cap.
3. Text-native layouts still generate useful but imperfect field-like suggestions.
4. Scan-like pages remain heuristic-heavy and need more benchmark diversity before any parser ranking is trustworthy.
5. LiteParse now has a real adapter seam, but the package itself is not installed in the current environment.

## Next Step

Prototype the optional LiteParse adapter seam and compare it against the local baseline when the package is available.
