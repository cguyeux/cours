# Étape 1 : construction du site statique (MkDocs) et de l'environnement Python
# du navigateur (JupyterLite + Pyodide embarqué).
FROM python:3.13-slim AS build

WORKDIR /src

COPY requirements.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY mkdocs.yml jupyter_lite_config.json ./
COPY docs/ ./docs/
COPY notebooks/ ./notebooks/
COPY vendor/ ./vendor/

# L'ordre compte : mkdocs vide site_build/, jupyter lite écrit ensuite dans site_build/lite.
RUN mkdocs build --strict \
 && jupyter lite build \
 && find site_build -name '*.map' -delete \
 && du -sh site_build

# Étape 2 : service du site. Aucun interpréteur Python en production.
FROM nginx:1.29-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/site_build /usr/share/nginx/html

EXPOSE 80
