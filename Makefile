VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
install: .venv/touchfile

.venv/touchfile: requirements-dev.txt requirements.txt
	sudo apt-get install python3.11-venv
	test -d venv || python3.11 -m virtualenv .venv
	. .venv/bin/activate; \
	python3 -m pip install -Ur requirements-dev.txt; \
	python3 -m pip install -e .
	touch .venv/touchfile

test: .venv/touchfile
	. .venv/bin/activate; coverage run -m pytest
	coverage report
	rm .coverage

clean:
	rm -rf .venv ;\
	rm -rf .coverage ;\
	rm -rf .pytest_cache ;\
	rm -rf htmlcov ;\
	find . -type f -name '*.pyc' -exec rm -f {} \; ;\
	find . -type f -name '*.pyo' -exec rm -f {} \; ;\
	find . -type d -name '__pycache__' -exec rm -rf {} \; ;\
	find . -type d -name '*.egg-info' -exec rm -rf {} \; ;\