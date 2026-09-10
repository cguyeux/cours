"""Exécute tout le code Python des pages du site.

Chaque page de TP est un programme linéaire : les blocs de code s'y enchaînent dans
l'ordre où l'étudiant les tape. Le test les rejoue donc à la suite, dans un espace de
noms unique par page, et échoue à la première exception. C'est la garantie qu'aucun
corrigé publié n'est faux.

Un bloc dont l'info-string porte autre chose que le seul mot ``python`` (typiquement
``python title="Ce code est volontairement incorrect"``) est ignoré : c'est ainsi que
l'on écrit un contre-exemple dans un énoncé sans casser le test.
"""

from __future__ import annotations

import io
import os
import pathlib
import re
import sys
from contextlib import redirect_stdout

import pytest

# Les corrigés qui tracent une courbe appellent plt.show() : sans backend non
# interactif, le test ouvrirait des fenêtres et bloquerait.
os.environ.setdefault("MPLBACKEND", "Agg")

RACINE = pathlib.Path(__file__).resolve().parent.parent
DOCS = RACINE / "docs"

# ```python  ... ```  (le bloc peut être indenté sous une admonition)
BLOC = re.compile(
    r"^(?P<indent>[ \t]*)```(?P<info>python[^\n]*)\n(?P<code>.*?)^(?P=indent)```",
    re.DOTALL | re.MULTILINE,
)


def pages() -> list[pathlib.Path]:
    return sorted(DOCS.rglob("*.md"))


def blocs_de(page: pathlib.Path) -> list[str]:
    texte = page.read_text(encoding="utf-8")
    trouves = []
    for m in BLOC.finditer(texte):
        if m.group("info").strip() != "python":
            continue  # contre-exemple explicitement marqué
        indent = m.group("indent")
        code = m.group("code")
        if indent:
            code = "\n".join(
                ligne[len(indent):] if ligne.startswith(indent) else ligne
                for ligne in code.splitlines()
            )
        trouves.append(code)
    return trouves


@pytest.mark.parametrize("page", pages(), ids=lambda p: p.relative_to(DOCS).as_posix())
def test_page_executable(page: pathlib.Path) -> None:
    blocs = blocs_de(page)
    if not blocs:
        pytest.skip("aucun bloc Python exécutable")
    espace: dict[str, object] = {"__name__": "__main__"}
    for numero, code in enumerate(blocs, start=1):
        sortie = io.StringIO()
        try:
            with redirect_stdout(sortie):
                exec(compile(code, f"{page.name}#bloc{numero}", "exec"), espace)
        except Exception as erreur:  # noqa: BLE001 - on veut le message brut
            raise AssertionError(
                f"{page.relative_to(RACINE)} : le bloc {numero} a échoué "
                f"({type(erreur).__name__}: {erreur})\n"
                f"--- code ---\n{code}"
            ) from erreur


if __name__ == "__main__":
    codes = 0
    for page in pages():
        blocs = blocs_de(page)
        if not blocs:
            continue
        try:
            test_page_executable(page)
        except AssertionError as erreur:
            codes += 1
            print(erreur, file=sys.stderr)
        else:
            print(f"OK   {page.relative_to(DOCS)}  ({len(blocs)} blocs)")
    sys.exit(1 if codes else 0)


def sorties(page: pathlib.Path) -> str:
    """Rejoue une page et renvoie tout ce qu'elle affiche, pour relecture humaine."""
    espace: dict[str, object] = {"__name__": "__main__"}
    morceaux = []
    for numero, code in enumerate(blocs_de(page), start=1):
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            exec(compile(code, f"{page.name}#bloc{numero}", "exec"), espace)
        texte = sortie.getvalue().strip()
        if texte:
            morceaux.append(f"--- bloc {numero} ---\n{texte}")
    return "\n".join(morceaux)
