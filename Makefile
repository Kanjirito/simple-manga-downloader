check: black-check line flake line
	@echo -e "\nEverything is fine"

black-format:
	black .

black-check:
	black . --check

flake:
	flake8 .

line:
	@echo ""

requirements:
	pipenv lock -r > requirements.txt
	pipenv lock -r --dev-only > requirements-dev.txt
