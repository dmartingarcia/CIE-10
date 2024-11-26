SHELL := /bin/bash

create_venv:
	python3 -m venv .venv

activate_venv:
	source .venv/bin/activate

install_deps:
	pip install -r requirements

update_deps:
	rm requirements.txt
	pip freeze > requirements.txt

collect_cie10:
	python3 collect_async.py
