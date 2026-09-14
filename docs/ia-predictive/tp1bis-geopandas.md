# TP1bis. Données géographiques avec GeoPandas

**Durée : 2 h.**

## Objectifs

- Comprendre ce que geopandas ajoute à pandas : une colonne géométrie et des opérations
  spatiales.
- Manipuler des géométries (points, polygones), calculer des aires et des distances.
- Comprendre pourquoi le choix du système de coordonnées (CRS) change tout.
- Effectuer une jointure spatiale et produire une carte thématique.

## Prérequis

Le [TP1](tp1-pandas.md) : les bases de pandas (sélection, filtrage, `groupby`).

```bash
pip install geopandas shapely matplotlib
```

## Ressources

- [Documentation GeoPandas](https://geopandas.org/).
- [Manuel Shapely](https://shapely.readthedocs.io/).

!!! info "Pas de jeu de données à télécharger"
    Les versions récentes de geopandas ont retiré le petit jeu de données intégré
    `naturalearth_lowres` qui servait autrefois de terrain de jeu par défaut : il faut
    désormais le télécharger séparément. Pour rester autonome, ce TP construit ses propres
    géométries directement en code, avec `shapely`, comme le fait déjà le TP4 d'agents du
    module IA générative pour d'autres raisons. Les territoires utilisés sont fictifs
    (`Vertland`, `Rougie`...) : ce ne sont pas de vraies frontières, seulement des
    rectangles commodes pour illustrer les opérations spatiales.

---

## Étape 1. Une GeoDataFrame, une DataFrame avec une colonne géométrie (20 min)

Une `GeoDataFrame` est une DataFrame pandas ordinaire, augmentée d'une colonne spéciale,
`geometry`, qui porte une forme géométrique par ligne (point, ligne, polygone) plutôt
qu'un nombre ou du texte.

```python
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point

territoires = gpd.GeoDataFrame(
    {
        "nom": ["Vertland", "Rougie", "Bleuma", "Jaunèse", "Griselle"],
        "population": [12_000_000, 3_500_000, 8_200_000, 1_100_000, 45_000_000],
        "groupe": ["nord", "nord", "sud", "sud", "nord"],
    },
    geometry=[
        Polygon([(0, 45), (3, 45), (3, 48), (0, 48)]),
        Polygon([(3, 45), (5, 45), (5, 48), (3, 48)]),
        Polygon([(0, 42), (3, 42), (3, 45), (0, 45)]),
        Polygon([(3, 42), (5, 42), (5, 45), (3, 45)]),
        Polygon([(5, 42), (8, 42), (8, 48), (5, 48)]),
    ],
    crs="EPSG:4326",
)

print(territoires)
print(territoires.geom_type.unique())
print(territoires.crs)
```

`crs="EPSG:4326"` déclare que les coordonnées sont des longitudes et des latitudes en
degrés (le système utilisé par le GPS) : c'est le CRS géographique le plus courant, et
celui qui va poser un piège à l'étape suivante.

!!! question "Exercice 1.1 : combien de territoires par groupe"
    Utilisez `value_counts()` sur la colonne `groupe`, exactement comme au TP1 sur
    `Species`, et affichez l'emprise totale des territoires avec `territoires.total_bounds`.

    **Résultat attendu :** trois territoires « nord », deux « sud ». L'emprise totale
    (longitude min, latitude min, longitude max, latitude max) vaut
    `[0.0, 42.0, 8.0, 48.0]`.

    ??? success "Corrigé"
        ```python
        print(territoires["groupe"].value_counts())
        print(territoires.total_bounds)
        ```

        `total_bounds` répond en une ligne à une question qu'il faudrait sinon poser à
        chaque géométrie individuellement : la GeoDataFrame se comporte comme une
        DataFrame ordinaire pour tout ce qui ne touche pas à la géométrie (`value_counts`,
        `groupby`, filtrage), et ajoute des méthodes dédiées (`total_bounds`, `area`,
        `distance`) pour ce qui en touche.

## Étape 2. Les aires, et le piège du système de coordonnées (25 min)

```python
print(territoires.geometry.area.round(2).tolist())
```

Cette ligne calcule une aire, mais dans quelle unité ? Les coordonnées sont en degrés, donc
le résultat est en « degrés carrés », une unité qui ne correspond à aucune mesure physique
utilisable. geopandas le signale d'ailleurs par un avertissement. Pour une aire en
kilomètres carrés, il faut d'abord reprojeter dans un CRS **métrique**, adapté à la zone
étudiée :

```python
territoires_m = territoires.to_crs(epsg=2154)  # Lambert-93, adapté à la France
print((territoires_m.geometry.area / 1e6).round(0).tolist())
```

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant « calcule l'aire de chaque polygone de ce GeoDataFrame » sans
    préciser de CRS. Le code obtenu appelle presque toujours `.area` directement sur les
    données telles quelles. Exécutez-le sur `territoires` (toujours en `EPSG:4326`) :

    ```python
    import warnings
    with warnings.catch_warnings(record=True) as attrapes:
        warnings.simplefilter("always")
        aires_brutes = territoires.geometry.area
        for a in attrapes:
            print("Avertissement :", a.message)
    print(aires_brutes.round(2).tolist())
    ```

    geopandas avertit explicitement : *« Results from 'area' are likely incorrect »*. Le
    nombre s'affiche quand même, sans planter, ce qui est le vrai danger : rien n'empêche
    de le prendre pour une vraie surface en kilomètres carrés et de le citer tel quel dans
    un rapport. Un assistant qui ne connaît pas la zone géographique visée ne pense pas
    toujours à reprojeter avant de calculer une aire ou une distance.

!!! question "Exercice 2.1 : deux projections, deux résultats"
    Reprojetez `territoires` en `EPSG:3857` (Web Mercator, la projection des cartes web
    grand public) plutôt qu'en Lambert-93, et recalculez les aires en km². Comparez aux
    valeurs obtenues avec Lambert-93.

    **Résultat attendu :** des valeurs **différentes** des deux côtés (par exemple
    `Griselle` autour de `157 569` km² en Lambert-93 contre `315 883` km² en Web Mercator) :
    Web Mercator déforme fortement les surfaces loin de l'équateur, ce n'est pas une
    projection adaptée à un calcul d'aire précis, seulement à un affichage web.

    ??? success "Corrigé"
        ```python
        territoires_web = territoires.to_crs(epsg=3857)
        print((territoires_web.geometry.area / 1e6).round(0).tolist())
        print((territoires_m.geometry.area / 1e6).round(0).tolist())
        ```

        La leçon dépasse ce seul exercice : « reprojeter » ne suffit pas, il faut
        reprojeter dans un CRS **choisi pour la mesure qu'on veut faire**. Lambert-93 est
        construit pour minimiser la déformation des surfaces sur le territoire français ;
        Web Mercator est construit pour que les angles restent corrects à toute échelle de
        zoom, au prix d'une déformation des surfaces qui s'aggrave avec la latitude.

## Étape 3. Points, distances et zones tampons (25 min)

Les points suivent les mêmes règles que les polygones. Voici cinq villes françaises,
avec leurs coordonnées réelles :

```python
villes = gpd.GeoDataFrame(
    {"ville": ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux"]},
    geometry=[
        Point(2.3522, 48.8566),
        Point(4.8357, 45.7640),
        Point(5.3698, 43.2965),
        Point(1.4442, 43.6047),
        Point(-0.5792, 44.8378),
    ],
    crs="EPSG:4326",
)

villes_m = villes.to_crs(epsg=2154)
paris = villes_m.loc[villes_m["ville"] == "Paris", "geometry"].iloc[0]
distances_km = (villes_m.geometry.distance(paris) / 1000).round(1)
print(pd.Series(distances_km.values, index=villes["ville"]))
```

Comme pour les aires, la distance se calcule après reprojection dans un CRS métrique :
`distance()` sur des coordonnées en degrés donnerait, encore, un nombre sans unité
physique exploitable.

!!! question "Exercice 3.1 : des zones tampons de 50 km"
    Créez un buffer de 50 km autour de chaque ville (`geometry.buffer(50_000)`, sur les
    données reprojetées `villes_m`), et calculez l'aire de chacun en km².

    **Résultat attendu :** cinq buffers, tous de la même aire (un cercle de rayon 50 km a
    une aire de \( \pi \times 50^2 \approx 7854 \) km², quelle que soit la ville, puisque
    le rayon est identique partout).

    ??? success "Corrigé"
        ```python
        buffers = villes_m.copy()
        buffers["geometry"] = buffers.geometry.buffer(50_000)
        print((buffers.geometry.area / 1e6).round(0).tolist())
        ```

        Le calcul confirme la géométrie : environ `7841` km² pour chacune (la petite
        différence avec la formule exacte du cercle vient de l'approximation polygonale
        que `shapely` utilise pour représenter un cercle). Un buffer sert typiquement à
        répondre à des questions du type « quels équipements sont à moins de 50 km de
        cette ville ? », en combinant ensuite le buffer avec une jointure spatiale, comme
        à l'étape suivante.

## Étape 4. Jointure spatiale (20 min)

Une jointure spatiale associe les lignes de deux GeoDataFrames selon une relation
géométrique (« est à l'intérieur de », « touche », « intersecte »), plutôt que selon une
colonne commune comme le ferait `pd.merge()`.

```python
jointes = gpd.sjoin(villes, territoires, how="left", predicate="within")
print(jointes[["ville", "nom"]])
```

!!! question "Exercice 4.1 : des villes sans territoire"
    Certaines villes n'obtiennent aucun `nom` de territoire après la jointure. Identifiez
    lesquelles, et expliquez pourquoi en comparant leurs coordonnées à `territoires.total_bounds`
    (étape 1).

    **Résultat attendu :** `Paris` (latitude `48.86`) et `Bordeaux` (longitude `-0.58`)
    ressortent avec un territoire manquant (`NaN`) : Paris dépasse la limite nord des
    territoires (latitude 48), Bordeaux dépasse leur limite ouest (longitude 0). Les trois
    autres villes tombent bien dans un des cinq rectangles.

    ??? success "Corrigé"
        ```python
        manquantes = jointes[jointes["nom"].isna()]
        print(manquantes[["ville"]])
        print(territoires.total_bounds)
        ```

        `how="left"` garde toutes les villes, y compris celles sans correspondance, avec
        des `NaN` à la place ; `how="inner"` (le défaut d'un `sjoin`) les aurait fait
        disparaître silencieusement. Un jeu de contours qui ne couvre pas toute la zone
        étudiée est une situation réelle, pas un cas d'école : c'est ainsi qu'on découvre
        qu'un jeu de données de référence est incomplet, et `how="left"` est le choix qui
        le révèle plutôt que de le cacher.

## Étape 5. Fusionner des géométries avec `dissolve` (15 min)

`dissolve` regroupe des géométries selon une colonne, comme `groupby`, mais fusionne aussi
les polygones du groupe en un seul :

```python
fusion = territoires.dissolve(by="groupe", aggfunc={"population": "sum"})
print(fusion[["population"]])
print(fusion.geom_type)
```

!!! question "Exercice 5.1 : la population totale par groupe"
    Vérifiez que la somme des populations après `dissolve` correspond bien à la somme des
    populations individuelles des territoires de chaque groupe.

    **Résultat attendu :** `60 500 000` pour le groupe « nord » (Vertland + Rougie +
    Griselle), `9 300 000` pour « sud » (Bleuma + Jaunèse), et ces deux totaux
    correspondent exactement à `territoires.groupby("groupe")["population"].sum()`.

    ??? success "Corrigé"
        ```python
        print(fusion["population"])
        print(territoires.groupby("groupe")["population"].sum())
        ```

        `dissolve(by=..., aggfunc=...)` est littéralement un `groupby().agg()` qui,
        en plus, fusionne les géométries du groupe avec une opération d'union. C'est
        l'outil qui transforme, par exemple, des polygones de communes en un polygone de
        région : la donnée statistique s'agrège exactement comme avec `groupby`, la
        géométrie fusionne avec elle.

## Étape 6. Cartographie thématique (15 min)

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7, 6))
territoires.plot(column="population", cmap="OrRd", edgecolor="black", legend=True, ax=ax)
villes.plot(ax=ax, color="blue", markersize=30)
ax.set_title("Population par territoire, et villes de référence")
plt.tight_layout()
plt.show()
```

Une carte choroplèthe (`column="population"`) colore chaque forme selon une valeur
numérique, exactement comme une heatmap colore chaque case d'un tableau au TP1 : c'est la
même idée, appliquée à des formes géographiques plutôt qu'à une grille.

!!! question "Exercice 6.1 : deux échelles de couleur"
    Reproduisez la carte avec `cmap="viridis"` puis avec `cmap="OrRd"`, côte à côte
    (`plt.subplots(1, 2)`). Laquelle des deux distingue le mieux `Jaunèse` (la plus petite
    population) de `Bleuma` (une population intermédiaire) ?

    **Résultat attendu :** un jugement visuel, pas un nombre : les palettes séquentielles
    comme `OrRd` ou `viridis` sont conçues pour qu'une différence de valeur se voie comme
    une différence de teinte perceptible, ce qui n'est pas garanti avec n'importe quelle
    palette (une palette arc-en-ciel, par exemple, crée des frontières visuelles qui
    n'existent pas dans les données).

    ??? success "Corrigé"
        ```python
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        territoires.plot(column="population", cmap="viridis", edgecolor="black", legend=True, ax=axes[0])
        territoires.plot(column="population", cmap="OrRd", edgecolor="black", legend=True, ax=axes[1])
        axes[0].set_title("viridis")
        axes[1].set_title("OrRd")
        plt.tight_layout()
        plt.show()
        ```

        Ce choix n'est pas cosmétique : une carte qui doit distinguer un ordre de
        grandeurs (une palette séquentielle, du clair au foncé) ne se choisit pas comme
        une carte qui doit distinguer des catégories sans ordre (une palette qualitative,
        des teintes contrastées sans hiérarchie). Utiliser la mauvaise famille de palette
        est une erreur aussi fréquente en cartographie qu'en visualisation de données
        classique.

## Pour aller plus loin

- **Lire et écrire de vrais fichiers géographiques.** `territoires.to_file("territoires.geojson", driver="GeoJSON")`
  exporte au format GeoJSON, lisible par la plupart des outils SIG ; `to_file(..., driver="GPKG")`
  produit un GeoPackage, le format aujourd'hui recommandé pour remplacer le Shapefile
  (qui éclate les données en plusieurs fichiers séparés).
- **Les vraies frontières administratives.** Pour un projet réel, la référence en France
  est l'IGN (Admin Express) ou Natural Earth (`geodatasets`, le paquet qui a remplacé
  `geopandas.datasets`) pour une échelle mondiale.
- **`explore()`** produit une carte interactive dans un notebook, si `folium` est installé,
  utile pour explorer visuellement un grand jeu de données avant de fixer le code d'une
  carte statique.

## Ce qu'il faut retenir

Une GeoDataFrame est une DataFrame pandas avec une colonne `geometry` en plus, et hérite
de tout ce que sait faire pandas (`groupby`, filtrage, `value_counts`). Le CRS dit dans
quelle unité et selon quelle déformation les coordonnées sont exprimées : un calcul d'aire
ou de distance sur des coordonnées en degrés (`EPSG:4326`) donne un nombre sans usage
physique, il faut reprojeter dans un CRS métrique adapté à la zone étudiée avant de
mesurer quoi que ce soit. `sjoin` associe deux GeoDataFrames par relation spatiale plutôt
que par colonne commune ; `dissolve` fusionne des géométries par groupe, comme un
`groupby` qui agirait aussi sur la géométrie. Et une carte choroplèthe colore des formes
selon une valeur numérique, exactement comme une heatmap colore une grille.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer ce qu'une GeoDataFrame ajoute à une DataFrame ;
- [ ] dire pourquoi un calcul d'aire ou de distance exige de reprojeter dans un CRS
      métrique d'abord ;
- [ ] créer un buffer autour d'un point et calculer son aire ;
- [ ] faire une jointure spatiale avec `sjoin` et interpréter un résultat `NaN` ;
- [ ] produire une carte choroplèthe avec une palette de couleur adaptée à la donnée
      représentée.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP2](tp2-clustering.md){ .md-button .md-button--primary }
