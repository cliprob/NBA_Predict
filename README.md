# NBA_Predict

Reproducible Python pipeline for predicting NBA regular season game outcomes.

This repository is a course-project fork of the original
[`Ttantivi/NBA_Predict`](https://github.com/Ttantivi/NBA_Predict) project. The
original R Markdown workflow is archived in [`legacy/`](legacy/). The active
pipeline is implemented as an installable Python package under
[`src/nba_predict`](src/nba_predict).

Collaborators should use the branch and pull request workflow described in
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Project Layout

```text
src/nba_predict/
  config.py      project paths and default settings
  download.py    NBA Stats API downloader using nba_api
  data.py        raw game log preprocessing and design matrix generation
  modeling.py    logistic, ridge, and lasso model classes
  pipeline.py    high-level data and evaluation pipeline
  cli.py         command line interface

data/
  raw/           generated raw game log CSV files
  processed/     generated design matrix CSV files

outputs/
  metrics/       generated model metrics
  predictions/   generated prediction CSV files
  figures/       generated plots
  models/        generated model artifacts

notebooks/
  demo_pipeline.ipynb

legacy/
  original upstream R Markdown workflow and images
```

## Setup

Install the package locally:

```bash
python -m pip install -e ".[dev]"
```

Install with the optional data downloader:

```bash
python -m pip install -e ".[dev,data]"
```

## Reproduce The Baseline Pipeline

Download the raw NBA team game logs using Python:

```bash
nba-predict download-data \
  --season-start 2013 \
  --season-end 2023 \
  --output data/raw/2012_2023_Data.csv
```

Generate the design matrix from the raw game log CSV:

```bash
nba-predict prepare-data \
  --raw data/raw/2012_2023_Data.csv \
  --output data/processed/design_matrix.csv
```

Evaluate one translated baseline model:

```bash
nba-predict evaluate --model lasso --season 2022-23 --cv-folds 3
```

Run all translated baseline models:

```bash
nba-predict run-baseline --season 2022-23 --cv-folds 3
```

The original R Markdown code used 10-fold cross-validation for ridge/lasso.
That setting is still available with `--cv-folds 10`, but the default is lower
so the rolling season evaluation remains practical during reproducibility checks.

## Models

The translated baseline models are:

- `logistic`: regular logistic regression with the full feature set.
- `inference-logistic`: regular logistic regression using the inference-focused
  feature set.
- `ridge`: cross-validated ridge logistic regression.
- `lasso`: cross-validated lasso logistic regression.

## Demonstration Notebook

A notebook demonstration of the package workflow is available at
[`notebooks/demo_pipeline.ipynb`](notebooks/demo_pipeline.ipynb).

The notebook shows how to:

- download or reuse raw data;
- build the design matrix;
- evaluate a baseline model;
- inspect generated metrics and predictions.

## Legacy Materials

The original upstream files have been moved to [`legacy/`](legacy/) to keep the
active project root focused on the reproducible Python pipeline. They are kept
for traceability and method comparison, not as the current execution path.
