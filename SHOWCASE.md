# NBA Predict — Reproducible NBA Prediction Pipeline

## Executive Summary

NBA Predict is a reproducible sports analytics pipeline for predicting NBA regular season game outcomes from historical team game data. This repository is Robert Mazurczak's portfolio mirror of a collaborative course project, with the original collaboration preserved at <https://github.com/AntonioZhouPL/NBA_Predict>. The project is presented as an engineering and reproducibility showcase: Dockerized execution, pinned dependencies, deterministic checks, CI, documentation, and report generation. It should be evaluated as a reproducible ML workflow rather than as a production betting system.

## What This Project Demonstrates

- Dockerized reproducibility
- Python package structure
- Makefile automation
- CI across operating systems
- Deterministic reproduction checks
- Collaborative Git workflow
- Reproducible sports analytics

## Architecture

The active implementation lives in [`src/nba_predict`](src/nba_predict). The pipeline follows this flow:

```text
raw data
  -> preprocessing / design matrix
  -> rolling model evaluation
  -> metrics and predictions
  -> Quarto report
```

The legacy R Markdown workflow is preserved in [`legacy/`](legacy/) for traceability, but the current execution path is the installable Python package and `nba-predict` CLI.

Key commands:

```bash
make check
make reproduce
make report
docker build -t cliprob/nba-predict:portfolio-check .
docker run --rm cliprob/nba-predict:portfolio-check make reproduce
```

## Reproducibility Design

Docker is used to make the runtime portable across Windows, macOS, and Linux. A reviewer can build the image and run the same Makefile targets without first matching the author's local Python version, shell, or system packages.

Dependency pinning matters because model results and report generation can change when packages move. The deterministic path installs dependencies from [`requirements-lock.txt`](requirements-lock.txt), then runs the package against a frozen design-matrix snapshot.

The frozen snapshot in [`data/reproducibility/design_matrix_snapshot.csv`](data/reproducibility/design_matrix_snapshot.csv) exists so `make reproduce` can verify known metrics without relying on live API calls. The expected metrics are stored in [`data/reproducibility/expected_metrics.json`](data/reproducibility/expected_metrics.json), and the artifact manifest is stored in [`data/reproducibility/MANIFEST.json`](data/reproducibility/MANIFEST.json).

Live data download through `nba_api` remains useful for refreshing the project, but it is not treated as the deterministic reproduction path because external APIs can change, fail, rate-limit, or return updated data.

## Engineering Evidence

| Capability | Where it appears | Why it matters |
| --- | --- | --- |
| Docker runtime | [`Dockerfile`](Dockerfile) | Defines a portable Python 3.11 + Quarto execution environment. |
| Compose workflow | [`docker-compose.yml`](docker-compose.yml) | Gives reviewers a short command for running the same containerized pipeline. |
| Makefile automation | [`Makefile`](Makefile) | Centralizes install, checks, docs, report, Docker, and reproducibility commands. |
| Python packaging | [`pyproject.toml`](pyproject.toml), [`src/nba_predict`](src/nba_predict) | Makes the workflow installable and exposes the `nba-predict` CLI. |
| Dependency lockfile | [`requirements-lock.txt`](requirements-lock.txt) | Pins the deterministic environment used by CI and Docker. |
| GitHub Actions CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Runs syntax checks, tests, linting, docs, and Docker reproduction. |
| Tests | [`tests/`](tests/) | Provides regression checks around package behavior and reproducibility helpers. |
| Sphinx docs | [`docs/`](docs/) | Documents package usage and API-oriented project information. |
| Quarto report | [`report/report.qmd`](report/report.qmd) | Produces a final reviewer-facing report from generated metrics. |
| Reproducibility snapshot | [`data/reproducibility/`](data/reproducibility/) | Keeps deterministic checks stable without committing generated raw/model outputs. |

## Collaboration and Attribution

This portfolio repository preserves the collaborative origin of the work instead of presenting it as a solo project. The original course repository is [`AntonioZhouPL/NBA_Predict`](https://github.com/AntonioZhouPL/NBA_Predict), and the contribution workflow is documented in [`CONTRIBUTING.md`](CONTRIBUTING.md).

The original project management evidence includes the [`Final reproducible project`](https://github.com/AntonioZhouPL/NBA_Predict/milestone/1) milestone, merged pull requests [#11](https://github.com/AntonioZhouPL/NBA_Predict/pull/11), [#12](https://github.com/AntonioZhouPL/NBA_Predict/pull/12), [#13](https://github.com/AntonioZhouPL/NBA_Predict/pull/13), and [#14](https://github.com/AntonioZhouPL/NBA_Predict/pull/14), plus Robert-owned issues [#9](https://github.com/AntonioZhouPL/NBA_Predict/issues/9) and [#10](https://github.com/AntonioZhouPL/NBA_Predict/issues/10). Those links are the evidence used for the portfolio narrative; the mirror does not invent additional contribution claims.

## Modeling Scope

The modeling layer is intentionally baseline-oriented. It includes logistic regression, inference-focused logistic regression, ridge, lasso, and rolling season evaluation. These models are useful for demonstrating a reproducible evaluation workflow and for comparing translated baseline approaches.

This repository does not claim to be a profitable betting model. It does not integrate betting market odds, closing-line-value validation, or bankroll allocation. The right framing is reproducible sports analytics and ML/research engineering.

## Limitations

- Baseline models only.
- No betting market odds integration.
- No closing-line-value validation.
- No bankroll or risk allocation layer.
- Live NBA API data can change, fail, or become temporarily unavailable.
- The current project is primarily an engineering and reproducibility showcase.

## Interview Talking Points

- How to make an ML workflow reproducible across machines using Docker, pinned dependencies, and Makefile targets.
- Why deterministic checks should use frozen inputs instead of live external APIs.
- How CI can verify syntax, tests, linting, documentation, and containerized reproduction.
- How the data pipeline separates download, preprocessing, modeling, metrics, and report generation.
- What changes when notebook/R-style exploratory work is converted into a maintainable Python package with a CLI.
- Why predictive accuracy and betting profitability are different claims.
- How to keep a portfolio mirror honest by preserving links to the original collaborative repository and contribution history.
