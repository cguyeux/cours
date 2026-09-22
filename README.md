# Site de cours — cours.gclab.fr

Supports de travaux pratiques de Christophe Guyeux, département informatique de l'IUT Nord
Franche-Comté. Site public, sans compte ni VPN : <https://cours.gclab.fr>

Contenu actuel : la ressource R1.07 « outils mathématiques fondamentaux » du BUT
informatique, semestre 1, soit cinq TP d'introduction à Python par les mathématiques, une
sixième séance de prolongement (géométrie du plan), un mémento et un QCM par TP.
Chaque TP porte une partie « Entraînement et approfondissement » hors séance mais au
programme, et une liste d'auto-évaluation. Les autres cours seront réintégrés section par
section.

## Organisation

| Chemin | Rôle |
|---|---|
| `docs/` | les pages, en Markdown ; source unique du contenu |
| `notebooks/` | carnets JupyterLite, **générés** depuis `docs/`, ne pas éditer à la main |
| `vendor/` | distribution Pyodide réduite (noyau, numpy, matplotlib), embarquée dans l'image |
| `tools/generer_carnets.py` | fabrique les carnets à partir des énoncés (dictionnaire `PAGES` à compléter pour tout nouveau TP) |
| `qcm/tpN/qcm.json` | pivot de chaque QCM ; rendu HTML dans `docs/outils-fondamentaux/qcm/` par le skill `qcm-generator` |
| `tools/pyodide_subset.py` | vérifie et complète le sous-ensemble Pyodide (`verifier`, `ajouter`) |
| `tests/test_corriges.py` | exécute tout le code des corrigés du site |
| `Dockerfile`, `nginx.conf` | image de production : MkDocs + JupyterLite, servis par nginx |
| `deploy.sh` | construction, envoi et mise en ligne sur Scaleway |

## Travailler sur le contenu

```
make install      # une fois : crée .venv et installe les dépendances
make build        # carnets + tests + site + JupyterLite
make servir       # sert le site sur http://127.0.0.1:8899
```

Le code des corrigés est **exécuté** à chaque construction : un corrigé faux fait échouer le
build. Un bloc volontairement incorrect dans un énoncé se marque
` ```python title="..." `, ce qui l'exclut de l'exécution.

Le test prouve que le code tourne, pas que les valeurs annoncées dans les énoncés sont les
bonnes. Après toute modification, relire les sorties réelles :

```
.venv/bin/python -c "import sys; sys.path.insert(0, 'tests'); import test_corriges as t; [print('==', p.name), print(t.sorties(p))] for p in t.pages() if t.blocs_de(p)]"
```

Régénérer un QCM après avoir modifié son pivot :

```
python3 ~/.claude/skills/qcm-generator/scripts/build_qcm.py qcm/tp1/qcm.json --formats html --outdir docs/outils-fondamentaux/qcm --basename qcm_tp1
```

## Mettre en ligne

```
./deploy.sh          # numérote automatiquement la version suivante
./deploy.sh v7       # ou impose un numéro
```

Le script refuse de terminer si un corrigé échoue ou si le site ne répond pas.

## Points d'attention

- **Jamais le tag `latest`** : Scaleway ne retélécharge pas une image de tag identique, et
  le site servirait silencieusement l'ancienne version.
- **Ne pas déclarer de bloc `types` dans `nginx.conf`** : il remplacerait la table MIME
  héritée, et toutes les pages seraient servies en `application/octet-stream`.
- **`.mjs` est absent de la table MIME de nginx** : sans la `location` qui le corrige, le
  navigateur refuse le module ES et JupyterLite ne démarre pas du tout.
- Le travail des étudiants dans JupyterLite est stocké dans leur navigateur, pas sur le
  serveur : la page de mise en route leur apprend à télécharger leur carnet.
- **Toucher au vendor Pyodide, jamais à la main** : `python tools/pyodide_subset.py verifier`
  avant tout déploiement, et `ajouter <paquets> --complet <archive>` pour en ajouter. Un tri
  manuel oublie les dépendances transitives, et le noyau meurt alors sans message lisible.
- **Vider `.jupyterlite.doit.db` avant toute reconstruction locale de vérification** : avec
  un cache, `jupyter lite build` saute le patch qui écrit `pyodideUrl` dans
  `site_build/lite/jupyter-lite.json`, et le noyau retombe silencieusement sur le CDN. La
  construction de l'image Docker, elle, part toujours d'un cache vide.
- **Aucune valeur absolue issue d'une image décodée dans un énoncé** : pillow ne donne pas
  exactement les mêmes pixels dans Pyodide et dans le venv. Les quantités relatives, elles,
  coïncident.
- **Embarquer un wheel ne suffit pas à le rendre importable** : le noyau du navigateur ne
  charge que les imports de premier niveau du code exécuté. Une bibliothèque qui importe sa
  dépendance dans une fonction (`networkx.pagerank` et scipy) échoue sans import explicite
  dans l'énoncé. Rejouer en entier dans le navigateur tout TP qui utilise une bibliothèque
  nouvellement embarquée.

## Miroir de secours

`deploy.sh` publie aussi le site construit sur la branche `gh-pages` du dépôt, servie par
GitHub Pages à l'adresse <https://secours.gclab.fr>. Si le conteneur Scaleway tombait la
veille d'une séance, cette adresse sert exactement le même contenu. L'adresse à communiquer
aux étudiants reste `cours.gclab.fr`. Pour publier sans le miroir : `SANS_MIROIR=1 ./deploy.sh`.

## Infrastructure

Conteneur Serverless Scaleway `site` du namespace `cours` (région `fr-par`), image dans
`rg.fr-par.scw.cloud/gclab-cours/site`, `cours.gclab.fr` en CNAME avec certificat Let's
Encrypt renouvelé automatiquement.
