# TP3. Classification

**Durée : 2 h.**

## Objectifs

- Entraîner et comparer trois familles de classifieurs : arbre de décision, forêt
  aléatoire, boosting de gradient (XGBoost).
- Séparer correctement un jeu de données en entraînement et test, avec stratification.
- Choisir la bonne métrique selon ce qu'une erreur coûte réellement.
- Lire une matrice de confusion et une importance de variables.

## Prérequis

Le [TP1](tp1-pandas.md) : manipuler un DataFrame.

```bash
pip install scikit-learn xgboost matplotlib pandas numpy
```

## Ressources

- [Documentation scikit-learn, arbres de décision](https://scikit-learn.org/stable/modules/tree.html).
- [Documentation scikit-learn, métriques de classification](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics).
- [Documentation XGBoost](https://xgboost.readthedocs.io/).

---

## Étape 1. Un jeu de données à deux classes (15 min)

Le jeu **Breast Cancer Wisconsin**, inclus dans scikit-learn, décrit 569 tumeurs par 30
mesures géométriques issues d'une image (rayon, périmètre, texture...), avec une étiquette
binaire : maligne ou bénigne. C'est un cas d'école pour la classification, avec un vrai
enjeu derrière chaque erreur.

```python
import pandas as pd
from sklearn.datasets import load_breast_cancer

donnees = load_breast_cancer()
X = pd.DataFrame(donnees.data, columns=donnees.feature_names)
y = pd.Series(donnees.target, name="target")

print(X.shape)
print(dict(zip([0, 1], donnees.target_names)))
print(y.value_counts())
```

`X.shape` vaut `(569, 30)`. La cible encode `0` pour « malignant » (maligne) et `1` pour
« benign » (bénigne), avec 212 tumeurs malignes contre 357 bénignes : un déséquilibre
modéré, à garder en tête pour l'étape 5.

## Étape 2. Séparer entraînement et test, avec stratification (15 min)

Évaluer un modèle sur les données qui ont servi à l'entraîner ne mesure rien
d'utile : il faut des données que le modèle n'a jamais vues.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print(X_train.shape, X_test.shape)
print(y_train.value_counts(normalize=True).round(3))
print(y_test.value_counts(normalize=True).round(3))
```

!!! question "Exercice 2.1 : ce que change la stratification"
    Refaites la séparation sans `stratify=y`, et comparez la proportion de tumeurs
    malignes dans le jeu de test des deux versions.

    **Résultat attendu :** avec `stratify=y`, la proportion de malignes dans le test
    (`36.8 %`) est quasi identique à celle du jeu complet (`37.3 %`). Sans stratification,
    l'écart peut être plus marqué, par simple effet du tirage aléatoire.

    ??? success "Corrigé"
        ```python
        X_train2, X_test2, y_train2, y_test2 = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        print("Sans stratification :", y_test2.value_counts(normalize=True).round(3).to_dict())
        print("Avec stratification :", y_test.value_counts(normalize=True).round(3).to_dict())
        ```

        Sur un jeu de 569 lignes et deux classes, l'écart reste modeste. Le problème
        devient sérieux sur un jeu plus petit ou plus déséquilibré : sans stratification,
        un tirage malchanceux peut produire un jeu de test qui ne contient presque aucun
        exemple de la classe minoritaire, rendant toute métrique sur cette classe
        instable.

## Étape 3. Un modèle de référence : l'arbre de décision (25 min)

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

arbre = DecisionTreeClassifier(max_depth=4, random_state=42)
arbre.fit(X_train, y_train)

pred_arbre = arbre.predict(X_test)
print("Exactitude test :", round(accuracy_score(y_test, pred_arbre), 3))
print(confusion_matrix(y_test, pred_arbre))
```

`max_depth=4` limite volontairement la profondeur de l'arbre. Sans cette limite, un arbre
de décision peut apprendre les données d'entraînement par cœur.

!!! question "Exercice 3.1 : voir le surapprentissage"
    Entraînez un second arbre, sans limite de profondeur (`max_depth=None`), et comparez
    son exactitude sur l'entraînement et sur le test à celle de l'arbre de l'étape 3.

    **Résultat attendu :** l'arbre non limité atteint `1.0` d'exactitude sur
    l'entraînement (il a mémorisé chaque exemple) mais seulement `0.912` sur le test,
    moins bien que l'arbre à profondeur 4, qui obtient `0.987` en entraînement et `0.939`
    en test. Un modèle parfait sur l'entraînement n'est pas un modèle qui généralise
    mieux, c'est souvent l'inverse.

    ??? success "Corrigé"
        ```python
        arbre_profond = DecisionTreeClassifier(max_depth=None, random_state=42)
        arbre_profond.fit(X_train, y_train)

        print("Profondeur libre : train", round(arbre_profond.score(X_train, y_train), 3),
              "test", round(arbre_profond.score(X_test, y_test), 3))
        print("Profondeur 4     : train", round(arbre.score(X_train, y_train), 3),
              "test", round(arbre.score(X_test, y_test), 3))
        ```

        Le nom de ce phénomène est le **surapprentissage** (*overfitting*) : le modèle a
        appris les particularités, y compris le bruit, des 455 exemples d'entraînement,
        au lieu d'apprendre la règle générale qui les sous-tend. Limiter la profondeur est
        une des façons les plus directes de le combattre pour un arbre de décision.

## Étape 4. Combiner des arbres : la forêt aléatoire (25 min)

Une forêt aléatoire entraîne de nombreux arbres, chacun sur un tirage aléatoire des
exemples et des variables, puis fait voter l'ensemble. Le vote lisse les erreurs
individuelles de chaque arbre.

```python
from sklearn.ensemble import RandomForestClassifier

foret = RandomForestClassifier(n_estimators=200, random_state=42)
foret.fit(X_train, y_train)

pred_foret = foret.predict(X_test)
print("Exactitude test :", round(accuracy_score(y_test, pred_foret), 3))

importances = pd.Series(foret.feature_importances_, index=X.columns).sort_values(ascending=False)
print(importances.head(5))
```

!!! question "Exercice 4.1 : la forêt bat-elle l'arbre unique ?"
    Comparez l'exactitude de la forêt à celle de l'arbre à profondeur 4 de l'étape 3.
    Les cinq variables les plus importantes selon la forêt ont-elles un lien avec la
    taille ou la forme de la tumeur ?

    **Résultat attendu :** la forêt atteint `0.956` d'exactitude, contre `0.939` pour
    l'arbre unique. Les variables les plus importantes (`worst perimeter`, `worst area`,
    `worst concave points`...) mesurent toutes la taille ou l'irrégularité du contour :
    cohérent avec ce qu'on sait cliniquement d'une tumeur maligne.

    ??? success "Corrigé"
        ```python
        print("Foret  :", round(accuracy_score(y_test, pred_foret), 3))
        print("Arbre  :", round(accuracy_score(y_test, pred_arbre), 3))
        print(importances.head(5))
        ```

        La forêt ne fait presque jamais moins bien qu'un arbre unique, pour une raison
        structurelle : dans le pire des cas, le vote majoritaire se comporte comme un
        arbre moyen ; dans le meilleur des cas, les erreurs de chaque arbre, différentes
        les unes des autres, s'annulent en partie au moment du vote.

## Étape 5. Le boosting séquentiel : XGBoost (25 min)

Une forêt aléatoire entraîne ses arbres indépendamment. XGBoost les entraîne l'un après
l'autre, chaque nouvel arbre corrigeant les erreurs de l'ensemble déjà construit.

```python
import xgboost as xgb

modele_xgb = xgb.XGBClassifier(
    n_estimators=200, learning_rate=0.1, max_depth=3, random_state=42, eval_metric="logloss"
)
modele_xgb.fit(X_train, y_train)

pred_xgb = modele_xgb.predict(X_test)
print("Exactitude test :", round(accuracy_score(y_test, pred_xgb), 3))
```

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant d'entraîner un `XGBClassifier`. Une réponse générée à partir
    d'anciens tutoriels ajoute souvent `use_label_encoder=True` aux paramètres. Testez :

    ```python
    import warnings
    with warnings.catch_warnings(record=True) as enregistrees:
        warnings.simplefilter("always")
        xgb.XGBClassifier(use_label_encoder=True, eval_metric="logloss")
        for w in enregistrees:
            print(w.category.__name__, ":", w.message)
    ```

    Le paramètre est accepté sans erreur, mais silencieusement ignoré (un simple
    avertissement, pas un plantage) : les versions récentes de xgboost encodent les
    étiquettes automatiquement et n'ont plus besoin de ce réglage, supprimé depuis
    plusieurs versions majeures. Un code qui « marche » n'est pas toujours un code qui
    fait ce que son auteur croit qu'il fait.

!!! question "Exercice 5.1 : learning_rate contre n_estimators"
    Entraînez deux variantes : `learning_rate=0.01` avec `n_estimators=200`, puis
    `learning_rate=0.3` avec les mêmes `n_estimators=200`. Laquelle est la plus proche du
    modèle de référence (`learning_rate=0.1`) en exactitude ?

    **Résultat attendu :** un `learning_rate` trop petit (`0.01`) sous-apprend avec
    seulement 200 arbres (chaque arbre corrige trop peu), un `learning_rate` trop grand
    (`0.3`) risque de sur-apprendre plus vite. Le réglage par défaut de cette page
    (`0.1`) atteint `0.947`, une valeur intermédiaire n'est pas un hasard.

    ??? success "Corrigé"
        ```python
        for taux in (0.01, 0.1, 0.3):
            modele = xgb.XGBClassifier(
                n_estimators=200, learning_rate=taux, max_depth=3, random_state=42, eval_metric="logloss"
            )
            modele.fit(X_train, y_train)
            print(f"learning_rate={taux} : exactitude test =", round(modele.score(X_test, y_test), 3))
        ```

        `learning_rate` et `n_estimators` se compensent partiellement : un taux plus
        faible demande plus d'arbres pour atteindre la même capacité d'apprentissage. Les
        régler indépendamment, sans regarder les deux ensemble, est une erreur fréquente
        de réglage.

## Étape 6. Comparer et choisir la bonne métrique (25 min)

L'exactitude (*accuracy*) mesure la proportion de bonnes réponses, toutes classes
confondues. Elle cache une question essentielle : **quelle erreur coûte le plus cher ?**
Ici, ne pas détecter une tumeur maligne (un faux négatif sur la classe « malignant ») a des
conséquences bien plus graves qu'une fausse alerte sur une tumeur bénigne.

```python
from sklearn.metrics import classification_report

print(classification_report(y_test, pred_arbre, target_names=donnees.target_names))
```

!!! question "Exercice 6.1 : le rappel, mais sur la bonne classe"
    Calculez `recall_score(y_test, pred_arbre)` sans argument, puis avec
    `pos_label=0`. Les deux nombres sont-ils identiques ? Lequel répond à la question
    « quelle proportion des tumeurs malignes le modèle détecte-t-il vraiment » ?

    **Résultat attendu :** `recall_score` sans argument vaut `0.944` (c'est le rappel de
    la classe `1`, « benign », le label positif par défaut de scikit-learn) ;
    `recall_score(..., pos_label=0)` vaut `0.929` (le rappel de la classe « malignant »,
    cliniquement la seule qui compte ici). Les deux chiffres sont proches sur ce jeu de
    données, mais rien ne le garantit en général : c'est le second qui répond à la
    question médicale, pas le premier.

    ??? success "Corrigé"
        ```python
        from sklearn.metrics import recall_score

        print("recall par défaut (classe 1, benign)   :", round(recall_score(y_test, pred_arbre), 3))
        print("recall classe 0, malignant              :", round(recall_score(y_test, pred_arbre, pos_label=0), 3))
        ```

        C'est un piège discret et documenté : `recall_score`, `precision_score` et
        `f1_score` de scikit-learn calculent par défaut la métrique pour la classe
        étiquetée `1`, quel que soit son sens réel. Rien n'empêche que `1` désigne, comme
        ici, la classe la moins préoccupante cliniquement. Avant de citer un rappel ou
        une précision dans un contexte à enjeu, vérifiez toujours **de quelle classe** il
        s'agit, avec `pos_label` ou `classification_report`, qui affiche les deux.

## Pour aller plus loin

- La validation croisée (`cross_val_score`, `StratifiedKFold`) donne une estimation plus
  robuste qu'un seul partage train/test, en particulier sur un jeu de cette taille.
- `GridSearchCV` ou `RandomizedSearchCV` automatisent la recherche d'hyperparamètres
  plutôt que de les essayer un par un comme à l'exercice 5.1.
- Sur un déséquilibre de classes plus marqué que celui-ci, les métriques et les
  techniques de rééchantillonnage (vues au TP8) deviennent nécessaires.

## Ce qu'il faut retenir

Un modèle s'évalue sur des données qu'il n'a jamais vues, avec `train_test_split` et une
stratification qui préserve les proportions de classes. Un arbre de décision trop profond
mémorise ses données d'entraînement plutôt que d'apprendre une règle générale : c'est le
surapprentissage. Une forêt aléatoire vote entre des arbres indépendants ; XGBoost
corrige séquentiellement les erreurs des arbres précédents. Et l'exactitude seule ne dit
jamais laquelle des deux classes vous intéresse le plus : `precision_score`,
`recall_score` et `f1_score` calculent par défaut la métrique de la classe `1`, qui n'est
pas forcément celle qui compte le plus dans votre problème.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer pourquoi on stratifie un `train_test_split` ;
- [ ] définir le surapprentissage et citer un réglage qui le limite pour un arbre de
      décision ;
- [ ] expliquer la différence de principe entre une forêt aléatoire et XGBoost ;
- [ ] lire une matrice de confusion et en déduire précision et rappel à la main ;
- [ ] dire pourquoi l'exactitude seule peut cacher l'information la plus importante d'un
      problème de classification.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP5](tp5-regression.md){ .md-button .md-button--primary }
