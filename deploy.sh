#!/usr/bin/env bash
# Déploiement du site de cours sur https://cours.gclab.fr
#
# Enchaîne : régénération des carnets, exécution de tout le code des corrigés,
# construction du site et de JupyterLite, image Docker versionnée, envoi au
# registre Scaleway, mise à jour du conteneur Serverless, attente de "ready",
# puis vérification fonctionnelle.
#
# Le tag est TOUJOURS versionné : un redéploiement sur un tag identique ne
# retélécharge pas l'image et le site sert silencieusement l'ancienne version.

set -euo pipefail

CONTENEUR_ID="0f8526c5-326a-4cd3-94e0-aee8270c21dd"
REGISTRE="rg.fr-par.scw.cloud/gclab-cours/site"
REGION="fr-par"
SITE="https://cours.gclab.fr"
RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$RACINE"

# --- version -----------------------------------------------------------------
if [ $# -ge 1 ]; then
    VERSION="$1"
else
    ACTUELLE=$(scw container container get "$CONTENEUR_ID" region="$REGION" -o json \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('image',''))")
    NUMERO=$(printf '%s' "$ACTUELLE" | sed -n 's/.*:v\([0-9]\+\)$/\1/p')
    VERSION="v$(( ${NUMERO:-0} + 1 ))"
fi
echo "==> version $VERSION (image en ligne : ${ACTUELLE:-inconnue})"

# --- contrôles avant tout envoi ----------------------------------------------
echo "==> régénération des carnets"
.venv/bin/python tools/generer_carnets.py

echo "==> exécution de tout le code des corrigés"
.venv/bin/python tests/test_corriges.py

# --- image --------------------------------------------------------------------
echo "==> construction de l'image"
docker build --network=host -t "$REGISTRE:$VERSION" .

echo "==> envoi au registre"
docker push "$REGISTRE:$VERSION"

# --- mise en ligne -------------------------------------------------------------
echo "==> mise à jour du conteneur"
scw container container update "$CONTENEUR_ID" image="$REGISTRE:$VERSION" region="$REGION" > /dev/null

echo -n "==> attente de ready "
for _ in $(seq 1 60); do
    ETAT=$(scw container container get "$CONTENEUR_ID" region="$REGION" -o json \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))")
    [ "$ETAT" = "ready" ] && break
    echo -n "."
    sleep 5
done
echo " $ETAT"
[ "$ETAT" = "ready" ] || { echo "le conteneur n'est pas revenu à ready" >&2; exit 1; }

# --- vérification fonctionnelle ------------------------------------------------
# Un statut "ready" ne prouve pas que la bonne version est servie : on interroge
# le site lui-même.
echo "==> vérification"
IP=$(dig +short cours.gclab.fr @1.1.1.1 | tail -1)
for chemin in / /outils-fondamentaux/ /lite/repl/index.html; do
    CODE=$(curl -s -o /dev/null -w '%{http_code}' --resolve "cours.gclab.fr:443:$IP" "$SITE$chemin")
    printf '    %-38s %s\n' "$chemin" "$CODE"
    [ "$CODE" = "200" ] || { echo "échec sur $chemin" >&2; exit 1; }
done

echo "==> en ligne : $SITE  (image $VERSION)"

# --- miroir de secours sur GitHub Pages ---------------------------------------
# Le même site construit, sans les source maps, poussé sur la branche gh-pages
# et servi à la racine de secours.gclab.fr. Branche orpheline réécrite à chaque
# publication (--force) pour que l'historique ne grossisse pas de 50 Mo par
# version. Aucun droit "workflow" n'est nécessaire : c'est un push ordinaire.
if [ "${SANS_MIROIR:-}" != "1" ]; then
    echo "==> miroir de secours (GitHub Pages)"
    MIROIR=$(mktemp -d)
    rsync -a --exclude='*.map' site_build/ "$MIROIR"/
    echo "secours.gclab.fr" > "$MIROIR/CNAME"
    touch "$MIROIR/.nojekyll"
    ( cd "$MIROIR" \
      && git init -q -b gh-pages \
      && git add -A \
      && git -c user.name="Christophe Guyeux" -c user.email="guyeux@gmail.com" \
             commit -q -m "Miroir de secours : site construit ($VERSION)" \
      && git push --force -q https://github.com/cguyeux/cours.git gh-pages:gh-pages )
    echo "    https://secours.gclab.fr  (branche gh-pages, $VERSION)"
fi
