# Data Directory

The original repository generated data with R's `nbastatR::game_logs()`, but it
did not commit the resulting CSV files. This fork supports a Python replacement
using `nba_api`.

Install the data dependency:

```bash
python -m pip install -e ".[data]"
```

Download the same end-year range used by the original R Markdown file:

```bash
nba-predict download-data \
  --season-start 2013 \
  --season-end 2023 \
  --output data/raw/2012_2023_Data.csv
```

This writes the normalized raw game log export at:

```text
data/raw/2012_2023_Data.csv
```

The Python preprocessing pipeline writes the model design matrix to:

```text
data/processed/design_matrix.csv
```

Raw and processed CSV files are ignored by Git so the repository stays small.
For final presentation reproducibility, the team should either freeze the exact
CSV used in a release artifact or build the Docker image with the selected data
already available.
