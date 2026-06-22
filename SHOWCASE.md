# NBA_Predict: Reproducibility Showcase

## Project Overview

NBA_Predict is a collaborative course project that refactors an older NBA game
prediction workflow into a reproducible Python research pipeline. Its strongest
portfolio signal is not a claim of state-of-the-art prediction quality; it is
the engineering around repeatable experiments: an installable package, a CLI,
locked dependencies, a Docker runtime, deterministic checks, automated tests,
cross-platform CI, documentation, and a generated report.

The original R Markdown materials remain in [`legacy/`](legacy/) for
traceability. The maintained execution path lives in
[`src/nba_predict/`](src/nba_predict/).

This is a team project. The repository's documented ownership assigns Docker
and final-report work to Robert and links that work to issues
[#9](https://github.com/AntonioZhouPL/NBA_Predict/issues/9) and
[#10](https://github.com/AntonioZhouPL/NBA_Predict/issues/10); the package,
data, automation, and reproducibility design reflect contributions from the
broader course team.

Collaboration links deliberately point to the
[source team repository](https://github.com/AntonioZhouPL/NBA_Predict), where
the issues and pull requests were recorded. This portfolio copy preserves that
history rather than presenting the project as solo work.

## Architecture Map

```text
nba_api
   |
   v
raw team game logs
   |  NBAStatsDownloader
   v
home-vs-away design matrix
   |  NBADataPreprocessor
   v
rolling logistic / ridge / lasso evaluation
   |  LogisticGamePredictor + RollingSeasonEvaluator
   v
JSON metrics and prediction artifacts
   |  nba_predict.reporting + Quarto
   v
generated research report
```

The live download path is replaceable by the frozen design-matrix snapshot for
the deterministic check. This separation keeps external data acquisition from
making the core reproduction test unstable.

## Reproducibility Story

- **Docker image:** [`Dockerfile`](Dockerfile) pins the Python 3.11
  `slim-bookworm` base image by digest and installs GNU Make and Quarto 1.9.38.
- **Dependency lockfile:** [`requirements-lock.txt`](requirements-lock.txt)
  records the exact Python environment used by Docker and CI.
- **Frozen snapshot:**
  [`data/reproducibility/design_matrix_snapshot.csv`](data/reproducibility/design_matrix_snapshot.csv)
  provides a small offline input independent of the live NBA API.
- **Artifact manifest:**
  [`data/reproducibility/MANIFEST.json`](data/reproducibility/MANIFEST.json)
  records the expected snapshot shape, columns, runtime, and supporting files.
- **Expected metrics:**
  [`data/reproducibility/expected_metrics.json`](data/reproducibility/expected_metrics.json)
  stores the deterministic smoke-test result. Its perfect scores on the tiny
  fixture are test expectations, not evidence of general model performance.
- **Single reproduction target:** [`Makefile`](Makefile) makes
  `make reproduce` regenerate all baseline metrics and compare them at a
  tolerance of `1e-9`.

The same Docker job also renders the Quarto report in CI, connecting executable
results to the reviewer-facing research artifact.

## Collaboration Story

The repository records work through GitHub
[issues](https://github.com/AntonioZhouPL/NBA_Predict/issues), task branches,
and pull requests. [`CONTRIBUTING.md`](CONTRIBUTING.md) specifies branch naming,
focused commits, PR descriptions, issue-closing keywords, verification, and the
policy against committing generated research artifacts.

Completed collaboration is visible in PRs
[#11](https://github.com/AntonioZhouPL/NBA_Predict/pull/11),
[#12](https://github.com/AntonioZhouPL/NBA_Predict/pull/12),
[#13](https://github.com/AntonioZhouPL/NBA_Predict/pull/13), and
[#14](https://github.com/AntonioZhouPL/NBA_Predict/pull/14). Planning is linked
through the public
[project board](https://github.com/users/AntonioZhouPL/projects/1) and the
[`Final reproducible project` milestone](https://github.com/AntonioZhouPL/NBA_Predict/milestone/1).

## Evidence

| Feature | File/link | Why it matters |
| --- | --- | --- |
| Installable Python package and CLI | [`pyproject.toml`](pyproject.toml), [`src/nba_predict/`](src/nba_predict/) | Uses standard package metadata, a `src/` layout, modular classes, and the `nba-predict` console entry point. |
| Containerized runtime | [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml) | Defines a portable Python, Make, and Quarto environment instead of relying on a collaborator's machine. |
| Locked dependencies | [`requirements-lock.txt`](requirements-lock.txt) | Makes the package set used by Docker and CI explicit and reviewable. |
| Deterministic reproduction | [`Makefile`](Makefile), [`src/nba_predict/reproducibility.py`](src/nba_predict/reproducibility.py) | Provides one command that regenerates metrics and fails on snapshot drift. |
| Versioned research fixture | [`data/reproducibility/`](data/reproducibility/) | Keeps the offline check independent of NBA API availability while recording expected shape and results. |
| Cross-platform and Docker CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml), [workflow runs](https://github.com/cliprob/NBA_Predict/actions/workflows/ci.yml) | Checks Python 3.11 on three operating systems and runs reproduction plus report rendering in Docker. |
| Automated quality checks | [`tests/`](tests/), Ruff settings in [`pyproject.toml`](pyproject.toml) | Exercises the CLI, data, download, modeling, pipeline, and reproduction code while enforcing consistent lint rules. |
| Developer and API documentation | [`CONTRIBUTING.md`](CONTRIBUTING.md), [`docs/`](docs/) | Makes collaboration conventions and package usage discoverable; Sphinx builds the API reference. |
| Executable final report | [`report/report.qmd`](report/report.qmd), [`_quarto.yml`](_quarto.yml) | Generates the research narrative from pipeline outputs rather than treating the report as an unrelated static file. |
| Generated-artifact policy | [`.gitignore`](.gitignore), [`.dockerignore`](.dockerignore) | Keeps raw/processed data, metrics, predictions, figures, models, caches, and rendered sites out of version control and image context. |
| Traceable team workflow | [`CONTRIBUTING.md`](CONTRIBUTING.md), [PR #11](https://github.com/AntonioZhouPL/NBA_Predict/pull/11), [milestone](https://github.com/AntonioZhouPL/NBA_Predict/milestone/1) | Leaves reviewable evidence of issue, branch, commit, and PR practices in a collaborative project. |

## How to Verify in 3 Commands

```bash
git clone https://github.com/cliprob/NBA_Predict.git NBA_Predict
docker build -t nba-predict:showcase NBA_Predict
docker run --rm nba-predict:showcase make reproduce
```

The last command is offline with respect to `nba_api`; Docker still needs
network access while building the image if its base image, Python packages, or
Quarto installer are not already cached.

## Limitations and Assumptions

- Live data download depends on the third-party `nba_api` client and the
  availability, behavior, and schema of NBA Stats endpoints.
- Deterministic checks therefore use a deliberately small frozen snapshot. It
  verifies workflow stability, not predictive performance on the full NBA
  population.
- The expected `1.0` fixture metrics reflect six held-out rows in a smoke-test
  dataset and must not be interpreted as real-world model accuracy.
- The package intentionally targets Python 3.11; other Python versions are not
  part of the declared reproducibility contract.
- The baseline models omit important production forecasting inputs such as
  injuries, lineups, travel, roster changes, and market information.
- Generated raw data, processed data, metrics, predictions, figures, models,
  documentation builds, and rendered reports are ignored by Git and must be
  recreated locally.
- Docker is the canonical cross-platform path; local `make` usage assumes the
  required Python environment and system tools are installed.

## What I Would Discuss in an Interview

1. Why the live data-acquisition path and deterministic validation path are
   separated, and what each one proves.
2. How the digest-pinned base image, Python lockfile, frozen fixture, manifest,
   and metric tolerance cover different layers of reproducibility.
3. Why a `src/` package with a console entry point is easier to test and reuse
   than a notebook-only workflow.
4. How rolling evaluation avoids training on future games, and where leakage
   risks can still enter time-dependent sports features.
5. Why CI combines a three-OS Python matrix with a Linux Docker job instead of
   treating either check as sufficient by itself.
6. How Make provides a small, shared interface across package checks, research
   execution, documentation, Docker, and Quarto report generation.
7. How issues, scoped branches, pull requests, attribution, and ignored
   generated artifacts support reviewable collaboration in research code.
