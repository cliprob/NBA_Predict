from __future__ import annotations

import json
from pathlib import Path

import pytest

from nba_predict.reproducibility import (
    collect_metric_mismatches,
    file_sha256,
    verify_artifact_manifest,
    verify_metrics_snapshot,
)


def test_collect_metric_mismatches_accepts_tolerated_float_difference() -> None:
    mismatches = collect_metric_mismatches(
        {"accuracy": 0.75},
        {"accuracy": 0.7500000001},
        tolerance=1e-6,
    )

    assert mismatches == []


def test_verify_metrics_snapshot_rejects_mismatch(tmp_path) -> None:
    expected_path = tmp_path / "expected.json"
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()

    expected_path.write_text(
        json.dumps(
            {
                "models": {
                    "logistic": {
                        "accuracy": 1.0,
                        "precision": 1.0,
                        "recall": 1.0,
                        "confusion_matrix": [[1, 0], [0, 1]],
                        "cumulative_errors": [0],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    (metrics_dir / "logistic_2022-23_metrics.json").write_text(
        json.dumps(
            {
                "accuracy": 0.5,
                "precision": 1.0,
                "recall": 1.0,
                "confusion_matrix": [[1, 0], [0, 1]],
                "cumulative_errors": [0],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="accuracy mismatch"):
        verify_metrics_snapshot(expected_path, metrics_dir, season="2022-23")


def test_verify_metrics_snapshot_accepts_repository_fixture(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    expected_path = repo_root / "data" / "reproducibility" / "expected_metrics.json"
    metrics_dir = tmp_path / "generated-metrics"
    metrics_dir.mkdir()

    payload = json.loads(expected_path.read_text(encoding="utf-8"))
    for model_name, metrics in payload["models"].items():
        (metrics_dir / f"{model_name}_2022-23_metrics.json").write_text(
            json.dumps(metrics),
            encoding="utf-8",
        )

    verify_metrics_snapshot(expected_path, metrics_dir, season="2022-23")


def test_verify_artifact_manifest_accepts_repository_manifest() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "data" / "reproducibility" / "MANIFEST.json"

    verify_artifact_manifest(manifest_path, project_root=repo_root)


def test_verify_artifact_manifest_rejects_hash_mismatch(tmp_path) -> None:
    data_path = tmp_path / "artifact.csv"
    data_path.write_text("a,b\n1,2\n", encoding="utf-8")
    manifest_path = tmp_path / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": "artifact.csv",
                        "sha256": "0" * 64,
                        "kind": "csv",
                        "rows": 1,
                        "columns": ["a", "b"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="sha256 mismatch"):
        verify_artifact_manifest(manifest_path, project_root=tmp_path)


def test_file_sha256_returns_lowercase_digest(tmp_path) -> None:
    path = tmp_path / "artifact.txt"
    path.write_bytes(b"reproducible\n")

    assert file_sha256(path) == (
        "9eea221f83299a3ebea16d547cb0f1cbbaace6be5c925cd9f0ccfcd1b6549c67"
    )
