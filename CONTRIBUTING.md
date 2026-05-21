# Contributing Workflow

This repository is maintained as a reproducible research course project. Use
issues, branches, commits, and pull requests so each collaborator's work remains
visible on GitHub.

## Branches

Create a branch for each task:

```bash
git checkout main
git pull origin main
git checkout -b your-name-short-task
```

Use descriptive branch names, for example:

```text
zhou-python-package-refactor
franek-makefile-pipeline
robert-docker-report
wojtek-updated-data
```

## Commits

Keep commits focused on one task. Commit messages should describe the project
change, not only the file edited:

```bash
git add path/to/files
git commit -m "Add reproducible data preparation command"
```

Do not commit raw data files, processed data files, model outputs, or generated
figures. These files should be produced through the documented pipeline commands.

## Pull Requests

Push your branch and open a pull request against `main`:

```bash
git push -u origin your-name-short-task
```

In the pull request description, include:

- the issue number it addresses;
- a short summary of the change;
- commands you ran to verify it;
- any reproducibility assumptions or limitations.

Use closing keywords such as `Closes #7` when the PR fully completes an issue.

## Local Checks

Before opening a pull request, run the checks relevant to your change:

```bash
make check
```

For data and model changes, verify the pipeline from raw data through metrics:

```bash
nba-predict download-data \
  --season-start 2013 \
  --season-end 2023 \
  --output data/raw/2012_2023_Data.csv

nba-predict prepare-data \
  --raw data/raw/2012_2023_Data.csv \
  --output data/processed/design_matrix.csv

nba-predict run-baseline --season 2022-23 --cv-folds 3
```
