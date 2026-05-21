"""Data preprocessing translated from the original R Markdown workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

RAW_COLUMNS = [
    "slugSeason",
    "dateGame",
    "idGame",
    "nameTeam",
    "isB2BSecond",
    "locationGame",
    "slugMatchup",
    "outcomeGame",
    "blk",
    "tov",
    "pf",
    "pts",
    "stl",
    "treb",
    "oreb",
    "dreb",
    "fga",
    "fgm",
    "ftm",
    "fta",
]

SUM_COLUMNS = {
    "blk": "sum_blk",
    "tov": "sum_tov",
    "pf": "sum_pf",
    "pts": "sum_pts",
    "stl": "sum_stl",
    "treb": "sum_treb",
    "oreb": "sum_oreb",
    "dreb": "sum_dreb",
    "fga": "sum_fga",
    "fgm": "sum_fgm",
    "ftm": "sum_ftm",
    "fta": "sum_fta",
}

FEATURE_COLUMNS = [
    "isB2BSecond",
    "avg_treb",
    "avg_stl",
    "avg_blk",
    "avg_tov",
    "avg_orate",
    "avg_drate",
    "avg_pl_min",
    "avg_true_s",
    "avg_win_perc",
]


def _binary_flag(values: pd.Series) -> pd.Series:
    """Convert boolean-like values to 0/1 integers."""

    if pd.api.types.is_bool_dtype(values):
        return values.astype(int)
    return (
        values.astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes"})
        .astype(int)
    )


def _win_flag(values: pd.Series) -> pd.Series:
    """Convert win/loss labels to 0/1 integers."""

    if pd.api.types.is_numeric_dtype(values):
        return values.astype(int)
    return values.astype(str).str.strip().str.upper().eq("W").astype(int)


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide while returning NaN where the denominator is zero."""

    denominator = denominator.replace(0, np.nan)
    return numerator / denominator


def _opponent_values(values: pd.Series) -> np.ndarray:
    """Return the paired opponent value for each two-team game group."""

    if len(values) != 2:
        return np.full(len(values), np.nan)
    return values.iloc[::-1].to_numpy()


@dataclass
class NBADataPreprocessor:
    """Build the model design matrix from raw NBA game logs.

    The implementation follows the intent of ``NBA_data_preprocessing.Rmd``:
    player-level game logs are aggregated to team-game rows, rolling team form
    is calculated over the last 10 games, and each final row represents the
    home team's rolling metrics minus the away team's rolling metrics.
    """

    rolling_window: int = 10
    drop_initial_rows: int = 310
    feature_columns: list[str] = field(default_factory=lambda: FEATURE_COLUMNS.copy())

    def load_raw(self, path: str | Path) -> pd.DataFrame:
        """Load raw game logs from a CSV file."""

        raw_path = Path(path)
        if not raw_path.exists():
            raise FileNotFoundError(
                f"Raw data file not found: {raw_path}. "
                "Place the nbastatR game log CSV in data/raw/ first."
            )
        return pd.read_csv(raw_path)

    def build_team_summary(self, gamelogs: pd.DataFrame) -> pd.DataFrame:
        """Aggregate player game logs into team-level game summaries."""

        missing = sorted(set(RAW_COLUMNS) - set(gamelogs.columns))
        if missing:
            raise ValueError(f"Raw data is missing required columns: {missing}")

        selected = gamelogs[RAW_COLUMNS].copy()
        selected["dateGame"] = pd.to_datetime(selected["dateGame"])

        aggregations = {
            "slugSeason": "first",
            "dateGame": "first",
            "isB2BSecond": "first",
            "locationGame": "first",
            "slugMatchup": "first",
            "outcomeGame": "first",
        }
        aggregations.update({source: "sum" for source in SUM_COLUMNS})

        team_summary = (
            selected.groupby(["idGame", "nameTeam"], as_index=False)
            .agg(aggregations)
            .rename(columns=SUM_COLUMNS)
            .sort_values(["idGame", "locationGame"], ascending=[True, False])
            .reset_index(drop=True)
        )

        group = team_summary.groupby("idGame", sort=False)
        for column in [
            "sum_pts",
            "sum_oreb",
            "sum_dreb",
            "sum_fga",
            "sum_fgm",
            "sum_fta",
            "sum_tov",
        ]:
            team_summary[f"opp_{column}"] = group[column].transform(_opponent_values)

        team_summary["trueshooting"] = _safe_divide(
            team_summary["sum_pts"],
            2 * (team_summary["sum_fga"] + 0.44 * team_summary["sum_fta"]),
        )

        own_poss = (
            team_summary["sum_fga"]
            + 0.4 * team_summary["sum_fta"]
            - 1.07
            * _safe_divide(
                team_summary["sum_oreb"],
                team_summary["sum_oreb"] + team_summary["opp_sum_dreb"],
            )
            * (team_summary["sum_fga"] - team_summary["sum_fgm"])
            + team_summary["sum_tov"]
        )
        opp_poss = (
            team_summary["opp_sum_fga"]
            + 0.4 * team_summary["opp_sum_fta"]
            - 1.07
            * _safe_divide(
                team_summary["opp_sum_oreb"],
                team_summary["opp_sum_oreb"] + team_summary["sum_dreb"],
            )
            * (team_summary["opp_sum_fga"] - team_summary["opp_sum_fgm"])
            + team_summary["opp_sum_tov"]
        )
        team_summary["poss"] = 0.5 * (own_poss + opp_poss)
        team_summary["orate"] = (
            _safe_divide(team_summary["sum_pts"], team_summary["poss"]) * 100
        )
        team_summary["drate"] = (
            _safe_divide(team_summary["opp_sum_pts"], team_summary["poss"]) * 100
        )
        team_summary["isB2BSecond"] = _binary_flag(team_summary["isB2BSecond"])
        team_summary["outcomeGame"] = _win_flag(team_summary["outcomeGame"])

        for column in ["sum_blk", "sum_tov", "sum_stl", "sum_pts", "sum_treb"]:
            team_summary[column] = (
                _safe_divide(team_summary[column], team_summary["poss"]) * 100
            )

        group = team_summary.groupby("idGame", sort=False)
        team_summary["opp_scaled_pts"] = group["sum_pts"].transform(_opponent_values)
        team_summary["plu_min"] = (
            team_summary["sum_pts"] - team_summary["opp_scaled_pts"]
        )
        return team_summary

    def build_design_matrix(self, gamelogs: pd.DataFrame) -> pd.DataFrame:
        """Build the home-minus-away design matrix used for model training."""

        design_matrix = self.build_team_summary(gamelogs)
        design_matrix = design_matrix.drop(
            columns=[
                "slugMatchup",
                "sum_pf",
                "sum_oreb",
                "sum_dreb",
                "sum_fga",
                "sum_fgm",
                "sum_ftm",
                "sum_fta",
                *[
                    column
                    for column in design_matrix.columns
                    if column.startswith("opp_")
                ],
            ],
            errors="ignore",
        )

        design_matrix = design_matrix.sort_values(["nameTeam", "dateGame", "idGame"])
        grouped = design_matrix.groupby("nameTeam", sort=False)
        rolling = grouped.rolling(self.rolling_window, min_periods=self.rolling_window)

        rolling_specs = {
            "avg_pts": "sum_pts",
            "avg_treb": "sum_treb",
            "avg_stl": "sum_stl",
            "avg_blk": "sum_blk",
            "avg_tov": "sum_tov",
            "avg_orate": "orate",
            "avg_drate": "drate",
            "avg_pl_min": "plu_min",
            "avg_true_s": "trueshooting",
        }
        for output_column, source_column in rolling_specs.items():
            design_matrix[output_column] = (
                rolling[source_column].mean().reset_index(level=0, drop=True)
            )
        design_matrix["avg_win_perc"] = (
            rolling["outcomeGame"].sum().reset_index(level=0, drop=True)
            / self.rolling_window
        )

        design_matrix = design_matrix.sort_values(
            ["dateGame", "idGame", "locationGame"], ascending=[True, True, False]
        ).reset_index(drop=True)
        if self.drop_initial_rows:
            design_matrix = design_matrix.iloc[self.drop_initial_rows :].copy()

        design_matrix = design_matrix.drop(
            columns=[
                "avg_pts",
                "sum_blk",
                "sum_tov",
                "sum_stl",
                "sum_pts",
                "sum_treb",
                "trueshooting",
                "poss",
                "orate",
                "drate",
                "plu_min",
            ],
            errors="ignore",
        )

        group = design_matrix.groupby("idGame", sort=False)
        for column in self.feature_columns:
            opponent = group[column].transform(_opponent_values)
            design_matrix[column] = np.where(
                design_matrix["locationGame"].eq("H"),
                design_matrix[column] - opponent,
                opponent,
            )

        final = (
            design_matrix.loc[design_matrix["locationGame"].eq("H")]
            .dropna()
            .drop(columns=["idGame", "nameTeam", "locationGame"], errors="ignore")
            .reset_index(drop=True)
        )
        final["dateGame"] = pd.to_datetime(final["dateGame"]).dt.date.astype(str)
        return final[["slugSeason", "dateGame", "outcomeGame", *self.feature_columns]]

    def save_design_matrix(
        self,
        raw_path: str | Path,
        output_path: str | Path,
    ) -> pd.DataFrame:
        """Create and save the design matrix from a raw game log CSV."""

        gamelogs = self.load_raw(raw_path)
        design_matrix = self.build_design_matrix(gamelogs)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        design_matrix.to_csv(output, index=False)
        return design_matrix
