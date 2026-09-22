# TP3. Dériver, descendre, diverger

**Durée : 2 h.**

## Objectifs

- Mesurer pourquoi une dérivée calculée par différence finie n'est jamais exacte, et
  constater qu'aucun choix de pas ne répare complètement le problème.
- Implémenter les nombres duaux, c'est-à-dire la dérivation automatique, en une quarantaine
  de lignes, et obtenir la dérivée exacte au bit près.
- S'en servir pour calculer un gradient, puis descendre, et comparer votre descente à
  l'optimiseur de scipy.
- Établir le seuil exact au-delà duquel un pas trop grand fait diverger la descente, et le
  relier au conditionnement.
- Découvrir qu'entre « ça converge » et « ça explose » il existe un régime entier où la
  descente oscille, se dédouble, puis devient chaotique.

## Prérequis

Le conditionnement d'une matrice, rencontré en première année au
[TP4 d'outils fondamentaux](../outils-fondamentaux/tp4-matrices-gauss.md) sur la matrice de
Hilbert : il réapparaît ici dans un tout autre rôle, celui d'une vitesse de convergence. La
surcharge d'opérateurs en Python, qui est le seul point de langage nouveau de la séance.
Aucune clé d'API, aucun téléchargement.

```bash
pip install numpy matplotlib scipy
```

## Ressources

- [Le carnet de ce TP](/lite/notebooks/index.html?path=modelisation-tp3.ipynb){ target=_blank },
  qui s'exécute dans votre navigateur, sans rien installer.
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp3.html){ target=_blank }, à faire après la
  séance.
- Robert May, *Simple mathematical models with very complicated dynamics*, Nature, 1976 :
  l'article qui a rendu célèbre la suite logistique de l'étape 5.
- La dérivation numérique et le choix du pas ont déjà été vus en première année, au
  [TP3 d'outils fondamentaux](../outils-fondamentaux/tp3-polynomes-fonctions.md) ; l'étape 1
  en reprend le résultat pour s'en servir de point de comparaison.

---

## Étape 1. Le pas qu'on ne sait pas choisir (15 min)

Une dérivée se définit comme une limite, et un ordinateur ne sait pas prendre de limite. Il
prend un `h` petit et espère. Deux formules se présentent, la différence avant et la
différence centrée :

```python
import math

import matplotlib.pyplot as plt
import numpy as np


def f(x):
    return math.exp(math.sin(x))


def f_prime_exacte(x):
    return math.cos(x) * math.exp(math.sin(x))


x0 = 1.5
exacte = f_prime_exacte(x0)
print("dérivée exacte :", exacte)

for k in range(1, 17):
    h = 10.0 ** (-k)
    avant = (f(x0 + h) - f(x0)) / h
    centree = (f(x0 + h) - f(x0 - h)) / (2 * h)
    print(f"h=1e-{k:02d} : avant {abs(avant - exacte) / abs(exacte):.3e}"
          f"   centrée {abs(centree - exacte) / abs(exacte):.3e}")
```

L'erreur ne décroît pas jusqu'au bout : elle descend, atteint un minimum, puis **remonte**.
C'est la signature de deux erreurs qui se combattent. L'erreur de troncature, celle du
développement de Taylor qu'on interrompt, diminue avec `h`. L'erreur d'arrondi, elle,
augmente quand `h` diminue, parce qu'on soustrait deux nombres de plus en plus proches puis
qu'on divise par un nombre de plus en plus petit.

!!! question "Exercice 1.1 : où se trouve le meilleur pas"
    Cherchez le `h` qui minimise l'erreur, pour chacune des deux formules, sur une grille
    plus fine que les puissances entières de 10. Comparez ce que vous trouvez à
    `sqrt(eps)` et à `eps ** (1/3)`, où `eps` est l'epsilon machine.

    **Résultat attendu :** pour la différence avant, le minimum est atteint vers
    `h = 4.5e-09` avec une erreur relative de `2.1e-08`, à comparer à
    `sqrt(eps) = 1.49e-08`. Pour la centrée, il est vers `h = 6.3e-06` avec une erreur de
    `1.0e-11`, à comparer à `eps ** (1/3) = 6.06e-06`. Les deux prédictions théoriques
    tombent au bon ordre de grandeur, mais aucune ne donne le pas exact.

    ??? success "Corrigé"
        ```python
        eps = np.finfo(float).eps


        def meilleur_pas(formule, exposants):
            resultats = [(abs(formule(10.0 ** (-k)) - exacte) / abs(exacte), 10.0 ** (-k))
                         for k in exposants]
            return min(resultats)


        avant = lambda h: (f(x0 + h) - f(x0)) / h
        centree = lambda h: (f(x0 + h) - f(x0 - h)) / (2 * h)

        err_a, h_a = meilleur_pas(avant, np.arange(6.0, 11.0, 0.05))
        err_c, h_c = meilleur_pas(centree, np.arange(3.0, 9.0, 0.05))
        print(f"avant   : h={h_a:.3e}  erreur {err_a:.3e}   sqrt(eps)      = {math.sqrt(eps):.3e}")
        print(f"centrée : h={h_c:.3e}  erreur {err_c:.3e}   eps**(1/3)     = {eps ** (1 / 3):.3e}")
        ```

        Retenez la conséquence pratique plutôt que les formules : le meilleur pas dépend de
        la fonction, du point où on la dérive, et de l'échelle de ses valeurs. Il n'existe
        donc pas de constante universelle à écrire dans un code, et même au meilleur pas
        vous perdez la moitié des chiffres significatifs pour la formule avant. Toute la
        suite de cette séance consiste à se débarrasser de ce compromis au lieu de
        l'optimiser.

## Étape 2. Les nombres duaux, ou dériver sans h (30 min)

Voici l'idée, et elle est courte. On invente un nombre `ε` non nul dont le carré est nul, et
on travaille avec des couples `a + b·ε`. La règle du produit tombe alors toute seule :

\[
(a + b\varepsilon)(c + d\varepsilon) = ac + (ad + bc)\varepsilon + bd\varepsilon^2 = ac + (ad + bc)\varepsilon
\]

et l'on reconnaît dans le facteur de `ε` la formule de la dérivée d'un produit. Si l'on
évalue une fonction en `x + 1·ε`, la partie en `ε` du résultat **est** `f'(x)`, sans aucun
pas et sans aucune limite. Il n'y a plus qu'à l'écrire en Python :

```python
class Dual:
    """Un nombre a + b·ε avec ε² = 0 : b porte la dérivée."""

    def __init__(self, valeur, derivee=0.0):
        self.valeur = valeur
        self.derivee = derivee

    @staticmethod
    def _promouvoir(autre):
        """Un flottant est un dual de dérivée nulle : c'est une constante."""
        return autre if isinstance(autre, Dual) else Dual(autre)

    def __add__(self, autre):
        autre = Dual._promouvoir(autre)
        return Dual(self.valeur + autre.valeur, self.derivee + autre.derivee)

    __radd__ = __add__

    def __mul__(self, autre):
        autre = Dual._promouvoir(autre)
        return Dual(self.valeur * autre.valeur,
                    self.derivee * autre.valeur + self.valeur * autre.derivee)

    __rmul__ = __mul__

    def __sub__(self, autre):
        autre = Dual._promouvoir(autre)
        return Dual(self.valeur - autre.valeur, self.derivee - autre.derivee)

    def __rsub__(self, autre):
        return Dual._promouvoir(autre) - self

    def __pow__(self, n):
        return Dual(self.valeur ** n, n * self.valeur ** (n - 1) * self.derivee)

    def __repr__(self):
        return f"{self.valeur} + {self.derivee}·ε"


def sin(u):
    return Dual(math.sin(u.valeur), math.cos(u.valeur) * u.derivee)


def exp(u):
    return Dual(math.exp(u.valeur), math.exp(u.valeur) * u.derivee)


print(Dual(3.0, 1.0) * Dual(5.0, 1.0))
```

Chaque opérateur transporte la valeur **et** sa dérivée, et `sin` comme `exp` appliquent la
règle de dérivation en chaîne : la dérivée de `sin(u)` est `cos(u)` fois celle de `u`.

```python
def g(x):
    return exp(sin(x))


resultat = g(Dual(x0, 1.0))
print("valeur  :", resultat.valeur)
print("dérivée :", resultat.derivee)
print("exacte  :", exacte)
```

!!! question "Exercice 2.1 : à quel point est-ce exact ?"
    Comparez la dérivée obtenue par les duaux à la dérivée analytique, non pas à `1e-10`
    près, mais **bit à bit** avec `==`. Que vaut l'écart, et pourquoi ce résultat n'a-t-il
    rien de miraculeux ?

    **Résultat attendu :** l'écart vaut exactement `0.0` et le test `==` renvoie `True`. Ce
    n'est pas une approximation très bonne, c'est le même calcul : la dérivée analytique
    s'écrit `cos(x) * exp(sin(x))`, et la classe `Dual` a effectué rigoureusement ces deux
    opérations flottantes, dans cet ordre. La dérivation automatique n'approche pas la
    dérivée, elle l'évalue.

    ??? success "Corrigé"
        ```python
        print("écart absolu :", abs(resultat.derivee - exacte))
        print("identiques bit à bit :", resultat.derivee == exacte)
        print("meilleure différence finie centrée :", f"{err_c:.3e}", "d'erreur relative")
        ```

        La différence est de nature, pas de degré. Une différence finie répond à la
        question « de combien la fonction varie-t-elle entre deux points proches », et cette
        question a une réponse bruitée. Les nombres duaux répondent à « quelles opérations
        la fonction enchaîne-t-elle », et appliquent à chacune sa règle de dérivation. C'est
        le principe exact de `torch.autograd` et de `jax.grad`, à la gestion mémoire près.

!!! question "Exercice 2.2 : la division manque"
    La classe ne sait pas encore diviser. Ajoutez `__truediv__` et `__rtruediv__`, puis
    vérifiez votre implémentation sur `t(x) = sin(x) / x` en `x = 2.0`, dont la dérivée
    analytique vaut `cos(x)/x - sin(x)/x²`.

    **Résultat attendu :** `t(2.0)` vaut `0.45464871341284085` et sa dérivée
    `-0.43539777497999166`, et l'écart avec la formule analytique est encore exactement
    `0.0`.

    ??? success "Corrigé"
        ```python
        def diviser(self, autre):
            autre = Dual._promouvoir(autre)
            return Dual(self.valeur / autre.valeur,
                        (self.derivee * autre.valeur - self.valeur * autre.derivee)
                        / autre.valeur ** 2)


        Dual.__truediv__ = diviser
        Dual.__rtruediv__ = lambda self, autre: diviser(Dual._promouvoir(autre), self)

        sortie = sin(Dual(2.0, 1.0)) / Dual(2.0, 1.0)
        analytique = math.cos(2.0) / 2.0 - math.sin(2.0) / 2.0 ** 2
        print("dual      :", sortie.valeur, sortie.derivee)
        print("analytique:", math.sin(2.0) / 2.0, analytique)
        print("écart sur la dérivée :", abs(sortie.derivee - analytique))
        ```

        Le quotient est la seule des quatre opérations dont la règle se trompe si on
        l'écrit de mémoire, à cause du signe moins au numérateur. C'est aussi la raison pour
        laquelle on l'écrit une fois, dans une classe testée, plutôt qu'à la main dans
        chaque programme qui a besoin d'un gradient.

## Étape 3. Du gradient à la descente (30 min)

Une fonction de plusieurs variables se dérive de la même façon, une variable à la fois : on
marque d'un `ε` celle qu'on dérive et on laisse les autres à `0`. Le gradient coûte donc
autant d'évaluations que de variables.

```python
def gradient(fonction, point):
    point = np.asarray(point, dtype=float)
    grad = np.zeros_like(point)
    for i in range(point.size):
        duaux = [Dual(valeur, 1.0 if j == i else 0.0)
                 for j, valeur in enumerate(point)]
        grad[i] = fonction(duaux).derivee
    return grad


def rosenbrock(v):
    """Vallée de Rosenbrock : minimum unique en (1, 1), où elle vaut 0."""
    x, y = v[0], v[1]
    return (1 - x) ** 2 + 100 * (y - x * x) ** 2
```

Remarquez que `rosenbrock` n'a pas été écrite pour les duaux : elle n'utilise que `+`, `-`,
`*` et `**`, et Python choisit l'implémentation selon le type qu'on lui passe. La même
fonction s'évalue donc sur des flottants ou se dérive sur des duaux, sans une ligne de plus.

!!! question "Exercice 3.1 : le gradient automatique contre le gradient à la main"
    Dérivez Rosenbrock à la main, ce qui donne `∂f/∂x = -2(1-x) - 400x(y-x²)` et
    `∂f/∂y = 200(y-x²)`, puis comparez au gradient automatique au point `(-1.2, 1.0)`.

    **Résultat attendu :** les deux valent `[-215.6, -88.0]`, mais pas au dernier bit :
    l'écart vaut `2.84e-14` sur la première composante et exactement `0` sur la seconde.
    Les deux calculs sont algébriquement identiques et n'enchaînent pas les mêmes
    opérations flottantes, ce qui suffit à les séparer d'un ou deux ulps. Rien ne permet de
    dire lequel des deux est le plus proche de la valeur réelle, et cela n'a aucune
    importance ici.

    ??? success "Corrigé"
        ```python
        def gradient_a_la_main(v):
            x, y = v
            return np.array([-2 * (1 - x) - 400 * x * (y - x * x), 200 * (y - x * x)])


        point = np.array([-1.2, 1.0])
        print("automatique :", gradient(rosenbrock, point))
        print("à la main   :", gradient_a_la_main(point))
        print("écart       :", np.abs(gradient(rosenbrock, point) - gradient_a_la_main(point)))
        ```

        Ce n'est pas un argument de précision, un ulp n'a jamais fait échouer une descente.
        C'est un argument de fiabilité : la formule à la main a demandé une dérivation, une
        transcription et une relecture, et chacune de ces trois étapes peut se tromper sans
        que rien ne le signale. La version automatique n'a demandé aucune des trois.

La descente de gradient consiste à répéter `x ← x - η ∇f(x)`. Le paramètre `η` est le pas,
aussi appelé taux d'apprentissage.

```python
def descente(fonction, depart, pas, iterations):
    v = np.array(depart, dtype=float)
    trajet = [v.copy()]
    for _ in range(iterations):
        v = v - pas * gradient(fonction, v)
        trajet.append(v.copy())
    return np.array(trajet)


for pas in [1e-4, 1e-3, 2e-3, 3e-3]:
    fin = descente(rosenbrock, [-1.2, 1.0], pas, 5000)[-1]
    print(f"pas={pas:g} : après 5000 itérations, f = {rosenbrock(fin):.6f}, point {fin.round(4)}")
```

!!! question "Exercice 3.2 : cinq mille itérations contre trente-deux"
    Confiez le même problème à scipy, en lui fournissant votre gradient automatique, et
    comparez le nombre d'évaluations de la fonction ainsi que la valeur finale.

    **Résultat attendu :** le meilleur pas fixe testé, `2e-3`, laisse `f = 0.000055` après
    5000 itérations, soit 5000 gradients et donc 10 000 évaluations duales. BFGS atteint
    `f = 2.535e-15` en `32` itérations et `39` évaluations. Deux ordres de grandeur d'écart
    sur le coût, dix sur le résultat.

    ??? success "Corrigé"
        ```python
        from scipy.optimize import minimize

        resultat = minimize(rosenbrock, [-1.2, 1.0],
                            jac=lambda v: gradient(rosenbrock, v), method="BFGS")
        print(f"BFGS : {resultat.nit} itérations, {resultat.nfev} évaluations")
        print(f"point final {resultat.x}, f = {resultat.fun:.3e}")
        ```

        BFGS ne se contente pas de la pente : il accumule, au fil des pas, une
        approximation de la **courbure**, et s'en sert pour choisir à la fois la direction
        et la longueur du pas. C'est pour cela qu'il n'a aucun paramètre `η` à régler. La
        descente à pas fixe reste pourtant partout en apprentissage profond, parce que
        stocker une approximation de courbure sur des millions de paramètres est hors de
        portée. Le bon choix dépend de la taille du problème, pas de la qualité des
        méthodes.

!!! tip "L'IA vous le donne en trois secondes"
    Demandez une descente de gradient à un assistant conversationnel. Le pas proposé sera
    presque toujours `0.01`, parfois `0.001`, présenté comme une valeur usuelle. Appliquez
    `0.01` à Rosenbrock et regardez les six premières itérations : `f` passe de `24.2` à
    `93.3`, puis `4.7e4`, puis `2.5e12`, et vaut `inf` à la sixième. Le même `0.01` sur
    `f(x,y) = (x² + y²)/2` converge parfaitement, à `2.6e-09` de l'optimum. Un pas n'est
    donc ni bon ni mauvais en soi ; il est bon ou mauvais **relativement à la courbure de
    votre fonction**, et l'étape suivante donne le seuil exact. Notez aussi la façon dont
    l'échec se manifeste : pas d'exception, pas de message, seulement un `RuntimeWarning`
    d'*overflow* et des `nan` qui se propagent en silence.

    ```python
    with np.errstate(over="ignore", invalid="ignore"):
        v = np.array([-1.2, 1.0])
        for k in range(1, 7):
            v = v - 0.01 * gradient_a_la_main(v)
            print(f"  itération {k} : f = {rosenbrock(v):.3e}")

    w = np.array([1.0, 1.0])
    for _ in range(2000):
        w = w - 0.01 * w
    print("sur (x²+y²)/2, le même pas donne ||x|| =", f"{np.linalg.norm(w):.1e}")
    ```

## Étape 4. Le seuil exact du pas (20 min)

Sur une fonction quadratique, la question se tranche complètement. Prenons
`f(x, y) = (x² + c·y²)/2`, dont le gradient est `[x, c·y]` et dont la matrice des dérivées
secondes est diagonale, de valeurs propres `1` et `c`. Une itération multiplie chaque
coordonnée par `1 - η·λ`, où `λ` est la valeur propre correspondante. La descente converge
donc si et seulement si `|1 - η·λ| < 1` pour **toutes** les valeurs propres, c'est-à-dire si
`η < 2/L` où `L` est la plus grande.

```python
def descente_quadratique(c, pas, iterations=200, depart=(1.0, 1.0)):
    v = np.array(depart, dtype=float)
    for _ in range(iterations):
        v = v - pas * np.array([v[0], c * v[1]])
    return np.linalg.norm(v)


for c in [1.0, 30.0]:
    L = max(1.0, c)
    print(f"\nc={c:g}, L={L:g}, seuil 2/L = {2 / L:.6f}")
    for fraction in [0.5, 1.0, 1.9, 2.0, 2.05]:
        norme = descente_quadratique(c, fraction / L)
        print(f"  η = {fraction:.2f}/L : ||x|| après 200 itérations = {norme:.3e}")
```

!!! question "Exercice 4.1 : ce qui se passe exactement au seuil"
    Trois régimes apparaissent dans le tableau ci-dessus. Décrivez ce qui arrive juste en
    dessous du seuil, exactement au seuil, et juste au-dessus, et expliquez chaque cas par
    la valeur de `1 - η·λ`.

    **Résultat attendu :** pour `c = 1`, juste en dessous (`η = 1.9/L`) la norme tombe à
    `9.977e-10` ; exactement au seuil (`η = 2/L`) elle vaut `1.414e+00`, c'est-à-dire
    exactement la norme de départ, parce que `1 - η·λ = -1` : le point saute d'un côté à
    l'autre du minimum sans jamais s'en approcher ; juste au-dessus (`η = 2.05/L`) elle
    atteint `2.446e+04` et continue de croître. Le cas `η = 1/L` est remarquable : le
    facteur vaut `0` et la convergence est atteinte en **une** itération.

    ??? success "Corrigé"
        ```python
        for fraction in [1.9, 2.0, 2.05]:
            facteur = 1 - fraction
            print(f"η = {fraction}/L : facteur 1-ηλ = {facteur:+.2f}, "
                  f"|facteur| = {abs(facteur):.2f}, "
                  f"après 200 itérations : {abs(facteur) ** 200:.3e} fois le départ")
        ```

        La divergence n'est pas une pathologie mystérieuse, c'est une suite géométrique de
        raison plus grande que 1 en valeur absolue. Retenez surtout le signe : dès que le
        facteur devient négatif, c'est-à-dire dès que `η > 1/L`, la descente **oscille**
        autour du minimum au lieu d'y glisser. Elle converge encore, mais en alternant de
        part et d'autre, et c'est ce comportement qui va dégénérer à l'étape 5.

!!! question "Exercice 4.2 : à partir de quand le conditionnement coûte-t-il"
    Le **conditionnement** `κ = L/μ` est le rapport de la plus grande à la plus petite
    valeur propre, ici `c`. Mesurez la norme finale à `η = 1.9/L` pour `κ` valant `1`, `10`,
    `30` puis `100`, et expliquez le tableau obtenu à l'aide des deux facteurs `1 - η·λ`,
    un par direction.

    **Résultat attendu :** il n'est pas monotone, et c'est le point de l'exercice. `κ = 10`
    converge **mieux** que `κ = 1` (`7.06e-10` contre `9.98e-10`), `κ = 30` est déjà en
    retard (`2.07e-06`) et `κ = 100` a pratiquement cessé d'avancer (`2.16e-02`). La raison
    est que la vitesse est fixée par le plus grand des deux facteurs en valeur absolue : la
    direction raide donne toujours `-0.9`, la direction molle donne `1 - 1.9/κ`, et celle-ci
    ne devient limitante qu'au-delà de `κ = 19`. En dessous, la direction molle s'écrase
    plus vite que la raide et le conditionnement ne coûte rien ; à `κ = 1` on paie même un
    facteur `√2` pour la seule raison que les deux coordonnées convergent aussi lentement
    l'une que l'autre.

    ??? success "Corrigé"
        ```python
        print("  κ |    ||x|| final | facteur raide | facteur mou")
        for c in [1.0, 10.0, 19.0, 30.0, 100.0]:
            eta = 1.9 / max(1.0, c)
            print(f"{c:4.0f} | {descente_quadratique(c, eta):.4e} |"
                  f" {1 - eta * c:+.4f} | {1 - eta * 1.0:+.4f}")
        ```

        Vérifiez la ligne `κ = 19` : les deux facteurs y valent `0.9` en valeur absolue, et
        la norme finale retombe exactement sur celle de `κ = 1`. C'est le conditionnement
        rencontré en première année sur la matrice de Hilbert, au
        [TP4 d'outils fondamentaux](../outils-fondamentaux/tp4-matrices-gauss.md), ici dans
        un tout autre rôle : il n'y mesurait pas une vitesse de convergence mais une perte
        de précision.
        Retenez la forme générale plutôt que le seuil `19`, qui dépend du pas choisi : un
        problème mal conditionné force de tout petits pas dans une direction parce qu'une
        autre est raide, et c'est la raison d'être de tout ce que vous verrez ensuite sous
        les noms de préconditionnement, de moment ou d'Adam.

## Étape 5. Diverger, mais pas tout de suite (25 min)

Entre « ça converge » et « ça explose », on s'attend à une frontière nette. Sur une
quadratique, c'est le cas. Dès que la fonction n'est plus quadratique, il n'en est rien.
Prenons `f(x) = x²/2 - x³/3`, dont la dérivée est `x - x²` et qui a un minimum local en
`x = 0`. Une itération de descente s'écrit alors :

\[
x \mapsto (1-\eta)x + \eta x^2
\]

```python
def iterer(eta, depart=0.37, transitoire=20000, garder=200):
    """Renvoie les valeurs visitées une fois le régime établi, ou None si ça diverge."""
    x = depart
    for _ in range(transitoire):
        x = (1 - eta) * x + eta * x * x
        if not np.isfinite(x) or abs(x) > 1e8:
            return None
    visitees = []
    for _ in range(garder):
        x = (1 - eta) * x + eta * x * x
        visitees.append(x)
    return np.array(visitees)


for eta in [1.9, 2.01, 2.1, 2.44, 2.45, 2.55, 2.57, 2.8, 3.0, 3.0001]:
    valeurs = iterer(eta)
    if valeurs is None:
        print(f"η = {eta:6.4f} : diverge")
    else:
        distinctes = len(np.unique(np.round(valeurs, 8)))
        print(f"η = {eta:6.4f} : {distinctes:3d} valeur(s) distincte(s) en régime établi")
```

La descente ne converge plus vers le minimum, mais elle ne diverge pas pour autant : elle
s'installe sur un cycle de deux points, puis de quatre, puis de huit, et finit par ne plus
se répéter du tout.

```python
etas = np.linspace(1.5, 3.0, 600)
x = np.full(etas.shape, 0.37)
for _ in range(1500):
    x = (1 - etas) * x + etas * x * x
    x = np.where(np.abs(x) > 1e3, np.nan, x)

abscisses, ordonnees = [], []
for _ in range(80):
    x = (1 - etas) * x + etas * x * x
    x = np.where(np.abs(x) > 1e3, np.nan, x)
    abscisses.append(etas.copy())
    ordonnees.append(x.copy())

plt.figure(figsize=(9, 5))
plt.plot(np.concatenate(abscisses), np.concatenate(ordonnees), ",k", alpha=0.5)
plt.xlabel("pas η")
plt.ylabel("valeurs visitées en régime établi")
plt.title("Descente de gradient sur x²/2 - x³/3 : diagramme de bifurcation")
plt.show()
```

!!! question "Exercice 5.1 : localiser les bifurcations"
    Encadrez au centième près les trois pas auxquels le comportement change de nature :
    passage du point fixe au cycle de deux, du cycle de deux à celui de quatre, et l'entrée
    dans le régime où plus aucune valeur ne se répète. Cherchez enfin le pas au-delà duquel
    tout diverge.

    **Résultat attendu :** point fixe jusqu'à `η = 1.99`, cycle de deux dès `η = 2.01`,
    cycle de quatre dès `η = 2.45` (encore deux valeurs à `2.449`), cycle de huit vers
    `η = 2.55`, plus aucune répétition à partir de `η = 2.57`. La suite reste bornée jusqu'à
    `η = 3.0` inclus et diverge dès `η = 3.0001`.

    ??? success "Corrigé"
        ```python
        for eta in [1.99, 2.0, 2.01, 2.449, 2.45, 2.56, 2.569, 2.57, 3.0, 3.0001]:
            valeurs = iterer(eta)
            if valeurs is None:
                print(f"η = {eta:6.4f} : diverge")
            else:
                print(f"η = {eta:6.4f} : {len(np.unique(np.round(valeurs, 8))):3d} valeurs")
        ```

        Le cas `η = 2.0` mérite un regard : il affiche `200` valeurs distinctes sans être
        chaotique pour autant. Le facteur `1 - η` y vaut exactement `-1`, la convergence
        n'est plus géométrique mais infiniment lente, et la suite descend encore vers `0` en
        oscillant, trop lentement pour que 20 000 itérations suffisent. Un compteur de
        valeurs distinctes ne distingue pas « chaotique » de « pas encore arrivé », et c'est
        une confusion qu'on ne détecte qu'en regardant l'amplitude, ici de l'ordre de
        `2.5e-03` et toujours décroissante.

!!! question "Exercice 5.2 : ce n'est pas une coïncidence"
    Ces quatre seuils, `2`, `2.449`, `2.570` et `3`, sont exactement ceux de la suite
    logistique `u ↦ r·u(1-u)`, décalés de `1`. Vérifiez que le changement de variable
    `x = A·u + 1` avec `A = -(η+1)/η` et `r = η + 1` transforme l'une en l'autre, en suivant
    les deux suites en parallèle.

    **Résultat attendu :** à `η = 1.5` et `η = 2.3`, les deux suites restent identiques à
    `2.3e-16` et `5.6e-16` près sur cinquante itérations, c'est-à-dire à la précision des
    flottants. À `η = 2.8`, en revanche, l'écart atteint `5.2e-06` : l'identité
    mathématique est la même, mais le régime est chaotique et deux calculs équivalents
    divergent l'un de l'autre.

    ??? success "Corrigé"
        ```python
        for eta in [1.5, 2.3, 2.8]:
            r = eta + 1
            A = -(eta + 1) / eta
            u, x = 0.37, A * 0.37 + 1.0
            ecart = 0.0
            for _ in range(50):
                u = r * u * (1 - u)
                x = (1 - eta) * x + eta * x * x
                ecart = max(ecart, abs(x - (A * u + 1.0)))
            print(f"η = {eta} (r = {r:.1f}) : écart maximal {ecart:.3e}")
        ```

        Les seuils `r = 3`, `r = 1 + √6 ≈ 3.449`, `r ≈ 3.5699` et `r = 4` de la suite
        logistique sont donc ceux de votre descente de gradient, à `1` près. Vous n'avez pas
        découvert un défaut de la descente de gradient : vous avez retrouvé la cascade de
        doublements de période décrite par May en 1976, dont les rapports successifs
        convergent vers la constante de Feigenbaum, la même pour toutes les fonctions à un
        seul maximum. Et le dernier écart de `5.2e-06` est la définition opérationnelle du
        chaos : une divergence exponentielle des trajectoires, ici mesurée entre deux
        façons d'écrire le même calcul.

!!! warning "Un départ malheureux se déguise en résultat"
    Reprenez `iterer(2.5)` avec `depart=0.4` au lieu de `0.37`. Vous obtenez deux valeurs
    distinctes, `-0.2` et `0.4`, au lieu des quatre du véritable attracteur : `0.4` tombe
    pile sur un cycle de période deux instable, dont il ne s'échappe jamais parce que les
    arrondis ne le poussent nulle part. Aucun message, aucun avertissement, et une
    conclusion fausse sur la nature du régime. Vérifiez toujours une dynamique depuis
    plusieurs points de départ.

## Ce qu'il faut retenir

Une dérivée par différence finie oblige à arbitrer entre l'erreur de troncature et l'erreur
d'arrondi, et même au meilleur pas elle perd la moitié des chiffres significatifs. Les
nombres duaux suppriment l'arbitrage : en transportant la dérivée à travers chaque
opération, ils rendent la dérivée exacte au bit près pour un coût comparable, et c'est le
principe de toutes les bibliothèques de dérivation automatique. Une fois le gradient obtenu,
la descente pose une seule question difficile, celle du pas : sur une fonction quadratique
elle converge si et seulement si `η < 2/L`, oscille dès que `η > 1/L`, et sa vitesse est
gouvernée par le conditionnement et non par le pas. Enfin, dès que la fonction n'est plus
quadratique, la frontière entre convergence et divergence n'est plus une frontière : c'est
une cascade de doublements de période puis un régime chaotique, mathématiquement identique à
la suite logistique. Un optimiseur qui ne converge pas n'a donc pas forcément explosé, et
c'est ce qui rend le diagnostic difficile.

## Auto-évaluation

- [ ] Je sais expliquer pourquoi l'erreur d'une différence finie remonte quand `h` devient
      trop petit.
- [ ] Je sais implémenter un nombre dual et dire pourquoi sa dérivée est exacte et non
      approchée.
- [ ] Je sais calculer un gradient par dérivation automatique, et dire ce qu'il coûte.
- [ ] Je sais comparer une descente à pas fixe à un optimiseur de scipy, et dire ce que
      BFGS utilise en plus.
- [ ] Je sais énoncer et vérifier la condition `η < 2/L`, et dire ce que fait le pas `1/L`.
- [ ] Je sais relier la lenteur d'une descente au conditionnement plutôt qu'au pas.
- [ ] J'ai vu une descente de gradient produire un cycle, puis du chaos, et je sais que ce
      n'est pas la même chose qu'une divergence.

[Le QCM du TP3](qcm/qcm_tp3.html){ .md-button target=_blank }
[Projet et évaluation](evaluation.md){ .md-button .md-button--primary }
[Revenir au TP2](tp2-marche-aleatoire.md){ .md-button }
