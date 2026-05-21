"""Model classes and evaluation helpers for NBA game prediction."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from nba_predict.config import DEFAULT_CV_FOLDS, DEFAULT_RANDOM_STATE, DEFAULT_SEASON
from nba_predict.data import FEATURE_COLUMNS


@dataclass
class EvaluationResult:
    """Structured output from a prediction evaluation run."""

    accuracy: float
    precision: float
    recall: float
    confusion_matrix: list[list[int]]
    cumulative_errors: list[int]
    predictions: pd.DataFrame

    def to_dict(self) -> dict[str, object]:
        """Return JSON-serializable metrics."""

        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "confusion_matrix": self.confusion_matrix,
            "cumulative_errors": self.cumulative_errors,
        }


@dataclass
class SeasonSplitter:
    """Split a design matrix into pre-season training rows and season test rows."""

    season: str = DEFAULT_SEASON

    def split(self, design_matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Split by the first row matching the configured season."""

        matching_positions = np.flatnonzero(design_matrix["slugSeason"].eq(self.season))
        if len(matching_positions) == 0:
            raise ValueError(
                f"Season {self.season!r} was not found in the design matrix."
            )
        test_start = matching_positions[0]
        return (
            design_matrix.iloc[:test_start].copy(),
            design_matrix.iloc[test_start:].copy(),
        )


@dataclass
class LogisticGamePredictor:
    """Logistic regression predictor for NBA home-team win probabilities."""

    penalty: str = "none"
    features: list[str] = field(default_factory=lambda: FEATURE_COLUMNS.copy())
    threshold: float = 0.5
    random_state: int = DEFAULT_RANDOM_STATE
    cv_folds: int = DEFAULT_CV_FOLDS
    max_iter: int = 5000

    def __post_init__(self) -> None:
        """Initialize the underlying scikit-learn estimator."""

        if self.penalty == "none":
            self.estimator = LogisticRegression(
                penalty=None,
                solver="lbfgs",
                max_iter=self.max_iter,
                random_state=self.random_state,
            )
        elif self.penalty in {"l1", "l2"}:
            self.estimator = make_pipeline(
                StandardScaler(),
                LogisticRegressionCV(
                    Cs=10,
                    cv=self.cv_folds,
                    penalty=self.penalty,
                    solver="liblinear",
                    scoring="accuracy",
                    max_iter=self.max_iter,
                    random_state=self.random_state,
                ),
            )
        else:
            raise ValueError("penalty must be one of: 'none', 'l1', 'l2'.")

    def fit(self, data: pd.DataFrame) -> LogisticGamePredictor:
        """Fit the predictor on a design matrix."""

        self.estimator.fit(data[self.features], data["outcomeGame"].astype(int))
        return self

    def predict_proba(self, data: pd.DataFrame) -> np.ndarray:
        """Predict home-team win probabilities."""

        return self.estimator.predict_proba(data[self.features])[:, 1]

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict binary home-team outcomes using the configured threshold."""

        return (self.predict_proba(data) > self.threshold).astype(int)


class RollingSeasonEvaluator:
    """Evaluate a model by refitting it before each game day in a target season."""

    def __init__(self, season: str = DEFAULT_SEASON) -> None:
        self.season = season

    def evaluate(
        self,
        design_matrix: pd.DataFrame,
        predictor_factory: Callable[[], LogisticGamePredictor],
    ) -> EvaluationResult:
        """Run rolling game-day evaluation for a season."""

        data = design_matrix.copy()
        data["dateGame"] = pd.to_datetime(data["dateGame"])
        data = data.sort_values(["dateGame", "slugSeason"]).reset_index(drop=True)

        season_rows = data.loc[data["slugSeason"].eq(self.season)]
        game_days = season_rows["dateGame"].drop_duplicates().tolist()
        if not game_days:
            raise ValueError(
                f"Season {self.season!r} was not found in the design matrix."
            )

        prediction_frames: list[pd.DataFrame] = []
        daily_errors: list[int] = []
        for game_day in game_days:
            test_mask = data["dateGame"].eq(game_day) & data["slugSeason"].eq(
                self.season
            )
            first_test_index = data.index[test_mask][0]
            train_data = data.iloc[:first_test_index].copy()
            test_data = data.loc[test_mask].copy()

            predictor = predictor_factory().fit(train_data)
            probabilities = predictor.predict_proba(test_data)
            predictions = (probabilities > predictor.threshold).astype(int)
            actual = test_data["outcomeGame"].astype(int).to_numpy()

            daily_errors.append(int(np.sum(predictions != actual)))
            prediction_frames.append(
                pd.DataFrame(
                    {
                        "dateGame": test_data["dateGame"].dt.date.astype(str),
                        "slugSeason": test_data["slugSeason"],
                        "actual": actual,
                        "predicted": predictions,
                        "probability_home_win": probabilities,
                    }
                )
            )

        predictions_df = pd.concat(prediction_frames, ignore_index=True)
        matrix = confusion_matrix(
            predictions_df["actual"],
            predictions_df["predicted"],
            labels=[0, 1],
        )
        accuracy = float(np.trace(matrix) / matrix.sum())
        precision = float(
            precision_score(
                predictions_df["actual"],
                predictions_df["predicted"],
                zero_division=0,
            )
        )
        recall = float(
            recall_score(
                predictions_df["actual"],
                predictions_df["predicted"],
                zero_division=0,
            )
        )
        cumulative_errors = np.cumsum(daily_errors).astype(int).tolist()
        return EvaluationResult(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            confusion_matrix=matrix.astype(int).tolist(),
            cumulative_errors=cumulative_errors,
            predictions=predictions_df,
        )
