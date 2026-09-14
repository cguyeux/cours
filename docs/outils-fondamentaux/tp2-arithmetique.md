# TP2. Arithmétique et nombres premiers

**Durée : 1 h 45.**

## Objectifs

- Écrire les algorithmes classiques de l'arithmétique : diviseurs, PGCD, primalité, crible.
- **Mesurer** le temps d'exécution d'un programme, et comprendre pourquoi trois programmes
  justes peuvent différer d'un facteur un million.
- Distinguer un algorithme correct d'un algorithme utilisable.

## Prérequis

Le [TP1](tp1-calcul-numerique.md) : boucles, conditions, fonctions, `//` et `%`.

## Ressources

- Le [mémento Python](memento.md).
- [Le carnet de ce TP](/lite/notebooks/index.html?path=tp2.ipynb){ target=_blank }.
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp2.html){ target=_blank }, à faire après la séance.

---

## Étape 1. Diviseurs (15 min)

Un entier \( d \) divise un entier \( n \) lorsque le reste de la division de \( n \) par
\( d \) est nul. En Python, cela s'écrit `n % d == 0`. Tout le TP découle de cette ligne.

!!! question "Exercice 1.1 : la liste des diviseurs"
    Écrivez une fonction `diviseurs(n)` qui renvoie la liste des diviseurs positifs de `n`,
    dans l'ordre croissant.

    **Résultat attendu :** `diviseurs(28)` vaut `[1, 2, 4, 7, 14, 28]`.

    ??? success "Corrigé"
        ```python
        def diviseurs(n):
            """Liste croissante des diviseurs positifs de n."""
            resultat = []
            for d in range(1, n + 1):
                if n % d == 0:
                    resultat.append(d)
            return resultat

        print(diviseurs(28))
        print(diviseurs(97))
        ```

        `diviseurs(97)` renvoie `[1, 97]` : 97 est premier, et c'est exactement la
        définition d'un nombre premier, avoir exactement deux diviseurs.

!!! tip "Pour aller plus loin : les nombres parfaits"
    Un entier est **parfait** quand il est égal à la somme de ses diviseurs stricts. Le
    premier est 6, car \( 1 + 2 + 3 = 6 \). Cherchez tous les nombres parfaits inférieurs
    à 10 000, et comparez votre liste à ce que dit la littérature. Vous n'en trouverez que
    quatre, et on ignore encore aujourd'hui s'il en existe un seul qui soit impair.

    ```python
    def est_parfait(n):
        return sum(d for d in range(1, n) if n % d == 0) == n

    print([n for n in range(2, 10000) if est_parfait(n)])
    ```

---

## Étape 2. Le PGCD, et pourquoi Euclide (20 min)

Le plus grand commun diviseur de deux entiers peut se calculer bêtement, en essayant tous
les diviseurs possibles. Il peut aussi se calculer par l'algorithme d'Euclide, vieux de
vingt-trois siècles, qui repose sur une seule observation : le PGCD de \( a \) et \( b \)
est aussi celui de \( b \) et du reste de \( a \) par \( b \).

!!! question "Exercice 2.1 : les deux PGCD"
    Écrivez `pgcd_naif(a, b)`, qui essaie tous les entiers de 1 à `min(a, b)`, puis
    `pgcd(a, b)`, qui applique Euclide. Vérifiez qu'ils donnent le même résultat.

    **Résultat attendu :** `pgcd(1071, 462)` vaut `21`, comme `pgcd_naif(1071, 462)`.

    ??? success "Corrigé"
        ```python
        def pgcd_naif(a, b):
            """PGCD par essai de tous les diviseurs possibles."""
            meilleur = 1
            for d in range(1, min(a, b) + 1):
                if a % d == 0 and b % d == 0:
                    meilleur = d
            return meilleur

        def pgcd(a, b):
            """PGCD par l'algorithme d'Euclide."""
            while b != 0:
                a, b = b, a % b
            return a

        print(pgcd_naif(1071, 462), pgcd(1071, 462))
        ```

        La ligne `a, b = b, a % b` échange et met à jour les deux variables en une fois.
        Sans cette écriture simultanée, il faudrait une variable temporaire, car écrire
        `a = b` puis `b = a % b` utiliserait le nouveau `a` et donnerait un résultat faux.
        C'est un piège classique, essayez-le pour voir.

        La boucle d'Euclide se termine toujours : le reste diminue strictement à chaque
        tour, donc il atteint zéro. Et elle est très rapide : sur `pgcd(1071, 462)` elle
        fait quatre tours, là où la version naïve en fait quatre cent soixante-deux.

---

## Étape 3. Tester la primalité, et mesurer (35 min)

Voici le cœur de la séance. Un nombre est premier s'il a exactement deux diviseurs, 1 et
lui-même. Trois programmes vont répondre correctement à cette question, et l'un d'eux est
un million de fois plus rapide que l'autre.

### Version naïve

```python
def est_premier_naif(n):
    """Teste la primalité en essayant tous les diviseurs jusqu'à n - 1."""
    if n < 2:
        return False
    for d in range(2, n):
        if n % d == 0:
            return False
    return True

print(est_premier_naif(97), est_premier_naif(91))
```

`91` n'est pas premier, c'est \( 7 \times 13 \), et beaucoup de gens s'y trompent de tête.

### Version qui s'arrête à la racine

Si \( n = a \times b \) avec \( a \le b \), alors \( a \le \sqrt{n} \). Autrement dit : si
aucun diviseur inférieur ou égal à \( \sqrt{n} \) n'a été trouvé, il n'y en a aucun.
Inutile d'aller plus loin.

```python
def est_premier(n):
    """Teste la primalité en s'arrêtant à la racine carrée de n."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d = d + 2
    return True

print(est_premier(97), est_premier(91), est_premier(2), est_premier(1))
```

Remarquez le traitement séparé de 2, puis le pas de 2 dans la boucle : une fois les pairs
écartés, un diviseur ne peut être que impair, ce qui divise encore le travail par deux.

### Mesurer, au lieu de croire

Python mesure le temps avec `time.perf_counter`, qui donne une durée en secondes.

```python
import time

def duree(fonction, argument):
    """Renvoie le temps d'exécution de fonction(argument), en secondes."""
    debut = time.perf_counter()
    fonction(argument)
    return time.perf_counter() - debut

n = 1_000_003  # un nombre premier
print(f"naif        : {duree(est_premier_naif, n):.4f} s")
print(f"jusqu'a rac : {duree(est_premier, n):.6f} s")
```

!!! question "Exercice 3.1 : le tableau des temps"
    Mesurez les deux fonctions sur les nombres premiers 10 007, 100 003 et 1 000 003, et
    présentez les résultats. Que se passe-t-il quand `n` est multiplié par 10 ?

    **Résultat attendu :** le temps de la version naïve est multiplié par 10 à chaque
    ligne, celui de la version à racine carrée par 3 environ.

    ??? success "Corrigé"
        ```python
        for n in (10_007, 100_003, 1_000_003):
            t_naif = duree(est_premier_naif, n)
            t_rac = duree(est_premier, n)
            print(f"{n:>9} : naif {t_naif:.5f} s | racine {t_rac:.6f} s")
        ```

        La version naïve fait \( n \) tours de boucle, la seconde en fait
        \( \sqrt{n}/2 \). Quand \( n \) est multiplié par 100, la première met cent fois
        plus de temps, la seconde seulement dix fois. C'est ce qu'on appelle la
        **complexité** d'un algorithme, et c'est la notion la plus rentable de toute votre
        première année.

        Poussez l'expérience mentalement : pour \( n = 10^{12} \), la version naïve
        demanderait des heures, la seconde répond en un millième de seconde. Essayez
        `est_premier(1_000_000_000_039)`, qui est premier, mais n'essayez pas la version
        naïve dessus.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant : « écris une fonction Python qui teste si un nombre est
    premier ». Puis vérifiez systématiquement quatre points sur sa réponse.

    1. Que répond-elle pour `n = 1` ? La bonne réponse est `False`, 1 n'est pas premier.
    2. Que répond-elle pour `n = 2` ? La bonne réponse est `True`, et beaucoup de versions
       optimisées se trompent ici.
    3. Que répond-elle pour un nombre négatif ?
    4. Sa boucle s'arrête-t-elle à `n` ou à `sqrt(n)` ? Mesurez sur 1 000 003.

    Notez ce que vous trouvez. Sur ces quatre points, il est fréquent qu'au moins un pose
    problème, et le seul moyen de le voir est de savoir ce qu'est un nombre premier.

---

## Étape 4. Le crible d'Ératosthène (20 min)

Pour obtenir **tous** les nombres premiers jusqu'à une limite, tester chaque nombre un par
un est un gâchis. Ératosthène, au troisième siècle avant notre ère, propose l'inverse :
partir de tous les entiers, et rayer les multiples.

```python
def crible(limite):
    """Renvoie la liste des nombres premiers de 2 à limite inclus."""
    est_premier_tab = [True] * (limite + 1)
    est_premier_tab[0] = False
    if limite >= 1:
        est_premier_tab[1] = False
    d = 2
    while d * d <= limite:
        if est_premier_tab[d]:
            for multiple in range(d * d, limite + 1, d):
                est_premier_tab[multiple] = False
        d = d + 1
    return [n for n in range(limite + 1) if est_premier_tab[n]]

premiers = crible(100)
print(premiers)
print(len(premiers), "premiers jusqu'a 100")
```

Deux détails valent une explication. On commence à rayer à \( d^2 \) et non à \( 2d \),
parce que tous les multiples plus petits ont déjà été rayés par un facteur plus petit. Et
la boucle extérieure s'arrête à \( \sqrt{\text{limite}} \), pour la même raison qu'à
l'étape précédente.

!!! question "Exercice 4.1 : combien de premiers sous 100 000 ?"
    Comptez les nombres premiers inférieurs à 100 000, avec le crible, et mesurez le temps.
    Comparez au temps qu'il faudrait en appelant `est_premier` sur chaque entier.

    **Résultat attendu :** `9592` nombres premiers, obtenus en quelques centièmes de
    seconde par le crible.

    ??? success "Corrigé"
        ```python
        debut = time.perf_counter()
        p = crible(100_000)
        t_crible = time.perf_counter() - debut

        debut = time.perf_counter()
        combien = sum(1 for n in range(100_001) if est_premier(n))
        t_un_par_un = time.perf_counter() - debut

        print(len(p), combien)
        print(f"crible {t_crible:.4f} s | un par un {t_un_par_un:.4f} s")
        ```

        Les deux comptes valent `9592`, ce qui est rassurant : deux méthodes
        indépendantes qui tombent d'accord constituent une vérification bien plus
        convaincante que la relecture de son propre code.

        Le crible est nettement plus rapide, parce qu'il ne teste rien : il raye.
        Retenez la leçon générale, qui dépasse largement l'arithmétique. Changer
        d'algorithme rapporte presque toujours davantage qu'optimiser le code d'un
        mauvais algorithme.

---

## Étape 5. Décomposition en facteurs premiers (15 min)

Tout entier supérieur à 1 s'écrit d'une seule manière comme produit de nombres premiers.
C'est le théorème fondamental de l'arithmétique, et c'est sur la difficulté de retrouver
cette décomposition pour de très grands nombres que repose une partie de la cryptographie
que vous étudierez en deuxième année.

!!! question "Exercice 5.1 : factoriser"
    Écrivez `facteurs(n)` qui renvoie la liste des facteurs premiers de `n`, avec leurs
    répétitions.

    **Résultat attendu :** `facteurs(360)` vaut `[2, 2, 2, 3, 3, 5]`, et le produit de
    cette liste redonne `360`.

    ??? success "Corrigé"
        ```python
        def facteurs(n):
            """Facteurs premiers de n, avec multiplicité, dans l'ordre croissant."""
            resultat = []
            d = 2
            while d * d <= n:
                while n % d == 0:
                    resultat.append(d)
                    n = n // d
                d = d + 1
            if n > 1:
                resultat.append(n)
            return resultat

        f = facteurs(360)
        print(f)

        produit = 1
        for x in f:
            produit = produit * x
        print(produit)
        ```

        La dernière ligne du corps de la fonction est indispensable : quand la boucle
        s'arrête, ce qui reste de `n` est soit 1, soit un nombre premier plus grand que
        \( \sqrt{n} \), qu'il faut ajouter. Sans elle, `facteurs(14)` renverrait `[2]` au
        lieu de `[2, 7]`. Essayez de l'enlever pour voir.

        Et vérifiez toujours par le produit : c'est le même réflexe qu'à l'exercice 1.1
        du TP1, où l'on contrôlait la division euclidienne en recomposant le dividende.

!!! tip "Pour aller plus loin : le principe de RSA en dix lignes"
    Multipliez deux nombres premiers de six chiffres. Le produit se calcule
    instantanément. Donnez maintenant ce produit à `facteurs` et mesurez. Puis imaginez la
    même chose avec deux nombres premiers de trois cents chiffres : la multiplication reste
    instantanée, la factorisation dépasse l'âge de l'univers. Tout le chiffrement RSA tient
    dans cet écart, et vous venez de le mesurer vous-même.

---

## Entraînement et approfondissement

À faire après la séance, ou en séance si vous avez terminé. Ces exercices sont au programme
de l'évaluation, sauf ceux marqués « pour aller plus loin ». Ils reprennent le fil du TP,
mesurer plutôt que croire, sur deux nouveaux terrains : les suites définies par récurrence
et l'arithmétique modulaire, qui prépare directement le TP5.

### Étape 6. Une suite, deux programmes, et quatre ordres de grandeur

La suite de Fibonacci est définie par \( F_0 = 0 \), \( F_1 = 1 \) et
\( F_n = F_{n-1} + F_{n-2} \). La définition se traduit mot à mot en Python, par une
fonction qui s'appelle elle-même :

```python
def fibonacci_recursif(n):
    """F(n) en suivant la définition, par récurrence."""
    if n < 2:
        return n
    return fibonacci_recursif(n - 1) + fibonacci_recursif(n - 2)

print([fibonacci_recursif(n) for n in range(15)])
```

C'est élégant, c'est juste, et c'est une catastrophe.

!!! question "Exercice 6.1 : mesurer la catastrophe"
    Mesurez le temps de `fibonacci_recursif` pour `n = 20`, `25` et `30`. Que devient le
    temps quand `n` augmente de 5 ?

    **Résultat attendu :** le temps est multiplié par une dizaine tous les cinq rangs, et
    `fibonacci_recursif(30)` demande déjà un ou deux dixièmes de seconde.

    ??? success "Corrigé"
        ```python
        for n in (20, 25, 30):
            print(f"F({n}) : {duree(fibonacci_recursif, n):.4f} s")
        ```

        Multiplier le temps par dix tous les cinq rangs, c'est le multiplier par
        \( 1{,}6 \) à chaque rang : la croissance est **exponentielle**. Pour `n = 50`,
        il faudrait des heures ; pour `n = 100`, plus que l'âge de l'univers. Une
        croissance exponentielle est la pire chose qui puisse arriver à un algorithme, et
        aucune machine, aussi rapide soit-elle, n'y change rien.

!!! question "Exercice 6.2 : comprendre pourquoi"
    Ajoutez à `fibonacci_recursif` un compteur d'appels, par exemple un dictionnaire qui
    note combien de fois chaque valeur de `n` est demandée. Combien de fois `F(1)` est-il
    recalculé pour obtenir `F(30)` ?

    **Résultat attendu :** `F(1)` est calculé `832040` fois, et l'appel total déclenche
    environ 2,7 millions d'appels.

    ??? success "Corrigé"
        ```python
        appels = {}

        def fibonacci_compte(n):
            appels[n] = appels.get(n, 0) + 1
            if n < 2:
                return n
            return fibonacci_compte(n - 1) + fibonacci_compte(n - 2)

        resultat = fibonacci_compte(30)
        print("F(30) =", resultat)
        print("appels a F(1) :", appels[1])
        print("appels en tout :", sum(appels.values()))
        ```

        Le nombre d'appels à `F(1)` est exactement `F(30)`. Ce n'est pas un hasard : le
        programme recalcule la même chose des centaines de milliers de fois, parce qu'il
        ne garde aucune mémoire de ce qu'il a déjà obtenu. Le problème n'est pas la
        récurrence en soi, c'est la **répétition** du travail.

!!! question "Exercice 6.3 : la version qui se souvient"
    Écrivez `fibonacci(n)` avec une simple boucle qui fait avancer deux variables, la
    valeur courante et la précédente. Vérifiez qu'elle donne les mêmes résultats que la
    version récursive jusqu'à `n = 25`, puis calculez `fibonacci(10_000)`.

    **Résultat attendu :** les deux versions coïncident ; `fibonacci(10_000)` a 2 090
    chiffres et s'obtient en quelques millisecondes.

    ??? success "Corrigé"
        ```python
        def fibonacci(n):
            """F(n) par une boucle : deux variables suffisent."""
            precedent, courant = 0, 1
            for _ in range(n):
                precedent, courant = courant, precedent + courant
            return precedent

        print(all(fibonacci(n) == fibonacci_recursif(n) for n in range(26)))
        print(f"F(30) en {duree(fibonacci, 30):.6f} s")
        grand = fibonacci(10_000)
        print(len(str(grand)), "chiffres")
        ```

        Plusieurs dizaines de milliers de fois plus rapide sur `n = 30`, et la version
        récursive n'atteindra jamais `n = 10 000`. On retrouve l'écriture simultanée `a, b = b, a + b` de
        l'algorithme d'Euclide, pour la même raison : les deux variables doivent changer
        ensemble.

        La leçon dépasse Fibonacci. Chaque fois qu'une fonction récursive se rappelle
        plusieurs fois sur des arguments qui se recoupent, elle refait du travail, et le
        remède est toujours le même : garder en mémoire ce qui a déjà été calculé, soit
        en parcourant les valeurs dans l'ordre comme ici, soit en les notant dans un
        dictionnaire au fur et à mesure. Vous reverrez cette technique en deuxième année
        sous le nom de programmation dynamique.

!!! tip "Pour aller plus loin : la suite de Syracuse"
    Partez d'un entier ; s'il est pair, divisez-le par 2, sinon remplacez-le par
    \( 3n + 1 \) ; recommencez. La conjecture de Syracuse affirme qu'on atteint toujours 1,
    et personne n'a jamais su le démontrer. Écrivez `temps_de_vol(n)` qui compte le nombre
    d'étapes avant d'atteindre 1, vérifiez que `temps_de_vol(27)` vaut `111`, puis
    cherchez l'entier inférieur à 10 000 dont le vol est le plus long : c'est 6 171, avec
    261 étapes. Attention, votre boucle `while` ne s'arrête que si la conjecture est vraie,
    ce que personne ne garantit ; mettez un plafond.

### Étape 7. Calculer modulo, sans faire déborder la machine

Le reste `%` est l'opération centrale de la cryptographie que vous croiserez au TP5. Deux
algorithmes classiques la mettent en œuvre, et tous deux illustrent le même principe : ne
jamais laisser un nombre grossir quand seul son reste nous intéresse.

!!! question "Exercice 7.1 : l'algorithme d'Euclide étendu"
    L'algorithme d'Euclide donne le PGCD ; sa version étendue donne en plus deux entiers
    \( u \) et \( v \) tels que \( au + bv = \mathrm{pgcd}(a, b) \). Écrivez
    `euclide_etendu(a, b)` qui renvoie le triplet `(pgcd, u, v)`. Indication : si
    `(g, u, v)` convient pour `(b, a % b)`, alors `(g, v, u - (a // b) * v)` convient pour
    `(a, b)`.

    **Résultat attendu :** `euclide_etendu(1071, 462)` vaut `(21, -3, 7)`, et
    \( 1071 \times (-3) + 462 \times 7 = 21 \).

    ??? success "Corrigé"
        ```python
        def euclide_etendu(a, b):
            """Renvoie (g, u, v) avec g = pgcd(a, b) et a u + b v = g."""
            if b == 0:
                return a, 1, 0
            g, u, v = euclide_etendu(b, a % b)
            return g, v, u - (a // b) * v

        g, u, v = euclide_etendu(1071, 462)
        print(g, u, v, 1071 * u + 462 * v == g)
        ```

        Ici la récurrence est la bonne solution, contrairement à Fibonacci : chaque appel
        n'en déclenche qu'un seul, donc aucun travail n'est refait, et la profondeur reste
        petite parce que le reste décroît très vite.

        L'intérêt pratique est immédiat. Si \( \mathrm{pgcd}(a, n) = 1 \), alors
        \( au + nv = 1 \), donc \( au \equiv 1 \pmod n \) : \( u \) est **l'inverse de
        \( a \) modulo \( n \)**. Essayez `euclide_etendu(5, 26)` : vous obtenez
        `(1, -5, 1)`, et \( -5 \equiv 21 \pmod{26} \). Retenez ce 21, vous le
        retrouverez au TP5, où il sera calculé par recherche exhaustive ; vous saurez
        alors faire mieux.

!!! question "Exercice 7.2 : l'exponentiation rapide"
    Calculer \( a^{e} \bmod n \) en calculant d'abord \( a^{e} \) est absurde quand
    \( e \) est grand : le nombre intermédiaire aurait des millions de chiffres. La
    solution naïve fait `e` multiplications en réduisant modulo `n` à chaque tour. La
    solution rapide remarque que \( a^{2k} = (a^{k})^{2} \) : on élève au carré et on ne
    multiplie par \( a \) que lorsque le bit correspondant de \( e \) vaut 1. Écrivez les
    deux, `puissance_mod_naive(a, e, n)` et `puissance_mod(a, e, n)`, et comparez leurs
    temps pour \( 7^{10^{7}} \bmod 1\,000\,003 \).

    **Résultat attendu :** le même résultat, `pow(a, e, n)` de Python le confirme, en une
    seconde environ pour la version naïve et en une dizaine de microsecondes pour la
    rapide.

    ??? success "Corrigé"
        ```python
        def puissance_mod_naive(a, e, n):
            """a^e mod n, par e multiplications successives."""
            resultat = 1
            for _ in range(e):
                resultat = resultat * a % n
            return resultat

        def puissance_mod(a, e, n):
            """a^e mod n, par élévations au carré successives."""
            resultat = 1
            a = a % n
            while e > 0:
                if e % 2 == 1:
                    resultat = resultat * a % n
                a = a * a % n
                e = e // 2
            return resultat

        a, e, n = 7, 10 ** 7, 1_000_003
        print(puissance_mod(a, e, n), pow(a, e, n))

        debut = time.perf_counter()
        puissance_mod_naive(a, e, n)
        t_naive = time.perf_counter() - debut
        debut = time.perf_counter()
        puissance_mod(a, e, n)
        t_rapide = time.perf_counter() - debut
        print(f"naive {t_naive:.3f} s | rapide {t_rapide:.6f} s")
        ```

        La version rapide fait autant de tours que \( e \) a de chiffres binaires,
        vingt-quatre ici, contre dix millions. Pour un exposant de trois cents chiffres,
        comme en cryptographie réelle, elle fait un millier de tours ; la version naïve
        ne terminerait jamais. C'est cette fonction, `pow(a, e, n)`, qui rend RSA
        utilisable, et c'est aussi elle qui permet de tester la primalité de nombres
        gigantesques sans jamais chercher un diviseur.

!!! tip "Pour aller plus loin : le petit théorème de Fermat"
    Si \( p \) est premier et ne divise pas \( a \), alors \( a^{p-1} \equiv 1 \pmod p \).
    Ce théorème donne un test de primalité d'une rapidité stupéfiante : calculez
    `pow(2, n - 1, n)`, et si le résultat n'est pas 1, `n` n'est pas premier, sans avoir
    cherché un seul diviseur. Le test n'est pas parfait : `pow(2, 340, 341)` vaut `1`
    alors que \( 341 = 11 \times 31 \). Cherchez les autres menteurs de ce genre en dessous
    de 10 000, il y en a une vingtaine. Les tests probabilistes utilisés en pratique, comme
    celui de Miller-Rabin, sont des raffinements de cette idée qui ne se laissent plus
    tromper.

---

## Ce qu'il faut retenir

`n % d == 0` teste la divisibilité, et tout le reste en découle. L'algorithme d'Euclide
calcule un PGCD en quelques tours au lieu de quelques milliers, et sa version étendue
donne l'inverse modulaire. Un test de primalité doit s'arrêter à \( \sqrt{n} \), sans quoi
il devient inutilisable. Le crible d'Ératosthène donne tous les premiers d'un coup, plus
vite que de les tester un par un. Une récurrence qui refait le même travail est
exponentielle, et il faut mémoriser. Et surtout : deux programmes justes ne se valent
pas, il faut mesurer.

## Auto-évaluation

Avant de passer au TP3, vous devez pouvoir, sans regarder le corrigé :

- [ ] écrire l'algorithme d'Euclide en trois lignes, et dire pourquoi il se termine ;
- [ ] expliquer pourquoi un test de primalité peut s'arrêter à \( \sqrt{n} \) ;
- [ ] dire ce que devient le temps de la version naïve, puis de la version à racine, quand
  `n` est multiplié par 100 ;
- [ ] expliquer pourquoi le crible commence à rayer à \( d^{2} \) et non à \( 2d \) ;
- [ ] mesurer un temps avec `time.perf_counter` ;
- [ ] dire pourquoi la version récursive de Fibonacci est exponentielle, et comment on la
  répare.

[Le QCM du TP2](qcm/qcm_tp2.html){ .md-button target=_blank }
[Passer au TP3](tp3-polynomes-fonctions.md){ .md-button .md-button--primary }
