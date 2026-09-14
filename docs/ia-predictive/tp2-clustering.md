# TP2. Clustering : méthodes modernes et évaluation

**Durée : 2 h 30.**

## Objectifs

- Regrouper des observations non étiquetées avec K-Means, et connaître ses limites.
- Comprendre pourquoi un clustering par densité (DBSCAN, HDBSCAN) résout certains cas où
  K-Means échoue, sans être universellement meilleur.
- Choisir un nombre de clusters avec une métrique, plutôt qu'à l'œil.
- Réduire la dimension d'un jeu de données pour le visualiser après clustering.

## Prérequis

Le [TP1](tp1-pandas.md) : manipuler un DataFrame. Bibliothèques supplémentaires :

```bash
pip install scikit-learn umap-learn hdbscan matplotlib numpy pandas
```

## Ressources

- [Clustering, documentation scikit-learn](https://scikit-learn.org/stable/modules/clustering.html).
- [Documentation HDBSCAN](https://hdbscan.readthedocs.io/).
- [Documentation UMAP](https://umap-learn.readthedocs.io/).

!!! info "Un jeu de données synthétique, pas Mall Customers"
    L'exercice classique de ce TP utilise le jeu Kaggle *Mall Customers* (âge, revenu,
    score de dépense). Pour rester autonome sans compte ni téléchargement, ce TP génère un
    jeu **synthétique** de même structure et du même esprit (200 à 300 clients fictifs,
    trois variables), avec une graine fixe pour que les résultats soient reproductibles.

---

## Étape 1. K-Means, et pourquoi il faut normaliser (25 min)

```python
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score

rng = np.random.default_rng(0)
n_par_groupe = 60
centres = [(25, 20), (25, 80), (45, 50), (65, 20), (65, 80)]
vrais_groupes = []
morceaux = []
for i, (cx, cy) in enumerate(centres):
    age = rng.normal(30, 6, n_par_groupe)
    revenu = rng.normal(cx * 1000, 8000, n_par_groupe)      # en euros, ordre de grandeur 25 000-65 000
    score = rng.normal(cy, 10, n_par_groupe).clip(1, 100)   # score de dépense, 1-100
    morceaux.append(pd.DataFrame({"age": age, "revenu": revenu, "score_depense": score}))
    vrais_groupes += [i] * n_par_groupe
clients = pd.concat(morceaux, ignore_index=True)

X = clients[["age", "revenu", "score_depense"]].values
print(clients.describe().round(1))
```

`revenu` varie sur des dizaines de milliers d'euros, `score_depense` sur une échelle
1-100 : deux échelles très différentes. K-Means mesure une distance euclidienne entre
points, donc une variable à grande échelle domine mécaniquement le calcul, au détriment
des autres.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant d'appliquer K-Means sur ce DataFrame. Il propose souvent
    `KMeans(n_clusters=5).fit(X)` directement, sans normaliser. Comparez :

    ```python
    km_brut = KMeans(n_clusters=5, random_state=42, n_init=10).fit(X)
    print("ARI sans normalisation :", round(adjusted_rand_score(vrais_groupes, km_brut.labels_), 3))

    Xs = StandardScaler().fit_transform(X)
    km_norm = KMeans(n_clusters=5, random_state=42, n_init=10).fit(Xs)
    print("ARI avec normalisation :", round(adjusted_rand_score(vrais_groupes, km_norm.labels_), 3))
    ```

    L'ARI (*Adjusted Rand Index*) mesure ici l'accord entre les clusters trouvés et les
    cinq groupes réellement utilisés pour générer les données (1 = accord parfait, 0 =
    accord au hasard). Sans normalisation, l'ARI vaut environ `0.295` ; avec
    `StandardScaler`, il monte à `0.58`, presque le double. Un assistant qui connaît
    K-Means en théorie ne pense pas toujours à normaliser en pratique.

!!! question "Exercice 1.1 : K-Means échoue sur des clusters non convexes"
    Générez `make_moons(n_samples=500, noise=0.1, random_state=42)` (deux croissants
    entrelacés) et appliquez K-Means avec `n_clusters=2`. Mesurez l'ARI contre les vraies
    étiquettes de `make_moons`.

    **Résultat attendu :** un ARI autour de `0.27`, loin de `1`. K-Means suppose des
    clusters à peu près sphériques (il assigne chaque point au centre le plus proche) ; un
    croissant n'est pas une forme sphérique, K-Means le découpe donc n'importe comment.

    ??? success "Corrigé"
        ```python
        from sklearn.datasets import make_moons

        X_moons, y_moons = make_moons(n_samples=500, noise=0.1, random_state=42)
        km_moons = KMeans(n_clusters=2, random_state=42, n_init=10).fit_predict(X_moons)
        print("ARI K-Means sur make_moons :", round(adjusted_rand_score(y_moons, km_moons), 3))
        ```

        Ce n'est pas un problème de réglage : aucune valeur de `n_clusters` ni
        d'initialisation ne corrige ce défaut, parce qu'il est structurel à la méthode.
        L'étape suivante montre une famille d'algorithmes construite sur un principe
        différent, justement pour ce genre de forme.

## Étape 2. DBSCAN : des clusters définis par la densité (25 min)

DBSCAN ne suppose aucune forme : un cluster est une région dense de points, séparée des
autres par une région clairsemée. Deux paramètres suffisent : `eps` (le rayon de
voisinage) et `min_samples` (le nombre de voisins minimal pour qu'un point soit « dense »).

```python
from sklearn.cluster import DBSCAN

db_moons = DBSCAN(eps=0.2, min_samples=5).fit_predict(X_moons)
print("ARI DBSCAN sur make_moons :", round(adjusted_rand_score(y_moons, db_moons), 3))
print("clusters trouvés :", sorted(set(db_moons)))
```

!!! question "Exercice 2.1 : choisir `eps` avec le graphe des k-distances"
    Plutôt que de deviner `eps`, tracez la distance de chaque point à son 5ᵉ plus proche
    voisin, triée par ordre croissant (`NearestNeighbors(n_neighbors=5)`). Le « coude » de
    cette courbe est une estimation raisonnable de `eps`.

    **Résultat attendu :** une courbe globalement croissante avec un coude net autour
    d'une valeur proche de `0.15` à `0.2`, cohérente avec le `eps=0.2` utilisé ci-dessus.

    ??? success "Corrigé"
        ```python
        from sklearn.neighbors import NearestNeighbors

        voisins = NearestNeighbors(n_neighbors=5).fit(X_moons)
        distances, _ = voisins.kneighbors(X_moons)
        distances_triees = np.sort(distances[:, -1])

        import matplotlib.pyplot as plt
        plt.figure(figsize=(7, 4))
        plt.plot(distances_triees)
        plt.xlabel("Points, triés")
        plt.ylabel("Distance au 5ᵉ plus proche voisin")
        plt.title("Graphe des k-distances")
        plt.tight_layout()
        plt.show()

        print("distance au coude, approx :", round(distances_triees[480], 3))
        ```

        Ce graphe répond à une question précise : « à partir de quelle distance la
        majorité des points cessent-ils d'avoir un voisinage dense ? ». Avant le coude,
        les distances sont petites et régulières (l'intérieur des clusters) ; après, elles
        augmentent brusquement (les points isolés, ou la transition entre clusters). C'est
        la même logique que la méthode du coude sur l'inertie de K-Means, appliquée à une
        autre quantité.

## Étape 3. Combien de clusters ? Le score de silhouette (25 min)

Sur le jeu de clients (étape 1), rien n'indique a priori qu'il faille `5` clusters. Le
score de silhouette mesure, pour chaque point, s'il est plus proche de son propre cluster
que du cluster voisin le plus proche (entre `-1` et `1`, plus haut est meilleur) :

```python
from sklearn.metrics import silhouette_score

resultats = []
for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(Xs)
    resultats.append((k, km.inertia_, silhouette_score(Xs, km.labels_)))

for k, inertie, silhouette in resultats:
    print(f"k={k} : inertie={inertie:.1f}, silhouette={silhouette:.3f}")
```

!!! question "Exercice 3.1 : le score retrouve-t-il le bon nombre de groupes ?"
    Identifiez le `k` qui maximise le score de silhouette dans la liste `resultats`
    ci-dessus. Correspond-il au nombre de groupes réellement utilisés pour générer
    `clients` à l'étape 1 (variable `centres`) ?

    **Résultat attendu :** le maximum de silhouette est atteint à `k=5` (silhouette
    d'environ `0.347`), exactement le nombre de centres utilisés à la génération. Ce n'est
    pas garanti en général (un vrai jeu de données n'a pas de « bon » nombre de clusters
    connu d'avance), mais ça confirme que la métrique fonctionne sur un cas où la réponse
    est connue.

    ??? success "Corrigé"
        ```python
        meilleur_k, _, meilleure_silhouette = max(resultats, key=lambda t: t[2])
        print(f"meilleur k : {meilleur_k}, silhouette : {meilleure_silhouette:.3f}")
        print("nombre de centres à la génération :", len(centres))
        ```

        La méthode du coude sur l'inertie (la première colonne de `resultats`) pointe
        souvent dans la même direction, mais elle demande un jugement visuel (« où
        l'inertie cesse-t-elle de baisser vite ? ») là où la silhouette donne un nombre
        directement comparable entre valeurs de `k`. Les deux se complètent plutôt qu'elles
        ne s'excluent.

## Étape 4. HDBSCAN : plus robuste, mais pas toujours meilleur (25 min)

HDBSCAN prolonge DBSCAN en évitant de choisir `eps` à la main, et en s'adaptant à des
densités variables selon les régions. Sur `make_moons`, il fait aussi bien que DBSCAN.
Sur le jeu de clients (des groupes à peu près sphériques, exactement l'hypothèse que fait
K-Means), la comparaison est plus intéressante :

```python
import hdbscan

clusterer = hdbscan.HDBSCAN(min_cluster_size=15, min_samples=5)
labels_hdbscan = clusterer.fit_predict(Xs)

print("clusters trouvés par HDBSCAN :", sorted(set(labels_hdbscan)))
print(pd.Series(labels_hdbscan).value_counts())
print("ARI HDBSCAN vs vrais groupes :", round(adjusted_rand_score(vrais_groupes, labels_hdbscan), 3))
print("ARI K-Means vs vrais groupes :", round(adjusted_rand_score(vrais_groupes, km_norm.labels_), 3))
```

!!! question "Exercice 4.1 : pourquoi HDBSCAN fait moins bien ici"
    Comptez combien de clusters distincts (hors bruit, étiqueté `-1`) HDBSCAN trouve sur
    `Xs`. Comparez à `5`, le vrai nombre de groupes. Avec ce que vous savez du principe de
    HDBSCAN (des régions denses séparées par des creux de densité), pourquoi cinq
    gaussiennes qui se chevauchent légèrement sont-elles plus difficiles pour HDBSCAN que
    pour K-Means ?

    **Résultat attendu :** HDBSCAN ne trouve que `2` clusters (plus du bruit) sur ce jeu,
    contre `5` pour K-Means, et son ARI (`0.139`) est nettement inférieur à celui de
    K-Means (`0.58`). Quand des groupes gaussiens se touchent, la densité ne baisse jamais
    vraiment entre eux : il n'y a pas de « creux » net à détecter, alors que K-Means, qui
    ne cherche pas de creux mais des centres, n'a pas ce problème.

    ??? success "Corrigé"
        ```python
        nb_clusters = len(set(labels_hdbscan) - {-1})
        print("clusters trouvés (hors bruit) :", nb_clusters, "contre", len(centres), "réels")
        ```

        Retenez la leçon au delà de ce cas précis : DBSCAN et HDBSCAN excellent quand les
        clusters ont des formes arbitraires séparées par du vide (comme `make_moons`), et
        perdent leur avantage quand les clusters sont convexes et se touchent, exactement
        le terrain où K-Means est le plus à l'aise. « Plus récent » ou « plus sophistiqué »
        ne veut pas dire « meilleur en toutes circonstances » : le bon algorithme dépend de
        la forme réelle des données, jamais de sa date de publication.

## Étape 5. Réduire la dimension pour visualiser (20 min)

Le jeu de clients a trois variables : impossible à représenter directement sur un graphique
à deux axes. PCA et UMAP projettent les données en deux dimensions en essayant de préserver
au mieux leur structure :

```python
from sklearn.decomposition import PCA
import umap
import matplotlib.pyplot as plt

X_pca = PCA(n_components=2, random_state=42).fit_transform(Xs)
X_umap = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42).fit_transform(Xs)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=km_norm.labels_, cmap="tab10", alpha=0.7)
axes[0].set_title("PCA")
axes[1].scatter(X_umap[:, 0], X_umap[:, 1], c=km_norm.labels_, cmap="tab10", alpha=0.7)
axes[1].set_title("UMAP")
plt.tight_layout()
plt.show()
```

!!! question "Exercice 5.1 : la variance expliquée par la PCA"
    Affichez `pca.explained_variance_ratio_` (nécessite de refaire `pca = PCA(...)` avant
    `fit_transform` pour garder l'objet). Que signifie la somme de ces deux valeurs ?

    **Résultat attendu :** deux valeurs dont la somme est inférieure à `1` : c'est la
    proportion de la variance totale des trois variables originales que les deux axes de
    la PCA parviennent à représenter. Une projection en 2D perd nécessairement une partie
    de l'information d'un jeu à 3 variables ou plus.

    ??? success "Corrigé"
        ```python
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(Xs)
        print(pca.explained_variance_ratio_.round(3))
        print("variance totale représentée :", round(pca.explained_variance_ratio_.sum(), 3))
        ```

        Une PCA qui ne représente que 60 % de la variance signifie que 40 % de ce qui
        distingue les points entre eux n'apparaît pas sur le graphique : deux points
        proches sur le graphique PCA peuvent donc être plus éloignés qu'ils n'en ont l'air
        sur la troisième variable, absente de la projection. UMAP n'a pas cette limite de
        variance expliquée, mais il ne préserve pas non plus les distances globales de
        façon aussi directement quantifiable : les deux méthodes se lisent différemment,
        aucune n'est une carte fidèle à 100 % des données originales.

## Pour aller plus loin

- **Clustering hiérarchique** (`AgglomerativeClustering`) construit un dendrogramme, un
  arbre de fusions successives, qui évite de fixer un nombre de clusters à l'avance et se
  lit visuellement à n'importe quelle hauteur de coupe.
- **Gaussian Mixture Models** (`sklearn.mixture.GaussianMixture`) font un clustering
  « souple » : chaque point reçoit une probabilité d'appartenance à chaque cluster plutôt
  qu'une assignation unique, utile quand les frontières entre groupes sont floues.
- **Les métriques externes** (`adjusted_rand_score` déjà vu, mais aussi
  `normalized_mutual_info_score`, `v_measure_score`) exigent de connaître les vraies
  étiquettes, ce qui n'est presque jamais le cas en pratique : elles servent surtout à
  valider une méthode sur un jeu de données de test avant de l'appliquer à l'aveugle.

## Ce qu'il faut retenir

K-Means suppose des clusters à peu près sphériques et de taille comparable, et exige de
normaliser les variables avant de mesurer une distance entre elles. DBSCAN et HDBSCAN
définissent un cluster par la densité plutôt que par une forme, ce qui leur permet de
réussir là où K-Means échoue (des clusters non convexes) et de rater là où K-Means
excelle (des groupes convexes qui se touchent). Le score de silhouette aide à choisir un
nombre de clusters sans étiquette connue. Et une réduction de dimension (PCA, UMAP) rend
un jeu de données à plusieurs variables visualisable en 2D, au prix d'une perte
d'information qu'il faut savoir quantifier ou, pour UMAP, garder à l'esprit.

## Auto-évaluation

Avant de passer au TP suivant, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer pourquoi normaliser les variables change le résultat de K-Means ;
- [ ] citer un cas où DBSCAN réussit là où K-Means échoue, et un cas inverse ;
- [ ] utiliser le score de silhouette pour choisir un nombre de clusters ;
- [ ] distinguer ce que PCA et UMAP préservent chacun d'une donnée à plusieurs variables ;
- [ ] dire pourquoi un algorithme plus récent n'est pas automatiquement meilleur.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP2bis (réduction de dimension)](tp2bis-reduction-dimension.md){ .md-button .md-button--primary }
