check: black-check isort-check flake
	@echo -e "\nEverything is fine"

format: black-format isort-format

black-format:
	black .

black-check:
	black . --check

isort-check:
	isort . -c

isort-format:
	isort .

flake:
	flake8 .

flake-show:
	flake8 . --show-source

requirements:
	pipenv requirements > requirements.txt
	pipenv requirements --dev-only > requirements-dev.txt
