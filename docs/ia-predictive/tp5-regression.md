# TP5. Régression et validation croisée

**Durée : 2 h.**

## Objectifs

- Distinguer un problème de régression (sortie continue) d'un problème de classification
  (sortie discrète), et choisir les bonnes métriques.
- Aller au-delà d'un simple partage entraînement/test avec la validation croisée.
- Comprendre l'hyperparamètre `max_depth` comme un curseur entre sous-apprentissage et
  surapprentissage, et le régler par une méthode plutôt qu'à l'œil.

## Prérequis

Le [TP3](tp3-classification.md) : `train_test_split`, arbre de décision, surapprentissage.
Ce TP transpose ces notions à une sortie continue plutôt qu'à une étiquette.

```bash
pip install scikit-learn matplotlib pandas numpy
```

## Ressources

- [Documentation scikit-learn, régression](https://scikit-learn.org/stable/supervised_learning.html#supervised-learning).
- [Documentation scikit-learn, validation croisée](https://scikit-learn.org/stable/modules/cross_validation.html).

---

## Étape 1. Régression contre classification (15 min)

Une classification prédit une étiquette parmi un ensemble fini (malin ou bénin, au TP3).
Une régression prédit un nombre, qui peut prendre n'importe quelle valeur dans un
intervalle continu : un prix, une température, une durée. Les métriques changent en
conséquence : plus d'exactitude ni de rappel, mais des mesures d'écart.

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

housing = fetch_california_housing(as_frame=True)
X = housing.data
y = housing.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

reg = DecisionTreeRegressor(random_state=42)
reg.fit(X_train, y_train)
predictions = reg.predict(X_test)

print("MAE  :", round(mean_absolute_error(y_test, predictions), 3))
print("RMSE :", round(root_mean_squared_error(y_test, predictions), 3))
print("R2   :", round(r2_score(y_test, predictions), 3))
```

Le jeu **California Housing** donne le prix médian d'un logement (en centaines de
milliers de dollars) pour un secteur, à partir de huit variables (revenu médian, âge des
logements, nombre de pièces...). Un arbre de décision non limité atteint ici un `MAE` de
`0.454` (soit environ 45 400 $ d'erreur moyenne) et un `R2` de `0.623`.

!!! question "Exercice 1.1 : trois métriques, trois lectures"
    `MAE` (erreur absolue moyenne), `RMSE` (racine de l'erreur quadratique moyenne) et
    `R2` (part de variance expliquée) mesurent tous un écart entre prédiction et réalité,
    mais pas de la même façon. Le `RMSE` (`0.703`) est-il plus grand ou plus petit que le
    `MAE` (`0.454`) ? Pourquoi, structurellement, ne peut-il jamais être plus petit ?

    **Résultat attendu :** `RMSE > MAE` toujours, sauf cas particulier où toutes les
    erreurs sont identiques. Le `RMSE` élève chaque écart au carré avant de moyenner,
    donc une seule grosse erreur pèse disproportionnellement plus qu'un ensemble de
    petites erreurs de même somme.

    ??? success "Corrigé"
        ```python
        import numpy as np

        ecarts = np.abs(y_test.values - predictions)
        print("MAE recalculé  :", round(ecarts.mean(), 3))
        print("RMSE recalculé :", round(np.sqrt((ecarts ** 2).mean()), 3))
        print("Plus grosse erreur :", round(ecarts.max(), 3))
        ```

        Choisir `RMSE` plutôt que `MAE` revient à décider que les grosses erreurs comptent
        plus que proportionnellement à leur taille : pertinent si une erreur énorme est
        particulièrement coûteuse (une estimation immobilière dix fois trop haute), moins
        pertinent si toutes les erreurs se valent également.

## Étape 2. Au-delà du simple partage entraînement/test (20 min)

Ajuster un hyperparamètre en regardant le score sur le jeu de test, encore et encore,
finit par surapprendre **ce jeu de test précis**, même sans jamais l'utiliser pour
entraîner directement le modèle. La validation croisée limite ce risque en faisant
tourner plusieurs partages.

```python
from sklearn.model_selection import KFold, cross_val_score

reg5 = DecisionTreeRegressor(max_depth=5, random_state=42)
kf = KFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(reg5, X_train, y_train, scoring="neg_root_mean_squared_error", cv=kf)
print("Scores (négatifs) :", scores.round(3))
print("RMSE moyen :", round(-scores.mean(), 3))
print("Écart-type :", round(scores.std(), 3))
```

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant de calculer un RMSE avec scikit-learn. Une réponse
    fréquente, héritée d'anciens tutoriels, écrit
    `mean_squared_error(y_test, predictions, squared=False)`. Testez-la :

    ```python
    from sklearn.metrics import mean_squared_error

    try:
        mean_squared_error(y_test, predictions, squared=False)
    except TypeError as erreur:
        print("Erreur :", erreur)
    ```

    Le paramètre `squared` a été retiré de `mean_squared_error` : la fonction dédiée
    `root_mean_squared_error`, utilisée dans ce TP depuis l'étape 1, l'a remplacé. Une
    erreur de ce genre, `TypeError` explicite, se corrige vite ; le risque réel est un
    assistant qui écrit `mean_squared_error(...) ** 0.5` à la place, du code qui
    fonctionne mais réinvente une fonction déjà fournie, moins lisible pour qui relit.

!!! question "Exercice 2.1 : pourquoi les scores sont négatifs"
    `scoring="neg_root_mean_squared_error"` renvoie des valeurs négatives, que le code
    ci-dessus retourne avec `-scores.mean()`. Cherchez dans la documentation scikit-learn
    pourquoi le signe est inversé plutôt que de fournir directement `"root_mean_squared_error"`.

    **Résultat attendu :** par convention, les fonctions de score de scikit-learn suivent
    la règle « plus grand est meilleur », pour que `GridSearchCV` et les outils de
    sélection de modèle puissent toujours **maximiser** un score, quelle que soit la
    métrique. Une erreur, elle, doit être minimisée : la négation transforme donc
    « minimiser une erreur » en « maximiser un score », uniformément.

    ??? success "Corrigé"
        Il n'y a pas de code supplémentaire ici, la réponse est dans la documentation
        scikit-learn (section *Scoring parameter*). Retenez la conséquence pratique :
        n'oubliez jamais le signe `-` en lisant un score `neg_*`, une erreur classique
        étant de rapporter un RMSE négatif dans un tableau de résultats sans s'apercevoir
        de l'absurdité du signe.

## Étape 3. Comparer plusieurs modèles par validation croisée (25 min)

```python
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import pandas as pd

def evalue(modele, X, y):
    scores = -cross_val_score(modele, X, y, scoring="neg_root_mean_squared_error", cv=5, n_jobs=-1)
    return scores.mean()

modeles = {
    "Arbre de décision": DecisionTreeRegressor(random_state=42),
    "Forêt aléatoire": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    "Boosting de gradient": GradientBoostingRegressor(random_state=42),
}

resultats = pd.DataFrame(
    [{"modèle": nom, "rmse_cv": round(evalue(m, X_train, y_train), 3)} for nom, m in modeles.items()]
)
print(resultats.sort_values("rmse_cv"))
```

!!! question "Exercice 3.1 : le meilleur modèle en validation tient-il sur le test ?"
    Réentraînez le modèle le mieux classé en validation croisée sur tout `X_train`, puis
    évaluez-le sur `X_test`. Le RMSE de test est-il cohérent avec le RMSE de validation
    croisée ?

    **Résultat attendu :** la forêt aléatoire arrive en tête en validation croisée avec un
    RMSE moyen d'environ `0.511`, loin devant l'arbre seul (`0.724`) et le boosting de
    gradient (`0.534`). Le RMSE de test du modèle réentraîné reste proche du RMSE de
    validation croisée, ce qui confirme que l'estimation n'était pas un coup de chance.

    ??? success "Corrigé"
        ```python
        meilleur = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        meilleur.fit(X_train, y_train)
        rmse_test = root_mean_squared_error(y_test, meilleur.predict(X_test))
        print("RMSE test :", round(rmse_test, 3))
        ```

        Un RMSE de test très différent du RMSE de validation croisée serait un signal
        d'alerte : soit le jeu de test n'est pas représentatif (rare avec un partage
        aléatoire sur 20 000 lignes), soit une fuite de données s'est glissée quelque part
        dans le protocole. Ici, les deux valeurs concordent, ce qui est le résultat
        attendu quand tout est fait correctement.

## Étape 4. `max_depth`, un curseur entre deux erreurs (25 min)

Un arbre trop peu profond ne capte pas la structure des données (sous-apprentissage) ; un
arbre trop profond mémorise le bruit de l'entraînement (surapprentissage, déjà vu au
TP3). Entre les deux se trouve un optimum, que la validation croisée permet de localiser
sans toucher au jeu de test.

```python
resultats_profondeur = []
for profondeur in range(2, 11):
    reg = DecisionTreeRegressor(max_depth=profondeur, random_state=42)
    rmse_cv = -cross_val_score(reg, X_train, y_train, scoring="neg_root_mean_squared_error", cv=5, n_jobs=-1).mean()
    resultats_profondeur.append({"max_depth": profondeur, "rmse_cv": round(rmse_cv, 3)})

df_profondeur = pd.DataFrame(resultats_profondeur)
print(df_profondeur)
```

!!! question "Exercice 4.1 : trouver le minimum, pas le supposer"
    À partir de `df_profondeur`, trouvez automatiquement la profondeur qui minimise
    `rmse_cv`, sans la lire à l'œil dans le tableau affiché.

    **Résultat attendu :** le minimum se trouve à `max_depth = 9` (`rmse_cv ≈ 0.633`).
    Le RMSE diminue de façon presque monotone de la profondeur 2 à 9, puis remonte
    légèrement à la profondeur 10 : la signature typique d'un optimum, pas d'un plateau.

    ??? success "Corrigé"
        ```python
        ligne_minimale = df_profondeur.loc[df_profondeur["rmse_cv"].idxmin()]
        print(ligne_minimale)
        ```

        `idxmin()` plutôt qu'une lecture visuelle du tableau n'est pas qu'une question de
        confort : sur un tableau plus long, ou généré automatiquement par un pipeline sans
        supervision humaine, c'est la seule façon fiable de retrouver le bon réglage. Cette
        même logique (chercher le minimum d'une courbe erreur-complexité) est celle de
        `GridSearchCV`, qui automatise ce que cette boucle fait à la main.

## Pour aller plus loin

- Visualiser le sous-apprentissage et le surapprentissage sur un jeu **synthétique** en
  une dimension (par exemple `y = sin(x) + bruit`) rend le compromis biais-variance
  visible directement sur la courbe de prédiction, pas seulement sur un score.
- `GridSearchCV` combine la recherche d'hyperparamètres et la validation croisée en un
  seul appel, plutôt que la boucle manuelle de l'étape 4.
- Sur un jeu de données avec des variables de nature très différente (revenu, superficie,
  proximité d'une autoroute), une normalisation préalable peut aider certains modèles
  (moins les arbres, qui n'en ont pas besoin) : sujet du TP8.

## Ce qu'il faut retenir

Une régression prédit une valeur continue, évaluée par MAE, RMSE ou R2, jamais par
l'exactitude. Le RMSE pénalise davantage les grosses erreurs que le MAE. La validation
croisée protège contre le risque de choisir un hyperparamètre qui colle trop bien au seul
jeu de test observé, en faisant tourner plusieurs partages et en moyennant. Les scores
`neg_*` de scikit-learn sont négatifs par convention, pour que maximiser un score
corresponde toujours à minimiser une erreur. Et `max_depth`, comme tout hyperparamètre de
complexité, a un optimum qui se cherche par une courbe erreur-profondeur, pas en devinant
une valeur ronde.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] citer trois métriques de régression et dire ce que chacune mesure ;
- [ ] expliquer pourquoi RMSE est toujours supérieur ou égal à MAE ;
- [ ] expliquer ce qu'apporte la validation croisée par rapport à un simple partage
      entraînement/test ;
- [ ] dire pourquoi les scores `neg_*` de scikit-learn sont négatifs ;
- [ ] trouver, par le code, la valeur d'un hyperparamètre qui minimise une erreur de
      validation croisée.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP4](tp4-xgboost.md){ .md-button .md-button--primary }
