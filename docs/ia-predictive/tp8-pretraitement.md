# TP8. Prétraitement des variables

**Durée : 3 h.**

## Objectifs

- Mesurer quelles variables portent réellement de l'information pour une tâche donnée.
- Construire un pipeline de normalisation et d'encodage sans fuite de données.
- Détecter des valeurs aberrantes, et savoir qu'une méthode de détection n'est pas neutre.
- Diagnostiquer et traiter un déséquilibre de classes, sans se fier à la seule *accuracy*.

## Prérequis

Le [TP3](tp3-classification.md) : entraîner et évaluer un classifieur avec scikit-learn.

```bash
pip install pandas numpy scikit-learn imbalanced-learn matplotlib
```

## Ressources

- [Documentation scikit-learn, sélection de variables](https://scikit-learn.org/stable/modules/feature_selection.html).
- [Documentation scikit-learn, prétraitement](https://scikit-learn.org/stable/modules/preprocessing.html).
- [Documentation imbalanced-learn](https://imbalanced-learn.org/stable/).

---

## Étape 1. Sélectionner les variables pertinentes (35 min)

Le jeu de données *Adult Income* (recensement américain) vise à prédire si un revenu
annuel dépasse 50 000 $ à partir de variables socio-démographiques. Il mélange colonnes
numériques et catégorielles, exactement le cas où la question « quelles variables
compte-t-il de garder ? » se pose vraiment.

```python
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split

brut = fetch_openml(name="adult", version=2, as_frame=True, parser="auto")
X, y = brut.data.copy(), brut.target.copy()
y_binaire = (y == ">50K").astype(int)

colonnes_num = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
colonnes_cat = X.select_dtypes(include=["category"]).columns.tolist()
print(colonnes_num)
print(colonnes_cat)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_binaire, test_size=0.2, stratify=y_binaire, random_state=42
)
```

`stratify=y_binaire` garantit que la proportion de hauts revenus est la même dans le train
et le test, un réflexe systématique dès qu'une classe est minoritaire (étape 4).

Une première méthode de sélection, l'information mutuelle, mesure la dépendance
statistique entre chaque variable et la cible, sans supposer de relation linéaire :

```python
from sklearn.feature_selection import mutual_info_classif
import pandas as pd

info_mutuelle = mutual_info_classif(X_train[colonnes_num], y_train, random_state=42)
classement = pd.Series(info_mutuelle, index=colonnes_num).sort_values(ascending=False)
print(classement.round(3))
```

!!! question "Exercice 1.1 : deux méthodes, deux classements"
    Entraînez une forêt aléatoire sur l'ensemble des variables (numériques et
    catégorielles, encodées avec `OneHotEncoder`), et comparez son classement de
    `feature_importances_` au classement de l'information mutuelle ci-dessus. Une
    variable catégorielle apparaît-elle en bonne place ?

    **Résultat attendu :** `capital-gain` arrive en tête dans les deux classements, mais
    la forêt fait remonter des variables catégorielles absentes du premier classement
    (qui ne portait que sur les variables numériques) : `marital-status` (mariée à un
    civil) et `relationship` (époux) comptent parmi les variables les plus importantes,
    presque autant que `capital-gain`.

    ??? success "Corrigé"
        ```python
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import OneHotEncoder
        from sklearn.ensemble import RandomForestClassifier

        pretraitement = ColumnTransformer([
            ("num", "passthrough", colonnes_num),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encodeur", OneHotEncoder(handle_unknown="ignore")),
            ]), colonnes_cat),
        ])

        foret = Pipeline([
            ("pre", pretraitement),
            ("modele", RandomForestClassifier(n_estimators=200, max_depth=12, n_jobs=-1, random_state=42)),
        ])
        foret.fit(X_train, y_train)

        noms_colonnes = foret.named_steps["pre"].get_feature_names_out()
        importances = pd.Series(
            foret.named_steps["modele"].feature_importances_, index=noms_colonnes
        ).sort_values(ascending=False)
        print(importances.head(6).round(3))
        ```

        L'information mutuelle calculée plus haut ne portait que sur les variables déjà
        numériques : elle ne pouvait tout simplement pas voir `marital-status`. C'est un
        piège courant de la sélection de variables : la méthode choisie détermine par
        construction ce qu'elle est capable de voir, pas seulement ce qui compte vraiment.
        Comparer deux méthodes sur le même pied demande de leur donner accès aux mêmes
        variables.

## Étape 2. Normaliser et encoder, sans fuite de données (40 min)

Un encodage *one-hot* transforme chaque catégorie en une colonne binaire, ce qui peut vite
faire exploser le nombre de colonnes :

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

pipeline_num = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])
pipeline_cat = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encodeur", OneHotEncoder(handle_unknown="ignore")),
])
pretraitement_complet = ColumnTransformer([
    ("num", pipeline_num, colonnes_num),
    ("cat", pipeline_cat, colonnes_cat),
])

transforme = pretraitement_complet.fit_transform(X_train)
print("avant :", X_train.shape, "après :", transforme.shape)
```

Quatorze colonnes d'origine deviennent 105 colonnes après encodage : les huit variables
catégorielles, dont `native-country` (une quarantaine de pays), portent l'essentiel de
cette explosion.

Le pipeline est **ajusté sur le train uniquement** (`fit_transform` sur `X_train`, puis
`transform` seul sur `X_test`, jamais l'inverse) : ajuster un `StandardScaler` ou un
imputeur sur l'ensemble des données avant de séparer train et test ferait fuiter de
l'information du test vers l'entraînement, une variante du même problème que la moyenne
glissante mal calée du TP6.

!!! question "Exercice 2.1 : le scaler change-t-il vraiment le résultat ?"
    Entraînez une `LogisticRegression` sur les données catégorielles encodées mais les
    variables numériques **non standardisées** (`"passthrough"` au lieu de `StandardScaler`
    dans le `ColumnTransformer`), et comparez à la version avec `StandardScaler`.

    **Résultat attendu :** sans standardisation, un avertissement de non-convergence
    (`ConvergenceWarning`) apparaît malgré `max_iter=2000`, et les métriques sont
    légèrement inférieures (`accuracy` environ `0.846` contre `0.852`, `f1` environ
    `0.644` contre `0.656`). La standardisation n'est pas cosmétique : elle change la
    vitesse à laquelle l'algorithme d'optimisation converge.

    ??? success "Corrigé"
        ```python
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score

        pretraitement_sans_scaler = ColumnTransformer([
            ("num", "passthrough", colonnes_num),
            ("cat", pipeline_cat, colonnes_cat),
        ])

        modele_sans = Pipeline([("pre", pretraitement_sans_scaler), ("clf", LogisticRegression(max_iter=2000))])
        modele_sans.fit(X_train, y_train)
        pred_sans = modele_sans.predict(X_test)

        modele_avec = Pipeline([("pre", pretraitement_complet), ("clf", LogisticRegression(max_iter=2000))])
        modele_avec.fit(X_train, y_train)
        pred_avec = modele_avec.predict(X_test)

        print("sans scaler : accuracy", round(accuracy_score(y_test, pred_sans), 3), "f1", round(f1_score(y_test, pred_sans), 3))
        print("avec scaler : accuracy", round(accuracy_score(y_test, pred_avec), 3), "f1", round(f1_score(y_test, pred_avec), 3))
        ```

        `capital-gain` va de 0 à plus de 90 000, `age` de 17 à 90 : sans mise à l'échelle,
        l'algorithme d'optimisation doit gérer des gradients à des échelles très
        différentes d'une variable à l'autre, ce qui ralentit ou empêche sa convergence.
        Un modèle à base d'arbres (forêt aléatoire, XGBoost) est, lui, insensible à
        l'échelle des variables : ce piège est spécifique aux modèles qui optimisent une
        fonction par descente de gradient.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant d'écrire un `OneHotEncoder` pour ce jeu de données. Beaucoup
    de réponses omettent `handle_unknown="ignore"`, le comportement par défaut de
    scikit-learn étant de lever une erreur face à une catégorie inconnue. Sur un jeu de
    données propre et déjà découpé, ce choix passe inaperçu, jusqu'au jour où une
    catégorie rare tombe uniquement dans le test :

    ```python
    ligne_rare = X[X["native-country"] == "Holand-Netherlands"]  # une seule ligne sur 48842
    reste = X.drop(ligne_rare.index)
    X_train_demo, X_test_demo = train_test_split(reste, test_size=0.2, random_state=42)
    X_test_demo = pd.concat([X_test_demo, ligne_rare])  # force le cas limite

    from sklearn.preprocessing import OneHotEncoder as OHE
    encodeur_strict = OHE(handle_unknown="error")
    encodeur_strict.fit(X_train_demo[colonnes_cat])
    try:
        encodeur_strict.transform(X_test_demo[colonnes_cat])
    except ValueError as erreur:
        print("Erreur :", str(erreur)[:80])
    ```

    Le message d'erreur confirme le diagnostic : une catégorie présente dans le test mais
    absente du train fait planter le pipeline avec le comportement par défaut. En
    production, une catégorie jamais vue à l'entraînement finira par arriver un jour ;
    `handle_unknown="ignore"` la traite comme « toutes les colonnes de cette variable à
    zéro » plutôt que de faire planter tout le service.

## Étape 3. Détecter les valeurs aberrantes (35 min)

La méthode de l'écart interquartile (IQR) marque comme aberrante toute valeur en dehors de
`[Q1 - 1,5×IQR, Q3 + 1,5×IQR]`. Le z-score marque comme aberrante toute valeur à plus de
3 écarts-types de la moyenne.

```python
def bornes_iqr(colonne):
    q1, q3 = colonne.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

for col in ["capital-gain", "hours-per-week", "age"]:
    bas, haut = bornes_iqr(X_train[col])
    part = ((X_train[col] < bas) | (X_train[col] > haut)).mean()
    print(f"{col} : bornes ({bas:.1f}, {haut:.1f}), part hors bornes {part:.1%}")
```

!!! question "Exercice 3.1 : quand l'IQR ment"
    Regardez la part de lignes marquées « aberrantes » sur `hours-per-week` ci-dessus.
    Un quart de la population peut-il raisonnablement être considéré comme un cas
    extrême ? Calculez `Q1` et `Q3` de cette colonne pour comprendre ce qui se passe, puis
    comparez avec la méthode du z-score (`|z| > 3`) sur la même colonne.

    **Résultat attendu :** l'IQR marque environ 27,8 % des lignes de `hours-per-week`
    comme aberrantes, alors que `Q1 = 40` et `Q3 = 45` (la plupart des gens travaillent
    autour d'un temps plein) : l'écart interquartile est minuscule, donc les bornes
    `[32,5 ; 52,5]` sont très resserrées et excluent une grande partie des travailleurs à
    temps partiel ou en heures supplémentaires, qui n'ont pourtant rien d'anormal. Le
    z-score, moins sensible à une distribution très concentrée, marque une proportion
    bien plus faible de points comme aberrants.

    ??? success "Corrigé"
        ```python
        q1, q3 = X_train["hours-per-week"].quantile([0.25, 0.75])
        print("Q1 :", q1, "Q3 :", q3, "IQR :", q3 - q1)

        z = (X_train["hours-per-week"] - X_train["hours-per-week"].mean()) / X_train["hours-per-week"].std()
        print("part |z| > 3 :", (z.abs() > 3).mean())
        ```

        L'IQR suppose implicitement une distribution suffisamment étalée pour que « à
        1,5 IQR des quartiles » ait un sens. Sur une variable très concentrée autour
        d'une valeur usuelle (ici, le temps plein), cette hypothèse casse silencieusement :
        la méthode continue de rendre un résultat, mais ce résultat ne veut plus rien dire.
        Une méthode de détection d'outliers n'est jamais neutre : elle encode une
        hypothèse sur la forme de la distribution, à vérifier avant de lui faire confiance.

## Étape 4. Diagnostiquer et traiter un déséquilibre de classes (40 min)

```python
print(y.value_counts(normalize=True).round(3))
```

Environ 76 % des personnes gagnent 50 000 $ ou moins, 24 % gagnent plus : un déséquilibre
modéré, mais suffisant pour rendre l'*accuracy* trompeuse.

!!! question "Exercice 4.1 : battre un modèle qui ne prédit jamais rien"
    Calculez l'*accuracy* d'un modèle absurde qui prédit toujours « revenu ≤ 50 000 $ »,
    sans entraînement. Comparez-la à celle d'une vraie régression logistique. Que dit le
    `f1` du modèle absurde, que l'*accuracy* ne dit pas ?

    **Résultat attendu :** le modèle absurde atteint une *accuracy* d'environ `76,1 %`,
    proche de la vraie régression logistique (environ `85,2 %`) : l'écart paraît faible.
    Mais son `f1` sur la classe minoritaire vaut exactement `0` (il ne trouve jamais un
    seul haut revenu), là où le vrai modèle atteint `0,656`. L'*accuracy* seule aurait
    laissé croire que le modèle absurde n'est pas si mauvais.

    ??? success "Corrigé"
        ```python
        import numpy as np
        from sklearn.metrics import accuracy_score, f1_score

        pred_absurde = np.zeros_like(y_test)
        print("accuracy absurde :", round(accuracy_score(y_test, pred_absurde), 3))
        print("f1 absurde :", round(f1_score(y_test, pred_absurde), 3))
        ```

        C'est la raison pour laquelle un jeu de données déséquilibré exige de regarder
        `f1`, `recall` ou `roc_auc` en plus de l'*accuracy*, jamais l'*accuracy* seule :
        elle récompense mécaniquement tout modèle qui penche vers la classe majoritaire,
        même un modèle qui n'a rien appris.

Deux leviers classiques corrigent ce biais : pondérer les classes dans la fonction de
perte, ou choisir un seuil de décision différent de 0,5.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, recall_score

modele_pondere = Pipeline([("pre", pretraitement_complet), ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))])
modele_pondere.fit(X_train, y_train)
pred_pondere = modele_pondere.predict(X_test)

print("f1 pondéré :", round(f1_score(y_test, pred_pondere), 3))
print("rappel classe minoritaire, pondéré :", round(recall_score(y_test, pred_pondere), 3))
```

!!! question "Exercice 4.2 : un compromis, pas un gain gratuit"
    Comparez `f1`, *accuracy* et rappel de la classe minoritaire entre le modèle standard
    (étape 2) et le modèle avec `class_weight="balanced"`. Le gain sur une métrique
    se paie-t-il sur une autre ?

    **Résultat attendu :** avec `class_weight="balanced"`, le rappel de la classe
    minoritaire monte fortement (d'environ `0,589` à `0,844`) et le `f1` progresse aussi
    (`0,656` à `0,677`), mais l'*accuracy* recule (`0,852` à `0,807`) : le modèle
    pondéré accepte plus de faux positifs (des gens classés « haut revenu » à tort) pour
    rater moins de vrais hauts revenus.

    ??? success "Corrigé"
        ```python
        modele_standard = Pipeline([("pre", pretraitement_complet), ("clf", LogisticRegression(max_iter=2000))])
        modele_standard.fit(X_train, y_train)
        pred_standard = modele_standard.predict(X_test)

        print("standard : accuracy", round(accuracy_score(y_test, pred_standard), 3),
              "f1", round(f1_score(y_test, pred_standard), 3),
              "rappel", round(recall_score(y_test, pred_standard), 3))
        print("pondéré  : accuracy", round(accuracy_score(y_test, pred_pondere), 3),
              "f1", round(f1_score(y_test, pred_pondere), 3),
              "rappel", round(recall_score(y_test, pred_pondere), 3))
        ```

        Aucune des deux versions n'est « meilleure » dans l'absolu : le bon choix dépend
        du coût métier d'un faux négatif face à un faux positif. Refuser un crédit à
        quelqu'un de solvable (faux positif côté banque) et accorder un crédit à quelqu'un
        d'insolvable (faux négatif) n'ont pas le même coût, et c'est ce coût, pas une
        métrique générique, qui doit trancher entre les deux modèles.

## Pour aller plus loin

- Le rééchantillonnage (`SMOTE`, `RandomOverSampler`, `RandomUnderSampler` de
  `imbalanced-learn`) agit sur les **données** plutôt que sur la fonction de perte : à
  tester et comparer à `class_weight="balanced"`.
- Ajuster directement le seuil de décision (`predict_proba` puis un seuil autre que 0,5,
  choisi via une courbe précision-rappel) offre un contrôle plus fin que le choix binaire
  entre pondérer ou non.
- `IsolationForest` et `LocalOutlierFactor` détectent des anomalies multivariées, que
  l'IQR (variable par variable) ne peut pas voir : une combinaison de valeurs individuelles
  banales peut être conjointement improbable.
- XGBoost (TP4) gère nativement les catégories (`enable_categorical=True`) et les classes
  déséquilibrées (`scale_pos_weight`), une alternative au pipeline scikit-learn complet de
  ce TP.

## Ce qu'il faut retenir

Une méthode de sélection de variables ne peut faire remonter que ce qu'elle est capable de
voir : l'information mutuelle sur les seules colonnes numériques ignore les colonnes
catégorielles par construction. Un `ColumnTransformer` s'ajuste toujours sur le train
seul, jamais sur l'ensemble des données avant séparation. La standardisation n'est pas
cosmétique pour un modèle optimisé par descente de gradient : son absence peut empêcher la
convergence. Une méthode de détection d'outliers encode une hypothèse sur la forme de la
distribution, et cette hypothèse peut casser silencieusement (IQR sur une variable très
concentrée). Et sur un jeu de données déséquilibré, l'*accuracy* seule ne suffit jamais :
un modèle qui ne prédit jamais la classe minoritaire peut afficher une *accuracy*
trompeusement correcte.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer pourquoi deux méthodes de sélection de variables peuvent donner des
      classements différents ;
- [ ] construire un `ColumnTransformer` qui normalise les numériques et encode les
      catégorielles, ajusté sur le train seul ;
- [ ] dire pourquoi `handle_unknown="ignore"` importe pour un `OneHotEncoder` en
      production ;
- [ ] expliquer pourquoi l'IQR peut mal se comporter sur une variable très concentrée ;
- [ ] choisir entre `class_weight="balanced"` et un modèle standard selon un coût métier,
      pas seulement selon une métrique.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP9](tp9-xgboost-explicabilite-causalite.md){ .md-button .md-button--primary }
