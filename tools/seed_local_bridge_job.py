#!/usr/bin/env python3
"""Seed one disposable local desktop job bound to an authenticated subject.

This helper is intentionally a proof fixture, not a production job creator.
It writes through the existing desktop workflow store and creates no document
bytes. The seeded job points at a missing private source so the browser proof
can exercise the canonical retry and recovery path safely.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import replace
from pathlib import Path
import sys
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", required=True, help="Exact authenticated workspace subject to bind")
    parser.add_argument("--data-dir", help="Isolated SIGNKIT_DATA_DIR used by the local companion")
    parser.add_argument(
        "--receipt-reference",
        default="sha256:local-bridge-proof-receipt",
        help="Opaque artifact receipt reference to project; no receipt bytes are read",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    subject = args.subject.strip()
    if not subject:
        raise SystemExit("--subject must not be empty")
    if args.data_dir:
        os.environ["SIGNKIT_DATA_DIR"] = str(Path(args.data_dir).expanduser().resolve())

    from desktop_app.workflows import authorization, models, store

    recipe_id = f"local-bridge-proof-{uuid4().hex}"
    recipe = models.ControlledSigningRecipe.new(
        recipe_id=recipe_id,
        name="Local browser bridge proof",
        status=models.RecipeStatus.ACTIVE.value,
        input_folder=models.FolderConfig(
            folder_id=f"input-{uuid4().hex}",
            path=str(store.APP_DIR),
        ),
        output_folder=models.FolderConfig(
            folder_id=f"output-{uuid4().hex}",
            path=str(store.APP_DIR),
        ),
    )
    store.save_recipe(recipe)
    grant = authorization.create_grant(recipe.recipe_id, {}, subject)
    job = models.WorkflowJob.new(
        job_id=f"local-bridge-job-{uuid4().hex}",
        input_path_ref=str(store.APP_DIR / "private-source-document.pdf"),
        input_fingerprint="sha256:local-bridge-proof-input",
        recipe_id=recipe.recipe_id,
        recipe_version=recipe.version,
        state=models.WorkflowState.RETRY,
        grant_id=grant.grant_id,
    )
    # Seed the final permitted retry boundary so the real engine produces a
    # terminal FAILED passport and the browser can show recovery guidance.
    receipt_reference = args.receipt_reference.strip()
    if not receipt_reference:
        raise SystemExit("--receipt-reference must not be empty")
    job = replace(job, attempts=2, receipt_reference=receipt_reference)
    store.save_job(job)
    store.append_job_event(
        event_id=None,
        job_id=job.job_id,
        state_from=models.WorkflowState.VERIFYING,
        state_to=models.WorkflowState.RETRY,
        actor="local-bridge-proof",
        code="ERR_SIGNING_FAILED",
        message="private source path is intentionally withheld from the browser projection",
    )
    print(
        json.dumps(
            {
                "job_id": job.job_id,
                "subject": subject,
                "store_file": str(store.WORKFLOW_STORE_FILE),
                "status": job.state.value,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
