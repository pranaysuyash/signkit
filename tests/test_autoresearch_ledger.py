"""Validate the source-controlled SignKit autoresearch ledger contract."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "experiments/signkit_autoresearch/results.tsv"


def test_autoresearch_ledger_has_reproducible_baseline_rows() -> None:
    with LEDGER.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    assert len(rows) >= 2
    required = {
        "run_id",
        "timestamp",
        "hypothesis",
        "pipeline",
        "dataset_revision",
        "eval_split",
        "status",
        "decision",
        "notes",
    }
    assert required.issubset(rows[0])
    assert {row["run_id"] for row in rows} >= {
        "baseline-signverod-20260813",
        "baseline-synthetic-heldout-20260813",
    }

    for row in rows:
        assert row["timestamp"]
        assert row["dataset_revision"]
        assert row["status"] in {"complete", "running", "crashed", "discarded", "investigate"}
        assert row["decision"] in {"baseline", "keep", "discard", "investigate"}
        assert row["notes"]


def test_autoresearch_ledger_does_not_claim_unmeasured_presence_metrics() -> None:
    with LEDGER.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    signverod = next(row for row in rows if row["run_id"] == "baseline-signverod-20260813")
    assert signverod["presence_precision"] == ""
    assert signverod["presence_recall"] == ""
    assert "Presence exact accuracy 0.1288" in signverod["notes"]
