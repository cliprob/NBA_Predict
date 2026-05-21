"""Download NBA game logs with the Python ``nba_api`` package."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


def season_end_year_to_slug(end_year: int) -> str:
    """Convert an NBA season end year to a season slug.

    Examples:
        ``2023`` becomes ``"2022-23"``.
    """

    start_year = end_year - 1
    return f"{start_year}-{str(end_year)[-2:]}"


@dataclass
class NBAStatsDownloader:
    """Download team game logs and normalize them for the project pipeline."""

    season_start: int = 2013
    season_end: int = 2023
    season_type: str = "Regular Season"
    pause_seconds: float = 0.6
    timeout: int = 60

    def download(self) -> pd.DataFrame:
        """Download and combine all configured seasons."""

        try:
            from nba_api.stats.endpoints import leaguegamelog
        except ImportError as exc:
            raise ImportError(
                "Install the data extra before downloading NBA data: "
                'python -m pip install -e ".[data]"'
            ) from exc

        frames = []
        for end_year in range(self.season_start, self.season_end + 1):
            season = season_end_year_to_slug(end_year)
            endpoint = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star=self.season_type,
                player_or_team_abbreviation="T",
                direction="ASC",
                sorter="DATE",
                timeout=self.timeout,
            )
            season_frame = endpoint.get_data_frames()[0]
            frames.append(self._normalize_season(season_frame, season))
            time.sleep(self.pause_seconds)

        return pd.concat(frames, ignore_index=True)

    def save(self, output_path: str | Path) -> pd.DataFrame:
        """Download and save the normalized raw CSV."""

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        data = self.download()
        data.to_csv(output, index=False)
        return data

    def _normalize_season(self, data: pd.DataFrame, season: str) -> pd.DataFrame:
        """Map ``nba_api`` team game logs to the original raw CSV schema."""

        required = {
            "GAME_ID",
            "GAME_DATE",
            "TEAM_ID",
            "TEAM_NAME",
            "MATCHUP",
            "WL",
            "BLK",
            "TOV",
            "PF",
            "PTS",
            "STL",
            "REB",
            "OREB",
            "DREB",
            "FGA",
            "FGM",
            "FTM",
            "FTA",
        }
        missing = sorted(required - set(data.columns))
        if missing:
            raise ValueError(f"nba_api response is missing columns: {missing}")

        normalized = pd.DataFrame(
            {
                "slugSeason": season,
                "dateGame": pd.to_datetime(data["GAME_DATE"]).dt.date.astype(str),
                "idGame": data["GAME_ID"].astype(str),
                "idTeam": data["TEAM_ID"],
                "nameTeam": data["TEAM_NAME"],
                "locationGame": data["MATCHUP"].map(self._location_from_matchup),
                "slugMatchup": data["MATCHUP"],
                "outcomeGame": data["WL"],
                "blk": data["BLK"],
                "tov": data["TOV"],
                "pf": data["PF"],
                "pts": data["PTS"],
                "stl": data["STL"],
                "treb": data["REB"],
                "oreb": data["OREB"],
                "dreb": data["DREB"],
                "fga": data["FGA"],
                "fgm": data["FGM"],
                "ftm": data["FTM"],
                "fta": data["FTA"],
            }
        )
        normalized["isB2BSecond"] = self._back_to_back_flags(normalized)
        return normalized[
            [
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
        ]

    @staticmethod
    def _location_from_matchup(matchup: object) -> str:
        """Infer home/away from NBA matchup strings."""

        matchup_text = str(matchup)
        if "@" in matchup_text:
            return "A"
        if "vs." in matchup_text or "vs" in matchup_text:
            return "H"
        raise ValueError(f"Cannot infer location from matchup: {matchup_text!r}")

    @staticmethod
    def _back_to_back_flags(data: pd.DataFrame) -> pd.Series:
        """Flag team games played one calendar day after the previous game."""

        with_dates = data.copy()
        with_dates["dateGame"] = pd.to_datetime(with_dates["dateGame"])
        with_dates = with_dates.sort_values(["idTeam", "dateGame", "idGame"])
        previous_game_date = with_dates.groupby("idTeam")["dateGame"].shift(1)
        is_b2b = (with_dates["dateGame"] - previous_game_date).dt.days.eq(1)
        return is_b2b.reindex(data.index).fillna(False).astype(bool)

