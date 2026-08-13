#!/usr/bin/env python3
"""Build and validate the machine-readable SignKit release artifact ledger.

The ledger records artifact identity and release evidence. It deliberately does
not infer signing, smoke, or rollback evidence from the presence of a file.
Those statuses must be supplied by the release workflow or an operator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "signkit.release-ledger.v1"
ALLOWED_SIGNING_STATUSES = {"signed", "not_applicable", "not_verified", "not_recorded", "failed"}
ALLOWED_SMOKE_STATUSES = {"passed", "not_applicable", "not_run", "failed"}
READY_SIGNING_STATUSES = {"signed", "not_applicable"}
READY_SMOKE_STATUSES = {"passed", "not_applicable"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _sha256_and_size(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _parse_artifact_spec(spec: str) -> tuple[str, str, str, Path, str, str, str, str]:
    parts = spec.split("|")
    if len(parts) not in {6, 8} or any(not part.strip() for part in parts[:6]):
        raise ValueError(
            "artifact must use name|platform|architecture|path|signing_status|smoke_status|signing_evidence|smoke_evidence"
        )
    name, platform, architecture, raw_path, signing_status, smoke_status = (
        part.strip() for part in parts[:6]
    )
    signing_evidence = parts[6].strip() if len(parts) == 8 else ""
    smoke_evidence = parts[7].strip() if len(parts) == 8 else ""
    if signing_status not in ALLOWED_SIGNING_STATUSES:
        raise ValueError(f"unsupported signing_status: {signing_status}")
    if smoke_status not in ALLOWED_SMOKE_STATUSES:
        raise ValueError(f"unsupported smoke_status: {smoke_status}")
    return (
        name,
        platform,
        architecture,
        Path(raw_path),
        signing_status,
        smoke_status,
        signing_evidence,
        smoke_evidence,
    )


def build_ledger(
    *,
    release_tag: str,
    source_sha: str,
    release_url: str,
    rollback_artifact: str,
    generated_at: str,
    artifact_specs: Iterable[str],
) -> dict[str, Any]:
    """Build a ledger from explicit artifact specifications."""

    if not release_tag.strip():
        raise ValueError("release_tag is required")
    if not source_sha.strip():
        raise ValueError("source_sha is required")
    if not generated_at.strip():
        raise ValueError("generated_at is required")

    artifacts: list[dict[str, Any]] = []
    for raw_spec in artifact_specs:
        (
            name,
            platform,
            architecture,
            path,
            signing_status,
            smoke_status,
            signing_evidence,
            smoke_evidence,
        ) = _parse_artifact_spec(raw_spec)
        if not path.is_file():
            raise ValueError(f"artifact path is not a regular file: {path}")
        sha256, size = _sha256_and_size(path)
        artifacts.append(
            {
                "name": name,
                "platform": platform,
                "architecture": architecture,
                "path": str(path),
                "bytes": size,
                "sha256": sha256,
                "signing_status": signing_status,
                "smoke_status": smoke_status,
                "signing_evidence": signing_evidence,
                "smoke_evidence": smoke_evidence,
            }
        )

    if not artifacts:
        raise ValueError("at least one artifact is required")

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "release_tag": release_tag,
        "source_sha": source_sha,
        "release_url": release_url,
        "rollback_artifact": rollback_artifact,
        "artifacts": artifacts,
    }


def validate_ledger(ledger: Any, *, require_ready: bool = False) -> list[str]:
    """Return deterministic validation errors for a ledger."""

    errors: list[str] = []
    if not isinstance(ledger, dict):
        return ["ledger must be an object"]
    if ledger.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    for field in ("generated_at", "release_tag", "source_sha", "release_url", "rollback_artifact"):
        if not isinstance(ledger.get(field), str) or not ledger[field].strip():
            errors.append(f"{field} is required")

    artifacts = ledger.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must contain at least one item")
        return errors

    for index, artifact in enumerate(artifacts):
        label = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{label} must be an object")
            continue
        for field in (
            "name",
            "platform",
            "architecture",
            "path",
            "signing_status",
            "smoke_status",
            "signing_evidence",
            "smoke_evidence",
        ):
            if not isinstance(artifact.get(field), str) or not artifact[field].strip():
                errors.append(f"{label}.{field} is required")
        size = artifact.get("bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            errors.append(f"{label}.bytes must be a non-negative integer")
        digest = artifact.get("sha256")
        if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
            errors.append(f"{label}.sha256 must be a lowercase SHA-256 digest")
        signing_status = artifact.get("signing_status")
        if signing_status not in ALLOWED_SIGNING_STATUSES:
            errors.append(f"{label}.signing_status is unsupported: {signing_status}")
        smoke_status = artifact.get("smoke_status")
        if smoke_status not in ALLOWED_SMOKE_STATUSES:
            errors.append(f"{label}.smoke_status is unsupported: {smoke_status}")
        if require_ready and signing_status not in READY_SIGNING_STATUSES:
            errors.append(f"{label}.signing_status must be signed or not_applicable")
        if require_ready and smoke_status not in READY_SMOKE_STATUSES:
            errors.append(f"{label}.smoke_status must be passed or not_applicable")
        if require_ready and not _has_evidence_reference(artifact.get("signing_evidence")):
            errors.append(f"{label}.signing_evidence is required for a ready release")
        if require_ready and not _has_evidence_reference(artifact.get("smoke_evidence")):
            errors.append(f"{label}.smoke_evidence is required for a ready release")

    if require_ready:
        rollback = ledger.get("rollback_artifact")
        if not isinstance(rollback, str) or not rollback.strip() or rollback.strip() in {
            "not-recorded",
            "not_recorded",
        }:
            errors.append("rollback_artifact must identify a recoverable prior release")
    return errors


def _has_evidence_reference(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(value.strip()) and value.strip() not in {"not-recorded", "not_recorded"}


def _render_markdown(ledger: dict[str, Any], errors: list[str]) -> str:
    lines = [
        "# SignKit release artifact ledger",
        "",
        f"- Schema: `{ledger.get('schema_version', '')}`",
        f"- Release tag: `{ledger.get('release_tag', '')}`",
        f"- Source SHA: `{ledger.get('source_sha', '')}`",
        f"- Release URL: {ledger.get('release_url', '')}",
        f"- Rollback artifact: `{ledger.get('rollback_artifact', '')}`",
        f"- Generated at: `{ledger.get('generated_at', '')}`",
        "",
        "| Artifact | Platform | Architecture | Bytes | SHA-256 | Signing | Smoke | Signing evidence | Smoke evidence |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for artifact in ledger.get("artifacts", []):
        lines.append(
            "| {name} | {platform} | {architecture} | {bytes} | `{sha256}` | {signing_status} | {smoke_status} | {signing_evidence} | {smoke_evidence} |".format(
                **artifact
            )
        )
    lines.extend(["", "## Validation", ""])
    if errors:
        lines.extend(["Status: **blocked**", ""])
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("Status: **valid for the requested gate**")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, ledger: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, help="validate an existing ledger instead of building one")
    parser.add_argument("--output", type=Path, help="JSON output path when building a ledger")
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--release-tag")
    parser.add_argument("--source-sha")
    parser.add_argument("--release-url", default="")
    parser.add_argument("--rollback-artifact", default="not-recorded")
    parser.add_argument("--generated-at", default="generated-by-release-workflow")
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="name|platform|architecture|path|signing_status|smoke_status|signing_evidence|smoke_evidence",
    )
    parser.add_argument("--require-ready", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.ledger:
            ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
        else:
            if not args.output:
                raise ValueError("--output is required when building a ledger")
            if not args.release_tag or not args.source_sha:
                raise ValueError("--release-tag and --source-sha are required when building a ledger")
            ledger = build_ledger(
                release_tag=args.release_tag,
                source_sha=args.source_sha,
                release_url=args.release_url,
                rollback_artifact=args.rollback_artifact,
                generated_at=args.generated_at,
                artifact_specs=args.artifact,
            )
            _write_json(args.output, ledger)

        errors = validate_ledger(ledger, require_ready=args.require_ready)
        if args.markdown_output:
            args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
            args.markdown_output.write_text(_render_markdown(ledger, errors), encoding="utf-8")
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Release ledger valid: {ledger.get('release_tag', '<unknown>')}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
