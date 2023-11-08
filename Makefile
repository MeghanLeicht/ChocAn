VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
install: .venv/touchfile

.venv/touchfile: requirements-dev.txt requirements.txt
	test -d $(VENV) || python3.11 -m virtualenv $(VENV)
	. $(VENV)/bin/activate
	$(PYTHON) -m $(PIP) install -Ur requirements-dev.txt
	$(PYTHON) -m $(PIP) install -e .
	touch $(VENV)/touchfile

test: .venv/touchfile
	coverage run -m pytest
	coverage report
	rm .coverage

clean:
	rm -rf $(VENV)
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf htmlcov
	find . -type f -name '*.pyc' -exec rm -f {} \;
	find . -type f -name '*.pyo' -exec rm -f {} \;
	find . -type d -name '__pycache__' -exec rm -rf {} \;
	find . -type d -name '*.egg-info' -exec rm -rf {} \;
