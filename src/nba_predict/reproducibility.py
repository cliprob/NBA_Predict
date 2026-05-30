"""Utilities for deterministic reproduction checks from a frozen snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from numbers import Real
from pathlib import Path

DEFAULT_REPRO_TOLERANCE = 1e-9


def file_sha256(path: str | Path) -> str:
    """Return the SHA256 digest for a file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_shape(path: Path) -> tuple[int, list[str]]:
    """Return data-row count and header columns for a CSV file."""

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        try:
            columns = next(reader)
        except StopIteration:
            return 0, []
        rows = sum(1 for _ in reader)
    return rows, columns


def verify_artifact_manifest(
    manifest_path: str | Path,
    project_root: str | Path = ".",
) -> None:
    """Validate reproducibility artifact hashes and simple file metadata."""

    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    root = Path(project_root)
    failures: list[str] = []

    for item in manifest.get("files", []):
        relative_path = Path(item["path"])
        path = root / relative_path
        if not path.exists():
            failures.append(f"Missing manifest file: {relative_path}")
            continue

        expected_hash = str(item["sha256"]).lower()
        actual_hash = file_sha256(path)
        if actual_hash != expected_hash:
            failures.append(
                f"{relative_path} sha256 mismatch: "
                f"expected {expected_hash}, got {actual_hash}"
            )

        if item.get("kind") == "csv":
            rows, columns = _csv_shape(path)
            if "rows" in item and rows != item["rows"]:
                failures.append(
                    f"{relative_path} row count mismatch: "
                    f"expected {item['rows']}, got {rows}"
                )
            if "columns" in item and columns != item["columns"]:
                failures.append(
                    f"{relative_path} columns mismatch: "
                    f"expected {item['columns']}, got {columns}"
                )

    if failures:
        raise AssertionError("\n".join(failures))


def collect_metric_mismatches(
    expected: object,
    actual: object,
    tolerance: float = DEFAULT_REPRO_TOLERANCE,
    path: str = "metrics",
) -> list[str]:
    """Recursively compare metrics structures with numeric tolerance."""

    if isinstance(expected, dict) and isinstance(actual, dict):
        mismatches = []
        expected_keys = set(expected)
        actual_keys = set(actual)
        for key in sorted(expected_keys - actual_keys):
            mismatches.append(f"{path}.{key} missing from actual metrics")
        for key in sorted(actual_keys - expected_keys):
            mismatches.append(f"{path}.{key} unexpectedly present in actual metrics")
        for key in sorted(expected_keys & actual_keys):
            mismatches.extend(
                collect_metric_mismatches(
                    expected[key],
                    actual[key],
                    tolerance=tolerance,
                    path=f"{path}.{key}",
                )
            )
        return mismatches

    if isinstance(expected, list) and isinstance(actual, list):
        mismatches = []
        if len(expected) != len(actual):
            return [
                f"{path} length mismatch: expected {len(expected)}, got {len(actual)}"
            ]
        for index, (expected_item, actual_item) in enumerate(
            zip(expected, actual, strict=True)
        ):
            mismatches.extend(
                collect_metric_mismatches(
                    expected_item,
                    actual_item,
                    tolerance=tolerance,
                    path=f"{path}[{index}]",
                )
            )
        return mismatches

    if isinstance(expected, Real) and isinstance(actual, Real):
        if math.isclose(float(expected), float(actual), rel_tol=0.0, abs_tol=tolerance):
            return []
        return [f"{path} mismatch: expected {expected}, got {actual}"]

    if expected != actual:
        return [f"{path} mismatch: expected {expected!r}, got {actual!r}"]
    return []


def verify_metrics_snapshot(
    expected_path: str | Path,
    metrics_dir: str | Path,
    season: str,
    tolerance: float = DEFAULT_REPRO_TOLERANCE,
) -> None:
    """Validate generated metrics against a versioned expected snapshot."""

    payload = json.loads(Path(expected_path).read_text(encoding="utf-8"))
    expected_models = payload["models"]
    metrics_root = Path(metrics_dir)

    failures: list[str] = []
    for model_name, expected_metrics in expected_models.items():
        actual_path = metrics_root / f"{model_name}_{season}_metrics.json"
        if not actual_path.exists():
            failures.append(f"Missing generated metrics file: {actual_path}")
            continue

        actual_metrics = json.loads(actual_path.read_text(encoding="utf-8"))
        failures.extend(
            collect_metric_mismatches(
                expected_metrics,
                actual_metrics,
                tolerance=tolerance,
                path=model_name,
            )
        )

    if failures:
        raise AssertionError("\n".join(failures))


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser for reproducibility verification."""

    parser = argparse.ArgumentParser(
        description=(
            "Verify generated metrics against a frozen reproducibility snapshot."
        )
    )
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--metrics-dir", type=Path, required=True)
    parser.add_argument("--season", required=True)
    parser.add_argument("--tolerance", type=float, default=DEFAULT_REPRO_TOLERANCE)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional manifest of reproducibility files to verify.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Project root used to resolve manifest file paths.",
    )
    return parser


def main() -> None:
    """Run the reproducibility verification command line entry point."""

    args = build_parser().parse_args()
    if args.manifest is not None:
        verify_artifact_manifest(args.manifest, project_root=args.project_root)
    verify_metrics_snapshot(
        expected_path=args.expected,
        metrics_dir=args.metrics_dir,
        season=args.season,
        tolerance=args.tolerance,
    )
    print("Reproducibility metrics match the frozen snapshot.")


if __name__ == "__main__":
    main()
