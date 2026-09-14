# TP1. Manipuler des données avec pandas

**Durée : 2 h (+ 30 min pour les exercices bonus).**

## Objectifs

- Charger un jeu de données réel dans un DataFrame pandas, et l'explorer.
- Sélectionner, filtrer et transformer des lignes et des colonnes.
- Gérer des valeurs manquantes.
- Agréger des données par groupe.
- Lire et écrire des fichiers CSV, et produire des visualisations avec matplotlib.

## Prérequis

Des bases en Python (listes, fonctions, boucles). Aucune connaissance préalable de pandas
n'est supposée.

```bash
pip install pandas scikit-learn matplotlib numpy
```

## Ressources

- [Documentation pandas](https://pandas.pydata.org/docs/).
- Le jeu de données Iris, inclus dans scikit-learn : aucun téléchargement nécessaire.

---

## Étape 1. Charger et explorer un jeu de données (20 min)

Le jeu de données Iris décrit 150 fleurs par quatre mesures (longueur et largeur des
sépales et des pétales) et leur espèce. C'est l'un des jeux de données les plus utilisés
pour apprendre l'analyse de données, précisément parce qu'il est petit, propre, et déjà
connu de toute la communauté : vous pourrez comparer vos résultats à ceux de n'importe quel
tutoriel.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

iris = load_iris()
df = pd.DataFrame(iris.data, columns=["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"])
df["Species"] = [iris.target_names[i] for i in iris.target]

print(df.head())
print(df.shape)
```

`df.head()` affiche les cinq premières lignes, `df.shape` donne le nombre de lignes puis
de colonnes : `(150, 5)`.

!!! question "Exercice 1.1 : lire un DataFrame avant d'y toucher"
    Affichez `df.info()` (les types de chaque colonne et le nombre de valeurs non nulles),
    puis `df.describe()` (les statistiques descriptives des colonnes numériques). Combien
    de colonnes `describe()` couvre-t-il, et pourquoi pas toutes les colonnes de `df` ?

    **Résultat attendu :** `describe()` porte sur les 4 colonnes numériques, pas sur
    `Species` : une moyenne ou un écart-type n'a pas de sens pour une colonne de texte.

    ??? success "Corrigé"
        ```python
        print(df.info())
        print(df.describe())
        print(df.dtypes)
        ```

        `df.dtypes` confirme le diagnostic : quatre colonnes en `float64`, une en
        `object` (du texte). C'est ce même type qui explique pourquoi, à l'étape 5, une
        moyenne calculée sur `df` entier plutôt que sur ses colonnes numériques échoue.

## Étape 2. Sélectionner et filtrer (20 min)

Trois façons de choisir un sous-ensemble d'un DataFrame, qui répondent à des besoins
différents :

```python
print(df[["SepalLengthCm", "PetalLengthCm"]].head())          # par nom de colonne
print(df.loc[10:20, ["Species", "PetalWidthCm"]])              # par étiquette
print(df.iloc[:5, :2])                                          # par position
```

`loc` sélectionne par **étiquette** (le nom des colonnes, l'index des lignes), `iloc` par
**position** (le énième, en partant de 0). La différence compte dès que l'index d'un
DataFrame n'est plus une simple suite de nombres, par exemple après un filtrage.

Filtrer des lignes se fait avec une condition booléenne entre crochets, ou avec `query()`
pour une syntaxe plus lisible :

```python
grandes = df[df["SepalLengthCm"] > 6.0]
print(len(grandes), "fleurs avec SepalLengthCm > 6.0")

filtre = df[(df["SepalLengthCm"] > 5.5) & (df["PetalLengthCm"] < 4.0)]
print(len(filtre), "fleurs avec les deux conditions")

versicolor = df.query("Species == 'versicolor'")
print(len(versicolor), "fleurs versicolor")
```

!!! question "Exercice 2.1 : combiner sélection et filtrage"
    Écrivez, en une ligne, l'expression qui sélectionne la colonne `PetalLengthCm` des
    seules fleurs de l'espèce `setosa`.

    **Résultat attendu :** une série pandas de 50 valeurs (il y a 50 fleurs par espèce
    dans ce jeu de données), toutes inférieures à 2 cm.

    ??? success "Corrigé"
        ```python
        petales_setosa = df.loc[df["Species"] == "setosa", "PetalLengthCm"]
        print(len(petales_setosa))
        print(petales_setosa.describe())
        ```

        `df.loc[condition, colonne]` combine en une seule opération ce que l'exemple du
        dessus faisait en deux (`df[condition]` puis sélection de colonne) : c'est la même
        chose, écrite plus directement, et c'est la forme que vous rencontrerez le plus
        souvent dans du code pandas existant.

## Étape 3. Transformer un DataFrame (20 min)

Ajouter une colonne calculée, catégoriser une valeur numérique, trier, réindexer :

```python
df_travail = df.copy()
df_travail["PetalRatio"] = df_travail["PetalLengthCm"] / df_travail["PetalWidthCm"]

def categorise(longueur):
    if longueur < 5.0:
        return "petite"
    elif longueur < 6.5:
        return "moyenne"
    return "grande"

df_travail["Taille"] = df_travail["SepalLengthCm"].apply(categorise)
print(df_travail["Taille"].value_counts())

df_travail = df_travail[df_travail["SepalLengthCm"] >= 5.0]
df_travail = df_travail.sort_values(by="PetalLengthCm", ascending=False)
df_travail = df_travail.reset_index(drop=True)
print(df_travail.head())
```

Travailler sur `df.copy()` plutôt que sur `df` directement est une habitude à prendre tout
de suite : sans elle, une erreur de manipulation oblige à tout recharger depuis le début.

!!! question "Exercice 3.1 : une colonne sans condition écrite à la main"
    Refaites la colonne `Taille` avec `pd.cut()`, qui découpe une colonne numérique en
    catégories à partir de bornes, sans écrire de fonction `categorise`.

    **Résultat attendu :** les mêmes effectifs par catégorie qu'avec `apply(categorise)` :
    22 « petite », 93 « moyenne », 35 « grande ».

    ??? success "Corrigé"
        ```python
        taille_cut = pd.cut(
            df["SepalLengthCm"],
            bins=[-float("inf"), 5.0, 6.5, float("inf")],
            labels=["petite", "moyenne", "grande"],
            right=False,
        )
        print(taille_cut.value_counts())
        ```

        `pd.cut()` fait exactement ce qu'une fonction `apply` ferait à la main, mais en une
        opération vectorisée, plus rapide sur un grand jeu de données. Pour un DataFrame de
        150 lignes la différence est invisible ; sur un million de lignes, elle ne l'est
        plus.

        Remarquez que la comparaison se fait contre `df`, pas contre `df_travail` : ce
        dernier a déjà perdu ses fleurs « petite » un peu plus haut (le filtre
        `SepalLengthCm >= 5.0`). C'est `df`, jamais modifié depuis l'étape 1, qui reste la
        référence stable pour ce genre de comparaison.

## Étape 4. Gérer les valeurs manquantes (15 min)

Un jeu de données réel a presque toujours des trous. Simulons-en, pour apprendre à les
détecter et à les traiter :

```python
np.random.seed(42)
df_nan = df.copy()
indices = df_nan.sample(5, random_state=42).index
df_nan.loc[indices, "PetalWidthCm"] = np.nan

print(df_nan.isna().sum())
print(df_nan[df_nan.isna().any(axis=1)])
```

`isna().sum()` compte les valeurs manquantes par colonne : ici, cinq dans
`PetalWidthCm`, zéro ailleurs.

!!! question "Exercice 4.1 : deux façons de traiter un manque, et leur différence"
    Créez deux versions de `df_nan` : une où les valeurs manquantes de `PetalWidthCm`
    sont remplacées par la moyenne de la colonne (`fillna`), une où les lignes concernées
    sont supprimées (`dropna`). Comparez le nombre de lignes des deux résultats.

    **Résultat attendu :** la version `fillna` garde 150 lignes, la version `dropna` n'en
    garde que 145. Le choix entre les deux n'est pas neutre : `fillna` invente une valeur,
    `dropna` perd de l'information sur les quatre autres colonnes de ces lignes-là.

    ??? success "Corrigé"
        ```python
        df_rempli = df_nan.copy()
        df_rempli["PetalWidthCm"] = df_rempli["PetalWidthCm"].fillna(df_nan["PetalWidthCm"].mean())
        print(len(df_rempli), "lignes après fillna")

        df_sans_nan = df_nan.dropna()
        print(len(df_sans_nan), "lignes après dropna")
        ```

        Il n'y a pas de bon choix universel entre les deux. `dropna` convient quand les
        lignes incomplètes sont rares et que l'analyse ne peut pas tolérer de valeur
        inventée ; `fillna` convient quand en perdre trop coûterait plus cher que
        l'approximation introduite. Un jeu de données réel avec 30 % de valeurs
        manquantes sur une colonne ne se traite pas comme celui-ci, où il y en a 3 %.

## Étape 5. Agrégations et regroupements (20 min)

`groupby` répond à la question « une statistique, mais pour chaque groupe » : ici, chaque
espèce.

```python
print(df["Species"].value_counts())
print(df.groupby("Species").mean(numeric_only=True).round(2))
print(df.groupby("Species").agg(["mean", "std", "min", "max"]))
```

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant « la moyenne de chaque colonne de `df` », sans préciser
    `numeric_only=True` ni exclure `Species` vous-même. Exécutez le code obtenu tel quel :

    ```python
    try:
        print(df.mean())
    except TypeError as erreur:
        print("Erreur :", erreur)
    ```

    `df.mean()` sur le DataFrame entier lève une `TypeError`, parce que `Species` est du
    texte et qu'une moyenne de texte n'a pas de sens. `df.corr()` échoue de la même façon.
    Un assistant qui a appris sur d'anciennes versions de pandas propose parfois du code
    qui ignorait silencieusement les colonnes non numériques ; les versions récentes
    refusent explicitement, ce qui est plus sûr mais casse du code plus ancien recopié
    tel quel. Retenez le réflexe : sélectionner les colonnes numériques avant une
    opération numérique, plutôt que d'espérer que pandas le fasse à votre place.

!!! question "Exercice 5.1 : un tableau croisé"
    Construisez un tableau croisé entre `Species` et une colonne `Taille` (reprenez la
    fonction `categorise` de l'étape 3), avec `pd.crosstab()`.

    **Résultat attendu :** un tableau à trois lignes (les espèces) et trois colonnes (les
    tailles), dont la somme de toutes les cellules vaut 150. Les *setosa* n'ont aucune
    fleur « grande », les *virginica* n'en ont presque aucune « petite ».

    ??? success "Corrigé"
        ```python
        taille = df["SepalLengthCm"].apply(categorise)
        tableau = pd.crosstab(df["Species"], taille)
        print(tableau)
        ```

        Ici encore, la colonne `Taille` se recalcule depuis `df`, pas depuis `df_travail`,
        pour la même raison qu'à l'exercice 3.1 : `df_travail` a changé de forme en cours
        de route (filtré, trié, réindexé), et croiser deux colonnes qui ne portent plus
        les mêmes lignes sous le même index produirait un résultat qui semble valide, sans
        l'être.

        Ce tableau croise deux informations qu'aucune des deux statistiques prises
        séparément ne montre : la taille moyenne d'une espèce (étape précédente) ne dit
        pas si cette espèce est homogène ou étalée sur toutes les catégories de taille.
        C'est exactement ce que révèle ce tableau : *versicolor* et *virginica* se
        chevauchent sur la catégorie « moyenne », *setosa* ne déborde jamais vers
        « grande ».

## Étape 6. Lire et écrire des fichiers CSV (10 min)

```python
df.to_csv("iris.csv", index=False)
df_relu = pd.read_csv("iris.csv")
print("Identiques :", df.equals(df_relu))
```

!!! question "Exercice 6.1 : un export avec un autre séparateur"
    Exportez `df` en CSV avec `;` comme séparateur, rechargez-le avec le bon paramètre, et
    vérifiez à nouveau l'égalité.

    **Résultat attendu :** `True` dans les deux cas, `,` et `;`, à condition d'indiquer le
    bon séparateur au rechargement. Un fichier rechargé avec le **mauvais** séparateur ne
    lève pourtant aucune erreur : il produit un DataFrame à une seule colonne, tout le
    contenu collé ensemble.

    ??? success "Corrigé"
        ```python
        df.to_csv("iris_pv.csv", index=False, sep=";")
        df_pv = pd.read_csv("iris_pv.csv", sep=";")
        print("Identiques :", df.equals(df_pv))

        df_pv_mal_lu = pd.read_csv("iris_pv.csv")  # sans préciser sep=";"
        print(df_pv_mal_lu.shape, "colonnes au lieu de 5")

        import os
        os.remove("iris.csv")
        os.remove("iris_pv.csv")
        ```

        C'est un piège silencieux classique : un fichier mal relu ne plante presque
        jamais, il produit juste un résultat absurde (une seule colonne au lieu de cinq),
        que rien ne signale tant que vous ne regardez pas `df.shape` ou `df.head()`.
        Prenez l'habitude de vérifier la forme d'un DataFrame juste après tout chargement.

!!! tip "Pour aller plus loin : le CSV ne garde pas tous les types"
    Cet exercice fonctionne parce que `Species` est ici du texte simple. Si vous convertissez
    `Species` en type `category` avant l'export (`df["Species"] = df["Species"].astype("category")`),
    `df.equals(df_relu)` redevient `False` après un aller-retour CSV : le format CSV ne
    connaît que du texte, pas le type `category` de pandas, qui redevient une simple chaîne
    de caractères à la relecture. Un format comme Parquet préserve les types ; le CSV,
    universel et lisible par un humain, ne le fait jamais.

## Étape 7. Visualiser avec matplotlib (25 min)

```python
plt.figure(figsize=(8, 5))
plt.hist(df["SepalLengthCm"], bins=15, edgecolor="black")
plt.title("Distribution de SepalLengthCm")
plt.xlabel("SepalLengthCm")
plt.ylabel("Fréquence")
plt.tight_layout()
plt.show()
```

```python
couleurs = {"setosa": "#e74c3c", "versicolor": "#3498db", "virginica": "#2ecc71"}
plt.figure(figsize=(8, 6))
for espece in df["Species"].unique():
    sous_ensemble = df[df["Species"] == espece]
    plt.scatter(
        sous_ensemble["SepalLengthCm"],
        sous_ensemble["PetalLengthCm"],
        label=espece,
        color=couleurs[espece],
        alpha=0.7,
    )
plt.xlabel("SepalLengthCm")
plt.ylabel("PetalLengthCm")
plt.legend()
plt.tight_layout()
plt.show()
```

Sur ce nuage de points coloré par espèce, la séparation visuelle entre les trois groupes
saute aux yeux, en particulier entre *setosa* et les deux autres espèces : c'est la
raison pour laquelle Iris reste, plus de quatre-vingts ans après sa publication, le jeu de
données par défaut pour illustrer une classification.

!!! question "Exercice 7.1 : une matrice de corrélation en heatmap"
    Affichez la matrice de corrélation des quatre colonnes numériques avec
    `plt.imshow()`, une échelle de couleur (`plt.colorbar()`), et les noms de colonnes en
    étiquettes des axes.

    **Résultat attendu :** une image 4×4, avec une diagonale à 1 (une colonne est
    parfaitement corrélée à elle-même), et la plus forte corrélation hors diagonale entre
    `PetalLengthCm` et `PetalWidthCm` (environ `0.96`).

    ??? success "Corrigé"
        ```python
        colonnes = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]
        correlation = df[colonnes].corr()
        print(correlation.round(2))

        plt.figure(figsize=(6, 5))
        plt.imshow(correlation, cmap="RdYlBu_r", vmin=-1, vmax=1)
        plt.colorbar(label="Corrélation")
        plt.xticks(range(len(colonnes)), colonnes, rotation=45, ha="right")
        plt.yticks(range(len(colonnes)), colonnes)
        plt.tight_layout()
        plt.show()
        ```

        Retenez pourquoi cet exercice suit directement l'exercice 5.1 dans la même
        logique : un tableau de nombres (`correlation.round(2)`) et sa version visuelle
        (la heatmap) disent la même chose, mais la seconde fait immédiatement ressortir
        que `SepalWidthCm` est la seule colonne à corréler négativement avec les trois
        autres, un fait qu'il faut chercher activement dans le tableau de nombres.

## Pour aller plus loin

- **Un outlier révélateur.** La fleur au plus grand `PetalRatio` (`PetalLengthCm /
  PetalWidthCm`) est une *setosa*, avec un ratio d'environ `15`, très supérieur aux
  autres. Est-ce une anomalie de mesure ? Regardez `PetalWidthCm` pour cette fleur avant
  de conclure.
- **Coefficient de variation.** `écart-type / moyenne`, par espèce et par colonne, mesure
  la dispersion relative plutôt qu'absolue : une colonne dont les valeurs sont toutes
  proches de 5 avec un écart-type de 1 est plus variable, relativement, qu'une colonne
  autour de 50 avec le même écart-type absolu.
- **Repérer les fleurs atypiques.** Avec `apply()` sur chaque ligne, marquez une fleur
  comme « typique » si toutes ses mesures sont à moins d'un écart-type de la moyenne de
  son espèce. Combien en trouvez-vous, et à quoi ressemble une fleur qui ne l'est pas ?

## Ce qu'il faut retenir

Un DataFrame se sélectionne par nom (`df[...]`), par étiquette (`loc`), ou par position
(`iloc`). Un filtre est une condition booléenne entre crochets, ou une chaîne lisible
avec `query()`. `groupby` répond à « une statistique, par groupe » ; `agg()` en calcule
plusieurs à la fois. Une opération numérique (`mean`, `corr`) échoue sur un DataFrame qui
contient encore une colonne de texte : sélectionnez vos colonnes numériques avant, ne
comptez pas sur pandas pour deviner votre intention. Le format CSV ne connaît que du
texte : un type comme `category` ne survit pas à un aller-retour, contrairement à un
`float64`. Et une visualisation révèle souvent en un coup d'œil ce qu'un tableau de
nombres demande de chercher activement.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer la différence entre `loc` et `iloc` ;
- [ ] écrire un filtre à deux conditions sur un DataFrame ;
- [ ] choisir entre `fillna` et `dropna` pour une colonne à valeurs manquantes, et
      justifier le choix ;
- [ ] dire pourquoi `df.mean()` peut échouer sur un DataFrame qui contient une colonne de
      texte, et comment l'éviter ;
- [ ] produire un tableau croisé avec `pd.crosstab()` et une visualisation avec
      matplotlib pour la même question.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.
