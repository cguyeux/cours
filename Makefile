# Chaîne de construction locale. La production passe par le Dockerfile,
# qui exécute exactement les mêmes étapes.

VENV := .venv
PY := $(VENV)/bin/python

.PHONY: aide install carnets test site lite build servir docker deployer

aide:
	@echo "make install   installe les dépendances dans .venv"
	@echo "make carnets   régénère les carnets JupyterLite depuis les énoncés"
	@echo "make test      exécute tout le code des corrigés"
	@echo "make build     carnets + test + site + JupyterLite"
	@echo "make servir    construit puis sert le site sur http://127.0.0.1:8899"
	@echo "make docker    construit l'image du conteneur"
	@echo "make deployer  construit, pousse et met en ligne sur cours.gclab.fr"

install:
	python3 -m venv $(VENV)
	$(PY) -m pip install -U pip wheel
	$(PY) -m pip install -r requirements-dev.txt

carnets:
	$(PY) tools/generer_carnets.py

test:
	$(PY) tests/test_corriges.py

site:
	$(VENV)/bin/mkdocs build --strict

lite:
	$(VENV)/bin/jupyter lite build

build: carnets test site lite
	@du -sh site_build

servir: build
	@echo "http://127.0.0.1:8899"
	cd site_build && ../$(PY) -m http.server 8899 --bind 127.0.0.1

docker:
	docker build --network=host -t cours-gclab:local .

deployer:
	./deploy.sh
