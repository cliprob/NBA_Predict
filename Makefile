.PHONY: install-dev lint test check download-data prepare-data evaluate baseline data-2025-26 prepare-2025-26 baseline-2025-26 reproduce report docker-build docker-reproduce clean

VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
NBA_PREDICT ?= $(VENV)/bin/nba-predict
QUARTO ?= quarto
SEASON ?= 2022-23
SEASON_START ?= 2013
SEASON_END ?= 2023
CV_FOLDS ?= 3
RAW ?= data/raw/2012_2023_Data.csv
DESIGN_MATRIX ?= data/processed/design_matrix.csv
MODEL ?= logistic
REPRO_DESIGN_MATRIX ?= data/reproducibility/design_matrix_snapshot.csv
REPRO_EXPECTED ?= data/reproducibility/expected_metrics.json
REPRO_MANIFEST ?= data/reproducibility/MANIFEST.json
REPRO_REQUIREMENTS ?= requirements-lock.txt
REPRO_TOLERANCE ?= 1e-9
NEW_SEASON ?= 2025-26
NEW_SEASON_END ?= 2026
NEW_RAW ?= data/raw/2012_2026_Data.csv
NEW_DESIGN_MATRIX ?= data/processed/design_matrix_2012_2026.csv
DOCKER_IMAGE ?= airmazurczak/nba-predict:latest
REPORT_SUMMARY ?= report/generated/metrics_summary.md

install-dev:
	test -d $(VENV) || python3 -m venv $(VENV)
	$(PYTHON) -m pip install -r $(REPRO_REQUIREMENTS)
	$(PYTHON) -m pip install -e . --no-deps

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
		--design-matrix $(DESIGN_MATRIX) \
		--cv-folds $(CV_FOLDS)

data-2025-26:
	$(MAKE) download-data \
		SEASON_END=$(NEW_SEASON_END) \
		RAW=$(NEW_RAW)

prepare-2025-26:
	$(MAKE) prepare-data \
		RAW=$(NEW_RAW) \
		DESIGN_MATRIX=$(NEW_DESIGN_MATRIX)

baseline-2025-26:
	$(MAKE) baseline \
		SEASON=$(NEW_SEASON) \
		DESIGN_MATRIX=$(NEW_DESIGN_MATRIX)

reproduce:
	$(MAKE) baseline \
		SEASON=$(SEASON) \
		CV_FOLDS=$(CV_FOLDS) \
		DESIGN_MATRIX=$(REPRO_DESIGN_MATRIX)
	$(PYTHON) -m nba_predict.reproducibility \
		--manifest $(REPRO_MANIFEST) \
		--expected $(REPRO_EXPECTED) \
		--metrics-dir outputs/metrics \
		--season $(SEASON) \
		--tolerance $(REPRO_TOLERANCE)

report:
	$(PYTHON) -m nba_predict.reporting \
		--metrics-dir outputs/metrics \
		--output $(REPORT_SUMMARY)
	$(QUARTO) render report/report.qmd

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-reproduce:
	docker run --rm $(DOCKER_IMAGE) make reproduce

clean:
	rm -rf .pytest_cache .ruff_cache build dist
	find src tests -type d -name "__pycache__" -prune -exec rm -rf {} +
