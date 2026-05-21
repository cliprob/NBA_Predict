# NBA_Predict

Reproducible Python pipeline for predicting NBA regular season game outcomes.

This repository is a course-project fork of
[`Ttantivi/NBA_Predict`](https://github.com/Ttantivi/NBA_Predict). The original
R Markdown workflow is preserved in [`legacy/`](legacy/) for traceability. The
active project is implemented as an installable Python package under
[`src/nba_predict`](src/nba_predict).

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
| Linting settings | Ruff configuration is stored in [`pyproject.toml`](pyproject.toml). Run `python -m ruff check src`. Pre-commit hook setup is tracked in issue [#15](https://github.com/AntonioZhouPL/NBA_Predict/issues/15). | Partially done |
| Tests | Testing is tracked in issue [#6](https://github.com/AntonioZhouPL/NBA_Predict/issues/6). | Pending, owner: Franek |
| Sphinx documentation | Sphinx HTML documentation is tracked in issue [#15](https://github.com/AntonioZhouPL/NBA_Predict/issues/15). | Pending |
| Demonstration notebook | [`notebooks/demo_pipeline.ipynb`](notebooks/demo_pipeline.ipynb) demonstrates the package workflow. | Done |
| Final report | Dynamic report using Quarto or Marimo is tracked in issue [#9](https://github.com/AntonioZhouPL/NBA_Predict/issues/9). | Pending, owner: Robert |
| Reproducible data pipeline | Python data download and design matrix generation are implemented through `nba-predict download-data` and `nba-predict prepare-data`. Updated data work is tracked in issues [#1](https://github.com/AntonioZhouPL/NBA_Predict/issues/1) and [#2](https://github.com/AntonioZhouPL/NBA_Predict/issues/2). | Partially done |
| Fixed deterministic execution mode | Tracked in issue [#8](https://github.com/AntonioZhouPL/NBA_Predict/issues/8). | Pending, owner: Franek |
| Docker environment | Docker reproducibility and DockerHub image are tracked in issue [#10](https://github.com/AntonioZhouPL/NBA_Predict/issues/10). | Pending, owner: Robert |
| Automation | Makefile automation is tracked in issue [#7](https://github.com/AntonioZhouPL/NBA_Predict/issues/7). | Pending, owner: Franek |

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

## Data Reproduction

The upstream repository did not commit the generated CSV files. It generated
data from R using `nbastatR::game_logs()`. This fork replaces that step with a
Python downloader based on `nba_api`.

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

## Demonstration Notebook

[`notebooks/demo_pipeline.ipynb`](notebooks/demo_pipeline.ipynb) shows how to:

- import the Python package;
- download or reuse raw data;
- build the design matrix;
- evaluate a baseline model;
- inspect generated metrics and predictions.

The notebook is a demonstration artifact. The active pipeline remains the Python
package and CLI.

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
