# TP3. Polynômes et fonctions

**Durée : 1 h 45.**

## Objectifs

- Représenter un polynôme en machine et l'évaluer, naïvement puis intelligemment.
- Dériver un polynôme, chercher ses racines par dichotomie et par la méthode de Newton.
- Tracer une fonction, et lire le graphique pour comprendre un algorithme.

## Prérequis

Les [TP1](tp1-calcul-numerique.md) et [TP2](tp2-arithmetique.md) : fonctions, boucles,
listes, mesure de temps.

## Ressources

- Le [mémento Python](memento.md), section listes et section matplotlib.
- [Le carnet de ce TP](/lite/notebooks/index.html?path=tp3.ipynb){ target=_blank }.
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp3.html){ target=_blank }, à faire après la séance.

---

## Étape 1. Un polynôme est une liste (20 min)

Un polynôme \( P(x) = 2 + 3x + 5x^{3} \) est entièrement déterminé par ses coefficients.
La convention que nous prenons, et qui est celle de la plupart des bibliothèques, place le
coefficient constant en premier :

```python
P = [2, 3, 0, 5]   # 2 + 3x + 0x^2 + 5x^3
```

Le coefficient de \( x^{i} \) est donc `P[i]`, et le degré du polynôme est
`len(P) - 1`. Évaluer le polynôme en un point, c'est faire la somme des \( P_i x^{i} \).

!!! question "Exercice 1.1 : évaluation naïve"
    Écrivez `evaluer_naif(P, x)` qui calcule \( P(x) \) en suivant la définition, avec une
    puissance par terme.

    **Résultat attendu :** `evaluer_naif([2, 3, 0, 5], 2)` vaut `48`, car
    \( 2 + 6 + 40 = 48 \).

    ??? success "Corrigé"
        ```python
        def evaluer_naif(P, x):
            """Évalue le polynôme P au point x, terme par terme."""
            total = 0
            for i in range(len(P)):
                total = total + P[i] * x ** i
            return total

        print(evaluer_naif([2, 3, 0, 5], 2))
        print(evaluer_naif([2, 3, 0, 5], 0))
        ```

        En `x = 0`, on retrouve le coefficient constant, `2` : un bon test rapide, car
        toute erreur d'indice se voit immédiatement.

---

## Étape 2. Le schéma de Horner (25 min)

L'évaluation naïve recalcule les puissances de \( x \) à chaque terme, ce qui est du
gaspillage. Horner remarque qu'on peut factoriser :

\[ 2 + 3x + 0x^{2} + 5x^{3} = 2 + x\,(3 + x\,(0 + x \cdot 5)) \]

Il ne reste que des multiplications et des additions, une de chaque par degré, et plus
aucune puissance. On part du coefficient de plus haut degré et on remonte.

!!! question "Exercice 2.1 : Horner"
    Écrivez `evaluer(P, x)` par le schéma de Horner, et vérifiez qu'elle donne le même
    résultat que la version naïve sur plusieurs points.

    **Résultat attendu :** les deux fonctions coïncident, et Horner est plus rapide sur un
    polynôme de degré élevé.

    ??? success "Corrigé"
        ```python
        def evaluer(P, x):
            """Évalue le polynôme P au point x par le schéma de Horner."""
            total = 0
            for coefficient in reversed(P):
                total = total * x + coefficient
            return total

        P = [2, 3, 0, 5]
        for x in (-2, 0, 1, 2, 10):
            print(x, evaluer_naif(P, x), evaluer(P, x))
        ```

        `reversed(P)` parcourt la liste de la fin vers le début : on commence donc par le
        coefficient dominant, et chaque tour multiplie l'accumulateur par `x` avant
        d'ajouter le coefficient suivant. Trois lignes, et c'est optimal : on démontre
        qu'aucune méthode ne peut évaluer un polynôme général avec moins de
        multiplications.

!!! question "Exercice 2.2 : mesurer, et se méfier de ses prévisions"
    Construisez des polynômes dont tous les coefficients valent 1, de degrés 1 000, 5 000
    et 20 000, et comparez le temps des deux méthodes en `x = 1.0001`. Avant de lancer la
    mesure, écrivez votre prévision : de combien Horner devrait-il être plus rapide ?

    **Résultat attendu :** un rapport d'environ 2, **constant** quand le degré augmente.
    Ce n'est probablement pas ce que vous aviez prévu.

    ??? success "Corrigé"
        ```python
        import time

        for degre in (1000, 5000, 20000):
            P = [1] * (degre + 1)

            debut = time.perf_counter()
            a = evaluer_naif(P, 1.0001)
            t_naif = time.perf_counter() - debut

            debut = time.perf_counter()
            b = evaluer(P, 1.0001)
            t_horner = time.perf_counter() - debut

            print(f"degre {degre:>6} : naif {t_naif:.5f} s | horner {t_horner:.5f} s "
                  f"| rapport {t_naif / t_horner:.1f} | ecart des valeurs {abs(a - b):.2e}")
        ```

        Beaucoup s'attendent à ce que l'écart se creuse avec le degré, en raisonnant ainsi :
        la méthode naïve calcule \( x^{i} \) pour chaque terme, donc elle ferait
        \( 1 + 2 + \dots + n \) multiplications, soit un coût quadratique. **Ce
        raisonnement est faux**, et la mesure le montre : le rapport reste à 2 environ,
        que le degré soit mille ou vingt mille. Les deux méthodes sont donc linéaires.

        La raison est que `x ** i` sur un flottant n'est pas une boucle de `i`
        multiplications : c'est une opération unique, calculée par le processeur à partir
        du logarithme et de l'exponentielle, en temps essentiellement constant. La méthode
        naïve fait donc \( n \) exponentiations et \( n \) multiplications, Horner fait
        \( n \) multiplications et \( n \) additions. D'où un facteur constant, et non
        un changement d'ordre de grandeur.

        **La leçon vaut plus que le résultat** : on ne devine pas le coût d'un programme,
        on le mesure. Un raisonnement de complexité s'appuie toujours sur des hypothèses
        concernant le coût des opérations élémentaires, et ces hypothèses peuvent être
        fausses dans le langage que vous utilisez.

        Regardez enfin la dernière colonne. Au degré 20 000, les deux méthodes ne donnent
        plus tout à fait le même nombre : l'écart est de l'ordre de \( 10^{-12} \).
        Accumuler vingt mille puissances de flottants n'est pas la même opération
        qu'enchaîner vingt mille multiplications, et chaque arrondi laisse une trace.
        Horner est donc, à égalité d'ordre de grandeur, un peu plus rapide et surtout plus
        stable numériquement. C'est pour cette dernière raison qu'il est employé partout.

!!! question "Exercice 2.3 : le cas où l'écart explose vraiment"
    Refaites la mesure en évaluant en `x = 3`, un **entier**, sur des degrés 200, 400
    et 800. Le rapport reste-t-il constant ?

    **Résultat attendu :** cette fois le rapport grandit avec le degré, d'environ 4 à
    environ 6.

    ??? success "Corrigé"
        ```python
        for degre in (200, 400, 800):
            P = [1] * (degre + 1)

            debut = time.perf_counter()
            a = evaluer_naif(P, 3)
            t_naif = time.perf_counter() - debut

            debut = time.perf_counter()
            b = evaluer(P, 3)
            t_horner = time.perf_counter() - debut

            print(f"degre {degre:>4} : rapport {t_naif / t_horner:.1f} | resultats egaux : {a == b}")
        ```

        Avec un entier, `3 ** 800` est un nombre de trois cent quatre-vingts chiffres, que
        Python calcule exactement, comme au TP1. L'exponentiation n'est plus une opération
        à coût constant : elle manipule des entiers de plus en plus grands, et le coût
        croît réellement avec le degré. Le raisonnement écarté à l'exercice précédent
        redevient valable ici.

        Deux mesures, deux conclusions opposées, pour le même code : tout dépend du type
        des données. Retenez-le, c'est l'une des différences les plus profondes entre
        Python et un langage où un entier fait toujours 64 bits.

        Notez enfin que les deux résultats sont **exactement** égaux cette fois, puisqu'on
        ne manipule que des entiers, donc aucun arrondi.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez « une fonction Python qui évalue un polynôme donné par ses coefficients ».
    Vous obtiendrez presque toujours la version naïve avec `x ** i`, parce que c'est celle
    qui ressemble le plus à la définition écrite dans les manuels. Elle est juste.
    Demandez ensuite explicitement Horner.

    Puis posez la vraie question : « de combien Horner est-il plus rapide que la version
    naïve, en Python, sur un polynôme de degré 20 000 évalué en un flottant ? » Comparez
    sa réponse à votre mesure de l'exercice 2.2. Si elle vous annonce un gain quadratique
    ou un facteur considérable, elle se trompe, pour exactement la même raison que la
    moitié de la promotion. Un assistant reproduit les raisonnements les plus répandus,
    y compris les raisonnements faux ; seule la mesure tranche.

---

## Étape 3. Dériver un polynôme (15 min)

La dérivée de \( \sum_i a_i x^{i} \) est \( \sum_{i \ge 1} i\,a_i x^{i-1} \). Sur la
représentation par liste, cela se lit directement : le coefficient d'indice `i` devient le
coefficient d'indice `i - 1`, multiplié par `i`.

!!! question "Exercice 3.1 : la dérivée"
    Écrivez `deriver(P)` qui renvoie la liste des coefficients du polynôme dérivé.

    **Résultat attendu :** `deriver([2, 3, 0, 5])` vaut `[3, 0, 15]`, c'est-à-dire
    \( 3 + 15x^{2} \).

    ??? success "Corrigé"
        ```python
        def deriver(P):
            """Coefficients du polynôme dérivé de P."""
            return [i * P[i] for i in range(1, len(P))]

        print(deriver([2, 3, 0, 5]))
        print(deriver([7]))
        ```

        La dérivée d'une constante est le polynôme nul, représenté ici par la liste vide
        `[]`. Vérifiez que votre fonction `evaluer` renvoie bien `0` sur une liste vide,
        sans quoi le cas se propagera en erreur plus loin. Avec le schéma de Horner, c'est
        automatique : la boucle ne fait aucun tour et l'accumulateur reste à zéro.

---

## Étape 4. Trouver une racine (30 min)

Résoudre \( f(x) = 0 \) est le problème numérique le plus courant qui soit. Deux méthodes,
d'esprits opposés.

### La dichotomie : lente, mais elle ne rate jamais

Si \( f \) est continue et si \( f(a) \) et \( f(b) \) sont de signes contraires, alors une
racine se trouve entre les deux. On coupe l'intervalle en deux, on garde la moitié où le
changement de signe persiste, et on recommence. À chaque tour la précision double.

!!! question "Exercice 4.1 : dichotomie"
    Écrivez `dichotomie(f, a, b, tolerance)` qui renvoie une racine de `f` entre `a` et
    `b`. Appliquez-la à \( x^{2} - 2 \) sur \( [0, 2] \).

    **Résultat attendu :** une valeur proche de \( \sqrt{2} \approx 1{,}414214 \).

    ??? success "Corrigé"
        ```python
        def dichotomie(f, a, b, tolerance=1e-12):
            """Racine de f dans [a, b], par bissection. Exige f(a) et f(b) de signes opposés."""
            fa, fb = f(a), f(b)
            if fa == 0:
                return a
            if fb == 0:
                return b
            if fa * fb > 0:
                raise ValueError("f(a) et f(b) doivent etre de signes opposes")
            while b - a > tolerance:
                milieu = (a + b) / 2
                if f(a) * f(milieu) <= 0:
                    b = milieu
                else:
                    a = milieu
            return (a + b) / 2

        def carre_moins_deux(x):
            return x * x - 2

        racine = dichotomie(carre_moins_deux, 0, 2)
        print(racine)
        print(abs(racine - 2 ** 0.5) < 1e-9)
        ```

        Le test `fa * fb > 0` refuse un intervalle où la méthode n'a aucun sens, plutôt
        que de renvoyer un résultat arbitraire. C'est le même réflexe qu'au TP1 avec la
        racine carrée d'un nombre négatif : une fonction sérieuse refuse les entrées
        qu'elle ne sait pas traiter.

### La méthode de Newton : rapide, mais elle peut s'égarer

Newton part d'un point, remplace la courbe par sa tangente, et prend le point où cette
tangente coupe l'axe :

\[ x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)} \]

Quand elle converge, elle double le nombre de décimales exactes à chaque tour, là où la
dichotomie n'en gagne qu'un tous les trois tours. Vous l'avez déjà rencontrée : la méthode
de Héron du TP1 est exactement Newton appliqué à \( x^{2} - a \).

!!! question "Exercice 4.2 : Newton sur un polynôme"
    Écrivez `newton(P, depart, tolerance)` qui cherche une racine du polynôme `P` en
    utilisant `evaluer` et `deriver`. Appliquez-la à \( x^{3} - 2x - 5 \), en partant de 2.

    **Résultat attendu :** environ `2.0945515`, atteint en cinq tours ou moins.

    ??? success "Corrigé"
        ```python
        def newton(P, depart, tolerance=1e-12, tours_max=100):
            """Racine du polynôme P par la méthode de Newton, à partir de depart."""
            derivee = deriver(P)
            x = float(depart)
            for tour in range(tours_max):
                valeur = evaluer(P, x)
                pente = evaluer(derivee, x)
                if pente == 0:
                    raise ZeroDivisionError("tangente horizontale, Newton ne peut pas continuer")
                suivant = x - valeur / pente
                if abs(suivant - x) <= tolerance * max(1.0, abs(suivant)):
                    return suivant, tour + 1
                x = suivant
            raise RuntimeError("pas de convergence en {} tours".format(tours_max))

        # x^3 - 2x - 5
        Q = [-5, -2, 0, 1]
        racine, tours = newton(Q, 2)
        print(racine, "en", tours, "tours")
        print(abs(evaluer(Q, racine)) < 1e-10)
        ```

        Trois protections méritent d'être remarquées. La tangente horizontale est
        détectée au lieu de provoquer une division par zéro incompréhensible. Le nombre
        de tours est plafonné, sans quoi une divergence donnerait une boucle infinie. Et
        le critère d'arrêt est relatif, comme au TP1.

!!! question "Exercice 4.3 : faire échouer Newton"
    Appliquez `newton` au polynôme \( x^{3} - 2x + 2 \), c'est-à-dire `[2, -2, 0, 1]`, en
    partant de `0`. Affichez le trajet des premiers itérés pour comprendre ce qui se passe.

    **Résultat attendu :** aucune convergence, et un trajet qui alterne entre `0` et `1`
    indéfiniment.

    ??? success "Corrigé"
        ```python
        def newton_trace(P, depart, tours):
            """Renvoie la liste des premiers itérés de Newton, sans test d'arrêt."""
            derivee = deriver(P)
            x = float(depart)
            trajet = [x]
            for _ in range(tours):
                pente = evaluer(derivee, x)
                if pente == 0:
                    break
                x = x - evaluer(P, x) / pente
                trajet.append(x)
            return trajet

        R = [2, -2, 0, 1]          # x^3 - 2x + 2
        print(newton_trace(R, 0, 8))

        try:
            print(newton(R, 0))
        except RuntimeError as erreur:
            print("echec :", erreur)
        ```

        Le trajet est `[0.0, 1.0, 0.0, 1.0, 0.0, 1.0, ...]` : la tangente en 0 renvoie en
        1, celle en 1 renvoie en 0, et la méthode tourne en rond pour toujours. On parle
        d'un **cycle** de la méthode de Newton. Sans le plafond `tours_max` que nous avons
        mis dans la fonction, votre programme ne s'arrêterait jamais, et c'est là toute
        l'utilité de ce garde-fou.

        Essayez aussi de partir de `math.sqrt(2 / 3)` sur le polynôme
        \( x^{3} - 2x - 5 \) de l'exercice précédent : c'est un point où la dérivée
        s'annule, la tangente est presque horizontale, et le premier pas projette le
        calcul à environ \( -2{,}7 \times 10^{16} \). La méthode met ensuite des
        dizaines de tours à revenir, sans converger dans le budget imparti.

!!! question "Exercice 4.4 : le prix d'un mauvais point de départ"
    Reprenez \( x^{3} - 2x - 5 \) et comparez le nombre de tours de `newton` en partant
    de `2`, puis de `0`.

    **Résultat attendu :** cinq tours depuis `2`, une vingtaine depuis `0`.

    ??? success "Corrigé"
        ```python
        Q = [-5, -2, 0, 1]
        for depart in (2, 1, 0):
            racine, tours = newton(Q, depart)
            print(f"depart {depart:>2} : {tours:>2} tours, racine {racine:.9f}")
        ```

        Les trois appels trouvent la même racine, donc les trois sont « justes ». Mais
        depuis `0`, la méthode commence par s'éloigner, passe par `-2.5`, `-1.57`,
        `-3.82`, erre un moment, puis finit par tomber dans la zone où la convergence
        quadratique s'enclenche. Newton n'est rapide que **près** de la racine : loin
        d'elle, son comportement n'a aucune garantie.

        C'est pourquoi, en pratique, on encadre d'abord la racine par quelques
        dichotomies avant de passer à Newton. Les bibliothèques sérieuses, comme
        `scipy.optimize.brentq`, font exactement cela.

---

## Étape 5. Voir la fonction (15 min)

Un graphique explique en une seconde ce qu'un tableau de nombres cache. La bibliothèque
`matplotlib` trace des courbes ; elle est disponible dans votre navigateur comme sur votre
machine.

```python
import matplotlib.pyplot as plt

Q = [-5, -2, 0, 1]          # x^3 - 2x - 5
xs = [i / 100 for i in range(-300, 301)]
ys = [evaluer(Q, x) for x in xs]

plt.figure()
plt.plot(xs, ys, label="x^3 - 2x - 5")
plt.axhline(0, linewidth=0.8)
plt.axvline(0, linewidth=0.8)
plt.ylim(-20, 20)
plt.xlabel("x")
plt.ylabel("P(x)")
plt.legend()
plt.title("Un polynome et son unique racine reelle")
plt.show()
```

!!! question "Exercice 5.1 : lire le graphique"
    Sur le tracé, repérez la racine trouvée par Newton. Combien de fois la courbe
    coupe-t-elle l'axe des abscisses ? Ce polynôme est de degré 3 : que dire de ses autres
    racines ?

    ??? success "Corrigé"
        La courbe ne coupe l'axe qu'une seule fois, près de `2.0945`. Un polynôme de
        degré 3 possède toujours trois racines dans les nombres complexes ; ici les deux
        autres sont complexes conjuguées, donc invisibles sur un tracé réel. Un graphique
        montre ce qui existe dans les réels, jamais ce qui n'y est pas : c'est une limite
        à connaître avant de conclure « il n'y a pas d'autre solution ».

!!! tip "Pour aller plus loin"
    Tracez la suite des itérés de Newton sur la même figure, en marquant chaque \( x_n \)
    par un point. Vous verrez la convergence quadratique de vos yeux : les points se
    rapprochent d'abord lentement, puis s'écrasent sur la racine. Refaites le même tracé
    en partant de `0`, et vous verrez la divergence.

---

## Entraînement et approfondissement

À faire après la séance, ou en séance si vous avez terminé. Ces exercices sont au programme
de l'évaluation, sauf ceux marqués « pour aller plus loin ». Ils complètent le TP sur deux
points du programme que la séance n'a fait qu'effleurer : le calcul algébrique sur les
polynômes, et le calcul numérique d'une dérivée et d'une intégrale.

### Étape 6. L'algèbre des polynômes

Additionner ou multiplier deux polynômes, c'est manipuler leurs listes de coefficients.
La multiplication est la plus instructive : le coefficient de \( x^{k} \) dans \( PQ \)
est la somme des \( p_i q_j \) pour tous les couples tels que \( i + j = k \).

!!! question "Exercice 6.1 : somme et produit"
    Écrivez `somme(P, Q)` et `produit_poly(P, Q)`. Attention, les deux listes n'ont pas
    forcément la même longueur.

    **Résultat attendu :** `produit_poly([1, 1], [1, 1])` vaut `[1, 2, 1]`, c'est-à-dire
    \( (1 + x)^{2} = 1 + 2x + x^{2} \), et `produit_poly([-1, 1], [1, 1])` vaut
    `[-1, 0, 1]`, l'identité \( (x - 1)(x + 1) = x^{2} - 1 \).

    ??? success "Corrigé"
        ```python
        def somme(P, Q):
            """Somme de deux polynômes donnés par leurs coefficients."""
            longueur = max(len(P), len(Q))
            P = P + [0] * (longueur - len(P))
            Q = Q + [0] * (longueur - len(Q))
            return [P[i] + Q[i] for i in range(longueur)]

        def produit_poly(P, Q):
            """Produit de deux polynômes donnés par leurs coefficients."""
            if not P or not Q:
                return []
            R = [0] * (len(P) + len(Q) - 1)
            for i in range(len(P)):
                for j in range(len(Q)):
                    R[i + j] = R[i + j] + P[i] * Q[j]
            return R

        print(somme([1, 2], [0, 0, 3]))
        print(produit_poly([1, 1], [1, 1]))
        print(produit_poly([-1, 1], [1, 1]))
        ```

        Le degré du produit est la somme des degrés, d'où la longueur
        `len(P) + len(Q) - 1`. Vérifiez la fonction autrement qu'en lisant le résultat :
        évaluez `P`, `Q` et leur produit en un même point, et contrôlez que
        `evaluer(produit_poly(P, Q), x)` vaut `evaluer(P, x) * evaluer(Q, x)`. C'est le
        même réflexe que la vérification de la division euclidienne au TP1.

!!! question "Exercice 6.2 : le triangle de Pascal, par les polynômes"
    Calculez \( (1 + x)^{10} \) en multipliant dix fois `[1, 1]` par lui-même. Que
    reconnaissez-vous dans la liste obtenue ?

    **Résultat attendu :** `[1, 10, 45, 120, 210, 252, 210, 120, 45, 10, 1]`.

    ??? success "Corrigé"
        ```python
        binome = [1]
        for _ in range(10):
            binome = produit_poly(binome, [1, 1])
        print(binome)
        print(sum(binome), 2 ** 10)
        ```

        Ce sont les coefficients binomiaux \( \binom{10}{k} \), la dixième ligne du
        triangle de Pascal. Leur somme vaut \( 2^{10} \), ce qui est la formule du binôme
        évaluée en \( x = 1 \). Une identité algébrique que vous avez apprise par cœur
        devient ici une vérification en deux lignes.

### Étape 7. Dériver numériquement, et le mur des flottants

Quand on ne connaît pas la formule de la dérivée, on l'approche par un taux de variation :

\[ f'(x) \approx \frac{f(x + h) - f(x)}{h} \qquad \text{ou, mieux,} \qquad
   f'(x) \approx \frac{f(x + h) - f(x - h)}{2h} \]

On se dit que plus \( h \) est petit, meilleure est l'approximation. C'est vrai en
mathématiques, et faux sur une machine.

!!! question "Exercice 7.1 : trouver le meilleur pas"
    Écrivez `derivee_avant(f, x, h)` et `derivee_centree(f, x, h)`. Calculez l'erreur de
    chacune sur \( \sin \) en \( x = 1 \), dont la dérivée exacte est \( \cos 1 \), pour
    `h` valant \( 10^{-1}, 10^{-2}, 10^{-4}, 10^{-6}, 10^{-8}, 10^{-10}, 10^{-12} \).

    **Résultat attendu :** l'erreur diminue puis **remonte**. Le meilleur pas est de
    l'ordre de \( 10^{-8} \) pour la formule avant, \( 10^{-6} \) pour la formule centrée,
    et à \( h = 10^{-12} \) l'erreur est remontée de quatre à six ordres de grandeur
    par rapport à ce meilleur pas.

    ??? success "Corrigé"
        ```python
        import math

        def derivee_avant(f, x, h):
            return (f(x + h) - f(x)) / h

        def derivee_centree(f, x, h):
            return (f(x + h) - f(x - h)) / (2 * h)

        exacte = math.cos(1.0)
        for h in (1e-1, 1e-2, 1e-4, 1e-6, 1e-8, 1e-10, 1e-12):
            e_avant = abs(derivee_avant(math.sin, 1.0, h) - exacte)
            e_centree = abs(derivee_centree(math.sin, 1.0, h) - exacte)
            print(f"h = {h:.0e} : avant {e_avant:.1e} | centree {e_centree:.1e}")
        ```

        Deux erreurs se disputent le résultat. L'erreur **de méthode**, due au fait qu'un
        taux de variation n'est pas une dérivée, diminue avec \( h \) : proportionnelle à
        \( h \) pour la formule avant, à \( h^{2} \) pour la formule centrée, ce qui se
        lit dans les premières lignes, où l'erreur centrée perd deux zéros quand `h` en
        perd un. L'erreur **d'arrondi**, due à la soustraction de deux valeurs presque
        égales, est celle de l'exercice 7.1 du TP1 : elle vaut environ
        \( 10^{-16} / h \) et **grandit** quand \( h \) diminue. Le meilleur pas est celui
        où les deux se croisent.

        La formule centrée est meilleure sur toute la ligne : à même coût, deux
        évaluations de \( f \), elle gagne quatre à cinq chiffres. Retenez-la, et retenez
        surtout qu'en calcul numérique « plus fin » ne veut pas dire « plus juste ».

### Étape 8. Intégrer numériquement

Calculer \( \int_a^b f(x)\,dx \) quand on n'a pas de primitive, c'est approcher l'aire sous
la courbe par des morceaux simples. Trois méthodes, de plus en plus fines, découpent
\( [a, b] \) en \( n \) tranches de largeur \( h = (b - a)/n \) :

- **rectangles** : chaque tranche est un rectangle de hauteur \( f \) à son bord gauche ;
- **trapèzes** : chaque tranche est un trapèze qui relie \( f \) aux deux bords ;
- **Simpson** : on remplace \( f \) par une parabole sur chaque paire de tranches.

!!! question "Exercice 8.1 : les trois méthodes"
    Écrivez `rectangles(f, a, b, n)`, `trapezes(f, a, b, n)` et `simpson(f, a, b, n)`.
    Testez-les sur \( \int_0^1 x^{2}\,dx = 1/3 \) pour `n` valant 10, 100 et 1000.

    **Résultat attendu :** l'erreur des rectangles est divisée par 10 quand `n` est
    multiplié par 10, celle des trapèzes par 100, et Simpson donne le résultat exact, à
    un arrondi de \( 10^{-17} \) près.

    ??? success "Corrigé"
        ```python
        def rectangles(f, a, b, n):
            """Intégrale de f sur [a, b] par n rectangles à gauche."""
            h = (b - a) / n
            return h * sum(f(a + i * h) for i in range(n))

        def trapezes(f, a, b, n):
            """Intégrale de f sur [a, b] par n trapèzes."""
            h = (b - a) / n
            interieur = sum(f(a + i * h) for i in range(1, n))
            return h * ((f(a) + f(b)) / 2 + interieur)

        def simpson(f, a, b, n):
            """Intégrale de f sur [a, b] par la méthode de Simpson, n pair."""
            if n % 2 == 1:
                n = n + 1
            h = (b - a) / n
            impairs = sum(f(a + i * h) for i in range(1, n, 2))
            pairs = sum(f(a + i * h) for i in range(2, n, 2))
            return h / 3 * (f(a) + f(b) + 4 * impairs + 2 * pairs)

        def carre(x):
            return x * x

        for n in (10, 100, 1000):
            e_rect = abs(rectangles(carre, 0, 1, n) - 1 / 3)
            e_trap = abs(trapezes(carre, 0, 1, n) - 1 / 3)
            e_simp = abs(simpson(carre, 0, 1, n) - 1 / 3)
            print(f"n = {n:>4} : rectangles {e_rect:.1e} | trapezes {e_trap:.1e} | simpson {e_simp:.1e}")
        ```

        On dit que les rectangles sont d'**ordre 1**, les trapèzes d'**ordre 2** : l'erreur
        est proportionnelle à \( h \), puis à \( h^{2} \). Simpson est d'ordre 4, et il
        est même **exact** sur tout polynôme de degré au plus 3, ce qui explique le zéro
        de la dernière colonne. Pour le voir travailler, essayez une fonction qui n'est
        pas un polynôme : \( \int_0^{\pi} \sin x\,dx = 2 \), où l'erreur de Simpson est
        divisée par \( 10^{4} \) chaque fois que `n` est multiplié par 10.

!!! question "Exercice 8.2 : calculer π"
    On a \( \int_0^1 \frac{4}{1 + x^{2}}\,dx = \pi \). Calculez cette intégrale par les
    trapèzes et par Simpson avec `n = 1000`, et comparez à `math.pi`.

    **Résultat attendu :** une erreur de l'ordre de \( 10^{-7} \) pour les trapèzes, et
    un résultat indistinguable de `math.pi` pour Simpson.

    ??? success "Corrigé"
        ```python
        def arctangente_derivee(x):
            return 4 / (1 + x * x)

        approx_trap = trapezes(arctangente_derivee, 0, 1, 1000)
        approx_simp = simpson(arctangente_derivee, 0, 1, 1000)
        print(approx_trap, abs(approx_trap - math.pi))
        print(approx_simp, abs(approx_simp - math.pi))
        ```

        Mille évaluations d'une fraction, et l'on obtient toutes les décimales de π que
        la machine sait écrire. Avec les rectangles, il en faudrait des milliards. Comme
        au TP2, changer de méthode rapporte infiniment plus qu'augmenter `n`.

!!! tip "Pour aller plus loin : Newton sur une fonction quelconque"
    La fonction `newton` de l'étape 4 exige un polynôme, parce qu'elle a besoin de la
    dérivée. Avec `derivee_centree`, écrivez une version `newton_general(f, depart)` qui
    accepte n'importe quelle fonction. Appliquez-la à \( \cos x - x = 0 \), dont la
    solution vaut environ `0.7390851332`. Puis trouvez un point de départ pour lequel elle
    diverge, et expliquez pourquoi à l'aide d'un tracé.

---

## Ce qu'il faut retenir

Un polynôme se représente par la liste de ses coefficients, s'évalue par le schéma de
Horner, plus rapide et plus stable que la formule naïve, et se multiplie en sommant les
produits de coefficients d'indices \( i + j = k \). Dériver revient à décaler et multiplier
la liste. Pour trouver une racine, la dichotomie ne rate jamais mais avance lentement ;
Newton va vite mais peut diverger, et il faut donc toujours borner le nombre de tours. En
calcul numérique, dériver ou intégrer plus finement n'est pas toujours plus juste, et
changer de méthode vaut mieux qu'augmenter le nombre de points. Enfin, tracer la fonction
avant de la traiter fait gagner un temps considérable.

## Auto-évaluation

Avant de passer au TP4, vous devez pouvoir, sans regarder le corrigé :

- [ ] écrire le schéma de Horner en trois lignes et dire ce qu'il évite ;
- [ ] expliquer pourquoi la version naïve n'est pas quadratique sur des flottants, mais
  l'est sur des entiers ;
- [ ] écrire la dichotomie et dire quelle hypothèse elle exige sur `f(a)` et `f(b)` ;
- [ ] citer deux façons dont Newton peut échouer, et les deux garde-fous correspondants ;
- [ ] dire pourquoi l'erreur d'une dérivée numérique remonte quand `h` devient trop petit ;
- [ ] classer rectangles, trapèzes et Simpson par ordre de précision.

[Le QCM du TP3](qcm/qcm_tp3.html){ .md-button target=_blank }
[Passer au TP4](tp4-matrices-gauss.md){ .md-button .md-button--primary }
