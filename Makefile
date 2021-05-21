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

requirements:
	pipenv lock -r > requirements.txt
	pipenv lock -r --dev-only > requirements-dev.txt
