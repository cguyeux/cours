# TP4. XGBoost : arrêt anticipé et ensemble de validation

**Durée : 1 h 45.**

## Objectifs

- Comprendre pourquoi un troisième ensemble, la **validation**, complète le couple
  entraînement/test des TP précédents.
- Mettre en œuvre l'arrêt anticipé (*early stopping*) d'XGBoost avec l'API actuelle.
- Relier le réglage du `learning_rate` au nombre d'arbres réellement utilisés avant
  l'arrêt.
- Lire une courbe d'apprentissage pour diagnostiquer sous-apprentissage et
  surapprentissage.

## Prérequis

Le [TP3](tp3-classification.md) (classification, arbres, forêts) et le
[TP5](tp5-regression.md) (validation croisée) : ce TP les combine sur XGBoost.

```bash
pip install xgboost scikit-learn matplotlib
```

## Ressources

- [Documentation XGBoost, arrêt anticipé](https://xgboost.readthedocs.io/en/stable/python/python_intro.html#early-stopping).

---

## Étape 1. Pourquoi un troisième ensemble (15 min)

Le TP3 séparait les données en entraînement et test. Ici, un troisième ensemble
s'intercale : la **validation**. L'entraînement s'arrête dès que la performance sur la
validation cesse de s'améliorer, un mécanisme qu'on ne peut pas piloter avec le seul jeu
de test, réservé à l'évaluation finale, jamais consultée pendant l'entraînement.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

donnees = load_breast_cancer()
X, y = donnees.data, donnees.target

X_train_complet, X_test, y_train_complet, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_complet, y_train_complet, test_size=0.2, random_state=42, stratify=y_train_complet
)
print(X_train.shape, X_val.shape, X_test.shape)
```

Sur les 569 tumeurs du TP3, ce double partage donne `364` exemples d'entraînement, `91`
de validation, `114` de test : la validation ampute l'entraînement d'un cinquième
supplémentaire, un coût réel qu'il faut mettre en balance avec ce qu'elle apporte.

## Étape 2. L'arrêt anticipé, avec l'API actuelle (25 min)

```python
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

modele = XGBClassifier(
    n_estimators=1000,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss",
    early_stopping_rounds=20,
)
modele.fit(
    X_train, y_train,
    eval_set=[(X_train, y_train), (X_val, y_val)],
    verbose=False,
)

predictions = modele.predict(X_test)
print("Exactitude test :", round(accuracy_score(y_test, predictions), 3))
print("Meilleure itération :", modele.best_iteration)
```

!!! warning "L'IA vous le donne en trois secondes"
    Beaucoup de tutoriels, et donc d'assistants entraînés dessus, écrivent
    `eval_metric="logloss"` et `early_stopping_rounds=20` comme arguments de `.fit()`
    plutôt que du constructeur `XGBClassifier(...)`. Testez :

    ```python
    modele_ancien_style = XGBClassifier(n_estimators=200, learning_rate=0.1, max_depth=4, random_state=42)
    try:
        modele_ancien_style.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            eval_metric="logloss",
            early_stopping_rounds=20,
            verbose=False,
        )
    except TypeError as erreur:
        print("Erreur :", erreur)
    ```

    Depuis XGBoost 2.0, `eval_metric` et `early_stopping_rounds` se déclarent dans le
    constructeur, pas dans `.fit()` : l'ancien style lève une `TypeError` explicite. C'est
    l'exemple même d'un changement d'API qui rend caduque une grande partie des exemples
    trouvés en ligne, y compris dans des cours récents, sans que le message d'erreur ne
    laisse deviner la cause si on ne connaît pas l'historique de la bibliothèque.

`best_iteration` (`99`) indique l'arbre où la validation était la meilleure, sur les
`1000` arbres autorisés : l'entraînement s'est arrêté vingt itérations plus tard sans
amélioration, à l'itération `119`, et XGBoost a conservé le modèle à l'itération `99`, pas
le dernier.

!!! question "Exercice 2.1 : n_estimators ne veut pas dire nombre d'arbres réellement utilisés"
    Affichez `modele.n_estimators` (le paramètre que vous avez fixé) et comparez-le à
    `modele.best_iteration + 1` (le nombre d'arbres réellement conservés). Que se
    passerait-il si vous fixiez `n_estimators=50` au lieu de `1000` ?

    **Résultat attendu :** `n_estimators` vaut `1000`, `best_iteration + 1` vaut `100` :
    l'arrêt anticipé a stoppé l'entraînement bien avant la limite fixée. Avec
    `n_estimators=50`, l'entraînement s'arrêterait à 50 arbres sans jamais déclencher le
    critère d'arrêt anticipé, qui a besoin de marge pour observer une dégradation.

    ??? success "Corrigé"
        ```python
        print("n_estimators (plafond fixé)   :", modele.n_estimators)
        print("arbres réellement utilisés    :", modele.best_iteration + 1)
        ```

        `n_estimators` est un plafond, pas un objectif : avec l'arrêt anticipé, il doit
        être fixé large (ici `1000`) pour ne jamais être le facteur limitant. C'est
        `early_stopping_rounds` qui décide réellement quand s'arrêter.

## Étape 3. `learning_rate` et le nombre d'arbres réellement utilisés (25 min)

```python
for taux in (0.2, 0.1, 0.05, 0.03, 0.01):
    m = XGBClassifier(
        n_estimators=1000, learning_rate=taux, max_depth=4, subsample=0.8, colsample_bytree=0.8,
        random_state=42, eval_metric="logloss", early_stopping_rounds=20,
    )
    m.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_val, y_val)], verbose=False)
    exactitude = accuracy_score(y_test, m.predict(X_test))
    print(f"learning_rate={taux} : arbres utilisés={m.best_iteration + 1}, exactitude test={round(exactitude, 3)}")
```

!!! question "Exercice 3.1 : la relation entre taux et nombre d'arbres"
    D'après la sortie ci-dessus, la relation entre `learning_rate` et le nombre d'arbres
    utilisés avant arrêt est-elle croissante ou décroissante ? Est-elle exactement
    proportionnelle (diviser le taux par deux double-t-il le nombre d'arbres) ?

    **Résultat attendu :** décroissante et nette : `41` arbres à `0.2`, `61` à `0.1`,
    `100` à `0.05`, `209` à `0.03`, `428` à `0.01`. La relation est croissante quand le
    taux diminue, mais pas exactement proportionnelle (passer de `0.1` à `0.05`, un
    facteur 2, ne fait pas exactement doubler le nombre d'arbres). L'exactitude sur le
    test, elle, reste dans une fourchette étroite (`0.939` à `0.947`) sur toute la plage :
    ici, le choix du taux affecte surtout le **coût** d'entraînement, peu la qualité
    finale.

    ??? success "Corrigé"
        Il n'y a pas de code supplémentaire, l'exercice porte sur la lecture des
        résultats déjà produits. Retenez la leçon pratique : quand plusieurs réglages de
        `learning_rate` donnent une qualité comparable, préférez le plus grand des taux
        qui fonctionne, il coûte moins d'itérations et donc moins de temps de calcul,
        pour un résultat final équivalent.

## Étape 4. Lire une courbe d'apprentissage (20 min)

```python
import matplotlib.pyplot as plt

modele.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_val, y_val)], verbose=False)
resultats = modele.evals_result()

plt.figure(figsize=(8, 5))
plt.plot(resultats["validation_0"]["logloss"], label="Entraînement")
plt.plot(resultats["validation_1"]["logloss"], label="Validation")
plt.axvline(modele.best_iteration, color="red", linestyle="--", label="Meilleure itération")
plt.xlabel("Nombre d'arbres")
plt.ylabel("Logloss")
plt.legend()
plt.tight_layout()
plt.show()
```

!!! question "Exercice 4.1 : diagnostiquer sur la courbe"
    Comparez la logloss d'entraînement et de validation aux dernières itérations
    (au delà de la ligne rouge). Laquelle continue de baisser, laquelle stagne ou
    remonte ? Que cela signifie-t-il ?

    **Résultat attendu :** la logloss d'entraînement continue de baisser après la
    meilleure itération (le modèle continue de mieux coller aux données qu'il a déjà
    vues), tandis que la logloss de validation stagne ou remonte légèrement : c'est
    exactement le signal du surapprentissage, déjà rencontré au TP3 avec l'arbre non
    limité, mais ici observable en continu sur une courbe plutôt qu'en un seul point.

    ??? success "Corrigé"
        ```python
        entrainement = resultats["validation_0"]["logloss"]
        validation = resultats["validation_1"]["logloss"]
        i = modele.best_iteration

        print("Logloss entraînement, à la meilleure itération puis 20 plus tard :",
              round(entrainement[i], 4), "->", round(entrainement[-1], 4))
        print("Logloss validation, à la meilleure itération puis 20 plus tard    :",
              round(validation[i], 4), "->", round(validation[-1], 4))
        ```

        C'est précisément ce que l'arrêt anticipé automatise : plutôt que d'inspecter
        cette courbe à l'œil après coup, XGBoost surveille la logloss de validation en
        continu et arrête dès qu'elle ne s'améliore plus pendant `early_stopping_rounds`
        itérations consécutives.

## Étape 5. Avec ou sans ensemble de validation (15 min)

```python
modele_sans_validation = XGBClassifier(
    n_estimators=100, learning_rate=0.05, max_depth=4, subsample=0.8, colsample_bytree=0.8,
    random_state=42,
)
modele_sans_validation.fit(X_train_complet, y_train_complet)
exactitude_sans = accuracy_score(y_test, modele_sans_validation.predict(X_test))
print("Sans validation, 100 arbres fixes :", round(exactitude_sans, 3))
print("Avec arrêt anticipé (étape 2)      :", round(accuracy_score(y_test, predictions), 3))
```

!!! question "Exercice 5.1 : ce que coûte, et ce que rapporte, l'ensemble de validation"
    Le modèle sans validation utilise `X_train_complet` (`455` exemples), le modèle avec
    arrêt anticipé n'utilise que `X_train` (`364` exemples, un cinquième de moins). Sur ce
    jeu de données précis, l'écart d'exactitude entre les deux est-il important ? Dans
    quel cas un praticien choisirait-il quand même l'arrêt anticipé ?

    **Résultat attendu :** un écart faible ou nul sur ce jeu de 569 lignes (les deux
    approches tournent autour de `0.94`), parce que le nombre d'arbres (`100`) était déjà
    raisonnable par construction. L'arrêt anticipé apporte surtout sa valeur quand on ne
    connaît **pas** à l'avance le bon nombre d'arbres : il l'estime automatiquement,
    plutôt que de forcer à le deviner ou à le rechercher par validation croisée complète,
    plus coûteuse en temps de calcul.

    ??? success "Corrigé"
        Pas de code supplémentaire : la comparaison est déjà dans le bloc précédent.
        Retenez le compromis : l'arrêt anticipé économise du **temps de recherche**
        d'hyperparamètre (pas besoin de tester `n_estimators` un par un comme au TP5), au
        prix d'un ensemble d'entraînement plus petit. Sur un grand jeu de données, ce coût
        devient négligeable ; sur un petit jeu, il peut peser.

## Pour aller plus loin

- `early_stopping_rounds` se règle habituellement entre 10 et 50 : trop petit, l'arrêt se
  déclenche sur une fluctuation normale du bruit ; trop grand, il perd son intérêt.
- Sur des classes déséquilibrées, `eval_metric="auc"` ou `"aucpr"` informe souvent mieux
  que `"logloss"` ou `"error"`.
- Combiner arrêt anticipé et `RandomizedSearchCV` (recherche d'autres hyperparamètres,
  `max_depth`, `subsample`) va plus loin que régler `learning_rate` seul comme dans ce TP.

## Ce qu'il faut retenir

Un ensemble de validation, distinct du test, permet à XGBoost de surveiller sa propre
progression et de s'arrêter dès qu'il cesse de s'améliorer, sans jamais consulter le jeu
de test réservé à l'évaluation finale. `n_estimators` doit être fixé large : c'est
`early_stopping_rounds` qui décide réellement combien d'arbres seront utilisés,
consultable après coup dans `best_iteration`. Un `learning_rate` plus petit demande plus
d'arbres avant l'arrêt, pour une qualité finale souvent comparable. Et depuis XGBoost 2.0,
`eval_metric` et `early_stopping_rounds` sont des paramètres du modèle, pas de `.fit()`,
contrairement à ce que montrent encore beaucoup d'exemples en circulation.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer pourquoi un ensemble de validation est distinct du jeu de test ;
- [ ] configurer `eval_metric` et `early_stopping_rounds` avec l'API XGBoost actuelle ;
- [ ] expliquer la différence entre `n_estimators` et `best_iteration + 1` ;
- [ ] lire une courbe entraînement/validation et y repérer un signe de surapprentissage ;
- [ ] relier qualitativement `learning_rate` au nombre d'arbres utilisés avant arrêt.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP6](tp6-series-temporelles.md){ .md-button .md-button--primary }
