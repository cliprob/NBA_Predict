"""Command line interface for the NBA prediction pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nba_predict.config import DEFAULT_CV_FOLDS, DEFAULT_SEASON
from nba_predict.pipeline import NBAPredictionPipeline


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""

    parser = argparse.ArgumentParser(description="Run the NBA prediction pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    download = subparsers.add_parser(
        "download-data",
        help="Download raw NBA team game logs with nba_api.",
    )
    download.add_argument("--output", type=Path, default=None)
    download.add_argument("--season-start", type=int, default=2013)
    download.add_argument("--season-end", type=int, default=2023)

    prepare = subparsers.add_parser("prepare-data", help="Build the design matrix.")
    prepare.add_argument(
        "--raw",
        type=Path,
        default=None,
        help="Raw game log CSV path.",
    )
    prepare.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output design matrix CSV path.",
    )

    evaluate = subparsers.add_parser("evaluate", help="Evaluate one model.")
    evaluate.add_argument(
        "--model",
        choices=["logistic", "inference-logistic", "ridge", "lasso"],
        default="lasso",
    )
    evaluate.add_argument("--season", default=DEFAULT_SEASON)
    evaluate.add_argument("--design-matrix", type=Path, default=None)
    evaluate.add_argument("--cv-folds", type=int, default=DEFAULT_CV_FOLDS)

    baseline = subparsers.add_parser(
        "run-baseline",
        help="Evaluate all baseline models.",
    )
    baseline.add_argument("--season", default=DEFAULT_SEASON)
    baseline.add_argument("--cv-folds", type=int, default=DEFAULT_CV_FOLDS)
    return parser


def main() -> None:
    """Run the command line interface."""

    args = build_parser().parse_args()
    pipeline = NBAPredictionPipeline(
        cv_folds=getattr(args, "cv_folds", DEFAULT_CV_FOLDS),
    )

    if args.command == "download-data":
        raw_data = pipeline.download_data(
            output_path=args.output,
            season_start=args.season_start,
            season_end=args.season_end,
        )
        print(f"Saved raw game logs with {len(raw_data)} rows.")
    elif args.command == "prepare-data":
        design_matrix = pipeline.prepare_data(
            raw_path=args.raw,
            output_path=args.output,
        )
        print(f"Saved design matrix with {len(design_matrix)} rows.")
    elif args.command == "evaluate":
        result = pipeline.evaluate_model(
            args.model,
            season=args.season,
            design_matrix_path=args.design_matrix,
        )
        print(json.dumps(result, indent=2))
    elif args.command == "run-baseline":
        result = pipeline.run_baseline(season=args.season)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
