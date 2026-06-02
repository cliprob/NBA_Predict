# Data Reproduction Notes for 2025-26

This note documents the generated 2025-26 NBA prediction artifacts currently
stored under `outputs/metrics/` and `outputs/predictions/`.

## Data Source and Fetch Date

- Source: `nba_api` 1.11.4, endpoint
  `nba_api.stats.endpoints.leaguegamelog.LeagueGameLog`.
- Upstream service: NBA.com Stats API at `stats.nba.com`.
- Endpoint mode: team game logs (`player_or_team_abbreviation="T"`).
- Season type: `Regular Season`.
- Fetch date: 2026-05-23.
- Downloaded season range: `2012-13` through `2025-26`
  (`--season-start 2013 --season-end 2026`).

The live NBA API request is intentionally separate from the deterministic
offline reproduction path in `data/reproducibility/`, because NBA.com responses
can change or become unavailable. The offline path is guarded by
`data/reproducibility/MANIFEST.json`, which records shape metadata for the
committed deterministic artifacts.

## Regeneration Commands

From a fresh checkout:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pip install -e . --no-deps
```

Regenerate the raw NBA.com export:

```bash
.venv/Scripts/nba-predict download-data \
  --season-start 2013 \
  --season-end 2026 \
  --output data/raw/2012_2026_Data.csv
```

Regenerate the processed design matrix:

```bash
.venv/Scripts/nba-predict prepare-data \
  --raw data/raw/2012_2026_Data.csv \
  --output data/processed/design_matrix_2012_2026.csv
```

Regenerate 2025-26 metrics and predictions:

```bash
.venv/Scripts/nba-predict run-baseline \
  --season 2025-26 \
  --design-matrix data/processed/design_matrix_2012_2026.csv \
  --cv-folds 3
```

On Unix-like shells, replace `.venv/Scripts/...` with `.venv/bin/...`.

## Generated Files

Raw and processed data:

- `data/raw/2012_2026_Data.csv`: 33798 normalized team-game rows.
- `data/processed/design_matrix_2012_2026.csv`: 16689 home-game rows.

2025-26 model artifacts:

- `outputs/metrics/logistic_2025-26_metrics.json`
- `outputs/metrics/inference-logistic_2025-26_metrics.json`
- `outputs/metrics/ridge_2025-26_metrics.json`
- `outputs/metrics/lasso_2025-26_metrics.json`
- `outputs/predictions/logistic_2025-26_predictions.csv`
- `outputs/predictions/inference-logistic_2025-26_predictions.csv`
- `outputs/predictions/ridge_2025-26_predictions.csv`
- `outputs/predictions/lasso_2025-26_predictions.csv`

Each prediction CSV has 1225 rows for `2025-26`.

## Raw Schema

`data/raw/2012_2026_Data.csv` is the normalized output of NBA.com
`LeagueGameLog`:

| Column | Meaning |
| --- | --- |
| `slugSeason` | NBA season slug, for example `2025-26`. |
| `dateGame` | Game date as `YYYY-MM-DD`. |
| `idGame` | NBA game identifier. |
| `nameTeam` | Team name. |
| `isB2BSecond` | Whether this team is playing one calendar day after its previous game. |
| `locationGame` | `H` for home, `A` for away, inferred from `MATCHUP`. |
| `slugMatchup` | NBA matchup text from the source API. |
| `outcomeGame` | `W` or `L`. |
| `blk`, `tov`, `pf`, `pts`, `stl`, `treb`, `oreb`, `dreb`, `fga`, `fgm`, `ftm`, `fta` | Team box-score statistics from NBA.com. |

## Processed Schema and Preprocessing Assumptions

`data/processed/design_matrix_2012_2026.csv` has one row per game from the home
team perspective:

| Column | Meaning |
| --- | --- |
| `slugSeason` | NBA season slug. |
| `dateGame` | Game date as `YYYY-MM-DD`. |
| `outcomeGame` | Binary target: `1` if the home team won, `0` otherwise. |
| `isB2BSecond` | Home minus away back-to-back flag. |
| `avg_treb`, `avg_stl`, `avg_blk`, `avg_tov` | Home minus away 10-game rolling averages of possession-scaled stats. |
| `avg_orate`, `avg_drate` | Home minus away 10-game rolling offensive and defensive ratings. |
| `avg_pl_min` | Home minus away 10-game rolling possession-scaled plus/minus. |
| `avg_true_s` | Home minus away 10-game rolling true shooting. |
| `avg_win_perc` | Home minus away 10-game rolling win percentage. |

Preprocessing assumptions implemented in `src/nba_predict/data.py`:

- Game logs are grouped by `idGame` and `nameTeam`.
- Possessions, offensive rating, defensive rating, true shooting, and
  possession-scaled box-score rates are recomputed from the normalized raw
  stats.
- Rolling form uses a 10-game window per team.
- The first 310 team-game rows are dropped to match the translated legacy
  preprocessing behavior.
- Final rows are home-team features minus away-team features.
- Rows with missing rolling/opponent values are dropped.

## 2025-26 Results

| Model | Accuracy | Precision | Recall | Confusion matrix `[[TN, FP], [FN, TP]]` |
| --- | ---: | ---: | ---: | --- |
| `logistic` | 0.7673 | 0.7729 | 0.8218 | `[[382, 164], [121, 558]]` |
| `inference-logistic` | 0.7282 | 0.7357 | 0.7953 | `[[352, 194], [139, 540]]` |
| `ridge` | 0.7649 | 0.7712 | 0.8189 | `[[381, 165], [123, 556]]` |
| `lasso` | 0.7673 | 0.7713 | 0.8247 | `[[380, 166], [119, 560]]` |

## Notes for Robert: Docker and Report Integration

The generated CSV/JSON files are ignored by Git via `.gitignore`. Docker and
the final report should therefore either regenerate them during the build/run
workflow or copy them in as external artifacts.

Recommended Docker path for reproducibility:

1. Install `requirements.txt`.
2. Install the package with `python -m pip install -e . --no-deps`.
3. Run the three regeneration commands above inside the container.
4. Make `data/raw/`, `data/processed/`, `outputs/metrics/`, and
   `outputs/predictions/` available to the report process.

Recommended report inputs:

- Read headline metrics from `outputs/metrics/*_2025-26_metrics.json`.
- Read prediction-level tables from
  `outputs/predictions/*_2025-26_predictions.csv`.
- Cite this document for data source, fetch date, preprocessing assumptions,
  and exact regeneration commands.
- If the report must be fully offline, bundle `data/raw/2012_2026_Data.csv`,
  `data/processed/design_matrix_2012_2026.csv`, `outputs/metrics/`, and
  `outputs/predictions/` into the Docker image or mount them into the same
  paths at runtime.
