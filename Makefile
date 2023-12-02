VENV     = .venv
PYTHON   = $(VENV)/bin/python
COVERAGE = $(VENV)/bin/coverage

.PHONY: install test clean

install:  requirements-dev.txt requirements.txt
	test -d $(VENV) || python3.11 -m virtualenv $(VENV)
	. $(VENV)/bin/activate
	$(PYTHON) -m pip install -Ur requirements-dev.txt
	$(PYTHON) -m pip install -e .

unittest:
	$(COVERAGE) run -m pytest -v tests/unit
	$(COVERAGE) report
	rm .coverage

systest:
	$(COVERAGE) run -m pytest -v tests/system
	$(COVERAGE) report -m
	rm .coverage

systest:
	$(COVERAGE) run -m pytest -v tests/system
	$(COVERAGE) report -m


clean:
	rm -rf $(VENV)
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf htmlcov
	find . -type f -name '*.pyc' -exec rm -f {} \;
	find . -type f -name '*.pyo' -exec rm -f {} \;
	find . -type d -name '__pycache__' -exec rm -rf {} \;
	find . -type d -name '*.egg-info' -exec rm -rf {} \;
