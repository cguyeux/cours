# TP6. Séries temporelles

**Durée : 3 h.**

## Objectifs

- Explorer une série temporelle réelle et identifier ses motifs (tendance, saisonnalité).
- Décomposer une série en tendance, saisonnalité et résidu, et tester sa stationnarité.
- Construire une prévision avec des modèles classiques (persistance, AR, ARIMA).
- Reformuler la prévision en un problème d'apprentissage supervisé avec des variables
  retardées, et comparer les deux familles d'approches.

## Prérequis

Le [TP1](tp1-pandas.md) pour la manipulation de données, le [TP5](tp5-regression.md) pour
la logique de validation d'un modèle de régression.

```bash
pip install pandas numpy matplotlib scikit-learn statsmodels xgboost
```

## Ressources

- [Documentation statsmodels, modèles ARIMA](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html).
- [Documentation scikit-learn, `TimeSeriesSplit`](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split).

---

## Étape 1. Charger et comprendre une série temporelle réelle (35 min)

Le jeu de données *Bike Sharing Demand* décrit la location horaire de vélos en libre-service
à Washington DC sur deux ans (2011-2012) : 17 379 heures, avec la météo du moment et le
nombre de locations. C'est un cas d'école pour la prévision de demande : les motifs y sont
nets (heures de pointe, week-ends, saisons) et le volume est assez grand pour que le bruit
ne domine pas le signal.

```python
from sklearn.datasets import fetch_openml
import pandas as pd

brut = fetch_openml(data_id=42712, as_frame=True, parser="auto")
df = brut.frame.copy()
for colonne in ["year", "month", "hour", "weekday"]:
    df[colonne] = df[colonne].astype(int)
df["count"] = df["count"].astype(int)

print(df.shape)
print(df[["season", "year", "month", "hour", "weekday", "count"]].head())
```

Ce miroir du jeu de données ne fournit pas la date calendaire exacte de chaque
observation, seulement l'année, le mois, l'heure et le jour de la semaine, dans l'ordre
chronologique. C'est suffisant pour tout ce TP : la plupart des analyses de série
temporelle raisonnent de toute façon en **position dans le cycle** (quelle heure, quel
jour) plutôt qu'en date absolue.

```python
serie = df["count"].reset_index(drop=True)
serie.index.name = "heure_sequentielle"
print(serie.describe())
```

La demande moyenne est d'environ 189 locations par heure, avec un écart-type de 181, ce
qui dit déjà quelque chose : l'écart-type dépasse presque la moyenne, la distribution est
loin d'être symétrique autour de sa moyenne.

!!! question "Exercice 1.1 : deux profils cycliques"
    Calculez la demande moyenne par heure de la journée, séparément pour les jours de
    semaine et pour le week-end (`weekday` vaut 0 pour lundi, 5 et 6 pour samedi et
    dimanche). Le week-end suit-il la même forme de profil horaire que la semaine ?

    **Résultat attendu :** en semaine, un profil à **deux pics nets** séparés par un creux,
    vers 8 h (environ 388 locations en moyenne) et surtout vers 17 h (environ 481), la
    signature d'un usage domicile-travail. Le week-end, un profil **sans creux**, qui monte
    progressivement le matin et reste élevé de 11 h à 17 h (entre 250 et 350 en moyenne),
    sans les deux pics séparés de la semaine.

    ??? success "Corrigé"
        ```python
        df["est_weekend"] = df["weekday"].isin([5, 6])
        profil_semaine = df[~df["est_weekend"]].groupby("hour")["count"].mean().round(1)
        profil_weekend = df[df["est_weekend"]].groupby("hour")["count"].mean().round(1)

        comparaison = pd.DataFrame({"semaine": profil_semaine, "weekend": profil_weekend})
        print(comparaison)
        print("creux de la semaine, à 10h :", profil_semaine.loc[10])
        print("weekend à la même heure, à 10h :", profil_weekend.loc[10])
        ```

        À 10 h, la semaine est en plein creux entre les deux pics (environ 159) alors que
        le week-end est déjà proche de son plateau (environ 211) : la même heure porte un
        sens complètement différent selon le jour. Deux populations d'usagers se cachent
        dans une seule série agrégée : c'est une des raisons qui motivent l'étape 5, où
        l'heure et le jour deviennent des variables du modèle plutôt qu'une moyenne qui les
        efface.

## Étape 2. Décomposer une série : tendance, saisonnalité, résidu (30 min)

Une série temporelle se pense comme la somme (modèle additif) ou le produit (modèle
multiplicatif) de plusieurs composantes : un niveau de fond qui évolue lentement (la
tendance), un motif qui se répète à intervalle fixe (la saisonnalité), et ce qui reste une
fois les deux retirés (le résidu).

```python
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

decomposition = seasonal_decompose(serie, model="additive", period=24)

fig, axes = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
decomposition.observed.plot(ax=axes[0], title="Série observée")
decomposition.trend.plot(ax=axes[1], title="Tendance")
decomposition.seasonal.plot(ax=axes[2], title="Saisonnalité (période 24 h)")
decomposition.resid.plot(ax=axes[3], title="Résidu")
plt.tight_layout()
plt.show()
```

`period=24` dit à `seasonal_decompose` de chercher un motif qui se répète toutes les 24
observations, l'hypothèse naturelle pour une série horaire avec un cycle quotidien.

!!! question "Exercice 2.1 : un second cycle, hebdomadaire, et sa vraie limite"
    Refaites la décomposition avec `period=24*7` (168, le cycle hebdomadaire) plutôt que
    24, et comparez la part de variance de la série que chaque décomposition explique
    (`1 - variance(résidu) / variance(série)`).

    **Résultat attendu :** les deux décompositions se valent presque, et c'est le résultat
    surprenant : environ 25 % de variance expliquée avec `period=24`, environ 24 % avec
    `period=168`. Aucune des deux ne capture l'essentiel de la variabilité de la série.

    ??? success "Corrigé"
        ```python
        decomposition_semaine = seasonal_decompose(serie, model="additive", period=24 * 7)

        variance_totale = serie.var()
        for nom, resultat in [("24", decomposition), ("168", decomposition_semaine)]:
            variance_residu = resultat.resid.dropna().var()
            part_expliquee = 1 - variance_residu / variance_totale
            print(f"period={nom} : part de variance expliquée = {part_expliquee:.3f}")
        ```

        Ni le cycle quotidien seul, ni le cycle hebdomadaire seul, n'expliquent la
        majorité de la variance : environ 75 % reste dans le résidu, dans les deux cas.
        L'exercice 1.1 donne la clé de cette énigme : le profil horaire n'est PAS le même
        en semaine et le week-end (deux pics contre un plateau). Une décomposition à une
        seule période force un unique profil moyen sur les 24 heures, qui n'est fidèle ni
        aux jours de semaine ni aux week-ends. C'est un cas où le bon diagnostic (variance
        mal expliquée) demande de croiser deux facteurs (l'heure ET le type de jour), pas
        d'ajouter une seconde période à une décomposition qui n'en gère qu'une à la fois.
        Des modèles plus avancés (SARIMA multi-saisonnier, Prophet, ou tout simplement le
        modèle supervisé de l'étape 5 qui inclut `heure` et `jour_semaine` comme variables
        séparées) répondent mieux à ce genre de structure croisée.

## Étape 3. Stationnarité : ce qu'un test ADF dit vraiment (25 min)

Un modèle AR ou ARIMA suppose une série **stationnaire** : une moyenne et une variance qui
ne dérivent pas dans le temps. Le test de Dickey-Fuller augmenté (ADF) teste cette
hypothèse.

```python
from statsmodels.tsa.stattools import adfuller

stat, pvalue, *_ = adfuller(serie)
print(f"statistique : {stat:.3f}, p-value : {pvalue:.4f}")
```

!!! question "Exercice 3.1 : une série saisonnière peut-elle être stationnaire ?"
    Exécutez le test ADF ci-dessus sur `serie`, la série brute, **sans** l'avoir
    différenciée. Le test conclut-il à la stationnarité (p-value < 0,05) ? Est-ce
    surprenant, sachant que la série a un motif quotidien évident (étape 1) ?

    **Résultat attendu :** oui, le test ADF conclut à la stationnarité de la série brute
    (p-value proche de `0`), alors même qu'elle est visiblement saisonnière. Ce n'est pas
    une erreur : le test ADF détecte une **racine unitaire** (une dérive de type marche
    aléatoire, où les chocs s'accumulent indéfiniment), pas une saisonnalité. Une série
    peut osciller fortement de façon parfaitement régulière, sans jamais dériver, et rester
    stationnaire au sens de ce test.

    ??? success "Corrigé"
        ```python
        stat, pvalue, *_ = adfuller(serie)
        print(f"série brute : statistique {stat:.3f}, p-value {pvalue:.4f}")

        diff1 = serie.diff().dropna()
        stat_d, pvalue_d, *_ = adfuller(diff1)
        print(f"différenciée (ordre 1) : statistique {stat_d:.3f}, p-value {pvalue_d:.6f}")
        ```

        La différenciation rend la statistique ADF encore plus négative (la série brute
        était déjà stationnaire, la différenciée l'est encore plus fortement), mais elle
        **retire** l'essentiel du niveau moyen et donc du motif quotidien, ce qui n'est
        pas toujours souhaitable : un ADF significatif ne dit pas qu'il faut différencier,
        il dit seulement qu'un modèle ARMA sans différenciation (`d=0`) est défendable. Le
        vrai critère pour choisir `d` est de regarder ce que la différenciation fait à
        l'interprétabilité et aux résidus, pas seulement à la p-value.

## Étape 4. Prévoir avec un modèle classique : persistance, AR, ARIMA (35 min)

Réservons les 7 derniers jours (168 heures) comme test, et entraînons nos modèles sur tout
ce qui précède.

```python
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

horizon = 24 * 7
train, test = serie.iloc[:-horizon], serie.iloc[-horizon:]
print(train.shape, test.shape)

# baseline : on répète la dernière valeur connue de l'entraînement sur tout l'horizon
prevision_plate = pd.Series(train.iloc[-1], index=test.index)
mae_plate = mean_absolute_error(test, prevision_plate)
rmse_plate = root_mean_squared_error(test, prevision_plate)
print(f"baseline plate : MAE {mae_plate:.2f}, RMSE {rmse_plate:.2f}")
```

C'est la baseline la plus honnête pour une prévision à horizon fixe : au moment de la
prévision, la seule chose que l'on connaît avec certitude est la dernière valeur observée.

```python
from statsmodels.tsa.ar_model import AutoReg

modele_ar = AutoReg(train, lags=24).fit()
prevision_ar = modele_ar.predict(start=len(train), end=len(train) + len(test) - 1)
prevision_ar.index = test.index

mae_ar = mean_absolute_error(test, prevision_ar)
rmse_ar = root_mean_squared_error(test, prevision_ar)
print(f"AR(24) : MAE {mae_ar:.2f}, RMSE {rmse_ar:.2f}")
```

!!! warning "L'IA vous le donne en trois secondes"
    Beaucoup de tutoriels et d'assistants écrivent encore `AutoReg(train, lags=24,
    old_names=False)`, un paramètre qui existait dans d'anciennes versions de statsmodels
    pour gérer une transition de nommage. Il a depuis été retiré :

    ```python
    try:
        AutoReg(train, lags=24, old_names=False)
    except TypeError as erreur:
        print("Erreur :", erreur)
    ```

    Ceci lève une `TypeError`, pas un avertissement : le code s'arrête. C'est un exemple de
    plus de la règle déjà rencontrée aux TP4 et TP5 : une bibliothèque de machine learning
    évolue vite, et du code qui fonctionnait il y a un an peut être du code mort
    aujourd'hui. Retirez simplement le paramètre.

```python
from statsmodels.tsa.arima.model import ARIMA

modele_arima = ARIMA(train, order=(2, 0, 2)).fit()
prevision_arima = modele_arima.forecast(steps=len(test))

mae_arima = mean_absolute_error(test.values, prevision_arima.values)
rmse_arima = root_mean_squared_error(test.values, prevision_arima.values)
print(f"ARIMA(2,0,2) : MAE {mae_arima:.2f}, RMSE {rmse_arima:.2f}")
```

!!! question "Exercice 4.1 : pourquoi ARIMA(2,0,2) perd contre la baseline"
    Comparez les trois MAE obtenus (baseline plate, AR(24), ARIMA(2,0,2)). L'un des trois
    modèles « avancés » fait-il moins bien que la baseline la plus simple ? Regardez les
    ordres `p`, `d`, `q` choisis pour comprendre pourquoi.

    **Résultat attendu :** ARIMA(2,0,2) (MAE autour de `123`) fait **nettement moins bien**
    que la baseline plate (MAE autour de `65`), elle-même battue par AR(24) (MAE autour de
    `50`). Ce n'est pas qu'ARIMA soit un mauvais modèle : c'est que `p=2` ne regarde que
    deux heures en arrière, bien trop court pour capturer le cycle de 24 heures identifié
    à l'étape 1. AR(24), lui, regarde explicitement jusqu'à 24 heures en arrière et attrape
    ainsi le cycle quotidien.

    ??? success "Corrigé"
        ```python
        comparaison = pd.DataFrame({
            "modèle": ["baseline plate", "AR(24)", "ARIMA(2,0,2)"],
            "MAE": [mae_plate, mae_ar, mae_arima],
            "RMSE": [rmse_plate, rmse_ar, rmse_arima],
        })
        print(comparaison.round(2))
        ```

        La leçon n'est pas « ARIMA est mauvais », elle est « le choix de l'ordre compte
        plus que le choix du modèle ». Un ARIMA avec un ordre `p` assez grand pour couvrir
        24 heures, ou une saisonnalité explicite (SARIMA), retrouverait un comportement
        comparable à AR(24). Comparer des modèles sans comparer leurs hypothèses
        (ici, la portée temporelle qu'ils regardent) mène à des conclusions trompeuses.

## Étape 5. Reformuler en apprentissage supervisé (35 min)

Une autre manière d'aborder la prévision : transformer la série en un problème de
régression classique, où les variables explicatives sont des valeurs passées de la série
elle-même (des **lags**) et des informations calendaires.

```python
caracteristiques = pd.DataFrame(index=serie.index)
caracteristiques["heure"] = df["hour"]
caracteristiques["jour_semaine"] = df["weekday"]
caracteristiques["mois"] = df["month"]
caracteristiques["est_weekend"] = caracteristiques["jour_semaine"].isin([5, 6]).astype(int)

for lag in [1, 2, 24, 168]:
    caracteristiques[f"lag_{lag}"] = serie.shift(lag)
caracteristiques["moyenne_glissante_24h"] = serie.shift(1).rolling(24).mean()
caracteristiques["count"] = serie

caracteristiques = caracteristiques.dropna()
print(caracteristiques.shape)
```

`serie.shift(1).rolling(24)`, et non `serie.rolling(24)` directement : la moyenne glissante
d'une heure ne doit dépendre **que** du passé, jamais de l'heure elle-même, sans quoi le
modèle « voit » indirectement ce qu'il doit prédire (une fuite de données, déjà rencontrée
au TP8 sous une autre forme).

```python
from sklearn.ensemble import RandomForestRegressor

entrainement = caracteristiques.iloc[:-horizon]
test_sup = caracteristiques.iloc[-horizon:]
X_train, y_train = entrainement.drop(columns="count"), entrainement["count"]
X_test, y_test = test_sup.drop(columns="count"), test_sup["count"]

foret = RandomForestRegressor(n_estimators=200, max_depth=12, min_samples_leaf=5, n_jobs=-1, random_state=42)
foret.fit(X_train, y_train)
prevision_foret = foret.predict(X_test)

mae_foret = mean_absolute_error(y_test, prevision_foret)
rmse_foret = root_mean_squared_error(y_test, prevision_foret)
print(f"Forêt aléatoire : MAE {mae_foret:.2f}, RMSE {rmse_foret:.2f}")
```

!!! question "Exercice 5.1 : quelle variable porte la prévision"
    Affichez `foret.feature_importances_` associé aux noms de colonnes, trié par ordre
    décroissant. Quelle variable domine largement les autres ? Est-ce cohérent avec ce
    que la baseline plate de l'étape 4 utilisait déjà ?

    **Résultat attendu :** `lag_1` (la valeur de l'heure précédente) porte environ 69 % de
    l'importance totale, très loin devant toutes les autres variables. `lag_168` (la même
    heure la semaine précédente) vient en second, autour de 16 %.

    ??? success "Corrigé"
        ```python
        importances = pd.Series(foret.feature_importances_, index=X_train.columns)
        print(importances.sort_values(ascending=False).round(3))
        ```

        C'est cohérent, et ça explique pourquoi ce modèle (MAE autour de `15`) bat de loin
        tous les modèles de l'étape 4 : il retrouve, via `lag_1`, une information très
        proche de celle qu'utilisait la baseline plate (la dernière valeur observée), mais
        y ajoute `lag_168` (le même moment la semaine passée) et le contexte calendaire.
        Le modèle supervisé ne gagne pas parce qu'il est plus sophistiqué en soi : il gagne
        parce qu'il a accès, comme la baseline plate, à la toute dernière valeur réelle
        juste avant l'instant à prédire, ce qu'ARIMA et AR, lancés une fois pour tout
        l'horizon de 7 jours, n'ont pas.

## Pour aller plus loin

- Un modèle **SARIMA** (`p,d,q`×`P,D,Q,s`) intègre directement une saisonnalité dans sa
  structure, plutôt que de compter sur un ordre `p` élevé pour l'attraper indirectement.
- Une **prévision glissante** (*rolling forecast*) réinjecte à chaque pas la vraie valeur
  observée, ou à défaut la prédiction précédente, pour comparer les modèles sur un horizon
  d'un pas plutôt que sur un horizon fixe de 7 jours.
- Les variables météo du jeu de données (`temp`, `humidity`, `windspeed`) n'ont pas été
  utilisées ici : les ajouter aux caractéristiques de l'étape 5 est un prolongement
  naturel.
- XGBoost (TP4) peut remplacer la forêt aléatoire dans l'étape 5 pour comparer les deux
  familles d'ensembles d'arbres sur ce problème.

## Ce qu'il faut retenir

Une série temporelle se décompose en tendance, saisonnalité et résidu, et cette
décomposition dépend d'une période choisie a priori. Le test ADF détecte une racine
unitaire, pas une saisonnalité : une série peut osciller fortement et rester stationnaire
au sens de ce test. Comparer des modèles de prévision exige de comparer des baselines
justes : une baseline « plate » (dernière valeur connue) pour un horizon fixe, pas une
baseline qui triche en réutilisant des valeurs futures. L'ordre d'un modèle AR ou ARIMA
doit couvrir la portée du cycle qu'on veut capturer, sinon un modèle plus simple mais mieux
dimensionné (ici, AR(24) contre ARIMA(2,0,2)) le bat largement. Et reformuler la prévision
en apprentissage supervisé avec des lags permet souvent de battre les modèles classiques,
en grande partie parce que le lag le plus récent contient déjà l'essentiel du signal.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] décomposer une série en tendance, saisonnalité et résidu, et choisir une période ;
- [ ] expliquer ce qu'un test ADF teste, et ce qu'il ne teste pas ;
- [ ] construire une baseline de prévision honnête pour un horizon fixe ;
- [ ] expliquer pourquoi l'ordre d'un modèle AR ou ARIMA doit être cohérent avec le cycle
      de la série ;
- [ ] construire des variables retardées (`lag`) et une moyenne glissante sans fuite de
      données, pour reformuler une série en problème supervisé.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP7](tp7-xgboost-objectifs-metriques.md){ .md-button .md-button--primary }
