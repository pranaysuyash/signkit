#!/usr/bin/env python3
"""Run a disposable local source-to-ready operator workflow proof.

The proof composes the existing local extraction, encrypted vault, controlled
workflow engine, execution passport, PDF signer, and artifact receipt owners.
It deliberately forces one transient signing failure after extraction and vault
resolution, then uses the canonical retry path to produce and verify the final
visual signature-placement PDF. It never contacts a hosted service.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import shutil
import sys
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from desktop_app.pdf.signer import sign_pdf as canonical_sign_pdf
from desktop_app.processing.extractor import SignatureExtractor
from desktop_app.processing.vault import NotaryVault
from desktop_app.workflows import authorization, engine as workflow_engine, models, passport, store
from desktop_app.workflows.verifier import build_artifact_receipt, verify_output, write_artifact_receipt

SAMPLE_PDF = ROOT / "desktop_app" / "tests" / "fixtures" / "sample.pdf"
OPERATOR = "local-proof-operator"
SCHEMA = "signkit.local_source_to_ready_proof.v1"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="directory for disposable source, ready output, receipt, and manifest",
    )
    return parser.parse_args()


def _default_output_dir() -> Path:
    destination = ROOT / ".codex-test-tmp" / f"source-to-ready-proof-{uuid4().hex[:10]}"
    destination.mkdir(parents=True, exist_ok=False)
    return destination


def _write_source_image(path: Path) -> None:
    image = Image.new("RGB", (480, 240), "white")
    draw = ImageDraw.Draw(image)
    points = []
    for x in range(55, 425, 3):
        y = 120 + int(24 * math.sin(x / 17.0))
        points.append((x, y))
    draw.line(points, fill=(18, 18, 18), width=5, joint="curve")
    draw.line([(80, 155), (180, 155), (235, 145)], fill=(18, 18, 18), width=4)
    image.save(path, format="PNG")


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _configure_store(output_dir: Path) -> tuple[Path, Path]:
    original = (store.APP_DIR, store.WORKFLOW_STORE_FILE)
    store.APP_DIR = output_dir / "workflow-store"
    store.WORKFLOW_STORE_FILE = store.APP_DIR / "workflow_store.json"
    return original


def _create_recipe(output_dir: Path, signature_id: str) -> models.ControlledSigningRecipe:
    input_folder = models.FolderConfig(
        folder_id="proof-input-folder",
        path=str(output_dir / "source"),
        recursive=False,
        require_stable_size=True,
    )
    output_folder = models.FolderConfig(
        folder_id="proof-output-folder",
        path=str(output_dir / "ready"),
        recursive=False,
        require_stable_size=True,
    )
    review_folder = models.FolderConfig(
        folder_id="proof-review-folder",
        path=str(output_dir / "review"),
        recursive=False,
        require_stable_size=True,
    )
    binding = models.SignatureFieldBinding.from_legacy_values(
        signature_path=signature_id,
        page_index=0,
        x_ratio=0.12,
        y_ratio=0.68,
        width_ratio=0.25,
        height_ratio=0.08,
        field_label="Local proof mark",
    )
    return models.ControlledSigningRecipe.new(
        recipe_id="local-source-to-ready-proof",
        name="Local Proof Packet",
        status=models.RecipeStatus.ACTIVE.value,
        document_matcher={"kind": models.MatchClass.EXACT.value},
        input_folder=input_folder,
        output_folder=output_folder,
        review_folder=review_folder,
        field_bindings=[binding],
        created_by=OPERATOR,
    )


def run_proof(output_dir: Path) -> dict[str, object]:
    if not SAMPLE_PDF.is_file():
        raise FileNotFoundError(f"missing canonical proof fixture: {SAMPLE_PDF}")

    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = output_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    ready_dir = output_dir / "ready"
    ready_dir.mkdir(parents=True, exist_ok=True)
    source_image = source_dir / "signature-source.png"
    source_pdf = source_dir / "source-document.pdf"
    _write_source_image(source_image)
    shutil.copy2(SAMPLE_PDF, source_pdf)

    extractor = SignatureExtractor()
    session_id = extractor.create_session(str(source_image))
    detected = extractor.auto_detect_signature(session_id)
    if detected is None:
        raise RuntimeError("source-to-ready proof could not detect the disposable signature fixture")
    x1, y1, x2, y2 = detected
    extracted_png = extractor.process_selection(
        session_id,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        threshold=128,
        color="#000000",
        auto_clean=True,
    )
    extracted_image = Image.open(io.BytesIO(extracted_png))
    extracted_image.load()
    extracted_mode = extracted_image.mode
    extracted_size = extracted_image.size

    vault_dir = output_dir / "vault"
    vault = NotaryVault(vault_dir=str(vault_dir))
    signature_id = vault.store_signature(
        extracted_png,
        {"source": "disposable_local_source_to_ready_proof", "operator": OPERATOR},
    )
    if vault.retrieve_signature(signature_id) != extracted_png:
        raise RuntimeError("vault round-trip changed extracted signature bytes")

    original_store_paths = _configure_store(output_dir)
    original_sign_pdf = workflow_engine.sign_pdf
    attempt_count = 0
    try:
        recipe = store.save_recipe(_create_recipe(output_dir, signature_id))
        grant = authorization.create_grant(
            recipe.recipe_id,
            policy={"matcher_modes": [models.MatchClass.EXACT.value], "allowed_assets": [signature_id]},
            runner=OPERATOR,
        )
        engine = workflow_engine.WorkflowEngine(
            actor=OPERATOR,
            audit_actor=OPERATOR,
            output_namer="{name}_{job_id}_ready.pdf",
            vault_factory=lambda: vault,
        )
        engine.start()

        def flaky_sign_pdf(input_path: str, output_path: str, signatures: list[dict[str, object]]) -> bool:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise RuntimeError("proof_forced_transient_failure")
            return bool(canonical_sign_pdf(input_path, output_path, signatures))

        workflow_engine.sign_pdf = flaky_sign_pdf
        created_job = engine.enqueue_path(str(source_pdf), recipe_id=recipe.recipe_id)
        failed_attempt = engine.run_job(created_job.job_id, actor=OPERATOR, action_subject=OPERATOR)
        if failed_attempt.state != models.WorkflowState.RETRY:
            raise RuntimeError(f"forced failure did not enter retry state: {failed_attempt.state.value}")
        failure_events = store.list_events(created_job.job_id)
        failure_passport = passport.project_local_job(failed_attempt, failure_events).to_payload()

        completed_job = engine.retry_job(created_job.job_id, actor=OPERATOR, action_subject=OPERATOR)
        if completed_job.state != models.WorkflowState.COMPLETED:
            raise RuntimeError(f"canonical retry did not complete: {completed_job.state.value}")
        final_events = store.list_events(created_job.job_id)
        output_pdf = Path(completed_job.output_path_ref)
        verification = verify_output(str(source_pdf), str(output_pdf))
        if not verification.ok:
            raise RuntimeError(f"ready artifact failed verification: {verification.reason}")

        receipt = build_artifact_receipt(
            str(source_pdf),
            str(output_pdf),
            operator_subject=OPERATOR,
            execution_id=completed_job.job_id,
        )
        receipt_path = output_dir / "artifact-receipt.json"
        write_artifact_receipt(receipt, str(receipt_path))
        completed_job = store.save_job(replace(completed_job, receipt_reference=receipt.artifact_id))
        final_passport = passport.project_local_job(
            completed_job,
            store.list_events(created_job.job_id),
        ).to_payload()
        manifest = {
            "schema": SCHEMA,
            "status": "pass",
            "proof_scope": "local_desktop_source_to_ready_with_retry",
            "hosted_service_contacted": False,
            "document_bytes_in_browser_workspace": False,
            "paths": {
                "source_image": _relative(source_image, output_dir),
                "source_document": _relative(source_pdf, output_dir),
                "ready_document": _relative(output_pdf, output_dir),
                "artifact_receipt": _relative(receipt_path, output_dir),
                "workflow_store": _relative(store.WORKFLOW_STORE_FILE, output_dir),
                "vault": _relative(vault_dir, output_dir),
            },
            "extraction": {
                "session_created": True,
                "detected_bbox": [x1, y1, x2, y2],
                "processed_mode": extracted_mode,
                "processed_size": list(extracted_size),
                "encrypted_vault_round_trip": True,
                "signature_asset_id": signature_id,
            },
            "workflow": {
                "recipe_id": recipe.recipe_id,
                "grant_id": grant.grant_id,
                "job_id": completed_job.job_id,
                "forced_failure_state": failed_attempt.state.value,
                "forced_failure_code": failed_attempt.last_error_code,
                "forced_failure_attempt": failed_attempt.attempts,
                "completed_state": completed_job.state.value,
                "completed_attempt": completed_job.attempts,
                "attempt_count": attempt_count,
                "event_codes": [event.code for event in final_events],
                "failure_passport": failure_passport,
                "final_passport": final_passport,
            },
            "artifact_receipt": receipt.to_dict(),
        }
        manifest_path = output_dir / "manifest.json"
        _write_json(manifest_path, manifest)
        manifest["manifest_path"] = str(manifest_path)
        return manifest
    finally:
        workflow_engine.sign_pdf = original_sign_pdf
        store.APP_DIR, store.WORKFLOW_STORE_FILE = original_store_paths


def main() -> int:
    args = _parse_args()
    output_dir = args.output_dir.expanduser().resolve() if args.output_dir else _default_output_dir()
    manifest = run_proof(output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
