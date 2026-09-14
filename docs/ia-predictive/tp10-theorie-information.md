# TP10. Théorie de l'information et analyse de données tabulaires

**Durée : 2 h.**

## Objectifs

- Définir l'entropie d'une variable aléatoire, et l'interpréter comme un nombre moyen de
  questions oui/non.
- Calculer une entropie conditionnelle et une information mutuelle, pour quantifier ce
  qu'une variable apprend sur une autre.
- Relier ces notions à un cas concret : quelles variables réduisent le plus l'incertitude
  sur une cible à prédire.
- Observer, sur un modèle XGBoost réel, le lien entre profondeur d'arbre et réduction
  d'incertitude.

## Prérequis

Le [TP1](tp1-pandas.md) (manipulation de données). Sujet plus mathématique que dépendant
des autres TP d'IA prédictive.

```bash
pip install numpy pandas xgboost scikit-learn
```

## Ressources

- Claude Shannon, *A Mathematical Theory of Communication* (1948), l'article fondateur.

---

## Étape 1. L'entropie, ou le nombre de questions qu'il faut poser (25 min)

L'entropie \( H(X) \) d'une variable aléatoire discrète mesure son incertitude moyenne :

\[ H(X) = -\sum_i p_i \log_2(p_i) \]

où \( p_i \) est la probabilité de chaque valeur possible. L'unité, le **bit**, a une
lecture concrète : c'est le nombre moyen de questions oui/non nécessaires pour deviner la
valeur de \( X \), avec une stratégie de questions optimale.

```python
import numpy as np

def entropie(distribution):
    """Entropie en bits d'une distribution de probabilités."""
    p = np.array(distribution, dtype=float)
    p = p[p > 0]  # log(0) n'est pas défini, une probabilité nulle ne contribue rien
    return float(-np.sum(p * np.log2(p)))

piece_equilibree = [0.5, 0.5]
piece_biaisee = [0.7, 0.3]
de_equilibre = [1 / 6] * 6

print("pièce équilibrée :", round(entropie(piece_equilibree), 3), "bits")
print("pièce biaisée 70/30 :", round(entropie(piece_biaisee), 3), "bits")
print("dé équilibré :", round(entropie(de_equilibre), 3), "bits")
```

Une pièce équilibrée vaut exactement 1 bit : une question (« est-ce face ? ») suffit en
moyenne. Un dé équilibré à six faces vaut `log2(6) ≈ 2,585` bits, le maximum possible pour
six issues : c'est la situation la plus incertaine, celle où aucune stratégie de question
ne fait mieux que l'autre.

!!! question "Exercice 1.1 : l'entropie décroît avec le déséquilibre"
    Calculez l'entropie d'un dé pipé `[0.4, 0.2, 0.1, 0.1, 0.1, 0.1]`, et comparez-la à
    celle du dé équilibré. Puis calculez l'entropie d'une distribution dégénérée
    `[1.0, 0.0, 0.0, 0.0, 0.0, 0.0]` (une face sort toujours).

    **Résultat attendu :** le dé pipé vaut environ `2,322` bits, moins que les `2,585`
    bits du dé équilibré : une issue plus probable que les autres réduit l'incertitude
    moyenne. La distribution dégénérée vaut exactement `0` bit : aucune question n'est
    nécessaire quand le résultat est certain d'avance.

    ??? success "Corrigé"
        ```python
        de_biaise = [0.4, 0.2, 0.1, 0.1, 0.1, 0.1]
        de_degenere = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        print("dé biaisé :", round(entropie(de_biaise), 3), "bits")
        print("dé dégénéré :", round(entropie(de_degenere), 3), "bits")
        ```

        L'entropie d'une distribution à \( n \) issues est toujours comprise entre `0`
        (une issue certaine) et `log2(n)` (toutes les issues équiprobables) : ce sont les
        deux bornes que ces deux exemples viennent d'illustrer concrètement.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant d'écrire une fonction d'entropie en Python. Une bonne partie
    des réponses utilisent `np.log` (le logarithme népérien, en **nats**) plutôt que
    `np.log2` (en **bits**), sans le signaler :

    ```python
    p = np.array([0.5, 0.5])
    print("en bits (log2) :", -np.sum(p * np.log2(p)))
    print("en nats (log naturel) :", -np.sum(p * np.log(p)))
    ```

    Une pièce équilibrée vaut exactement `1` bit, mais seulement `0,693` nat : ce n'est
    pas une erreur d'arrondi, ce sont deux unités différentes pour la même quantité, au
    facteur `ln(2) ≈ 0,693` près. Le calcul n'échoue jamais, donc rien ne vous avertit du
    mélange si vous ne connaissez pas la convention utilisée en amont : en apprentissage
    automatique et en théorie de l'information appliquée, le bit (`log2`) est la norme,
    et c'est ce que cette page utilise partout.

## Étape 2. Entropie conditionnelle et information mutuelle (25 min)

Une seule variable ne suffit pas à décrire une relation entre deux phénomènes. L'entropie
**conditionnelle** \( H(Y \mid X) \) mesure l'incertitude qui reste sur \( Y \) une fois
\( X \) connu :

\[ H(Y \mid X) = \sum_x P(X{=}x) \, H(Y \mid X{=}x) \]

C'est la moyenne, pondérée par la fréquence de chaque valeur de \( X \), de l'entropie de
\( Y \) restreinte à chaque sous-groupe. On a toujours \( H(Y \mid X) \le H(Y) \) :
connaître une information supplémentaire ne peut jamais **augmenter** l'incertitude,
seulement la réduire ou la laisser inchangée.

L'**information mutuelle** mesure exactement cette réduction :

\[ I(X;Y) = H(Y) - H(Y \mid X) \]

```python
def entropie_empirique(serie):
    """Entropie en bits d'une série de valeurs observées (comptage des fréquences)."""
    comptes = serie.value_counts()
    p = comptes / len(serie)
    return float(-np.sum(p * np.log2(p)))
```

!!! question "Exercice 2.1 : une information mutuelle sur un exemple jouet"
    Construisez deux colonnes : `X` qui vaut `"pair"` ou `"impair"` selon la parité d'un
    entier tiré entre 1 et 100, et `Y` qui vaut exactement `X` (une copie parfaite).
    Calculez \( H(Y) \), \( H(Y \mid X) \) et \( I(X;Y) \).

    **Résultat attendu :** \( H(Y) \) proche de `1` bit (deux issues à peu près
    équiprobables), \( H(Y \mid X) \) proche de `0` (connaître `X` détermine `Y` sans
    aucune ambiguïté), donc \( I(X;Y) \) proche de `1` : toute l'incertitude sur `Y` est
    expliquée par `X`, le cas limite où l'information mutuelle égale l'entropie de `Y`.

    ??? success "Corrigé"
        ```python
        import pandas as pd

        rng = np.random.default_rng(0)
        entiers = rng.integers(1, 101, size=1000)
        X = pd.Series(np.where(entiers % 2 == 0, "pair", "impair"))
        Y = X.copy()

        H_Y = entropie_empirique(Y)
        H_Y_par_groupe = Y.groupby(X).apply(entropie_empirique)
        H_Y_cond_X = (H_Y_par_groupe * X.value_counts(normalize=True)).sum()
        I_X_Y = H_Y - H_Y_cond_X

        print("H(Y) =", round(H_Y, 3))
        print("H(Y|X) =", round(H_Y_cond_X, 3))
        print("I(X;Y) =", round(I_X_Y, 3))
        ```

        Ce cas limite (`Y` copie exacte de `X`) sert de repère : dans un cas réel,
        l'information mutuelle se situe toujours entre `0` (aucun lien) et `H(Y)`
        (dépendance totale), et sa valeur absolue se lit en la comparant à `H(Y)`, jamais
        isolément.

## Étape 3. Un cas d'usage : prévoir les arrivées aux urgences (40 min)

Simulons trois ans de données journalières pour un service d'urgences, où le nombre
d'arrivées dépend du jour de la semaine, de la température, et d'une éventuelle épidémie
de grippe (doublement du volume) :

```python
import pandas as pd

np.random.seed(42)
jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
n_jours = 156 * 7  # 156 semaines
indice_jour = np.tile(np.arange(7), 156)

effet_jour = {0: 0.1, 1: 0.0, 2: -0.1, 3: -0.05, 4: 0.0, 5: 0.15, 6: 0.2}
temperatures = np.random.rand(n_jours) * 30
grippe = np.random.binomial(1, 0.2, size=n_jours)

log_lambda = (
    np.log(100)
    + np.array([effet_jour[j] for j in indice_jour])
    + 0.02 * temperatures
    + 0.693 * grippe  # 0.693 = ln(2) : la grippe double le volume moyen
)
arrivees = np.random.poisson(np.exp(log_lambda))

df = pd.DataFrame({
    "Jour": [jours[j] for j in indice_jour],
    "Temperature": temperatures,
    "Grippe": grippe,
    "Arrivees": arrivees,
})
print(df.head(3))
print(len(df), "jours simulés")
```

Discrétisons la température (continue) en quatre catégories, pour pouvoir calculer une
entropie empirique dessus comme sur les variables déjà discrètes :

```python
df["TempCat"] = pd.qcut(df["Temperature"], q=4, labels=["très frais", "frais", "doux", "chaud"])

H_Y = entropie_empirique(df["Arrivees"])

def information_mutuelle(cible, groupe):
    h_par_groupe = cible.groupby(groupe, observed=True).apply(entropie_empirique)
    h_conditionnelle = (h_par_groupe * groupe.value_counts(normalize=True)).sum()
    return H_Y - h_conditionnelle

I_jour = information_mutuelle(df["Arrivees"], df["Jour"])
I_temp = information_mutuelle(df["Arrivees"], df["TempCat"])
I_grippe = information_mutuelle(df["Arrivees"], df["Grippe"])

print("H(Arrivées) =", round(H_Y, 3), "bits")
print("I(Arrivées; Jour) =", round(I_jour, 3))
print("I(Arrivées; Température) =", round(I_temp, 3))
print("I(Arrivées; Grippe) =", round(I_grippe, 3))
```

!!! question "Exercice 3.1 : la variable la plus informative n'est pas forcément la plus visible"
    Comparez les trois informations mutuelles calculées. Le classement correspond-il à ce
    que suggère la comparaison brute des moyennes (`df.groupby("Grippe")["Arrivees"].mean()`,
    déjà utilisée dans des TP précédents) ?

    **Résultat attendu :** `I(Arrivées; Jour) ≈ 1,007` bit, `I(Arrivées; Température) ≈
    0,911`, `I(Arrivées; Grippe) ≈ 0,625` : le **jour** de la semaine, avec ses sept
    catégories, porte en réalité la plus grande information mutuelle, davantage que la
    grippe malgré son effet spectaculaire sur la moyenne (`143,8` contre `283,2` arrivées).
    Une variable à plus de catégories a mécaniquement plus de marge pour distinguer des
    sous-groupes différents, ce que l'information mutuelle capture mais qu'une simple
    comparaison de deux moyennes ne montre pas.

    ??? success "Corrigé"
        ```python
        print(df.groupby("Grippe")["Arrivees"].mean())
        print(df.groupby("Jour")["Arrivees"].mean())
        ```

        Cette remarque n'est pas un défaut de l'information mutuelle, c'est une mise en
        garde sur son interprétation : elle mesure une réduction d'incertitude, pas
        l'ampleur d'un effet perçu. Une variable binaire à effet massif (la grippe) et une
        variable à sept catégories avec un effet plus discret (le jour) peuvent porter des
        informations mutuelles comparables, pour des raisons différentes.

## Étape 4. XGBoost et information : la profondeur d'arbre compte l'incertitude réduite (30 min)

Un arbre de décision réduit l'entropie à chaque split, exactement le mécanisme que
l'étape 3 vient de quantifier à la main. Comparons un modèle XGBoost peu profond à un
modèle profond, avec l'objective `count:poisson` du TP7 puisque la cible est un comptage :

```python
import xgboost as xgb
from sklearn.metrics import mean_absolute_error

X = pd.get_dummies(df[["Jour", "Temperature", "Grippe"]], columns=["Jour"])
y = df["Arrivees"]

modele_peu_profond = xgb.XGBRegressor(
    objective="count:poisson", max_depth=2, n_estimators=50, learning_rate=0.1, random_state=42,
)
modele_profond = xgb.XGBRegressor(
    objective="count:poisson", max_depth=6, n_estimators=50, learning_rate=0.1, random_state=42,
)
modele_peu_profond.fit(X, y)
modele_profond.fit(X, y)

mae_peu_profond = mean_absolute_error(y, modele_peu_profond.predict(X))
mae_profond = mean_absolute_error(y, modele_profond.predict(X))
print("MAE, arbres peu profonds (max_depth=2) :", round(mae_peu_profond, 2))
print("MAE, arbres profonds (max_depth=6) :", round(mae_profond, 2))
```

!!! question "Exercice 4.1 : quelle variable domine le modèle, et est-ce cohérent"
    Affichez `feature_importances_` du modèle peu profond, trié par ordre décroissant.
    La variable en tête correspond-elle à celle qui portait la plus grande information
    mutuelle à l'étape 3 ?

    **Résultat attendu :** `Grippe` domine largement l'importance du modèle (autour de
    `0,72`, loin devant `Temperature` à `0,13`), alors qu'à l'étape 3 c'était `Jour` qui
    portait la plus grande information mutuelle **prise isolément**. Ce n'est pas une
    contradiction : XGBoost construit des splits sur des combinaisons de variables, et un
    split binaire net sur `Grippe` (l'écart entre groupes est spectaculaire et biaisé
    d'un seul côté) est plus facile à exploiter par un arbre qu'un effet plus doux réparti
    sur sept catégories.

    ??? success "Corrigé"
        ```python
        importance = pd.Series(
            modele_peu_profond.feature_importances_, index=X.columns
        ).sort_values(ascending=False)
        print(importance.head(5))
        ```

        Information mutuelle et importance d'un modèle d'arbres mesurent des choses
        liées mais pas identiques : la première quantifie une relation statistique brute
        entre deux variables, la seconde quantifie à quel point **cet algorithme
        précis**, avec ses contraintes de construction (splits binaires, profondeur
        limitée), a effectivement exploité cette relation pour réduire son erreur. Un
        modèle différent (une régression, un réseau de neurones) pourrait pondérer les
        mêmes variables autrement.

## Pour aller plus loin

- Le modèle profond réduit la MAE d'environ `16,6` à `9,5` sur ce jeu de données : ce gain
  correspond, en théorie de l'information, à une réduction supplémentaire de l'entropie
  résiduelle \( H(Y \mid X) \), que des arbres plus profonds parviennent à capturer en
  modélisant des interactions entre variables (par exemple, l'effet de la température
  combiné à un jour précis) qu'un arbre peu profond ne peut pas représenter.
- La divergence de Kullback-Leibler généralise l'idée d'information mutuelle à la
  comparaison de deux distributions quelconques ; pour un modèle de comptage, elle est
  étroitement liée à la déviance de Poisson.
- Refaites le calcul de l'étape 3 sans discrétiser la température (avec une estimation à
  noyau de la densité, par exemple) : la discrétisation en quartiles est une
  approximation commode, pas la seule façon de mesurer une information mutuelle sur une
  variable continue.

## Ce qu'il faut retenir

L'entropie mesure l'incertitude d'une variable, en bits, interprétable comme un nombre de
questions oui/non. L'entropie conditionnelle ne peut jamais dépasser l'entropie brute :
connaître une information supplémentaire ne peut que réduire l'incertitude, jamais
l'augmenter. L'information mutuelle quantifie cette réduction, et permet de comparer des
variables de nature différente (catégorielle à sept modalités, binaire, continue
discrétisée) sur une même échelle, ce qu'une simple comparaison de moyennes ne permet pas.
Enfin, l'importance qu'un modèle d'arbres attribue à une variable dépend aussi de la façon
dont cet algorithme construit ses splits, pas seulement de la force statistique brute du
lien entre la variable et la cible.

## Auto-évaluation

Vous devez pouvoir, sans regarder le corrigé :

- [ ] calculer l'entropie d'une distribution de probabilités, et l'interpréter en bits ;
- [ ] expliquer pourquoi `H(Y|X) <= H(Y)` est toujours vrai ;
- [ ] calculer une information mutuelle empirique entre une variable catégorielle et une
      cible ;
- [ ] expliquer pourquoi une variable à effet spectaculaire sur une moyenne n'est pas
      forcément celle qui porte la plus grande information mutuelle ;
- [ ] distinguer l'information mutuelle d'une variable de l'importance qu'un modèle
      d'arbres lui attribue.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Retour au module IA prédictive](index.md){ .md-button .md-button--primary }
