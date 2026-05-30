"""Generate markdown tables for the Quarto report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MODELS = ["logistic", "inference-logistic", "ridge", "lasso"]

DOCUMENTED_2022_23 = {
    "logistic": {"accuracy": 0.7114, "precision": 0.7436, "recall": 0.7675},
    "inference-logistic": {
        "accuracy": 0.6862,
        "precision": 0.7113,
        "recall": 0.7731,
    },
    "ridge": {"accuracy": 0.7098, "precision": 0.7409, "recall": 0.7689},
    "lasso": {"accuracy": 0.7098, "precision": 0.7415, "recall": 0.7675},
}

DOCUMENTED_2025_26 = {
    "logistic": {
        "accuracy": 0.7673,
        "precision": 0.7729,
        "recall": 0.8218,
        "confusion_matrix": [[382, 164], [121, 558]],
    },
    "inference-logistic": {
        "accuracy": 0.7282,
        "precision": 0.7357,
        "recall": 0.7953,
        "confusion_matrix": [[352, 194], [139, 540]],
    },
    "ridge": {
        "accuracy": 0.7649,
        "precision": 0.7712,
        "recall": 0.8189,
        "confusion_matrix": [[381, 165], [123, 556]],
    },
    "lasso": {
        "accuracy": 0.7673,
        "precision": 0.7713,
        "recall": 0.8247,
        "confusion_matrix": [[380, 166], [119, 560]],
    },
}


def _load_metrics(metrics_dir: Path, model: str, season: str) -> dict[str, Any] | None:
    path = metrics_dir / f"{model}_{season}_metrics.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _confusion_total(metrics: dict[str, Any]) -> int:
    matrix = metrics.get("confusion_matrix", [])
    return sum(sum(row) for row in matrix)


def _metrics_for_season(
    metrics_dir: Path,
    season: str,
    documented: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], str]:
    loaded = {
        model: metrics
        for model in MODELS
        if (metrics := _load_metrics(metrics_dir, model, season)) is not None
    }

    if season == "2022-23" and loaded:
        # The deterministic smoke-test snapshot has only six rows and should not
        # replace the full-season metrics in the final comparison.
        if all(_confusion_total(metrics) >= 100 for metrics in loaded.values()):
            return loaded, f"`outputs/metrics/*_{season}_metrics.json`"

    if season != "2022-23" and set(loaded) == set(MODELS):
        return loaded, f"`outputs/metrics/*_{season}_metrics.json`"

    return documented, "documented project results"


def _format_number(value: object) -> str:
    if isinstance(value, int | float):
        return f"{value:.4f}"
    return ""


def _comparison_rows(
    original: dict[str, dict[str, Any]],
    updated: dict[str, dict[str, Any]],
) -> list[str]:
    rows = [
        "| Model | 2022-23 accuracy | 2025-26 accuracy | Change | "
        "2025-26 precision | 2025-26 recall |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model in MODELS:
        original_accuracy = float(original[model]["accuracy"])
        updated_accuracy = float(updated[model]["accuracy"])
        rows.append(
            "| "
            f"`{model}` | "
            f"{original_accuracy:.4f} | "
            f"{updated_accuracy:.4f} | "
            f"{updated_accuracy - original_accuracy:+.4f} | "
            f"{_format_number(updated[model].get('precision'))} | "
            f"{_format_number(updated[model].get('recall'))} |"
        )
    return rows


def _confusion_rows(updated: dict[str, dict[str, Any]]) -> list[str]:
    rows = [
        "| Model | 2025-26 confusion matrix `[[TN, FP], [FN, TP]]` |",
        "| --- | --- |",
    ]
    for model in MODELS:
        matrix = updated[model].get("confusion_matrix", "")
        rows.append(f"| `{model}` | `{matrix}` |")
    return rows


def build_report_markdown(metrics_dir: Path) -> str:
    """Build the generated markdown section for the report."""

    original, original_source = _metrics_for_season(
        metrics_dir,
        "2022-23",
        DOCUMENTED_2022_23,
    )
    updated, updated_source = _metrics_for_season(
        metrics_dir,
        "2025-26",
        DOCUMENTED_2025_26,
    )

    lines = [
        "### Metric Sources",
        "",
        f"- Original 2022-23 metrics: {original_source}.",
        f"- Updated 2025-26 metrics: {updated_source}.",
        "- Data refresh notes: `DATA_REPRODUCTION_2025_26.md`.",
        "",
        "### Original vs New Data",
        "",
        *_comparison_rows(original, updated),
        "",
        "### 2025-26 Confusion Matrices",
        "",
        *_confusion_rows(updated),
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""

    parser = argparse.ArgumentParser(
        description="Generate markdown inputs for the Quarto report."
    )
    parser.add_argument("--metrics-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> None:
    """Generate the report markdown file."""

    args = build_parser().parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        build_report_markdown(args.metrics_dir),
        encoding="utf-8",
    )
    print(f"Wrote report summary to {args.output}")


if __name__ == "__main__":
    main()
