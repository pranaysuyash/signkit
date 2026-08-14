# Image calibration fixture provenance

- Dataset: `image-signatures-generated-v1`
- Detector: `image`
- Samples: `120`
- Split: deterministic `70/15/15` train, validation, test
- Seed: `20260814`
- Generator: `scripts/build_calibration_dataset.py`, generator version `1`
- Ground truth: programmatic synthetic labels for generated PNG fixtures
- Use: internal calibration research only
- Artifact policy: this note, `manifest.json`, and calibration reports are
  tracked; `images/*.png` is generated and ignored

Regenerate the assets from the recorded metadata with:

```bash
./.venv/bin/python scripts/build_calibration_dataset.py \
  --out datasets --image-n 120 --pdf-n 120 --seed 20260814
```

The generated files are not permissioned customer documents and must not be
used to support human, legal, production, or real-world accuracy claims.
