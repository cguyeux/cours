"""Gère le sous-ensemble Pyodide embarqué dans `vendor/pyodide-subset.tar.bz2`.

Pourquoi cet outil existe. Le 2026-09-15, le noyau du site est resté bloqué en
`Kernel status: Unknown` pendant des jours : le sous-ensemble avait été trié à la main sur
les paquets utiles au code *pédagogique* (numpy, matplotlib), sans la fermeture transitive
des dépendances du *noyau* lui-même (micropip, puis ipython et sa chaîne). Comme
`pyodide-lock.json` est copié tel quel depuis la distribution complète, il déclare le sha256
de paquets absents du disque : le fetch tombe sur la page 404 du site, le contrôle
d'intégrité échoue, et TOUT le noyau meurt sans message lisible. Un tri manuel ne peut pas
attraper ça ; un calcul de fermeture, si.

Deux sous-commandes :

    python tools/pyodide_subset.py verifier
        Vérifie que le sous-ensemble courant est complet et cohérent : chaque racine exigée
        par le noyau est présente, chaque dépendance de chaque paquet présent est présente,
        et chaque wheel a le sha256 que le lock lui attribue. À lancer après toute
        modification du vendor, et avant tout déploiement.

    python tools/pyodide_subset.py ajouter scipy networkx --complet <archive-pyodide.tar.bz2>
        Ajoute des paquets et leur fermeture transitive, en les prenant dans la distribution
        Pyodide complète. Le lock n'est jamais régénéré : on part du sous-ensemble qui
        fonctionne et on n'y ajoute que des fichiers, ce qui préserve les entrées ajoutées à
        la main (`comm`, absent de la distribution Pyodide mais exigé par pyodide_kernel).

Les deux sous-commandes acceptent `--vendor` pour travailler sur un autre fichier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys
import tarfile
import tempfile

RACINE = pathlib.Path(__file__).resolve().parent.parent
VENDOR = RACINE / "vendor" / "pyodide-subset.tar.bz2"
PREFIXE = "pyodide"

# Fichiers du noyau Pyodide lui-même, sans lesquels rien ne démarre.
NOYAU = [
    "pyodide.asm.mjs",
    "pyodide.asm.wasm",
    "pyodide.js",
    "pyodide.mjs",
    "pyodide-lock.json",
    "python_stdlib.zip",
]

# Paquets exigés par le noyau JupyterLite avant toute cellule utilisateur : micropip les
# installe au démarrage, et leur absence bloque le noyau entier (incident du 2026-09-15).
# `comm` est déclaré par le wheel `pyodide_kernel` mais absent de la distribution Pyodide :
# son entrée a été ajoutée à la main dans le lock, ne pas la perdre.
RACINES_NOYAU = ["micropip", "ipython", "comm"]


def lire_lock(repertoire: pathlib.Path) -> dict:
    return json.loads((repertoire / "pyodide-lock.json").read_text(encoding="utf-8"))


def normaliser(nom: str) -> str:
    """Nom de paquet canonique, au sens de la PEP 503.

    Indispensable ici : `pyodide-lock.json` n'est pas cohérent avec lui-même. Douze
    dépendances de la distribution complète sont écrites autrement que la clé qu'elles
    désignent, dont celle qui nous concerne, `ipython` -> `prompt_toolkit` quand la clé est
    `prompt-toolkit`. Comparer les noms bruts fait donc conclure à tort qu'un paquet
    présent est manquant.
    """
    return re.sub(r"[-_.]+", "-", nom).lower()


def index_normalise(lock: dict) -> dict[str, str]:
    return {normaliser(nom): nom for nom in lock["packages"]}


def fermeture(lock: dict, racines: list[str]) -> set[str]:
    """Tous les paquets atteignables depuis `racines` en suivant le champ `depends`.

    Rend des clés réelles du lock. Un nom qui ne correspond à aucune clé, même après
    normalisation, est conservé tel quel pour que l'appelant puisse le signaler.
    """
    index = index_normalise(lock)
    vus: set[str] = set()
    a_voir = [index.get(normaliser(n), n) for n in racines]
    while a_voir:
        nom = a_voir.pop()
        if nom in vus:
            continue
        vus.add(nom)
        fiche = lock["packages"].get(nom)
        if fiche is None:
            continue  # signalé par l'appelant, pas ici
        for dependance in fiche.get("depends", []):
            a_voir.append(index.get(normaliser(dependance), dependance))
    return vus


def sha256(chemin: pathlib.Path) -> str:
    h = hashlib.sha256()
    with chemin.open("rb") as f:
        for morceau in iter(lambda: f.read(1 << 20), b""):
            h.update(morceau)
    return h.hexdigest()


def extraire(archive: pathlib.Path, destination: pathlib.Path) -> pathlib.Path:
    with tarfile.open(archive, "r:bz2") as tar:
        tar.extractall(destination, filter="data")
    return destination / PREFIXE


def presents(repertoire: pathlib.Path, lock: dict) -> dict[str, str]:
    """Nom de paquet -> nom de fichier, pour les wheels réellement sur le disque."""
    fichiers = {c.name for c in repertoire.iterdir()}
    return {
        nom: fiche["file_name"]
        for nom, fiche in lock["packages"].items()
        if fiche["file_name"] in fichiers
    }


def verifier(repertoire: pathlib.Path) -> int:
    lock = lire_lock(repertoire)
    sur_disque = presents(repertoire, lock)
    problemes: list[str] = []

    for fichier in NOYAU:
        if not (repertoire / fichier).exists():
            problemes.append(f"fichier de noyau manquant : {fichier}")

    index = index_normalise(lock)
    for racine in RACINES_NOYAU:
        reelle = index.get(normaliser(racine))
        if reelle is None:
            problemes.append(f"racine du noyau absente du lock : {racine}")
        elif reelle not in sur_disque:
            problemes.append(f"racine du noyau absente du disque : {racine}")

    manquants = fermeture(lock, sorted(sur_disque)) - set(sur_disque)
    for nom in sorted(manquants):
        if nom in lock["packages"]:
            problemes.append(f"dépendance manquante : {nom} ({lock['packages'][nom]['file_name']})")
        else:
            problemes.append(f"dépendance déclarée mais absente du lock : {nom}")

    for nom, fichier in sorted(sur_disque.items()):
        attendu = lock["packages"][nom]["sha256"]
        obtenu = sha256(repertoire / fichier)
        if attendu != obtenu:
            problemes.append(f"sha256 divergent : {fichier} (lock {attendu[:12]}…, disque {obtenu[:12]}…)")

    print(f"{len(sur_disque)} paquets sur le disque, lock de {len(lock['packages'])} entrées")
    if problemes:
        print(f"\n{len(problemes)} problème(s) :")
        for p in problemes:
            print("  X", p)
        return 1
    print("sous-ensemble complet et cohérent : fermeture close, sha256 conformes")
    return 0


def ajouter(repertoire: pathlib.Path, complet: pathlib.Path, demandes: list[str]) -> int:
    lock = lire_lock(repertoire)
    sur_disque = presents(repertoire, lock)

    index = index_normalise(lock)
    inconnus = [n for n in demandes if normaliser(n) not in index]
    if inconnus:
        print("paquets absents du lock, à récupérer sur PyPI et à ajouter au lock à la main "
              f"(voir l'entrée `comm`) : {', '.join(inconnus)}")
        return 1

    voulus = fermeture(lock, demandes)
    a_copier = sorted(voulus - set(sur_disque))
    if not a_copier:
        print("rien à faire : tout est déjà présent")
        return 0

    print(f"fermeture de {', '.join(demandes)} : {len(voulus)} paquets, "
          f"{len(a_copier)} à copier")
    for nom in a_copier:
        print(f"  + {nom} ({lock['packages'][nom]['file_name']})")

    noms_de_fichier = {lock["packages"][n]["file_name"] for n in a_copier}
    with tarfile.open(complet, "r:bz2") as tar:
        trouves = 0
        for membre in tar:
            base = pathlib.PurePosixPath(membre.name).name
            if base not in noms_de_fichier:
                continue
            source = tar.extractfile(membre)
            if source is None:
                continue
            with (repertoire / base).open("wb") as cible:
                shutil.copyfileobj(source, cible)
            trouves += 1
    if trouves != len(noms_de_fichier):
        print(f"X {len(noms_de_fichier) - trouves} wheel(s) introuvable(s) dans la "
              f"distribution complète : sous-ensemble laissé incohérent, ne pas empaqueter")
        return 1
    print(f"{trouves} wheel(s) copié(s)")
    return 0


def empaqueter(repertoire: pathlib.Path, cible: pathlib.Path) -> None:
    provisoire = cible.with_suffix(".nouveau")
    with tarfile.open(provisoire, "w:bz2") as tar:
        tar.add(repertoire, arcname=PREFIXE)
    provisoire.replace(cible)
    taille = cible.stat().st_size / (1 << 20)
    print(f"{cible.name} réécrit : {taille:.1f} Mio")


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("commande", choices=["verifier", "ajouter"])
    parseur.add_argument("paquets", nargs="*", help="paquets à ajouter")
    parseur.add_argument("--complet", type=pathlib.Path, help="distribution Pyodide complète")
    parseur.add_argument("--vendor", type=pathlib.Path, default=VENDOR)
    arguments = parseur.parse_args()

    if not arguments.vendor.exists():
        print(f"introuvable : {arguments.vendor}")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        repertoire = extraire(arguments.vendor, pathlib.Path(tmp))

        if arguments.commande == "verifier":
            return verifier(repertoire)

        if not arguments.paquets:
            print("rien à ajouter")
            return 1
        if arguments.complet is None or not arguments.complet.exists():
            print("--complet est obligatoire et doit pointer vers la distribution complète")
            return 1

        code = ajouter(repertoire, arguments.complet, arguments.paquets)
        if code != 0:
            return code
        code = verifier(repertoire)
        if code != 0:
            print("\nvérification en échec après ajout : rien n'est empaqueté")
            return code
        empaqueter(repertoire, arguments.vendor)
        return 0


if __name__ == "__main__":
    sys.exit(main())
