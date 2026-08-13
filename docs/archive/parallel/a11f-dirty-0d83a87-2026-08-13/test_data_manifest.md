# Test Data Manifest

**Status:** In use (initial draft)
**Scope Date:** 2026-08-12

## Canonical Fixture Inventory

Each row must include:
- `file`: fixture path
- `type`: pdf | image | json | other
- `purpose`: unit, integration, benchmark, golden, smoke
- `generation`: synthetic | captured | converted | unknown
- `source`: explicit provenance
- `reproducible_seed`: seed or deterministic marker when synthetic/generated
- `origin`: short provenance note suitable for auditors
- `pii`: no/yes/unknown status of direct personal data presence
- `contains_pii`: yes/no/unknown
- `redacted`: yes/no/partial/n/a
- `reviewed_on`: last governance review date
- `sha256`: file checksum for drift detection

| file | type | purpose | generation | source | reproducible_seed | origin | pii | contains_pii | redacted | reviewed_on | sha256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `desktop_app/tests/fixtures/sample.pdf` | pdf | Integration + detector smoke | captured | repo fixture | N/A | synthetic test corpus | no | no | n/a | 2026-08-12 | 2450ba834348f1c87d3c2ff8707c19f2303a2856d91c10e3550701adde623979 |
| `desktop_app/tests/fixtures/signed_output.pdf` | pdf | Golden output comparison | captured | repo fixture | N/A | synthetic test corpus | no | no | n/a | 2026-08-12 | 5a16619783a8dd530ffd5ccb555e06fe9db7195be7eb1e91fc356358d5a234ea |
| `desktop_app/tests/fixtures/auto_detect_golden.json` | json | Golden labels | captured | `tests/test_integration_workflows.py` | n/a | synthetic workflow artifact | no | no | n/a | 2026-08-13 | d883d2dfe6c3489fc7db8837992e43aaffd5ec69dadd646b38389b005fd4431a |
| `desktop_app/tests/fixtures/native_form_benchmark.pdf` | pdf | Parser benchmark | generated | `tools/generate_native_form_fixture.py` | seed=20260812;version=1.0.0 | synthetic fixtures generator | no | no | n/a | 2026-08-12 | 8c6d35afc2aa849debcb10ae70042b147425e9a51f65705c442691748532c9bb |
| `desktop_app/tests/fixtures/checkbox_heavy_benchmark.pdf` | pdf | Parser benchmark | generated | `tools/generate_parser_benchmark_corpus.py` | seed=20260812;version=1.0.0 | synthetic fixtures generator | no | no | n/a | 2026-08-12 | 26e9f66041e09a4aadf1a974e4c465c08287b47815d10aaf66b6615c665ea34d |
| `desktop_app/tests/fixtures/mixed_layout_benchmark.pdf` | pdf | Parser benchmark | generated | `tools/generate_parser_benchmark_corpus.py` | seed=20260812;version=1.0.0 | synthetic fixtures generator | no | no | n/a | 2026-08-12 | a041b7c829e63ce717241b4d91cc70c601aa9e380dc1b621b13eb25efa4d5d41 |
| `desktop_app/tests/fixtures/scan_like_benchmark.pdf` | pdf | Parser benchmark | generated | `tools/generate_parser_benchmark_corpus.py` | seed=20260812;version=1.0.0 | synthetic fixtures generator | no | no | n/a | 2026-08-12 | 8e3f7c550194aec6efa588be9cd5c25f1afad27a5f7bead2600a801c29b758e4 |
| `desktop_app/tests/fixtures/test_signature.png` | image | Unit/perf signal | synthetic fallback | `tools/generate_synthetic_signature_asset.py` | deterministic synthetic mark; PNG compatibility fixture | generated identity-free template | no | no | n/a | 2026-08-13 | 42690124ae7f165802f1ef602e6820b145e2a1d03e52f3649b2f5936b659cba5 |
| `desktop_app/resources/signature_template_synthetic_512.jpg` | image | Synthetic fallback sample for first-run and manual signatures | generated | `tools/generate_synthetic_signature_asset.py`, `desktop_app/resources/sample_signature.py` | deterministic vector-like stroke pattern at 512x512; JPEG generated with fixed parameters | synthetic deterministic template; no identity-derived content | no | no | n/a | 2026-08-13 | 7f8383e267746ac5fe7de23648dfc3249252675595920dba3586fd24863b58e1 |
| `desktop_app/tests/fixtures/signature_edge_cases/metadata.json` | json | Edge-case fixture contract and coverage labels | generated | `tools/generate_signature_edge_case_fixtures.py` | seed=20260812;version=1.0.0 | synthetic-only edge corpus metadata; no identity-derived content | no | no | n/a | 2026-08-12 | 939ad4cc3dc46afdd989207d962df1cf42f8f6f78a99430f39c7641e0d2d5ffb |
| `desktop_app/tests/fixtures/signature_edge_cases/blank_canvas.png` | image | Edge-case negative control | generated | `tools/generate_signature_edge_case_fixtures.py` | seed=20260812;version=1.0.0 | synthetic blank canvas; no identity-derived content | no | no | n/a | 2026-08-12 | d8acccafa1fdcf03f3bb9112f5f2f30ad1558e446d5c12ec5644fc0d53c1e58b |
| `desktop_app/tests/fixtures/signature_edge_cases/low_contrast.png` | image | Edge-case extraction coverage | generated | `tools/generate_signature_edge_case_fixtures.py` | seed=20260812;version=1.0.0 | synthetic low-contrast mark; no identity-derived content | no | no | n/a | 2026-08-12 | 32a4155d0dcdca61998355d03f7568cb0f802c161609322aef05ae876cfe856f |
| `desktop_app/tests/fixtures/signature_edge_cases/rotated_tilted.png` | image | Edge-case extraction coverage | generated | `tools/generate_signature_edge_case_fixtures.py` | seed=20260812;version=1.0.0 | synthetic tilted mark; no identity-derived content | no | no | n/a | 2026-08-12 | 74bd26e70c93ac50fc6ee2832a3b8177dbbf67cead9a42f96f1f02cfcb29d8b1 |
| `desktop_app/tests/fixtures/signature_edge_cases/offset_noisy.png` | image | Edge-case extraction coverage | generated | `tools/generate_signature_edge_case_fixtures.py` | seed=20260812;version=1.0.0 | synthetic offset noisy mark; no identity-derived content | no | no | n/a | 2026-08-12 | 0b0fd3714f8b749c47577b14ab62982b9cb9bf658a6b8e86f4c48e631a59a1b8 |
| `desktop_app/tests/fixtures/signature_edge_cases/partial_occlusion.png` | image | Edge-case extraction coverage | generated | `tools/generate_signature_edge_case_fixtures.py` | seed=20260812;version=1.0.0 | synthetic partially occluded mark; no identity-derived content | no | no | n/a | 2026-08-12 | 90b45813600ef918600644d6cdbdf3d64fe064c50fd6a878639a3f0805e9885d |
| `desktop_app/tests/fixtures/signature_edge_cases/multi_signature.png` | image | Multi-signature count and localization coverage | generated | `tools/generate_signature_edge_case_fixtures.py` | seed=20260812;version=1.0.0 | synthetic multi-mark image; no identity-derived content | no | no | n/a | 2026-08-12 | 17538e2eed452740dcec043201ed2157680a8ba005ee7f2e914de2df87562a59 |
| `desktop_app/tests/fixtures/signature_benchmark_v1/metadata.json` | json | Subject-disjoint held-out benchmark metadata | generated | `tools/generate_signature_benchmark.py` | seed=20260813;version=1.0.0 | synthetic-only benchmark metadata; no human or production data | no | no | n/a | 2026-08-13 | 5057f2e54d9bb91172718996ed9d46cd9255c512f0a022c7f7afed8a5deb3aab |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-00-page-01.png` | image | Synthetic benchmark train negative | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-00 | synthetic negative page; no identity-derived content | no | no | n/a | 2026-08-13 | 7235c9a91b9a0a734b61adbf4ad082c7d5116c8e7cc0ee104033fa1f734105ee |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-01-page-01.png` | image | Synthetic benchmark train single signature | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-01 | synthetic blue-ink mark; no identity-derived content | no | no | n/a | 2026-08-13 | 108feb78dde4463e4531070e34bb126229c3641cadec6e2632768b6156b23308 |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-02-page-01.png` | image | Synthetic benchmark train multiple signatures | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-02 | synthetic blue-ink marks; no identity-derived content | no | no | n/a | 2026-08-13 | 11ff5349f928d7f08207f676519bae469c64b76fadb6946da408675581a01ada |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-03-page-01.png` | image | Synthetic benchmark train single signature | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-03 | synthetic blue-ink mark; no identity-derived content | no | no | n/a | 2026-08-13 | c182a0d2de5b1a2f3862197369c675984e78cd8fac14368435205e9fa3daaa6c |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-04-page-01.png` | image | Synthetic benchmark train negative | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-04 | synthetic negative page; no identity-derived content | no | no | n/a | 2026-08-13 | cbce17b066c6dd3b6fdbe08bb27d4060af04e1d57f97e32fec53c7cc9f199907 |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-05-page-01.png` | image | Synthetic benchmark train multiple signatures | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-05 | synthetic blue-ink marks; no identity-derived content | no | no | n/a | 2026-08-13 | 1d6ad4df24be0c415c189822df3d4ea0ac23f96bd03a2e0624ec5844315bf2e5 |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-06-page-01.png` | image | Synthetic benchmark validation single signature | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-06 | synthetic blue-ink mark; no identity-derived content | no | no | n/a | 2026-08-13 | 0ccc2772192fb0bd980753f80f441b831f8e6d436a7905aceaa9edfab53e2ca3 |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-07-page-01.png` | image | Synthetic benchmark validation multiple signatures | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-07 | synthetic blue-ink marks; no identity-derived content | no | no | n/a | 2026-08-13 | a0d95ad775b9ddfd4a16d9e318468cf6a329b42214bbab0963abf93006472e28 |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-08-page-01.png` | image | Synthetic benchmark validation negative | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-08 | synthetic negative page; no identity-derived content | no | no | n/a | 2026-08-13 | d4d1e87c056ac615bdd9c9a903e274fa77aefc7a807e3e51bd18505da8d0574a |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-09-page-01.png` | image | Synthetic benchmark held-out test single signature | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-09 | synthetic blue-ink mark; no identity-derived content | no | no | n/a | 2026-08-13 | 6cf08ac6e7e9ad8319224094e17b95143328c85ac58a05319693826a98d3ad0c |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-10-page-01.png` | image | Synthetic benchmark held-out test multiple signatures | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-10 | synthetic blue-ink marks; no identity-derived content | no | no | n/a | 2026-08-13 | 51d39e2b6e9d90b046725a16190929b268ad0b49a3f081d15efade75bea575e5 |
| `desktop_app/tests/fixtures/signature_benchmark_v1/synthetic-subject-11-page-01.png` | image | Synthetic benchmark held-out test single signature | generated | `tools/generate_signature_benchmark.py` | seed=20260813;subject=synthetic-subject-11 | synthetic blue-ink mark; no identity-derived content | no | no | n/a | 2026-08-13 | 78f256e07e9a2403ab0f7fe1c6cbf4eab3ff77b249d2b2bc8a768a18e8bf214b |

## Edge-case coverage tags (to maintain)

- `layout_complexity:high`
- `scan_noise:low`
- `scan_noise:high`
- `signature_position:center`
- `signature_position:offset`
- `field_density:dense`
- `field_density:sparse`
- `rotation:0`
- `rotation:tilted`
- `occlusion:none`
- `occlusion:partial`

## Governance and update rule

1. New fixtures must be added with one manifest row before commit.
2. Any file with potential personal data signals must have explicit `pii` / `contains_pii` / `redacted` values and remediation notes.
3. Synthetic outputs must include a reproducibility marker (seed, algorithm version, generator command, script hash if practical).
4. Every manifest row is reviewed whenever fixture behavior or data source changes.
