#!/usr/bin/env python3
"""Validate the governed external dataset candidate registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FIELDS = {
    "id",
    "name",
    "source_url",
    "owner",
    "license",
    "access_status",
    "download_status",
    "use_status",
    "consent_status",
    "identity_risk",
    "source_provenance_status",
    "annotation_profile",
    "multi_signature_context",
    "unknowns",
    "decision",
    "observed_on",
    "evidence_urls",
}


def validate_registry(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if payload.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    datasets = payload.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        return errors + ["datasets must be a non-empty list"]
    ids: set[str] = set()
    for index, dataset in enumerate(datasets):
        prefix = f"datasets[{index}]"
        if not isinstance(dataset, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = REQUIRED_FIELDS - set(dataset)
        errors.extend(f"{prefix} missing {field}" for field in sorted(missing))
        dataset_id = dataset.get("id")
        if not isinstance(dataset_id, str) or not dataset_id:
            errors.append(f"{prefix}.id must be non-empty")
        elif dataset_id in ids:
            errors.append(f"duplicate dataset id: {dataset_id}")
        else:
            ids.add(dataset_id)
        if not isinstance(dataset.get("source_url"), str) or not dataset["source_url"].startswith("https://"):
            errors.append(f"{prefix}.source_url must be an https URL")
        if not isinstance(dataset.get("unknowns"), list) or not all(isinstance(item, str) for item in dataset["unknowns"]):
            errors.append(f"{prefix}.unknowns must be a list of strings")
        if not isinstance(dataset.get("evidence_urls"), list) or not all(
            isinstance(item, str) and item.startswith("https://") for item in dataset["evidence_urls"]
        ):
            errors.append(f"{prefix}.evidence_urls must contain https URLs")
        if dataset.get("download_status") == "not_downloaded" and dataset.get("access_status") == "downloaded_private_external":
            errors.append(f"{prefix} cannot be both not_downloaded and downloaded_private_external")
        if dataset.get("use_status") == "approved_internal":
            errors.append(f"{prefix} cannot be approved_internal without an approval record")
        if dataset.get("decision") == "do_not_download" and dataset.get("download_status") != "not_downloaded":
            errors.append(f"{prefix} do_not_download entries must not be downloaded")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="docs/test_data_dataset_registry_2026-08-13.json")
    args = parser.parse_args()
    errors = validate_registry(Path(args.registry))
    if errors:
        print("DATASET_REGISTRY_ERROR:")
        for error in errors:
            print(f" - {error}")
        return 2
    print("Dataset registry OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
