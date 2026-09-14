# TP7. XGBoost, objectifs et métriques

**Durée : 2 h.**

## Objectifs

- Distinguer la fonction **objective** (ce que le modèle minimise) de la **métrique**
  (ce qu'on lit pour juger le modèle) : ce ne sont pas toujours la même chose.
- Choisir une objective adaptée à un type de cible : classification, comptage, montants
  avec beaucoup de zéros.
- Suivre plusieurs métriques à la fois, une pour l'arrêt anticipé, une pour les décideurs.
- Écrire une fonction objective personnalisée (gradient et hessien), et comprendre
  pourquoi une objective mal posée peut faire s'effondrer un modèle.

## Prérequis

Le [TP4](tp4-xgboost.md) : arrêt anticipé, ensembles d'entraînement/validation/test.

```bash
pip install xgboost scikit-learn matplotlib
```

## Ressources

- [Documentation XGBoost, paramètres](https://xgboost.readthedocs.io/en/stable/parameter.html#learning-task-parameters).
- [Documentation XGBoost, objectives et métriques personnalisées](https://xgboost.readthedocs.io/en/stable/tutorials/custom_metric_obj.html).

---

## Étape 1. L'objective n'est pas toujours la métrique (20 min)

XGBoost **minimise** une fonction objective à chaque itération. La métrique, elle, sert
uniquement à **lire** la performance : suivre `eval_metric="logloss"` ne change rien à ce
que le modèle optimise si l'objective reste `binary:logistic`, mais changer l'objective
change la façon dont chaque arbre est construit.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train_complet, X_test, y_train_complet, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_complet, y_train_complet, test_size=0.2, random_state=42, stratify=y_train_complet
)

modele = XGBClassifier(
    n_estimators=300, learning_rate=0.1, max_depth=4, subsample=0.8, colsample_bytree=0.8,
    random_state=42, objective="binary:logistic", eval_metric="logloss", early_stopping_rounds=20,
)
modele.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
print("exactitude test :", round(accuracy_score(y_test, modele.predict(X_test)), 3))
```

!!! question "Exercice 1.1 : une objective mal choisie pour la tâche"
    Entraînez le même problème avec `objective="rank:pairwise"` (conçue pour classer des
    éléments les uns par rapport aux autres, pas pour prédire une classe), en gardant les
    mêmes hyperparamètres. Comparez `model.predict()` à ce qu'il donnait avec
    `binary:logistic` : les valeurs ont-elles encore le même sens ?

    **Résultat attendu :** avec `binary:logistic`, `predict()` renvoie directement des
    classes 0 ou 1, exactitude environ `0.947`. Avec `rank:pairwise`, `predict()` renvoie
    des scores de classement bruts, pas des classes : les comparer à `y_test` directement
    (ou même après un seuillage naïf à la médiane) donne une exactitude nettement plus
    faible, autour de `0.70`, pour un modèle qui n'est pourtant pas « mauvais », juste
    employé hors de son usage prévu.

    ??? success "Corrigé"
        ```python
        import numpy as np
        from xgboost import XGBClassifier

        modele_rank = XGBClassifier(
            n_estimators=100, objective="rank:pairwise", eval_metric="auc", random_state=42,
        )
        modele_rank.fit(X_train, y_train)
        scores = modele_rank.predict(X_test)
        classes_naives = (scores > np.median(scores)).astype(int)
        print("exactitude avec rank:pairwise, seuillage naïf :", round(accuracy_score(y_test, classes_naives), 3))
        ```

        La leçon n'est pas que `rank:pairwise` est un mauvais objective, elle est que
        chaque objective produit une sortie dont la nature diffère (probabilité, log-odds,
        score de rang, log-compte...), et qu'une bonne exactitude sur un problème de
        classification suppose d'avoir choisi une objective dont la sortie *est* une
        probabilité ou une classe, pas un score dont l'échelle est arbitraire.

## Étape 2. Suivre plusieurs métriques, pour des publics différents (25 min)

Rien n'empêche de suivre une métrique technique (pour l'arrêt anticipé) et une métrique
métier (pour un rapport) en même temps :

```python
from sklearn.datasets import fetch_california_housing
from xgboost import XGBRegressor

X_h, y_h = fetch_california_housing(return_X_y=True)
Xh_train_complet, Xh_test, yh_train_complet, yh_test = train_test_split(X_h, y_h, test_size=0.2, random_state=42)
Xh_train, Xh_val, yh_train, yh_val = train_test_split(Xh_train_complet, yh_train_complet, test_size=0.2, random_state=42)

reg = XGBRegressor(
    n_estimators=500, learning_rate=0.1, max_depth=4, random_state=42,
    objective="reg:squarederror", eval_metric=["rmse", "mae"], early_stopping_rounds=30,
)
reg.fit(Xh_train, yh_train, eval_set=[(Xh_train, yh_train), (Xh_val, yh_val)], verbose=False)

resultats = reg.evals_result()
print("RMSE final validation :", round(resultats["validation_1"]["rmse"][-1], 3))
print("MAE final validation :", round(resultats["validation_1"]["mae"][-1], 3))
```

Avec `eval_metric` en liste, XGBoost journalise **toutes** les métriques mais n'utilise
que la **première** pour décider de l'arrêt anticipé : ici `rmse` pilote l'arrêt, `mae`
n'est là que pour être lue par un humain.

!!! question "Exercice 2.1 : tracer les deux courbes"
    Tracez `rmse` et `mae`, train et validation, sur deux sous-graphiques. La forme des
    deux courbes est-elle identique à un facteur d'échelle près ?

    **Résultat attendu :** les deux courbes décroissent puis se stabilisent au même
    rythme (elles mesurent le même écart, avec une pénalité différente sur les grandes
    erreurs), mais RMSE reste systématiquement au-dessus de MAE : c'est une propriété
    mathématique générale, pas un artefact de ce jeu de données, l'écart quadratique
    moyen pénalise davantage les grandes erreurs individuelles que l'écart absolu moyen.

    ??? success "Corrigé"
        ```python
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.plot(resultats["validation_0"]["rmse"], label="train")
        ax1.plot(resultats["validation_1"]["rmse"], label="validation")
        ax1.set_title("RMSE")
        ax1.legend()
        ax2.plot(resultats["validation_0"]["mae"], label="train")
        ax2.plot(resultats["validation_1"]["mae"], label="validation")
        ax2.set_title("MAE")
        ax2.legend()
        plt.tight_layout()
        plt.show()
        ```

        Un rapport destiné à des décideurs gagne presque toujours à afficher la MAE
        (« en moyenne, on se trompe de X »), plus lisible que la RMSE, réservée à piloter
        l'entraînement.

## Étape 3. Une objective adaptée aux comptages (25 min)

`reg:squarederror` ne sait pas qu'un comptage (nombre de locations, nombre d'incidents)
ne peut pas être négatif. `count:poisson` et `reg:tweedie` le savent, par construction.

```python
from sklearn.datasets import fetch_openml
import numpy as np

velos = fetch_openml(data_id=42712, as_frame=True, parser="auto")
df = velos.frame
y_v = df["count"].astype(float)
X_v = df.drop(columns=["count"]).select_dtypes(include=[np.number])

Xv_train, Xv_test, yv_train, yv_test = train_test_split(X_v, y_v, test_size=0.2, random_state=42)

for objective, params in [
    ("reg:squarederror", {}),
    ("count:poisson", {}),
    ("reg:tweedie", {"tweedie_variance_power": 1.3}),
]:
    modele_c = XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42, objective=objective, **params)
    modele_c.fit(Xv_train, yv_train)
    predictions = modele_c.predict(Xv_test)
    part_negative = (predictions < 0).mean()
    print(f"{objective:20s} part de prédictions négatives : {part_negative:.1%}")
```

!!! question "Exercice 3.1 : mesurer le vrai coût d'ignorer la nature du comptage"
    Comparez la MAE des trois objectives sur ce jeu de comptage de locations de vélos
    (`velos`, dataset OpenML Bike Sharing Demand, 17 379 lignes horaires).

    **Résultat attendu :** `reg:squarederror` produit environ `2,7 %` de prédictions
    négatives, un nombre de locations négatif étant évidemment absurde. `count:poisson`
    et `reg:tweedie` n'en produisent jamais. Sur ce jeu précis, `reg:tweedie` donne aussi
    la meilleure MAE des trois (environ `27,9` contre `31,2` pour `reg:squarederror`) :
    ce n'est pas garanti sur tout jeu de comptage, mais le fait de ne jamais halluciner de
    valeur négative, lui, l'est toujours.

    ??? success "Corrigé"
        ```python
        from sklearn.metrics import mean_absolute_error

        for objective, params in [
            ("reg:squarederror", {}),
            ("count:poisson", {}),
            ("reg:tweedie", {"tweedie_variance_power": 1.3}),
        ]:
            modele_c = XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42, objective=objective, **params)
            modele_c.fit(Xv_train, yv_train)
            predictions = np.clip(modele_c.predict(Xv_test), 0, None)
            print(objective, "MAE :", round(mean_absolute_error(yv_test, predictions), 2))
        ```

        `np.clip(predictions, 0, None)` est le correctif habituel pour forcer
        `reg:squarederror` à rester positif après coup : cela répare le symptôme, pas la
        cause. Une objective de comptage encode la contrainte de positivité **dans le
        modèle lui-même** (par une transformation exponentielle en sortie), ce qui évite
        d'avoir à corriger après coup.

## Étape 4. Une objective personnalisée, et pourquoi elle peut s'effondrer (35 min)

Une objective personnalisée fournit à XGBoost le **gradient** et le **hessien** de la
perte qu'on veut minimiser, avec `xgb.train` (l'API bas niveau, pas `XGBClassifier`).

Imaginons vouloir forcer la variance des prédictions à se rapprocher de celle de la
cible, par la perte \( \mathcal{L} = (\sigma_{\hat y}^2 - \sigma_y^2)^2 \) :

```python
import xgboost as xgb

X_train_h, X_temp_h, y_train_h, y_temp_h = train_test_split(X_h, y_h, test_size=0.4, random_state=42)
X_val_h, X_test_h, y_val_h, y_test_h = train_test_split(X_temp_h, y_temp_h, test_size=0.5, random_state=42)

sigma_y2 = np.var(y_train_h)
dtrain = xgb.DMatrix(X_train_h, label=y_train_h)
dval = xgb.DMatrix(X_val_h, label=y_val_h)

def variance_matching_obj(preds, dtrain):
    n = preds.size
    moyenne_preds = np.mean(preds)
    variance_preds = np.mean((preds - moyenne_preds) ** 2)
    grad = (4.0 / n) * (variance_preds - sigma_y2) * (preds - moyenne_preds)
    hess = np.full_like(preds, 4.0 / n)
    return grad, hess

params = {"max_depth": 4, "eta": 0.1, "subsample": 0.8, "colsample_bytree": 0.8}
bst = xgb.train(params, dtrain, num_boost_round=200, obj=variance_matching_obj,
                 evals=[(dval, "validation")], verbose_eval=False)

predictions_val = bst.predict(dval)
print("écart-type des prédictions :", round(np.std(predictions_val), 3))
print("écart-type de la cible d'entraînement :", round(np.std(y_train_h), 3))
```

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant de coder cette objective personnalisée depuis les formules de
    gradient et de hessien données par l'énoncé (comme ci-dessus). Le code qu'il produit
    ressemble exactement au bloc ci-dessus, et **il compile sans erreur**. Exécutez-le
    quand même jusqu'au bout et regardez `np.std(predictions_val)` : il vaut `0.0`. Le
    modèle s'est effondré sur une seule valeur constante, sans qu'aucune erreur ne le
    signale. La raison est mathématique : au premier tour, toutes les prédictions valent
    le même score de départ, donc `preds - moyenne_preds` est nul partout, donc le
    gradient est nul partout, et XGBoost n'a aucune raison de choisir un split plutôt
    qu'un autre. Une objective qui ne dépend que de la variance des prédictions n'a pas de
    prise sur leur position : c'est un point fixe dégénéré, pas une objective mal
    programmée. Un assistant qui se contente de traduire des formules mathématiques en
    code ne vérifie pas que la descente de gradient qui en résulte converge vers quelque
    chose d'utile.

!!! question "Exercice 4.1 : réparer l'objective en la mélangeant à une perte standard"
    La source suggère de mélanger la perte de variance à la MSE classique :
    \( \mathcal{L}_{total} = \text{MSE} + \lambda \, \mathcal{L}_{variance} \). Implémentez
    cette version mélangée avec `lam=0.3`, et vérifiez que le modèle ne s'effondre plus.

    **Résultat attendu :** un écart-type des prédictions redevenu comparable à celui de la
    cible (rapport de variance autour de `0,8`, contre `0,0` pour l'objective seule), et
    une RMSE quasi identique à un modèle `reg:squarederror` standard sur ce jeu de
    données : le terme MSE fournit le gradient qui manquait, le terme de variance n'a ici
    qu'un effet marginal supplémentaire.

    ??? success "Corrigé"
        ```python
        def objective_melangee(preds, dtrain, lam=0.3):
            labels = dtrain.get_label()
            n = preds.size
            moyenne_preds = np.mean(preds)
            variance_preds = np.mean((preds - moyenne_preds) ** 2)
            grad_variance = (4.0 / n) * (variance_preds - sigma_y2) * (preds - moyenne_preds)
            hess_variance = np.full_like(preds, 4.0 / n)
            residus = preds - labels
            grad_mse = residus
            hess_mse = np.ones_like(preds)
            return grad_mse + lam * grad_variance, hess_mse + lam * hess_variance

        bst_melange = xgb.train(params, dtrain, num_boost_round=200, obj=objective_melangee,
                                 evals=[(dval, "validation")], verbose_eval=False)
        predictions_melange = bst_melange.predict(dval)
        print("rapport de variance :", round(np.var(predictions_melange) / sigma_y2, 3))
        print("RMSE :", round(float(np.sqrt(np.mean((predictions_melange - y_val_h) ** 2))), 3))
        ```

        Le terme MSE n'est pas un simple à-côté ici : c'est lui qui donne à chaque
        prédiction individuelle une raison de s'écarter de la moyenne. Une objective
        composite fonctionne quand chacun de ses termes a un gradient non dégénéré en
        dehors de son minimum ; en avoir vérifié un seul (celui qui semblait le plus
        intéressant du point de vue métier) ne suffit pas.

## Pour aller plus loin

- Une métrique personnalisée s'écrit sur le même principe qu'une objective personnalisée,
  mais sans gradient ni hessien : `custom_metric=ma_fonction` dans `xgb.train` (nommé
  `feval` dans d'anciennes versions d'XGBoost, un autre exemple du même piège de
  documentation périmée que `use_label_encoder` au TP4).
- `rank:ndcg` et les autres objectives de classement se prêtent à des scénarios de
  recommandation ou de moteur de recherche, hors du cadre de ce TP.
- `survival:cox` traite les données de survie (temps avant événement, avec des
  observations censurées), un sujet à part entière en biostatistique.

## Ce qu'il faut retenir

L'objective est ce que XGBoost minimise, la métrique est ce qu'on lit : les deux peuvent
diverger, et suivre une bonne métrique ne corrige pas une mauvaise objective. Le choix de
l'objective doit correspondre à la nature de la cible : une classe (`binary:logistic`),
un comptage qui ne peut pas être négatif (`count:poisson`, `reg:tweedie`), ou un
classement relatif (`rank:pairwise`), pas une régression générique appliquée par défaut.
Plusieurs métriques peuvent être suivies en même temps, une seule pilote l'arrêt anticipé
(la première de la liste). Une objective personnalisée fournit gradient et hessien : elle
doit avoir un gradient non nul en dehors de son minimum, sans quoi l'entraînement peut
s'effondrer sur une solution dégénérée sans qu'aucune erreur ne le signale.

## Auto-évaluation

Avant de passer au TP9, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer la différence entre une fonction objective et une métrique ;
- [ ] choisir une objective de comptage plutôt que `reg:squarederror` pour une cible qui
      ne peut pas être négative, et dire pourquoi ;
- [ ] lire `model.evals_result()` pour tracer une courbe de métrique ;
- [ ] écrire une fonction objective personnalisée (gradient, hessien) avec `xgb.train` ;
- [ ] expliquer pourquoi une objective dont le gradient est nul à son point de départ peut
      faire s'effondrer un modèle sur une solution constante.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP8](tp8-pretraitement.md){ .md-button .md-button--primary }
