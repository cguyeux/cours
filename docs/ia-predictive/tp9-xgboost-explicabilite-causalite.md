# TP9. XGBoost, explicabilité et causalité

**Durée : 2 h.**

## Objectifs

- Distinguer trois mesures d'importance de variable (`weight`, `gain`, `cover`), et savoir
  laquelle répond à quelle question.
- Expliquer une prédiction individuelle avec les valeurs de Shapley (SHAP), et vérifier la
  propriété qui les rend interprétables : elles s'additionnent exactement.
- Comprendre pourquoi une variable importante pour un modèle n'est pas forcément une
  variable qui **cause** le résultat observé.
- Estimer un effet causal en présence de facteurs de confusion, et mesurer l'écart avec
  une simple corrélation.

## Prérequis

Le [TP4](tp4-xgboost.md) et le [TP7](tp7-xgboost-objectifs-metriques.md) : entraîner et
régler un modèle XGBoost.

```bash
pip install xgboost shap econml scikit-learn
```

## Ressources

- [Documentation SHAP](https://shap.readthedocs.io/).
- [Documentation EconML](https://econml.azurewebsites.net/).

!!! info "Une bibliothèque de la source remplacée dans cette page"
    L'énoncé original de ce TP s'appuie sur `dowhy` pour la partie causalité. Dans
    l'environnement de ce site, `dowhy` 0.8 (la seule version compatible avec les autres
    dépendances) est cassée sur les versions récentes de Python : elle appelle une
    fonction de `networkx` qui a été renommée. Cette page utilise donc **econml** à la
    place, une bibliothèque du même écosystème (PyWhy) qui répond à la même question
    (estimer un effet causal ajusté sur des facteurs de confusion), avec une API différente.

---

## Étape 1. Trois façons de mesurer l'importance d'une variable (25 min)

```python
import xgboost as xgb
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True, as_frame=True)
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

modele = xgb.XGBClassifier(
    n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
    eval_metric="logloss", random_state=42,
)
modele.fit(X_train, y_train, eval_set=[(X_valid, y_valid)], verbose=False)

fi = pd.Series(modele.feature_importances_, index=X.columns).sort_values(ascending=False)
print(fi.head(5))
```

`feature_importances_` donne le `gain` normalisé, mais trois mesures coexistent dans
XGBoost, accessibles via le `Booster` sous-jacent :

- **`weight`** : le nombre de fois où la variable sert à un split, toutes profondeurs
  confondues. Une variable très utilisée mais dans des splits peu décisifs a un `weight`
  élevé et un `gain` faible.
- **`gain`** : la réduction moyenne de la perte apportée par les splits sur cette
  variable. C'est la mesure la plus proche de « cette variable compte-t-elle vraiment ».
- **`cover`** : le nombre moyen d'observations concernées par les splits sur cette
  variable. Une variable qui sépare une petite minorité de cas peut avoir un `gain` élevé
  et un `cover` faible.

```python
booster = modele.get_booster()
poids = booster.get_score(importance_type="weight")
gain = booster.get_score(importance_type="gain")
```

!!! question "Exercice 1.1 : les trois mesures ne sont pas d'accord"
    Construisez un tableau avec les trois indicateurs pour chaque variable, et identifiez
    une variable dont le classement diffère nettement entre `weight` et `gain` (haute sur
    l'une, basse sur l'autre).

    **Résultat attendu :** `worst texture` arrive en tête en `weight` (`121` occurrences
    dans des splits) mais n'apparaît pas dans le top 3 en `gain`, où `worst perimeter`
    domine (`gain` moyen d'environ `27,4`) : une variable très souvent utilisée pour des
    ajustements fins n'est pas forcément celle qui structure le plus la décision.

    ??? success "Corrigé"
        ```python
        couverture = booster.get_score(importance_type="cover")
        noms = booster.feature_names

        tableau = pd.DataFrame({
            "feature": noms,
            "weight": [poids.get(nom, 0) for nom in noms],
            "gain": [gain.get(nom, 0.0) for nom in noms],
            "cover": [couverture.get(nom, 0.0) for nom in noms],
        })
        print("top weight :")
        print(tableau.sort_values("weight", ascending=False).head(3))
        print("top gain :")
        print(tableau.sort_values("gain", ascending=False).head(3))
        ```

        Aucune des trois mesures n'est « la bonne » dans l'absolu : `weight` répond à
        « quelle variable le modèle consulte-t-il souvent », `gain` à « quelle variable
        change le plus la décision », `cover` à « quelle variable touche le plus
        d'observations ». Un audit sérieux les croise plutôt que de n'en retenir qu'une.

        Remarquez que `poids.get(nom, 0)` va chercher directement le nom de la variable
        (`"worst texture"`), pas un identifiant générique `"f21"` : dès qu'un modèle est
        entraîné sur un DataFrame aux colonnes nommées, XGBoost restitue ces noms dans
        `get_score()`. Du code qui suppose systématiquement des clés `f0`, `f1`... (un
        réflexe hérité de l'API bas niveau sur matrice sans noms de colonnes) échouerait
        silencieusement ici : chaque `.get(f"f{i}", 0)` renverrait la valeur par défaut,
        et le tableau afficherait des zéros partout sans qu'aucune erreur ne se déclenche.

## Étape 2. Expliquer une prédiction individuelle avec SHAP (35 min)

`feature_importances_` décrit le modèle **en moyenne**. Les valeurs SHAP décrivent **une
prédiction précise** : pour chaque variable, de combien elle a décalé la prédiction par
rapport à une valeur de référence.

```python
import shap
import numpy as np

explainer = shap.TreeExplainer(modele)
valeurs_shap = explainer.shap_values(X_valid)
valeur_de_base = explainer.expected_value

indice = 0
contributions = pd.Series(valeurs_shap[indice], index=X.columns)
logodds_predit = modele.predict(X_valid.iloc[[indice]], output_margin=True)[0]

print("valeur de base (log-odds) :", round(float(valeur_de_base), 3))
print("somme des contributions + base :", round(float(contributions.sum() + valeur_de_base), 3))
print("log-odds réellement prédit :", round(float(logodds_predit), 3))
```

!!! question "Exercice 2.1 : vérifier l'additivité, la propriété qui rend SHAP fiable"
    Vérifiez que `contributions.sum() + valeur_de_base` est bien égal au log-odds prédit
    par le modèle pour trois observations différentes, pas seulement la première.

    **Résultat attendu :** une égalité exacte (à l'arrondi flottant près, de l'ordre de
    `1e-5`) pour chacune des trois observations. Ce n'est pas une coïncidence : c'est la
    propriété qui définit les valeurs de Shapley, contrairement à d'autres méthodes
    d'explication (comme une simple permutation de variable) qui n'offrent aucune garantie
    de ce genre.

    ??? success "Corrigé"
        ```python
        for indice_test in [0, 10, 50]:
            contributions_test = valeurs_shap[indice_test].sum()
            logodds_test = modele.predict(X_valid.iloc[[indice_test]], output_margin=True)[0]
            ecart = abs(contributions_test + valeur_de_base - logodds_test)
            print(f"observation {indice_test} : écart = {ecart:.2e}")
        ```

        C'est cette additivité exacte qui permet de dire une phrase comme « la variable
        `worst concave points` a ajouté 1,2 à la probabilité de malignité pour cette
        patiente » sans mentir : la somme de toutes ces phrases reconstitue exactement la
        prédiction, rien n'est approximé ni omis en cours de route.

!!! question "Exercice 2.2 : la variable qui compte en moyenne n'est pas toujours celle qui compte ici"
    Pour l'observation d'indice 0, identifiez la variable dont la contribution SHAP
    (en valeur absolue) est la plus grande. Est-ce la même que `worst perimeter`, en tête
    du classement `gain` de l'étape 1 ?

    **Résultat attendu :** pas nécessairement. Une variable peut dominer le classement
    `gain` global (moyenné sur toutes les observations d'entraînement) sans être celle qui
    pèse le plus sur un cas précis, où d'autres variables peuvent prendre des valeurs
    inhabituelles et donc contribuer davantage localement.

    ??? success "Corrigé"
        ```python
        contributions_abs = contributions.abs().sort_values(ascending=False)
        print(contributions_abs.head(3))
        ```

        C'est la différence entre importance **globale** (étape 1) et importance
        **locale** (SHAP) : la première résume le modèle sur l'ensemble du jeu de
        données, la seconde décrit un cas particulier. Un rapport d'audit qui ne cite que
        l'importance globale pour justifier une décision individuelle commet une erreur de
        niveau d'analyse.

## Étape 3. Corrélation et causalité, un exemple chiffré (30 min)

SHAP explique **comment le modèle utilise ses variables pour prédire**. Cela ne dit rien
sur **ce qui causerait réellement** un changement du résultat si on intervenait sur une
variable. Simulons un cas où les deux répondent à des questions différentes : une
campagne marketing, dont on connaît l'effet réel par construction (nous avons simulé les
données), pour pouvoir juger une méthode d'estimation à l'aune de la vérité.

```python
import numpy as np
import pandas as pd

n = 2000
rng = np.random.default_rng(0)
revenu = rng.normal(45000, 10000, size=n)
anciennete = rng.integers(1, 8, size=n)

# Les clientes à revenu élevé et ancienneté forte reçoivent plus souvent la campagne :
# revenu et ancienneté sont des facteurs de confusion (ils influencent le traitement ET la dépense).
propension = 1 / (1 + np.exp(-0.00008 * (revenu - 42000) + 0.3 * (anciennete - 3)))
traitement = rng.binomial(1, propension)

bruit = rng.normal(0, 150, size=n)
effet_causal_reel = 80.0  # connu ici, parce que nous l'avons fixé dans la simulation
depense = 500 + 0.05 * revenu + 15 * anciennete + effet_causal_reel * traitement + bruit

df = pd.DataFrame({"revenu": revenu, "anciennete": anciennete, "traitement": traitement, "depense": depense})

difference_naive = df.groupby("traitement")["depense"].mean().diff().iloc[-1]
print("différence brute de dépense (traitées - non traitées) :", round(difference_naive, 1))
```

!!! question "Exercice 3.1 : mesurer l'ampleur du biais"
    Comparez la différence brute calculée ci-dessus à l'effet causal réel (`80`, fixé dans
    la simulation). L'écart est-il négligeable ?

    **Résultat attendu :** une différence brute d'environ `384`, presque cinq fois l'effet
    réel de `80`. Les clientes qui reçoivent la campagne ont, par construction, un revenu
    et une ancienneté plus élevés, deux facteurs qui augmentent la dépense indépendamment
    de toute campagne : la différence brute mélange l'effet de la campagne avec l'effet de
    ces facteurs de confusion.

    ??? success "Corrigé"
        Pas de code supplémentaire : la comparaison porte sur la valeur déjà affichée
        (`384`) contre l'effet réel (`80`). Retenez l'ordre de grandeur : un biais de
        confusion n'est pas toujours une nuance mineure, il peut multiplier l'estimation
        par cinq et conduire à des décisions budgétaires très mal calibrées si on se fiait
        à cette différence brute pour évaluer le retour sur investissement de la campagne.

## Étape 4. Ajuster sur les facteurs de confusion avec econml (30 min)

`LinearDML` (*Double Machine Learning*) estime l'effet causal en retirant d'abord, par
apprentissage automatique, la part de la dépense et du traitement explicable par les
facteurs de confusion, puis en régressant ce qui reste l'un sur l'autre.

```python
from econml.dml import LinearDML
from sklearn.linear_model import LinearRegression, LogisticRegression

facteurs_confusion = df[["revenu", "anciennete"]].values

estimateur = LinearDML(
    model_y=LinearRegression(),
    model_t=LogisticRegression(),
    discrete_treatment=True,
    random_state=0,
)
estimateur.fit(df["depense"].values, df["traitement"].values, X=None, W=facteurs_confusion)

effet_estime = estimateur.ate()
intervalle = estimateur.ate_interval(alpha=0.05)
print("effet causal estimé :", round(float(effet_estime), 1))
print("intervalle de confiance 95 % :", tuple(round(float(b), 1) for b in intervalle))
```

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant « comment mesurer l'effet d'une campagne marketing sur les
    dépenses ». La réponse la plus fréquente est un calcul de différence de moyennes
    entre groupe traité et groupe témoin, exactement le calcul biaisé de l'exercice 3.1,
    sans qu'aucune mention de facteur de confusion n'apparaisse tant que vous ne la
    demandez pas explicitement. Le mot « causalité » ne déclenche pas automatiquement une
    vigilance sur les biais de sélection, même chez un assistant par ailleurs compétent en
    statistiques : c'est vous qui devez vous demander si le groupe traité et le groupe
    témoin sont comparables sur tout le reste avant de faire confiance à leur différence.

!!! question "Exercice 4.1 : l'ajustement fonctionne-t-il vraiment ?"
    Comparez `effet_estime` à l'effet réel (`80`) et vérifiez que l'intervalle de
    confiance à 95 % contient bien cette valeur.

    **Résultat attendu :** un effet estimé proche de `83,4`, et un intervalle de confiance
    approximativement `[68,9 ; 97,9]`, qui contient `80`. L'ajustement par
    `LinearDML` récupère un effet à moins de 5 % de la vraie valeur, là où la différence
    brute de l'étape 3 était fausse d'un facteur presque 5.

    ??? success "Corrigé"
        Le code est déjà celui de l'étape 4 : l'exercice consiste à comparer les deux
        chiffres et à formuler la conclusion. C'est la différence entre décrire des
        données observationnelles (SHAP, importances, différence brute) et estimer ce qui
        se passerait sous une intervention (ajustement causal) : les deux répondent à des
        questions différentes, et confondre l'une pour l'autre conduit à des conclusions
        opérationnelles fausses, ici surestimées d'un facteur cinq.

## Pour aller plus loin

- `shap.plots.waterfall` et `shap.summary_plot` transforment les contributions calculées
  ici en figures lisibles par un public non technique : l'une pour une observation, l'autre
  pour une vue d'ensemble du jeu de données.
- `shap.dependence_plot` révèle comment la contribution d'une variable évolue avec sa
  valeur, et détecte des interactions entre deux variables.
- `LinearDML` suppose un effet homogène dans la population ; `CausalForestDML`
  (toujours dans `econml`) permet d'estimer un effet qui varie selon les individus, utile
  quand on soupçonne que la campagne fonctionne mieux sur certains profils.
- Un test de type « placebo » (remplacer le vrai traitement par un traitement tiré au
  hasard, sans rapport avec les données) est une bonne façon de vérifier qu'une méthode
  d'estimation causale ne détecte pas d'effet là où il ne peut structurellement pas y en
  avoir.

## Ce qu'il faut retenir

`weight`, `gain` et `cover` mesurent trois choses différentes sur l'importance globale
d'une variable ; les croiser vaut mieux que n'en retenir qu'une. Les valeurs SHAP
expliquent une prédiction individuelle, avec une garantie mathématique forte : leur somme
plus la valeur de base reconstitue exactement la prédiction. Ni l'importance globale ni
SHAP ne mesurent un effet causal : une variable peut être très utile au modèle pour
prédire sans que la faire varier ne change réellement le résultat, si elle n'est corrélée
au résultat que par un facteur commun. Estimer un effet causal en présence de facteurs de
confusion suppose de les ajuster explicitement (ici avec `LinearDML`) : une simple
différence entre groupes peut être fausse d'un facteur important.

## Auto-évaluation

Avant de passer au TP10, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer la différence entre `weight`, `gain` et `cover` ;
- [ ] énoncer la propriété d'additivité des valeurs SHAP, et pourquoi elle importe ;
- [ ] distinguer une importance globale d'une explication locale ;
- [ ] expliquer pourquoi une différence brute entre groupe traité et groupe témoin peut
      être un mauvais estimateur d'un effet causal ;
- [ ] nommer au moins un facteur de confusion possible dans un scénario de votre choix.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP10](tp10-theorie-information.md){ .md-button .md-button--primary }
