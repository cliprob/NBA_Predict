"""Project configuration and default filesystem paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEASON = "2022-23"
DEFAULT_RANDOM_STATE = 254
DEFAULT_CV_FOLDS = 3


@dataclass(frozen=True)
class ProjectPaths:
    """Container for project-relative paths used by the pipeline."""

    root: Path = PROJECT_ROOT
    raw_data: Path = PROJECT_ROOT / "data" / "raw" / "2012_2023_Data.csv"
    design_matrix: Path = PROJECT_ROOT / "data" / "processed" / "design_matrix.csv"
    metrics_dir: Path = PROJECT_ROOT / "outputs" / "metrics"
    predictions_dir: Path = PROJECT_ROOT / "outputs" / "predictions"
    figures_dir: Path = PROJECT_ROOT / "outputs" / "figures"
    models_dir: Path = PROJECT_ROOT / "outputs" / "models"

    def ensure_output_dirs(self) -> None:
        """Create output directories required by the pipeline."""

        for path in (
            self.metrics_dir,
            self.predictions_dir,
            self.figures_dir,
            self.models_dir,
            self.design_matrix.parent,
        ):
            path.mkdir(parents=True, exist_ok=True)
