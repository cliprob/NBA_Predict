# NBA_Predict

[![CI](https://github.com/cliprob/NBA_Predict/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cliprob/NBA_Predict/actions/workflows/ci.yml)
![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-reproducible_runtime-2496ED?logo=docker&logoColor=white)
![Ruff](https://img.shields.io/badge/lint-Ruff-D7FF64?logo=ruff&logoColor=261230)
![Pytest](https://img.shields.io/badge/tests-Pytest-0A9EDC?logo=pytest&logoColor=white)

Reproducible Python research pipeline for evaluating baseline models that
predict NBA regular-season game outcomes.

## Portfolio Highlights

- **Reproducible Docker runtime:** a digest-pinned Python 3.11 base image,
  locked Python dependencies, GNU Make, and Quarto define the canonical
  environment.
- **Deterministic research workflow:** `make reproduce` runs against a frozen
  snapshot, validates its manifest, and compares regenerated metrics with
  versioned expectations.
- **Maintainable Python package and CLI:** the active implementation uses a
  `src/` layout, `pyproject.toml`, testable modules, and the `nba-predict`
  command-line entry point.
- **Cross-platform CI:** GitHub Actions runs syntax, Pytest, Ruff, and Sphinx
  checks on Linux, macOS, and Windows, then verifies reproduction and report
  rendering in Docker.
- **Visible Git collaboration:** issues, task branches, pull requests, a
  milestone, a project board, and [`CONTRIBUTING.md`](CONTRIBUTING.md) document
  how this course team worked together.
- **Generated documentation and report:** Sphinx builds the package reference,
  while Quarto turns regenerated metrics into the final research report.

## Quick Reproduction

From a clean checkout with Docker available:

```bash
docker build -t nba-predict:local .
docker run --rm nba-predict:local make reproduce
```

The equivalent Compose command is:

```bash
docker compose run --rm nba-predict make reproduce
```

## Reviewer Guide

For a reviewer-oriented explanation of the Git, Docker, CI, and
reproducibility design, see [`SHOWCASE.md`](SHOWCASE.md).

This repository is a course-project fork of
[`Ttantivi/NBA_Predict`](https://github.com/Ttantivi/NBA_Predict). The original
R Markdown workflow is preserved in [`legacy/`](legacy/) for traceability. The
active project is implemented as an installable Python package under
[`src/nba_predict`](src/nba_predict).

The canonical runtime is Python 3.11. For cross-platform reproduction, use the
Docker workflow below; it avoids relying on a collaborator's local Python,
operating system, or Make installation.

The repository includes a `.python-version` file for local version managers,
but Docker remains the canonical environment for final reproduction checks.

## Current Execution Path

The active pipeline is not run from the legacy R Markdown files. Use the Python
package and CLI:

```bash
python -m pip install -e ".[dev,data]"

nba-predict download-data \
  --season-start 2013 \
  --season-end 2023 \
  --output data/raw/2012_2023_Data.csv

nba-predict prepare-data \
  --raw data/raw/2012_2023_Data.csv \
  --output data/processed/design_matrix.csv

nba-predict run-baseline --season 2022-23 --cv-folds 3
```

This generates:

```text
data/raw/2012_2023_Data.csv
data/processed/design_matrix.csv
outputs/metrics/*.json
outputs/predictions/*.csv
```

Generated data and outputs are ignored by Git. They should be reproduced from
the pipeline, not committed to the repository.

## Project Layout

```text
src/nba_predict/
  config.py      project paths and default settings
  download.py    NBA Stats API downloader using nba_api
  data.py        raw game log preprocessing and design matrix generation
  modeling.py    logistic, ridge, and lasso model classes
  pipeline.py    high-level data and evaluation pipeline
  cli.py         command line interface

notebooks/
  demo_pipeline.ipynb

docs/
  Sphinx source files for package API documentation

data/
  raw/           generated raw game log CSV files
  processed/     generated design matrix CSV files

outputs/
  metrics/       generated model metrics
  predictions/   generated prediction CSV files
  figures/       generated plots
  models/        generated model artifacts

legacy/
  original upstream R Markdown workflow, PDF, and images
```

## Course Requirement Mapping

| Requirement area | What this repository does | Status |
| --- | --- | --- |
| Version control | Work is organized through GitHub issues, a public GitHub Project, pull requests, and the milestone [`Final reproducible project`](https://github.com/AntonioZhouPL/NBA_Predict/milestone/1). Collaboration rules are documented in [`CONTRIBUTING.md`](CONTRIBUTING.md). | Done |
| Branches and PRs | Completed changes were merged through PRs: [#11](https://github.com/AntonioZhouPL/NBA_Predict/pull/11), [#12](https://github.com/AntonioZhouPL/NBA_Predict/pull/12), [#13](https://github.com/AntonioZhouPL/NBA_Predict/pull/13), [#14](https://github.com/AntonioZhouPL/NBA_Predict/pull/14). | Done |
| Python package structure | Core code lives in [`src/nba_predict`](src/nba_predict) with `__init__.py`, package metadata in [`pyproject.toml`](pyproject.toml), and a CLI entry point `nba-predict`. | Done |
| Python classes | The refactor uses classes including `NBAStatsDownloader`, `NBADataPreprocessor`, `LogisticGamePredictor`, `RollingSeasonEvaluator`, and `NBAPredictionPipeline`. | Done |
| Core code outside notebooks | The production path is implemented in Python scripts under `src/nba_predict`; the notebook is only a demonstration. | Done |
| Docstrings | Public classes and methods in the Python package include docstrings. | Done |
| Linting settings | Ruff configuration is stored in [`pyproject.toml`](pyproject.toml), pre-commit hooks are configured in [`.pre-commit-config.yaml`](.pre-commit-config.yaml), and both are covered by the pinned development dependencies. | Done |
| Tests | Pytest coverage is stored under [`tests/`](tests/) and is run by GitHub Actions. | Done |
| Sphinx documentation | Sphinx source files live in [`docs/`](docs/) and HTML documentation is generated with `make docs`. | Done |
| Demonstration notebook | [`notebooks/demo_pipeline.ipynb`](notebooks/demo_pipeline.ipynb) demonstrates the package workflow. | Done |
| Final report | The Quarto report is defined in [`report/report.qmd`](report/report.qmd) and generated with `make report`. | Done, owner: Robert |
| Reproducible data pipeline | Python data download and design matrix generation are implemented through `nba-predict download-data` and `nba-predict prepare-data`. Updated data work is tracked in issues [#1](https://github.com/AntonioZhouPL/NBA_Predict/issues/1) and [#2](https://github.com/AntonioZhouPL/NBA_Predict/issues/2). | Partially done |
| Fixed deterministic execution mode | `make reproduce` runs the frozen snapshot and verifies metrics against [`data/reproducibility/expected_metrics.json`](data/reproducibility/expected_metrics.json). | Done, owner: Franek |
| Docker environment | [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml), and DockerHub commands are documented below. | Done, owner: Robert |
| Automation | [`Makefile`](Makefile) automates install, checks, data, baseline, report, and Docker commands. | Done, owner: Franek |

## Setup

Recommended local setup:

```bash
python -m pip install -e ".[dev,data]"
```

Or use the project automation targets:

```bash
make install-dev
make check
```

## Reproduce on Any Machine

The Docker image is the preferred way to reproduce the project on Windows,
macOS, and Linux. It uses a pinned Python 3.11 slim-bookworm base image, pinned
Python dependencies, GNU Make, and Quarto CLI 1.9.38.

Build locally from a clean checkout:

```bash
docker build -t airmazurczak/nba-predict:latest .
docker run --rm airmazurczak/nba-predict:latest make reproduce
```

After the image has been published to DockerHub, a reviewer can pull it instead
of building it:

```bash
docker pull airmazurczak/nba-predict:latest
docker run --rm airmazurczak/nba-predict:latest make reproduce
```

Generate the Quarto report while writing outputs back to the checked-out
repository.

macOS/Linux shells:

```bash
docker run --rm -v "$(pwd)":/app airmazurczak/nba-predict:latest make report
```

Open the rendered report on macOS:

```bash
open ./report/_site/report/report.html
```

Open the rendered report on Linux:

```bash
xdg-open ./report/_site/report/report.html
```

Windows PowerShell:

```powershell
docker run --rm -v ${PWD}:/app airmazurczak/nba-predict:latest make report
start .\report\_site\report\report.html
```

Docker Compose provides the same runtime configuration without mounting the
local working tree:

```bash
docker compose run --rm nba-predict make reproduce
docker compose run --rm nba-predict make report
```

For development, use the profiled Compose service that mounts the repository
into the container:

```bash
docker compose --profile dev run --rm nba-predict-dev make reproduce
```

Publish the multi-platform DockerHub image after logging in:

```bash
docker login
docker buildx build --platform linux/amd64,linux/arm64 \
  -t airmazurczak/nba-predict:latest \
  --push .
```

Local `make` usage is optional. On Windows, use Git Bash, WSL, MSYS2, or the
Docker commands above. Inside the Docker image, `make` is already installed.

For the pinned reproducibility environment:

```bash
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
```

For tools that expect a traditional requirements file, install the same runtime,
data, test, and lint dependencies with:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

If you only need the package without downloading data:

```bash
python -m pip install -e ".[dev]"
```

Check code style:

```bash
python -m ruff check src
make lint
```

Run the automated tests:

```bash
python -m pytest
make test
```

Check Python syntax:

```bash
python -m compileall src
```

Run the standard local verification bundle:

```bash
make check
```

Build the Sphinx HTML documentation:

```bash
make docs
```

On Windows PowerShell, build the documentation through Docker if local `make`
is not installed:

```powershell
docker run --rm -v ${PWD}:/app airmazurczak/nba-predict:latest make docs
```

The generated documentation is written to `docs/_build/html/index.html`.

Open the generated documentation on macOS:

```bash
open ./docs/_build/html/index.html
```

Open the generated documentation on Linux:

```bash
xdg-open ./docs/_build/html/index.html
```

Open the generated documentation on Windows:

```powershell
start .\docs\_build\html\index.html
```

Install and run pre-commit hooks locally after installing the development
environment. These hooks are local Git hooks; pulling the Docker image does not
install them on your machine. Docker is the canonical reproduction environment,
while pre-commit is optional local developer hygiene before creating commits.

```bash
python -m pre_commit install
python -m pre_commit run --all-files
```

## Data Reproduction

The upstream repository did not commit the generated CSV files. It generated
data from R using `nbastatR::game_logs()`. This fork replaces that step with a
Python downloader based on `nba_api`.

The 2025-26 data refresh, generated artifacts, schema notes, preprocessing
assumptions, and Docker/report handoff notes are documented in
[`DATA_REPRODUCTION_2025_26.md`](DATA_REPRODUCTION_2025_26.md).

Download raw team game logs:

```bash
nba-predict download-data \
  --season-start 2013 \
  --season-end 2023 \
  --output data/raw/2012_2023_Data.csv
```

Build the model design matrix:

```bash
nba-predict prepare-data \
  --raw data/raw/2012_2023_Data.csv \
  --output data/processed/design_matrix.csv
```

The design matrix represents home-team minus away-team rolling performance
features, following the original project idea.

## Model Reproduction

Evaluate one model:

```bash
nba-predict evaluate --model logistic --season 2022-23 --cv-folds 3
```

Run all translated baseline models:

```bash
nba-predict run-baseline --season 2022-23 --cv-folds 3
make baseline SEASON=2022-23 CV_FOLDS=3
```

Run the deterministic offline reproduction check from the frozen snapshot:

```bash
nba-predict run-baseline \
  --season 2022-23 \
  --design-matrix data/reproducibility/design_matrix_snapshot.csv \
  --cv-folds 3

make reproduce
```

Generate the final Quarto report:

```bash
make report
```

Open the rendered report on macOS:

```bash
open ./report/_site/report/report.html
```

Open the rendered report on Linux:

```bash
xdg-open ./report/_site/report/report.html
```

Open the rendered report on Windows:

```powershell
start .\report\_site\report\report.html
```

Available translated baseline models:

- `logistic`: regular logistic regression with the full feature set.
- `inference-logistic`: regular logistic regression using the inference-focused
  feature set.
- `ridge`: cross-validated ridge logistic regression.
- `lasso`: cross-validated lasso logistic regression.

The original R Markdown code used 10-fold cross-validation for ridge/lasso.
That setting is still available with `--cv-folds 10`, but the default example
uses `--cv-folds 3` so rolling season evaluation remains practical during
reproducibility checks.

## Verified Baseline Results

The current Python pipeline was verified on the 2022-23 season after downloading
2012-13 through 2022-23 team game logs.

| Model | Accuracy | Precision | Recall |
| --- | ---: | ---: | ---: |
| `logistic` | 0.7114 | 0.7436 | 0.7675 |
| `inference-logistic` | 0.6862 | 0.7113 | 0.7731 |
| `ridge` | 0.7098 | 0.7409 | 0.7689 |
| `lasso` | 0.7098 | 0.7415 | 0.7675 |

These metrics are generated under `outputs/metrics/` when the baseline command
is run.

## Deterministic Reproduction

The live `download-data` step depends on `nba_api`, so it is not treated as the
deterministic execution path. The fixed reproducibility path for this project is:

1. install the pinned dependencies from [`requirements-lock.txt`](requirements-lock.txt);
2. verify artifact presence and CSV shape in
   [`data/reproducibility/MANIFEST.json`](data/reproducibility/MANIFEST.json);
3. run the baseline models against the frozen snapshot
   [`data/reproducibility/design_matrix_snapshot.csv`](data/reproducibility/design_matrix_snapshot.csv);
4. verify the generated metrics against
   [`data/reproducibility/expected_metrics.json`](data/reproducibility/expected_metrics.json)
   using `make reproduce`.

This keeps the course-project reproduction check stable even if the upstream
NBA API changes over time.

## Demonstration Notebook

[`notebooks/demo_pipeline.ipynb`](notebooks/demo_pipeline.ipynb) shows how to:

- import the Python package;
- download or reuse raw data;
- build the design matrix;
- evaluate a baseline model;
- inspect generated metrics and predictions.

The notebook is a demonstration artifact. The active pipeline remains the Python
package and CLI.

## Continuous Integration

GitHub Actions runs syntax checks, Pytest, and Ruff on Python 3.11 across Linux,
macOS, and Windows. A separate Docker job builds the project image and runs
`make reproduce` inside the container.

## AI Usage

This project used AI assistance for planning, code editing, and documentation.
The scope and model details are documented in [`AI_USAGE.md`](AI_USAGE.md).

## Project Management

- GitHub Project board:
  <https://github.com/users/AntonioZhouPL/projects/1>
- Milestone:
  <https://github.com/AntonioZhouPL/NBA_Predict/milestone/1>
- Contribution workflow:
  [`CONTRIBUTING.md`](CONTRIBUTING.md)

Current ownership:

| Owner | Issues |
| --- | --- |
| Zhou | [#3](https://github.com/AntonioZhouPL/NBA_Predict/issues/3), [#4](https://github.com/AntonioZhouPL/NBA_Predict/issues/4), [#5](https://github.com/AntonioZhouPL/NBA_Predict/issues/5) |
| Wojtek | [#1](https://github.com/AntonioZhouPL/NBA_Predict/issues/1), [#2](https://github.com/AntonioZhouPL/NBA_Predict/issues/2) |
| Franek | [#6](https://github.com/AntonioZhouPL/NBA_Predict/issues/6), [#7](https://github.com/AntonioZhouPL/NBA_Predict/issues/7), [#8](https://github.com/AntonioZhouPL/NBA_Predict/issues/8) |
| Robert | [#9](https://github.com/AntonioZhouPL/NBA_Predict/issues/9), [#10](https://github.com/AntonioZhouPL/NBA_Predict/issues/10) |
| Unassigned | [#15](https://github.com/AntonioZhouPL/NBA_Predict/issues/15) |

## Legacy Materials

The original upstream files are archived in [`legacy/`](legacy/). They are kept
for traceability and method comparison, not as the current execution path.
