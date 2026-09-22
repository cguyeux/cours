#!/usr/bin/env python3
"""Rejoue dans le navigateur TOUT le code d'une page de TP, et compare au local.

Pourquoi cet outil existe. Le harnais `tests/test_corriges.py` prouve que le code
d'une page s'exécute dans le venv du site ; il ne prouve rien sur le noyau Pyodide
du navigateur, qui n'a ni les mêmes versions de bibliothèques ni le même mécanisme
de chargement de paquets. Deux pièges déjà payés imposent cette vérification
séparée :

1. Pyodide ne télécharge un paquet que s'il le voit comme **import de premier
   niveau du code exécuté** (`loadPackagesFromImports`). Un `exec()` de code
   distant ne déclenche donc AUCUN chargement : la cellule doit importer
   elle-même ce dont la page a besoin. C'est le même mécanisme qui faisait
   échouer `networkx.pagerank` au TP2 le 2026-09-15.
2. Le carnet produit par `generer_carnets.py` est une **feuille de travail** :
   des cellules « # votre réponse ici », vides. Un « Run All Cells » dessus
   n'exécute rien et donne une fausse assurance.
3. On ne passe donc PAS par le carnet, mais par le REPL, dont l'URL accepte
   `?code=<urlencodé>&execute=1`. Écrire dans une cellule de carnet suppose un
   vrai clic (un `.focus()` sur `.cm-content` ne fait pas entrer JupyterLab en
   mode édition, et CodeMirror n'expose aucun ref cliquable dans le snapshot) :
   la saisie part alors dans le vide et la cellule reste « # votre réponse ici ».

Usage :
    python tools/verifier_navigateur.py modelisation/tp3-gradient-bifurcation.md

Prérequis : `make build` passé (site_build/ à jour, lite/ construit), un serveur
local sur le port choisi, et `agent-browser` installé.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse
import time

RACINE = pathlib.Path(__file__).resolve().parent.parent
DOCS = RACINE / "docs"
SORTIE = RACINE / "site_build"

# Les paquets à importer dans la cellule pour que Pyodide les charge avant l'exec.
# Un import de premier niveau absent d'ici ne sera PAS chargé, quel que soit le
# contenu du fichier exécuté : c'est tout l'objet de la liste.
IMPORTS_CONNUS = {
    "numpy": "numpy",
    "matplotlib": "matplotlib.pyplot",
    "scipy": "scipy.optimize",
    "networkx": "networkx",
    "pandas": "pandas",
    "math": "math",
    "unicodedata": "unicodedata",
}


def blocs_executables(page: pathlib.Path) -> list[str]:
    """Les blocs ```python de la page, hors contre-exemples marqués par un titre."""
    motif = re.compile(
        r"^(?P<indent>[ \t]*)```(?P<info>python[^\n]*)\n(?P<code>.*?)^(?P=indent)```",
        re.DOTALL | re.MULTILINE,
    )
    trouves = []
    for m in motif.finditer(page.read_text(encoding="utf-8")):
        if m.group("info").strip() != "python":
            continue
        indent, code = m.group("indent"), m.group("code")
        if indent:
            code = "\n".join(
                ligne[len(indent):] if ligne.startswith(indent) else ligne
                for ligne in code.splitlines()
            )
        trouves.append(code)
    return trouves


def imports_de_premier_niveau(blocs: list[str]) -> list[str]:
    """Ce que la page importe, donc ce que la cellule devra importer pour elle."""
    vus = set()
    for code in blocs:
        for ligne in code.splitlines():
            m = re.match(r"^\s*(?:import|from)\s+([a-zA-Z_][\w]*)", ligne)
            if m:
                vus.add(m.group(1))
    return sorted(IMPORTS_CONNUS[nom] for nom in vus if nom in IMPORTS_CONNUS)


def ecrire_script(blocs: list[str], destination: pathlib.Path) -> None:
    lignes = ["# Généré par tools/verifier_navigateur.py — ne pas commiter.", ""]
    for numero, code in enumerate(blocs, start=1):
        lignes.append(f'print("=== BLOC {numero} ===", flush=True)')
        lignes.append(code)
        lignes.append("")
    lignes.append('print("=== FIN : TOUS LES BLOCS ONT PASSE ===", flush=True)')
    destination.write_text("\n".join(lignes), encoding="utf-8")


def nom_du_carnet(chemin_relatif: str) -> str | None:
    """Le carnet associé à une page, d'après PAGES de generer_carnets.py.

    Ce mapping fait autorité : le deviner depuis le nom de fichier donnerait
    `tp3-gradient-bifurcation` là où le carnet s'appelle `modelisation-tp3`.
    """
    sys.path.insert(0, str(RACINE / "tools"))
    from generer_carnets import PAGES  # noqa: PLC0415 - import tardif volontaire

    for carnet, page in PAGES.items():
        if page == chemin_relatif:
            return carnet
    return None


def ab(session: str, *args: str, timeout: int = 120) -> str:
    sortie = subprocess.run(
        ["agent-browser", "--session", session, *args],
        capture_output=True, text=True, timeout=timeout,
    )
    return sortie.stdout.strip()


def attendre_verdict(session: str, patience: int) -> str:
    """Interroge la cellule jusqu'à la ligne de fin, une erreur, ou l'échéance.

    Le noyau rend la main à `Shift+Enter` immédiatement : c'est la SORTIE de la
    cellule qu'il faut attendre, pas la commande du navigateur. Le premier
    chargement de scipy en WebAssembly prend à lui seul plusieurs dizaines de
    secondes.
    """
    debut = time.monotonic()
    texte = ""
    while time.monotonic() - debut < patience:
        lu = ab(session, "eval", "document.body.innerText")
        texte = json.loads(lu) if lu.startswith('"') else lu
        if "TOUS LES BLOCS ONT PASSE" in texte or re.search(r"Traceback|Error:", texte):
            return texte
        time.sleep(5)
    return texte


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("page", help="chemin relatif à docs/, ex. modelisation/tp3-....md")
    parseur.add_argument("--port", type=int, default=8899)
    parseur.add_argument("--session", default="verif")
    parseur.add_argument("--patience", type=int, default=900,
                         help="secondes d'attente maximale du verdict")
    parseur.add_argument("--garder", action="store_true",
                         help="ne pas supprimer le script servi à la fin")
    args = parseur.parse_args()

    page = DOCS / args.page
    if not page.exists():
        print(f"page introuvable : {page}", file=sys.stderr)
        return 1

    blocs = blocs_executables(page)
    if not blocs:
        print("aucun bloc exécutable dans cette page.", file=sys.stderr)
        return 1

    nom = f"verif_{page.stem}.py"
    servi = SORTIE / nom
    ecrire_script(blocs, servi)
    imports = imports_de_premier_niveau(blocs)
    print(f"{len(blocs)} blocs écrits dans {servi.relative_to(RACINE)}")
    print(f"imports que la cellule déclarera : {', '.join(imports) or '(aucun)'}")

    ligne = (f"import {', '.join(imports)}; "
             f"exec(__import__('pyodide').http.open_url('/{nom}').read())")
    url = (f"http://127.0.0.1:{args.port}/lite/repl/index.html?kernel=python"
           f"&toolbar=1&code={urllib.parse.quote(ligne)}&execute=1")
    print("ouverture du REPL (le carnet est une feuille de travail : il ne sert pas ici)")
    ab(args.session, "open", url, timeout=240)

    texte = attendre_verdict(args.session, args.patience)

    if not args.garder:
        servi.unlink(missing_ok=True)

    if "TOUS LES BLOCS ONT PASSE" in texte:
        print("NAVIGATEUR : tous les blocs ont passé.")
        return 0
    print("NAVIGATEUR : échec ou exécution inachevée. Extrait :", file=sys.stderr)
    print(texte[-1500:], file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
