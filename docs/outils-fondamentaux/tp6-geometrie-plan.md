# TP6. Géométrie du plan

**Durée : 1 h 45. Séance de prolongement.**

Le programme national de la ressource place la géométrie du plan en prolongement des
autres savoirs. Cette séance se fait donc en fin de semestre si le temps le permet, ou en
autonomie sinon. Elle réinvestit tout ce qui précède, les flottants du TP1, les fonctions
du TP3 et les matrices du TP4, sur les objets qu'un informaticien manipule dès qu'il
affiche quelque chose à l'écran : des points, des segments, des polygones.

## Objectifs

- Représenter un point et un vecteur, calculer une norme, un produit scalaire, un angle.
- Comprendre le déterminant \( 2 \times 2 \) comme une **aire orientée**, et en tirer
  l'aire d'un polygone quelconque, l'orientation d'un virage, l'intersection de deux
  segments.
- Décider si un point est à l'intérieur d'un polygone, l'algorithme que tout logiciel de
  dessin, tout jeu et tout système d'information géographique exécute en permanence.
- Retrouver les pièges des flottants là où on ne les attend pas : sur un dessin.

## Prérequis

Les TP1 à TP4. Le TP4 en particulier pour la partie matricielle.

## Ressources

- Le [mémento Python](memento.md), sections tuples et matplotlib.
- [Le carnet de ce TP](/lite/notebooks/index.html?path=tp6.ipynb){ target=_blank }.
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp6.html){ target=_blank }, à faire après la séance.

---

## Étape 1. Points, vecteurs, produit scalaire (20 min)

Un point du plan est un couple de nombres. En Python, un **tuple** `(x, y)` est la
représentation naturelle : deux valeurs qui vont ensemble et qu'on ne modifie pas. Un
vecteur est le même objet, avec un autre sens : une différence entre deux points.

```python
A = (1, 2)
B = (4, 6)
AB = (B[0] - A[0], B[1] - A[1])
print(AB)
```

Le produit scalaire \( \vec{u} \cdot \vec{v} = u_x v_x + u_y v_y \) porte toute la métrique
du plan : la norme est \( \|\vec{u}\| = \sqrt{\vec{u} \cdot \vec{u}} \), et l'angle entre
deux vecteurs vérifie \( \cos\theta = \dfrac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|\,\|\vec{v}\|} \).

!!! question "Exercice 1.1 : la boîte à outils"
    Écrivez `vecteur(A, B)`, `produit_scalaire(u, v)`, `norme(u)` et `angle(u, v)`, ce
    dernier en degrés.

    **Résultat attendu :** `norme((3, 4))` vaut `5.0`, `produit_scalaire((1, 2), (3, 4))`
    vaut `11`, `angle((1, 0), (1, 1))` vaut `45.0` à l'arrondi près, et
    `angle((1, 0), (0, 1))` vaut `90.0`.

    ??? success "Corrigé"
        ```python
        import math

        def vecteur(A, B):
            """Vecteur AB, de A vers B."""
            return (B[0] - A[0], B[1] - A[1])

        def produit_scalaire(u, v):
            return u[0] * v[0] + u[1] * v[1]

        def norme(u):
            return math.hypot(u[0], u[1])

        def angle(u, v):
            """Angle non orienté entre u et v, en degrés."""
            cosinus = produit_scalaire(u, v) / (norme(u) * norme(v))
            cosinus = max(-1.0, min(1.0, cosinus))
            return math.degrees(math.acos(cosinus))

        print(norme((3, 4)), produit_scalaire((1, 2), (3, 4)))
        print(angle((1, 0), (1, 1)), angle((1, 0), (0, 1)))
        print(angle((2, 0), (2, 0)))
        ```

        Deux détails de professionnel. `math.hypot(x, y)` calcule
        \( \sqrt{x^{2} + y^{2}} \) sans faire déborder les carrés quand `x` et `y` sont
        grands, là où `math.sqrt(x * x + y * y)` renverrait l'infini au delà de
        \( 10^{154} \). Et la ligne `max(-1.0, min(1.0, cosinus))` protège `acos` : par
        arrondi, le quotient peut valoir `1.0000000000000002` pour deux vecteurs
        parallèles, et `acos` refuserait alors de répondre. Les flottants du TP1 sont là,
        même en géométrie. Notez enfin que `angle((1, 0), (1, 1))` n'affiche pas
        exactement `45.0` : là encore, un arrondi.

!!! question "Exercice 1.2 : la distance d'un point à une droite"
    La distance du point \( P \) à la droite \( (AB) \) vaut
    \( \dfrac{|\vec{AB} \times \vec{AP}|}{\|\vec{AB}\|} \), où \( \times \) désigne le
    **déterminant** \( u_x v_y - u_y v_x \), que l'étape suivante interprète. Écrivez
    `determinant(u, v)` puis `distance_point_droite(P, A, B)`.

    **Résultat attendu :** la distance de l'origine à la droite passant par \( (0, 1) \) et
    \( (1, 0) \) vaut \( \sqrt{2}/2 \approx 0{,}7071 \), et celle de \( (3, 4) \) à l'axe des
    abscisses vaut `4.0`.

    ??? success "Corrigé"
        ```python
        def determinant(u, v):
            """Déterminant de (u, v), aire orientée du parallélogramme qu'ils engendrent."""
            return u[0] * v[1] - u[1] * v[0]

        def distance_point_droite(P, A, B):
            AB = vecteur(A, B)
            AP = vecteur(A, P)
            return abs(determinant(AB, AP)) / norme(AB)

        print(distance_point_droite((0, 0), (0, 1), (1, 0)), math.sqrt(2) / 2)
        print(distance_point_droite((3, 4), (0, 0), (1, 0)))
        ```

        La formule vient de l'aire : le déterminant est l'aire du parallélogramme construit
        sur \( \vec{AB} \) et \( \vec{AP} \), et cette aire vaut aussi base fois hauteur,
        la base étant \( \|\vec{AB}\| \) et la hauteur la distance cherchée.

---

## Étape 2. Le déterminant est une aire orientée (20 min)

Le nombre \( u_x v_y - u_y v_x \) est l'aire du parallélogramme construit sur \( \vec{u} \)
et \( \vec{v} \), **avec un signe** : positif si l'on tourne de \( \vec{u} \) vers
\( \vec{v} \) dans le sens direct, celui inverse des aiguilles d'une montre, négatif sinon,
nul si les deux vecteurs sont alignés. Ce signe est l'outil le plus utile de toute la
géométrie algorithmique : il dit **de quel côté** d'une droite se trouve un point.

!!! question "Exercice 2.1 : à gauche ou à droite ?"
    Écrivez `orientation(A, B, C)` qui renvoie `1` si le trajet \( A \to B \to C \) tourne
    à gauche, `-1` s'il tourne à droite, `0` si les trois points sont alignés.

    **Résultat attendu :** `orientation((0, 0), (1, 0), (1, 1))` vaut `1`,
    `orientation((0, 0), (1, 0), (1, -1))` vaut `-1`, et
    `orientation((0, 0), (1, 1), (2, 2))` vaut `0`.

    ??? success "Corrigé"
        ```python
        def orientation(A, B, C):
            """1 si A -> B -> C tourne à gauche, -1 à droite, 0 si alignés."""
            d = determinant(vecteur(A, B), vecteur(A, C))
            if d > 0:
                return 1
            if d < 0:
                return -1
            return 0

        print(orientation((0, 0), (1, 0), (1, 1)))
        print(orientation((0, 0), (1, 0), (1, -1)))
        print(orientation((0, 0), (1, 1), (2, 2)))
        ```

        Le cas `0` est fragile avec des flottants : trois points « presque » alignés
        donneront un déterminant de l'ordre de \( 10^{-16} \), donc `1` ou `-1` au
        hasard. C'est le problème de l'exercice 2.2 du TP1, et la bonne réponse est la
        même : comparer à une tolérance, pas à zéro. Les bibliothèques de géométrie
        sérieuses vont plus loin encore, et calculent ce signe en arithmétique exacte,
        avec des `Fraction` ou des entiers, parce qu'un signe faux fait planter tout ce
        qui suit.

!!! question "Exercice 2.2 : l'aire d'un polygone"
    Un polygone est une liste de sommets dans l'ordre. Son aire vaut la moitié de la
    valeur absolue de la somme des déterminants \( x_i y_{i+1} - x_{i+1} y_i \) sur les
    côtés consécutifs, le dernier sommet étant relié au premier : c'est la **formule du
    lacet**. Écrivez `aire(polygone)`.

    **Résultat attendu :** le carré unité a une aire de `1.0`, le triangle
    \( (0,0), (4,0), (0,3) \) une aire de `6.0`, et la maison du TP4,
    `[(0, 0), (2, 0), (2, 1.5), (1, 2.5), (0, 1.5)]`, une aire de `4.0`.

    ??? success "Corrigé"
        ```python
        def aire(polygone):
            """Aire d'un polygone simple donné par ses sommets dans l'ordre (formule du lacet)."""
            somme = 0
            n = len(polygone)
            for i in range(n):
                x1, y1 = polygone[i]
                x2, y2 = polygone[(i + 1) % n]
                somme = somme + (x1 * y2 - x2 * y1)
            return abs(somme) / 2

        carre = [(0, 0), (1, 0), (1, 1), (0, 1)]
        triangle = [(0, 0), (4, 0), (0, 3)]
        maison = [(0, 0), (2, 0), (2, 1.5), (1, 2.5), (0, 1.5)]
        print(aire(carre), aire(triangle), aire(maison))
        ```

        L'indice `(i + 1) % n` referme le polygone : le sommet qui suit le dernier est le
        premier. Vérifiez la maison à la main : un rectangle de \( 2 \times 1{,}5 = 3 \)
        surmonté d'un triangle de base 2 et de hauteur 1, soit \( 3 + 1 = 4 \). La formule
        marche pour n'importe quel polygone sans croisement, convexe ou non, en une seule
        boucle : c'est elle qu'utilisent les cadastres pour calculer la surface d'une
        parcelle à partir des coordonnées de ses bornes.

        Sans la valeur absolue, le signe dit dans quel sens les sommets sont parcourus :
        positif dans le sens direct. Essayez `maison[::-1]`.

---

## Étape 3. Deux segments se coupent-ils ? (20 min)

Le segment \( [AB] \) et le segment \( [CD] \) se coupent si et seulement si \( C \) et
\( D \) sont de part et d'autre de la droite \( (AB) \), **et** \( A \) et \( B \) de part
et d'autre de la droite \( (CD) \). Quatre orientations suffisent à le dire, sans calculer
le point d'intersection.

!!! question "Exercice 3.1 : le test de croisement"
    Écrivez `se_coupent(A, B, C, D)` avec quatre appels à `orientation`. Ne traitez pas les
    cas où trois points sont alignés : renvoyez `False`, et notez-le dans la docstring.

    **Résultat attendu :** les diagonales du carré unité se coupent ; les segments
    \( [(0,0), (1, 0)] \) et \( [(0, 1), (1, 1)] \), parallèles, ne se coupent pas ;
    \( [(0,0), (1,1)] \) et \( [(2,2), (3,3)] \), alignés mais disjoints, non plus.

    ??? success "Corrigé"
        ```python
        def se_coupent(A, B, C, D):
            """Vrai si les segments [AB] et [CD] se croisent franchement.

            Les cas dégénérés (trois points alignés) renvoient False.
            """
            o1 = orientation(A, B, C)
            o2 = orientation(A, B, D)
            o3 = orientation(C, D, A)
            o4 = orientation(C, D, B)
            return o1 * o2 < 0 and o3 * o4 < 0

        print(se_coupent((0, 0), (1, 1), (0, 1), (1, 0)))
        print(se_coupent((0, 0), (1, 0), (0, 1), (1, 1)))
        print(se_coupent((0, 0), (1, 1), (2, 2), (3, 3)))
        ```

        `o1 * o2 < 0` dit que `C` et `D` sont de signes opposés par rapport à \( (AB) \).
        Le produit est la manière la plus courte d'écrire « de signes contraires », déjà
        employée dans la dichotomie du TP3.

!!! question "Exercice 3.2 : le point d'intersection"
    Quand les segments se coupent, on veut souvent le point. En écrivant
    \( A + t\,\vec{AB} = C + u\,\vec{CD} \), on obtient un système de deux équations à deux
    inconnues \( t \) et \( u \), que les déterminants résolvent directement :
    \( t = \dfrac{\vec{AC} \times \vec{CD}}{\vec{AB} \times \vec{CD}} \) et
    \( u = \dfrac{\vec{AC} \times \vec{AB}}{\vec{AB} \times \vec{CD}} \). Écrivez
    `intersection(A, B, C, D)` qui renvoie le point, ou `None` si les segments ne se
    coupent pas.

    **Résultat attendu :** les diagonales du carré de côté 2 se coupent en `(1.0, 1.0)`.

    ??? success "Corrigé"
        ```python
        def intersection(A, B, C, D):
            """Point d'intersection des segments [AB] et [CD], ou None."""
            AB = vecteur(A, B)
            CD = vecteur(C, D)
            denominateur = determinant(AB, CD)
            if denominateur == 0:
                return None            # parallèles ou alignés
            AC = vecteur(A, C)
            t = determinant(AC, CD) / denominateur
            u = determinant(AC, AB) / denominateur
            if 0 <= t <= 1 and 0 <= u <= 1:
                return (A[0] + t * AB[0], A[1] + t * AB[1])
            return None

        print(intersection((0, 0), (2, 2), (0, 2), (2, 0)))
        print(intersection((0, 0), (1, 0), (0, 1), (1, 1)))
        print(intersection((0, 0), (1, 1), (2, 2), (3, 3)))
        ```

        C'est un système linéaire \( 2 \times 2 \), résolu par les formules de Cramer, qui
        ne sont rien d'autre que le pivot de Gauss du TP4 écrit pour la taille 2. Le test
        `denominateur == 0` est encore une comparaison exacte de flottants : pour deux
        segments presque parallèles, `t` et `u` seront énormes et le point renvoyé
        n'aura aucun sens. Un programme robuste compare `abs(denominateur)` à une
        tolérance, et les intersections presque parallèles sont la plaie de tous les
        logiciels de CAO.

---

## Étape 4. Un point est-il dans un polygone ? (25 min)

C'est **le** problème de la géométrie algorithmique appliquée : savoir si le clic de la
souris est sur le bouton, si le personnage est dans la zone, si l'adresse est dans la
commune. L'algorithme classique est le **lancer de rayon** : on trace une demi-droite
horizontale partant du point vers la droite, et on compte combien de côtés du polygone
elle traverse. Impair, le point est dedans ; pair, il est dehors.

!!! question "Exercice 4.1 : le lancer de rayon"
    Écrivez `dedans(P, polygone)`. Pour chaque côté \( [S_i S_{i+1}] \), le rayon le
    traverse si les deux ordonnées encadrent celle de \( P \) et si l'abscisse du point de
    croisement, obtenue par interpolation, est à droite de \( P \).

    **Résultat attendu :** dans la maison, `(1, 1)` et `(1, 2.4)` sont dedans, `(3, 1)`
    et `(0.2, 2.2)` sont dehors.

    ??? success "Corrigé"
        ```python
        def dedans(P, polygone):
            """Vrai si P est à l'intérieur du polygone, par lancer de rayon horizontal."""
            x, y = P
            n = len(polygone)
            interieur = False
            for i in range(n):
                x1, y1 = polygone[i]
                x2, y2 = polygone[(i + 1) % n]
                if (y1 > y) != (y2 > y):
                    x_croisement = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    if x < x_croisement:
                        interieur = not interieur
            return interieur

        for P in ((1, 1), (1, 2.4), (3, 1), (0.2, 2.2)):
            print(P, dedans(P, maison))
        ```

        La condition `(y1 > y) != (y2 > y)` est le cœur de l'algorithme, et elle est plus
        subtile qu'il n'y paraît : avec des inégalités strictes d'un côté et larges de
        l'autre, un rayon qui passe exactement par un sommet compte le sommet pour un seul
        des deux côtés qui s'y rejoignent, et non pour deux ou zéro. Sans cette précaution,
        les sommets seraient une source inépuisable de résultats faux. Le point
        `(0.2, 2.2)` est sous le toit mais hors du mur gauche : il faut un instant de
        réflexion pour voir qu'il est bien dehors, et la machine ne se trompe pas.

!!! question "Exercice 4.2 : l'aire par le hasard"
    On peut estimer une aire sans formule : tirer des points au hasard dans un rectangle
    qui contient la figure, compter ceux qui tombent dedans, et multiplier la proportion
    par l'aire du rectangle. C'est la **méthode de Monte-Carlo**. Estimez ainsi l'aire de
    la maison avec 200 000 points tirés dans le rectangle \( [0, 2] \times [0, 2{,}5] \).

    **Résultat attendu :** une valeur proche de `4.0`, à quelques centièmes près, et qui
    change à chaque exécution si vous ne fixez pas la graine.

    ??? success "Corrigé"
        ```python
        import random

        random.seed(0)
        tirages = 200_000
        touches = 0
        for _ in range(tirages):
            P = (random.uniform(0, 2), random.uniform(0, 2.5))
            if dedans(P, maison):
                touches = touches + 1

        aire_rectangle = 2 * 2.5
        print(aire_rectangle * touches / tirages)
        ```

        Deux cent mille tirages pour deux chiffres justes, contre une boucle de cinq
        tours pour la formule du lacet : Monte-Carlo est une méthode lente, dont l'erreur
        ne diminue que comme \( 1/\sqrt{N} \), il faut cent fois plus de points pour
        gagner une décimale. Mais elle marche sur **n'importe quelle** figure dont on sait
        seulement dire si un point est dedans, y compris en dimension 10 ou 1 000, là où
        aucune formule n'existe. C'est ainsi que se calculent les intégrales de la
        physique des particules et les prix des produits financiers.

---

## Étape 5. Dessiner (20 min)

Rien ne vaut un tracé pour vérifier une géométrie. La fonction ci-dessous dessine un
polygone fermé et des points, colorés selon qu'ils sont dedans ou dehors.

```python
import matplotlib.pyplot as plt

def tracer_polygone(polygone, points=()):
    xs = [s[0] for s in polygone] + [polygone[0][0]]
    ys = [s[1] for s in polygone] + [polygone[0][1]]
    plt.figure(figsize=(5, 5))
    plt.plot(xs, ys, color="black")
    for P in points:
        couleur = "green" if dedans(P, polygone) else "red"
        plt.scatter([P[0]], [P[1]], color=couleur)
    plt.axis("equal")
    plt.title("Vert : dedans, rouge : dehors")
    plt.show()

random.seed(1)
nuage = [(random.uniform(-0.5, 2.5), random.uniform(-0.5, 3)) for _ in range(60)]
tracer_polygone(maison, nuage)
```

!!! question "Exercice 5.1 : un polygone qui n'est pas convexe"
    Construisez un polygone en forme de L ou d'étoile, non convexe, et vérifiez sur un
    tracé que `dedans` et `aire` donnent des résultats corrects, y compris dans le creux.

    ??? success "Corrigé"
        ```python
        etoile = []
        for k in range(10):
            rayon = 2 if k % 2 == 0 else 0.8
            theta = math.pi / 2 + k * math.pi / 5
            etoile.append((rayon * math.cos(theta), rayon * math.sin(theta)))

        print(round(aire(etoile), 4))
        print(dedans((0, 0), etoile), dedans((0, 1.5), etoile), dedans((1.2, 1.2), etoile))
        tracer_polygone(etoile, [(0, 0), (0, 1.5), (1.2, 1.2), (0, 1.9)])
        ```

        Le centre est dedans, la pointe supérieure `(0, 1.5)` aussi, et `(1.2, 1.2)`,
        situé dans un creux entre deux branches, est dehors. Le lancer de rayon ne
        suppose rien sur la forme : il compte des traversées, et c'est ce qui le rend
        universel. La formule du lacet non plus. Les deux algorithmes que vous avez écrits
        sont exactement ceux des bibliothèques professionnelles, à la gestion des cas
        limites près.

---

## Entraînement et approfondissement

!!! question "Exercice 6.1 : le polygone le plus proche"
    On dispose de plusieurs polygones, par exemple les zones d'une carte, et d'un point
    cliqué. Écrivez `zone_de(P, zones)` qui renvoie l'indice de la zone contenant `P`, ou
    `None`. Testez avec la maison et le carré `[(3, 0), (4, 0), (4, 1), (3, 1)]`.

    **Résultat attendu :** `(1, 1)` est dans la zone `0`, `(3.5, 0.5)` dans la zone `1`,
    `(2.5, 0.5)` dans aucune.

    ??? success "Corrigé"
        ```python
        def zone_de(P, zones):
            """Indice de la première zone qui contient P, ou None."""
            for indice, zone in enumerate(zones):
                if dedans(P, zone):
                    return indice
            return None

        zones = [maison, [(3, 0), (4, 0), (4, 1), (3, 1)]]
        for P in ((1, 1), (3.5, 0.5), (2.5, 0.5)):
            print(P, zone_de(P, zones))
        ```

        Avec dix mille zones et un million de clics, cette boucle devient lente, et les
        systèmes d'information géographique la remplacent par un index spatial qui écarte
        d'un coup les zones dont le rectangle englobant ne contient pas le point. C'est le
        crible du TP2 appliqué à l'espace : ne pas tester ce qu'on peut éliminer en bloc.

!!! tip "Pour aller plus loin : l'enveloppe convexe"
    L'enveloppe convexe d'un nuage de points est le plus petit polygone convexe qui les
    contient tous, l'élastique tendu autour des clous. L'algorithme d'Andrew la construit
    en triant les points par abscisse, puis en parcourant la liste en ne gardant que les
    points qui « tournent à gauche », ce que dit votre fonction `orientation` : on
    construit ainsi la chaîne inférieure, puis la chaîne supérieure en repartant de la
    droite. Écrivez `enveloppe(points)`, vérifiez que l'enveloppe du carré unité augmenté
    de son centre est le carré, puis tracez l'enveloppe de deux cents points gaussiens.
    Elle compte typiquement une dizaine de sommets.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez « une fonction Python qui dit si un point est dans un polygone ». Vous
    obtiendrez le lancer de rayon, presque toujours correct sur des points quelconques.
    Testez-le alors sur un point situé **exactement** à la hauteur d'un sommet, par
    exemple `(1, 1.5)` dans la maison, et sur un point situé sur un côté, comme
    `(1, 0)`. Regardez comment sont écrites les inégalités de la condition d'encadrement,
    et cherchez le cas où deux côtés sont comptés pour un même sommet. Notez ce que vous
    trouvez : les cas limites sont l'endroit où la géométrie algorithmique se joue, et
    l'endroit où le code généré est le plus souvent faux.

---

## Ce qu'il faut retenir

Un point est un tuple, un vecteur une différence de points. Le produit scalaire donne
normes et angles, le déterminant donne l'aire orientée, et son signe dit de quel côté d'une
droite se trouve un point : c'est de lui que découlent l'aire d'un polygone, le test de
croisement de deux segments et l'orientation d'un virage. Le lancer de rayon décide si un
point est dans un polygone quelconque. Et les flottants restent des flottants : comparer un
déterminant à zéro est une faute, et les cas limites, sommets et côtés alignés, se traitent
à part.

## Auto-évaluation

- [ ] écrire de tête le produit scalaire et le déterminant de deux vecteurs du plan ;
- [ ] dire ce que signifient le signe et la valeur absolue d'un déterminant \( 2 \times 2 \) ;
- [ ] écrire la formule du lacet et expliquer le rôle de `(i + 1) % n` ;
- [ ] expliquer le lancer de rayon en trois phrases, et dire pourquoi la condition
  d'encadrement mêle une inégalité stricte et une inégalité large ;
- [ ] dire pourquoi la méthode de Monte-Carlo est lente, et quand on l'emploie malgré tout.

[Le QCM du TP6](qcm/qcm_tp6.html){ .md-button target=_blank }
[Retour au module](index.md){ .md-button .md-button--primary }
