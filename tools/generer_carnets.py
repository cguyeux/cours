"""Fabrique les carnets JupyterLite à partir des énoncés des TP.

Un carnet par TP : pour chaque exercice de la page, une cellule de texte reprenant
l'énoncé et le résultat attendu, suivie d'une cellule de code vide. Le corrigé n'est
jamais recopié dans le carnet : il reste sur le site, replié.

Usage : python tools/generer_carnets.py
"""

from __future__ import annotations

import json
import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parent.parent
SOURCE = RACINE / "docs"
CIBLE = RACINE / "notebooks"
SITE = "https://cours.gclab.fr"

# Nom du carnet produit -> chemin de l'énoncé, relatif à docs/. Le nom du carnet est ce que
# référence le lien `/lite/notebooks/index.html?path=<nom>.ipynb` en tête de chaque TP : ne
# pas le renommer sans corriger le lien correspondant.
PAGES = {
    "tp1": "outils-fondamentaux/tp1-calcul-numerique.md",
    "tp2": "outils-fondamentaux/tp2-arithmetique.md",
    "tp3": "outils-fondamentaux/tp3-polynomes-fonctions.md",
    "tp4": "outils-fondamentaux/tp4-matrices-gauss.md",
    "tp5": "outils-fondamentaux/tp5-synthese.md",
    "tp6": "outils-fondamentaux/tp6-geometrie-plan.md",
    "modelisation-tp1": "modelisation/tp1-matrice-svd.md",
    "modelisation-tp2": "modelisation/tp2-marche-aleatoire.md",
    "modelisation-tp3": "modelisation/tp3-gradient-bifurcation.md",
}

DEBUT_EXERCICE = re.compile(r'^!!! question "(?P<titre>[^"]+)"\s*$', re.MULTILINE)
DEBUT_CORRIGE = re.compile(r'^\s{4}\?\?\? success', re.MULTILINE)


def latex_jupyter(texte: str) -> str:
    """Jupyter attend $...$ et $$...$$ là où MkDocs accepte aussi les délimiteurs LaTeX."""
    texte = re.sub(r"\\\[(.+?)\\\]", lambda m: "$$" + m.group(1).strip() + "$$", texte, flags=re.DOTALL)
    texte = re.sub(r"\\\((.+?)\\\)", lambda m: "$" + m.group(1).strip() + "$", texte, flags=re.DOTALL)
    return texte


def desindente(bloc: str) -> str:
    lignes = []
    for ligne in bloc.splitlines():
        lignes.append(ligne[4:] if ligne.startswith("    ") else ligne)
    return "\n".join(lignes).strip()


def exercices(texte: str) -> list[tuple[str, str]]:
    trouves = []
    debuts = list(DEBUT_EXERCICE.finditer(texte))
    for numero, m in enumerate(debuts):
        fin = debuts[numero + 1].start() if numero + 1 < len(debuts) else len(texte)
        corps = texte[m.end():fin]
        corrige = DEBUT_CORRIGE.search(corps)
        if corrige:
            corps = corps[:corrige.start()]
        trouves.append((m.group("titre"), latex_jupyter(desindente(corps))))
    return trouves


def cellule(genre: str, source: str) -> dict:
    base = {"cell_type": genre, "metadata": {}, "source": source.splitlines(keepends=True)}
    if genre == "code":
        base.update({"execution_count": None, "outputs": []})
    return base


def titre_de(texte: str) -> str:
    for ligne in texte.splitlines():
        if ligne.startswith("# "):
            return ligne[2:].strip()
    return "TP"


def main() -> None:
    CIBLE.mkdir(exist_ok=True)
    for cle, chemin in PAGES.items():
        page = SOURCE / chemin
        texte = page.read_text(encoding="utf-8")
        titre = titre_de(texte)
        lien = f"{SITE}/{chemin[:-3]}/"

        cellules = [cellule("markdown", (
            f"# {titre}\n\n"
            f"Carnet de travail. L'énoncé complet, avec les corrigés, est sur le site :\n"
            f"{lien}\n\n"
            "Exécutez une cellule avec Maj+Entrée. **Pensez à télécharger ce carnet avant "
            "de partir** : menu File, puis Download.\n"
        ))]

        for intitule, enonce in exercices(texte):
            cellules.append(cellule("markdown", f"## {intitule}\n\n{enonce}\n"))
            cellules.append(cellule("code", "# votre réponse ici\n"))

        carnet = {
            "cells": cellules,
            "metadata": {
                "kernelspec": {"display_name": "Python (Pyodide)", "language": "python", "name": "python"},
                "language_info": {"name": "python"},
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        sortie = CIBLE / f"{cle}.ipynb"
        sortie.write_text(json.dumps(carnet, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{sortie.name} : {len(cellules)} cellules, {(len(cellules) - 1) // 2} exercices")


if __name__ == "__main__":
    main()
