.PHONY: install-dev lint test check download-data prepare-data evaluate baseline reproduce clean

VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
NBA_PREDICT ?= $(VENV)/bin/nba-predict
SEASON ?= 2022-23
SEASON_START ?= 2013
SEASON_END ?= 2023
CV_FOLDS ?= 3
RAW ?= data/raw/2012_2023_Data.csv
DESIGN_MATRIX ?= data/processed/design_matrix.csv
MODEL ?= logistic

install-dev:
	test -d $(VENV) || python3 -m venv $(VENV)
	$(PYTHON) -m pip install -e ".[dev,data]"

lint:
	$(PYTHON) -m ruff check src tests

test:
	$(PYTHON) -m pytest

check:
	$(PYTHON) -m compileall src
	$(MAKE) test
	$(MAKE) lint

download-data:
	$(NBA_PREDICT) download-data \
		--season-start $(SEASON_START) \
		--season-end $(SEASON_END) \
		--output $(RAW)

prepare-data:
	$(NBA_PREDICT) prepare-data \
		--raw $(RAW) \
		--output $(DESIGN_MATRIX)

evaluate:
	$(NBA_PREDICT) evaluate \
		--model $(MODEL) \
		--season $(SEASON) \
		--design-matrix $(DESIGN_MATRIX) \
		--cv-folds $(CV_FOLDS)

baseline:
	$(NBA_PREDICT) run-baseline \
		--season $(SEASON) \
		--cv-folds $(CV_FOLDS)

reproduce:
	$(MAKE) baseline SEASON=$(SEASON) CV_FOLDS=$(CV_FOLDS)

clean:
	rm -rf .pytest_cache .ruff_cache build dist
	find src tests -type d -name "__pycache__" -prune -exec rm -rf {} +
