"""High-level project pipeline for data preparation and model evaluation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from nba_predict.config import (
    DEFAULT_CV_FOLDS,
    DEFAULT_RANDOM_STATE,
    DEFAULT_SEASON,
    ProjectPaths,
)
from nba_predict.data import FEATURE_COLUMNS, NBADataPreprocessor
from nba_predict.download import NBAStatsDownloader
from nba_predict.modeling import LogisticGamePredictor, RollingSeasonEvaluator

INFERENCE_FEATURES = [
    "isB2BSecond",
    "avg_treb",
    "avg_stl",
    "avg_blk",
    "avg_tov",
    "avg_orate",
    "avg_drate",
    "avg_true_s",
]


@dataclass
class NBAPredictionPipeline:
    """Coordinate data preparation and model evaluation commands."""

    paths: ProjectPaths = field(default_factory=ProjectPaths)
    random_state: int = DEFAULT_RANDOM_STATE
    cv_folds: int = DEFAULT_CV_FOLDS

    def download_data(
        self,
        output_path: str | Path | None = None,
        season_start: int = 2013,
        season_end: int = 2023,
    ) -> pd.DataFrame:
        """Download normalized raw NBA game logs."""

        downloader = NBAStatsDownloader(
            season_start=season_start,
            season_end=season_end,
        )
        return downloader.save(output_path or self.paths.raw_data)

    def prepare_data(
        self,
        raw_path: str | Path | None = None,
        output_path: str | Path | None = None,
    ) -> pd.DataFrame:
        """Build and save the project design matrix."""

        self.paths.ensure_output_dirs()
        preprocessor = NBADataPreprocessor()
        return preprocessor.save_design_matrix(
            raw_path or self.paths.raw_data,
            output_path or self.paths.design_matrix,
        )

    def evaluate_model(
        self,
        model_name: str,
        season: str = DEFAULT_SEASON,
        design_matrix_path: str | Path | None = None,
    ) -> dict[str, object]:
        """Evaluate a configured model and save metrics plus predictions."""

        self.paths.ensure_output_dirs()
        model_name = model_name.lower()
        design_matrix = pd.read_csv(design_matrix_path or self.paths.design_matrix)
        evaluator = RollingSeasonEvaluator(season=season)

        result = evaluator.evaluate(
            design_matrix,
            predictor_factory=lambda: self._make_predictor(model_name),
        )

        metrics_path = self.paths.metrics_dir / f"{model_name}_{season}_metrics.json"
        predictions_path = (
            self.paths.predictions_dir / f"{model_name}_{season}_predictions.csv"
        )
        with metrics_path.open("w", encoding="utf-8") as file:
            json.dump(result.to_dict(), file, indent=2)
        result.predictions.to_csv(predictions_path, index=False)

        return {
            "model": model_name,
            "season": season,
            "metrics": result.to_dict(),
            "metrics_path": str(metrics_path),
            "predictions_path": str(predictions_path),
        }

    def run_baseline(self, season: str = DEFAULT_SEASON) -> list[dict[str, object]]:
        """Run the baseline set of translated logistic models."""

        return [
            self.evaluate_model(model_name, season=season)
            for model_name in ["logistic", "inference-logistic", "ridge", "lasso"]
        ]

    def _make_predictor(self, model_name: str) -> LogisticGamePredictor:
        """Create a predictor for a named model configuration."""

        if model_name == "logistic":
            return LogisticGamePredictor(
                penalty="none",
                features=FEATURE_COLUMNS.copy(),
                random_state=self.random_state,
            )
        if model_name == "inference-logistic":
            return LogisticGamePredictor(
                penalty="none",
                features=INFERENCE_FEATURES.copy(),
                random_state=self.random_state,
            )
        if model_name == "ridge":
            return LogisticGamePredictor(
                penalty="l2",
                features=FEATURE_COLUMNS.copy(),
                random_state=self.random_state,
                cv_folds=self.cv_folds,
            )
        if model_name == "lasso":
            return LogisticGamePredictor(
                penalty="l1",
                features=FEATURE_COLUMNS.copy(),
                random_state=self.random_state,
                cv_folds=self.cv_folds,
            )
        raise ValueError(
            "Unknown model. Choose one of: logistic, inference-logistic, ridge, lasso."
        )
