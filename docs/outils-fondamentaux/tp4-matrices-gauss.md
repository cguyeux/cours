# TP4. Matrices et systèmes linéaires

**Durée : 1 h 45.**

## Objectifs

- Représenter une matrice, la transposer, la multiplier, à la main d'abord.
- Écrire soi-même le pivot de Gauss, avec pivot partiel, et résoudre un système.
- Découvrir numpy, mesurer ce qu'il apporte, et comprendre pourquoi on ne calcule jamais
  l'inverse d'une matrice pour résoudre un système.

## Prérequis

Les TP1 à TP3 : listes, boucles imbriquées, fonctions, mesure de temps.

## Ressources

- Le [mémento Python](memento.md), sections listes et numpy.
- [Le carnet de ce TP](/lite/notebooks/index.html?path=tp4.ipynb){ target=_blank }.
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp4.html){ target=_blank }, à faire après la séance.

---

## Étape 1. Une matrice est une liste de listes (15 min)

En Python pur, une matrice se représente par une liste de lignes, chaque ligne étant
elle-même une liste :

```python
A = [[1, 2, 2],
     [1, 3, -2],
     [3, 5, 8]]

print(A[0])        # la premiere ligne
print(A[0][2])     # ligne 0, colonne 2
print(len(A), len(A[0]))   # nombre de lignes, nombre de colonnes
```

L'élément \( a_{ij} \) s'écrit donc `A[i][j]`, avec les indices qui commencent à zéro. La
matrice ci-dessus est celle du système que nous allons résoudre à l'étape 4 :

\[
\left\{
\begin{array}{rcl}
x_0 + 2x_1 + 2x_2 &=& 2 \\
x_0 + 3x_1 - 2x_2 &=& -1 \\
3x_0 + 5x_1 + 8x_2 &=& 8
\end{array}
\right.
\]

!!! question "Exercice 1.1 : la transposée"
    Écrivez `transposee(A)` qui échange lignes et colonnes.

    **Résultat attendu :** la transposée de `[[1, 2, 3], [4, 5, 6]]` est
    `[[1, 4], [2, 5], [3, 6]]`.

    ??? success "Corrigé"
        ```python
        def transposee(A):
            """Transposée de la matrice A, donnée comme liste de lignes."""
            lignes = len(A)
            colonnes = len(A[0])
            return [[A[i][j] for i in range(lignes)] for j in range(colonnes)]

        print(transposee([[1, 2, 3], [4, 5, 6]]))
        ```

        Notez l'ordre des deux boucles : la boucle extérieure engendre les lignes du
        résultat, donc elle parcourt les colonnes de `A`. Inverser les deux donne une
        matrice de la bonne taille mais fausse, erreur difficile à repérer sur une
        matrice carrée. Testez toujours sur une matrice **rectangulaire**, où une erreur
        de dimension saute aux yeux.

---

## Étape 2. Le produit matriciel, et son coût (20 min)

Le produit \( C = AB \) est défini par \( c_{ij} = \sum_k a_{ik} b_{kj} \). Chaque
coefficient du résultat demande une somme, et il y a autant de coefficients que de cases :
d'où trois boucles imbriquées.

!!! question "Exercice 2.1 : produit à la main"
    Écrivez `produit(A, B)`, et vérifiez sur un exemple que vous savez calculer de tête.

    **Résultat attendu :** multiplier une matrice par l'identité la laisse inchangée.

    ??? success "Corrigé"
        ```python
        def produit(A, B):
            """Produit matriciel A x B, en Python pur."""
            n, p = len(A), len(A[0])
            if len(B) != p:
                raise ValueError("dimensions incompatibles")
            q = len(B[0])
            C = [[0] * q for _ in range(n)]
            for i in range(n):
                for j in range(q):
                    somme = 0
                    for k in range(p):
                        somme = somme + A[i][k] * B[k][j]
                    C[i][j] = somme
            return C

        identite = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        A = [[1, 2, 2], [1, 3, -2], [3, 5, 8]]
        print(produit(A, identite) == A)
        print(produit([[1, 2], [3, 4]], [[0, 1], [1, 0]]))
        ```

        Attention au piège de l'initialisation : `[[0] * q] * n` semble équivalent à la
        ligne écrite ci-dessus, mais crée **n références vers la même ligne**. Modifier
        `C[0][0]` modifierait alors toutes les lignes à la fois. C'est l'une des erreurs
        les plus coûteuses en temps de débogage de toute la première année.

!!! question "Exercice 2.2 : mesurer le coût cubique"
    Mesurez le temps de `produit` sur deux matrices carrées aléatoires de taille 40, 80
    puis 120. Que devient le temps quand la taille double ?

    **Résultat attendu :** le temps est multiplié par environ 8 quand la taille double.

    ??? success "Corrigé"
        ```python
        import random
        import time

        random.seed(42)

        def matrice_aleatoire(n):
            return [[random.random() for _ in range(n)] for _ in range(n)]

        for n in (40, 80, 120):
            A = matrice_aleatoire(n)
            B = matrice_aleatoire(n)
            debut = time.perf_counter()
            produit(A, B)
            print(f"n = {n:>3} : {time.perf_counter() - debut:.4f} s")
        ```

        Trois boucles imbriquées de longueur \( n \) font \( n^{3} \) multiplications :
        doubler \( n \) multiplie le travail par \( 2^{3} = 8 \). Sur \( n = 1000 \), il
        faudrait un milliard d'opérations, soit plusieurs minutes en Python pur. C'est
        précisément pour cela que numpy existe.

---

## Étape 3. numpy, ou déléguer le calcul (15 min)

`numpy` est la bibliothèque de calcul numérique de Python. Ses tableaux sont stockés d'un
seul tenant en mémoire et ses opérations sont exécutées par du code compilé, souvent
parallélisé. Le gain n'est pas de quelques pourcents, il est d'un facteur cent ou mille.

```python
import numpy as np

A = np.array([[1.0, 2.0, 2.0],
              [1.0, 3.0, -2.0],
              [3.0, 5.0, 8.0]])
b = np.array([2.0, -1.0, 8.0])

print(A.shape)
print(A.T)          # transposée
print(A @ A)        # produit matriciel
print(A * A)        # produit terme à terme : ce n'est PAS le produit matriciel
```

La distinction entre `@` et `*` est essentielle : `@` est le produit matriciel,
`*` multiplie case par case. Les confondre donne un résultat de la bonne forme et
complètement faux.

!!! question "Exercice 3.1 : le rapport de temps"
    Reprenez la mesure de l'exercice 2.2 pour `n = 120`, et comparez au produit numpy des
    mêmes matrices.

    **Résultat attendu :** numpy est plus rapide de deux à trois ordres de grandeur.

    ??? success "Corrigé"
        ```python
        n = 120
        A = matrice_aleatoire(n)
        B = matrice_aleatoire(n)

        debut = time.perf_counter()
        produit(A, B)
        t_python = time.perf_counter() - debut

        An, Bn = np.array(A), np.array(B)
        debut = time.perf_counter()
        An @ Bn
        t_numpy = time.perf_counter() - debut

        print(f"python pur {t_python:.4f} s")
        print(f"numpy      {t_numpy:.6f} s")
        print("rapport :", round(t_python / max(t_numpy, 1e-9)))
        ```

        Ce rapport explique pourquoi tout le calcul scientifique en Python passe par
        numpy. Cela ne dispense pas d'avoir écrit le produit à la main une fois : c'est en
        l'écrivant qu'on comprend le coût cubique, et donc pourquoi multiplier deux
        matrices de dix mille lignes n'est pas une opération anodine, même avec numpy.

---

## Étape 4. Le pivot de Gauss (35 min)

Résoudre \( Ax = b \) à la main, c'est éliminer les inconnues une à une pour arriver à un
système triangulaire, qu'on résout ensuite de bas en haut. C'est la méthode du pivot de
Gauss, et vous allez l'écrire entièrement.

Trois opérations laissent l'ensemble des solutions inchangé : échanger deux lignes,
multiplier une ligne par un nombre non nul, ajouter à une ligne un multiple d'une autre.

### Le choix du pivot

À l'étape \( k \), on veut annuler les coefficients sous la diagonale dans la colonne
\( k \), en soustrayant un multiple de la ligne \( k \). Cela suppose que le coefficient
diagonal, le **pivot**, ne soit pas nul. En arithmétique exacte, il suffirait de prendre
n'importe quel pivot non nul. En arithmétique flottante, il faut faire mieux : on choisit
le plus grand pivot possible en valeur absolue, ce qu'on appelle le **pivot partiel**.
Diviser par un très petit nombre amplifie les erreurs d'arrondi, et le résultat peut être
faux de plusieurs ordres de grandeur.

!!! question "Exercice 4.1 : élimination et remontée"
    Écrivez `resoudre(A, b)` qui résout le système par le pivot de Gauss avec pivot
    partiel, et testez-la sur le système de l'étape 1.

    **Résultat attendu :** la solution est \( (3,\, -1,\, 0{,}5) \), et \( A x \)
    redonne bien \( b \).

    ??? success "Corrigé"
        ```python
        def resoudre(A, b, tolerance=1e-14):
            """Résout A x = b par le pivot de Gauss avec pivot partiel.

            A est une liste de lignes, b une liste. Ni A ni b ne sont modifiés.
            Un pivot inférieur ou égal à tolerance est considéré comme nul.
            """
            n = len(A)
            # copie de travail, matrice augmentée [A | b]
            M = [list(A[i]) + [b[i]] for i in range(n)]

            for k in range(n):
                # pivot partiel : la ligne dont le coefficient est le plus grand en valeur absolue
                meilleure = max(range(k, n), key=lambda i: abs(M[i][k]))
                if abs(M[meilleure][k]) <= tolerance:
                    raise ValueError("systeme singulier ou mal pose")
                M[k], M[meilleure] = M[meilleure], M[k]

                # élimination sous la diagonale
                for i in range(k + 1, n):
                    facteur = M[i][k] / M[k][k]
                    for j in range(k, n + 1):
                        M[i][j] = M[i][j] - facteur * M[k][j]

            # remontée : on résout de la dernière équation vers la première
            x = [0.0] * n
            for i in range(n - 1, -1, -1):
                somme = M[i][n]
                for j in range(i + 1, n):
                    somme = somme - M[i][j] * x[j]
                x[i] = somme / M[i][i]
            return x

        A = [[1, 2, 2], [1, 3, -2], [3, 5, 8]]
        b = [2, -1, 8]
        x = resoudre(A, b)
        print([round(v, 10) for v in x])

        # vérification : A x doit redonner b
        verif = [sum(A[i][j] * x[j] for j in range(3)) for i in range(3)]
        print([round(v, 10) for v in verif])
        ```

        Trois points à retenir. On travaille sur une **copie** : une fonction qui abîme
        ses arguments est une source de bogues inépuisable. On construit la matrice
        augmentée \( [A \mid b] \), ce qui évite de faire les mêmes opérations deux fois
        sur deux objets séparés. Et on vérifie le résultat en recalculant \( Ax \), plutôt
        qu'en relisant le code.

        Le seuil `tolerance` mérite un mot. Avec des flottants, un pivot « nul » ne vaut
        jamais exactement `0.0` : c'est un résidu d'arrondis, de l'ordre de
        \( 10^{-16} \). Comparer à zéro laisserait passer une matrice singulière, et la
        remontée diviserait par ce résidu pour produire des valeurs absurdes. On compare
        donc à un petit seuil, et on le laisse réglable : l'étape 8 montrera un cas où il
        faut le mettre à zéro.

!!! question "Exercice 4.2 : confronter à numpy"
    Comparez votre solution à celle de `numpy.linalg.solve` sur un système aléatoire de
    taille 50.

    **Résultat attendu :** les deux solutions coïncident à \( 10^{-9} \) près.

    ??? success "Corrigé"
        ```python
        random.seed(7)
        n = 50
        A = matrice_aleatoire(n)
        b = [random.random() for _ in range(n)]

        mienne = resoudre(A, b)
        celle_de_numpy = np.linalg.solve(np.array(A), np.array(b))

        ecart = max(abs(mienne[i] - celle_de_numpy[i]) for i in range(n))
        print("ecart maximal :", ecart)
        print(ecart < 1e-9)
        ```

        Les deux implémentations font le même travail ; celle de numpy est écrite en
        Fortran optimisé depuis quarante ans, mais l'algorithme est le vôtre. Un écart de
        l'ordre de \( 10^{-13} \) est normal : ce sont les arrondis du TP1, qui n'ont pas
        disparu.

---

## Étape 5. Pourquoi on n'inverse jamais une matrice (15 min)

Mathématiquement, \( x = A^{-1} b \). Il est donc tentant d'écrire `np.linalg.inv(A) @ b`.
C'est ce que propose spontanément à peu près tout le monde, humain ou machine. C'est
pourtant une mauvaise idée : calculer l'inverse coûte plus cher que résoudre, et surtout
amplifie les erreurs d'arrondi.

Pour le voir, on utilise une matrice réputée difficile, la matrice de Hilbert, dont les
coefficients valent \( 1/(i+j+1) \). Elle est parfaitement inversible en théorie, et
catastrophique en pratique.

```python
def hilbert(n):
    return np.array([[1.0 / (i + j + 1) for j in range(n)] for i in range(n)])

n = 12
H = hilbert(n)
x_vrai = np.ones(n)          # on choisit la solution d'avance
b = H @ x_vrai               # et on fabrique le second membre correspondant

x_solve = np.linalg.solve(H, b)
x_inverse = np.linalg.inv(H) @ b

print("erreur avec solve   :", float(np.max(np.abs(x_solve - x_vrai))))
print("erreur avec inv @ b :", float(np.max(np.abs(x_inverse - x_vrai))))
print("conditionnement     : {:.3e}".format(float(np.linalg.cond(H))))
```

!!! question "Exercice 5.1 : lire le résultat"
    Exécutez le bloc ci-dessus et commentez. Quelle méthode donne la solution la plus
    proche de la vraie ? Que vaut le conditionnement, et qu'est-ce que cela signifie ?

    ??? success "Corrigé"
        Les chiffres parlent d'eux-mêmes. Toutes les composantes de la vraie solution
        valent 1. `solve` se trompe d'environ 0,7, et `inv` suivi d'un produit d'environ
        21. La seconde méthode est donc à peu près trente fois pire que la première, et
        aucune des deux ne donne un résultat utilisable.

        La cause est le **conditionnement**, ici de l'ordre de \( 1{,}8 \times 10^{16} \).
        Ce nombre mesure de combien une petite perturbation des données peut perturber la
        solution. Quand il approche \( 10^{16} \), soit l'inverse de la précision des
        flottants, plus aucun chiffre du résultat n'est fiable, et aucun algorithme ne
        peut y remédier : c'est le problème lui-même qui est mal posé, pas votre
        programme. Refaites l'essai avec `n = 10` : le conditionnement tombe à
        \( 1{,}6 \times 10^{13} \), les erreurs à \( 1{,}7 \times 10^{-4} \) et
        \( 5{,}5 \times 10^{-3} \), et l'écart de trente entre les deux méthodes,
        lui, demeure.

        Retenez la règle pratique : pour résoudre un système, on écrit toujours
        `np.linalg.solve(A, b)`, jamais `np.linalg.inv(A) @ b`.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez « comment résoudre un système linéaire en Python avec numpy ». Notez si la
    réponse propose `inv(A) @ b` ou `solve(A, b)`. Les deux apparaissent couramment, parce
    que les deux sont écrites partout sur le web, et l'assistant reproduit ce qu'il a lu
    plutôt que ce qui est recommandé. Demandez-lui ensuite lequel des deux est préférable
    et pourquoi : la réponse sera juste. Il **sait**, mais il ne le dit que si on demande.
    C'est exactement le genre de question que seul quelqu'un qui connaît le sujet pense à
    poser.

---

## Étape 6. Les matrices transforment le plan (10 min)

Une matrice \( 2 \times 2 \) est une transformation géométrique. La rotation d'angle
\( \theta \) autour de l'origine s'écrit :

\[ R(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix} \]

```python
import matplotlib.pyplot as plt

def rotation(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s], [s, c]])

# une maison, comme suite de points (fermée)
maison = np.array([[0, 0], [2, 0], [2, 1.5], [1, 2.5], [0, 1.5], [0, 0]]).T

plt.figure(figsize=(5, 5))
plt.plot(maison[0], maison[1], label="depart")
for angle in (np.pi / 6, np.pi / 3, np.pi / 2):
    image = rotation(angle) @ maison
    plt.plot(image[0], image[1], label=f"rotation {int(np.degrees(angle))} degres")
plt.axis("equal")
plt.legend()
plt.title("Une matrice fait tourner une figure")
plt.show()
```

!!! question "Exercice 6.1 : composer deux transformations"
    Vérifiez numériquement que faire tourner de 30 degrés puis de 60 degrés revient à
    faire tourner de 90 degrés, autrement dit que
    \( R(60°) \cdot R(30°) = R(90°) \).

    ??? success "Corrigé"
        ```python
        gauche = rotation(np.pi / 3) @ rotation(np.pi / 6)
        droite = rotation(np.pi / 2)
        print(np.allclose(gauche, droite))
        print(np.round(droite, 10))
        ```

        `np.allclose` est le `math.isclose` du TP1, appliqué à un tableau entier : encore
        une fois, on ne compare pas des flottants avec `==`. Le produit de matrices
        **compose** les transformations, et l'ordre compte en général, même si deux
        rotations planes commutent exceptionnellement.

!!! tip "Pour aller plus loin"
    Ajoutez une homothétie \( \begin{pmatrix} 2 & 0 \\ 0 & 2 \end{pmatrix} \) et une
    symétrie par rapport à l'axe des abscisses, puis composez-les avec la rotation dans
    les deux ordres. Vous constaterez que le résultat dépend de l'ordre : le produit
    matriciel n'est pas commutatif, et cela se voit à l'œil sur le dessin.

---

## Entraînement et approfondissement

À faire après la séance, ou en séance si vous avez terminé. Ces exercices sont au programme
de l'évaluation, sauf ceux marqués « pour aller plus loin ». Le pivot de Gauss que vous
avez écrit à l'étape 4 est un outil bien plus général qu'une méthode de résolution : il
donne aussi le déterminant, l'inverse, et, en changeant simplement le type des nombres, une
solution exacte là où les flottants échouaient.

### Étape 7. Le déterminant, gratuitement

Le déterminant d'une matrice triangulaire est le produit de ses coefficients diagonaux. Or
l'élimination de Gauss transforme \( A \) en une matrice triangulaire par des opérations
dont on connaît l'effet sur le déterminant : ajouter à une ligne un multiple d'une autre ne
le change pas, et échanger deux lignes change son signe.

!!! question "Exercice 7.1 : déterminant par Gauss"
    Écrivez `determinant(A)` en reprenant l'élimination de `resoudre`, sans second membre :
    multipliez les pivots successifs, et changez le signe à chaque échange de lignes.
    Comparez à `np.linalg.det`.

    **Résultat attendu :** le déterminant de la matrice de l'étape 1 vaut `-2`, et celui
    de `[[1, 2], [2, 4]]` vaut `0`.

    ??? success "Corrigé"
        ```python
        def determinant(A):
            """Déterminant de A par élimination de Gauss avec pivot partiel."""
            n = len(A)
            M = [list(ligne) for ligne in A]
            det = 1.0
            for k in range(n):
                meilleure = max(range(k, n), key=lambda i: abs(M[i][k]))
                if abs(M[meilleure][k]) < 1e-14:
                    return 0.0
                if meilleure != k:
                    M[k], M[meilleure] = M[meilleure], M[k]
                    det = -det
                det = det * M[k][k]
                for i in range(k + 1, n):
                    facteur = M[i][k] / M[k][k]
                    for j in range(k, n):
                        M[i][j] = M[i][j] - facteur * M[k][j]
            return det

        A = [[1, 2, 2], [1, 3, -2], [3, 5, 8]]
        print(determinant(A), float(np.linalg.det(np.array(A, dtype=float))))
        print(determinant([[1, 2], [2, 4]]))
        ```

        Le coût est celui de l'élimination, de l'ordre de \( n^{3} \) opérations. La
        formule du déterminant que l'on apprend en cours, par développement suivant une
        ligne, coûte \( n! \) opérations : pour \( n = 20 \), c'est deux mille milliards
        de milliards, contre huit mille pour Gauss. Ne développez jamais un déterminant
        au delà de la taille 3, ni à la main ni en machine.

### Étape 8. Le même algorithme, des nombres exacts

À l'étape 5, la matrice de Hilbert de taille 12 a mis `solve` en échec : le problème est
mal conditionné, et aucun algorithme sur des flottants ne peut le résoudre. Mais la cause
est l'arrondi des flottants. Que se passe-t-il si l'on supprime l'arrondi ?

Le module `fractions` du TP1 fournit des rationnels exacts. Et votre fonction `resoudre`
ne fait que des additions, des multiplications et des divisions : elle marche donc, sans
la moindre modification, sur des `Fraction`.

!!! question "Exercice 8.1 : Hilbert vaincue"
    Construisez la matrice de Hilbert de taille 12 avec des `Fraction(1, i + j + 1)`, le
    second membre `b` comme somme des lignes, pour que la solution soit le vecteur de 1,
    puis appelez **votre** fonction `resoudre` de l'étape 4 dessus. Le premier essai échoue
    avec « système singulier ». Comprenez pourquoi avant de lire le corrigé, puis corrigez.

    **Résultat attendu :** exactement `[1, 1, ..., 1]`, douze fois `Fraction(1, 1)`, là
    où `solve` se trompait de 0,7.

    ??? success "Corrigé"
        ```python
        from fractions import Fraction

        def hilbert_exacte(n):
            return [[Fraction(1, i + j + 1) for j in range(n)] for i in range(n)]

        n = 12
        H_exacte = hilbert_exacte(n)
        b_exact = [sum(ligne) for ligne in H_exacte]

        try:
            resoudre(H_exacte, b_exact)
        except ValueError as erreur:
            print("premier essai :", erreur)

        x_exact = resoudre(H_exacte, b_exact, tolerance=0)
        print(x_exact)
        print(all(v == 1 for v in x_exact))
        ```

        Le premier essai échoue parce que le dernier pivot vaut exactement
        \( 1/170\,392\,979\,877\,120 \), soit environ \( 5{,}9 \times 10^{-15} \) :
        un nombre parfaitement non nul, que le seuil de \( 10^{-14} \), conçu pour
        écarter le bruit d'arrondi des flottants, prend pour du bruit. Sur des fractions,
        il n'y a pas de bruit : le seul pivot à refuser est le zéro exact, d'où
        `tolerance=0`. C'est le même algorithme, le même code, et un résultat parfait ;
        seule la notion de « nul » a changé avec le type des nombres.

        Regardez le prix. Les dénominateurs des coefficients atteignent seize chiffres
        pour \( n = 12 \), et une soixantaine pour \( n = 40 \), qui se résout tout de
        même en un dixième de seconde parce que la matrice est petite et très
        structurée. Sur un système de mille inconnues issu de mesures réelles, les
        fractions deviendraient ingérables. Les flottants ne sont pas un défaut de
        conception, ils sont un compromis : rapides et à taille fixe, au prix d'un
        arrondi que l'on doit savoir surveiller.

!!! tip "Pour aller plus loin : l'inverse par Gauss-Jordan"
    L'étape 5 a dit de ne jamais inverser une matrice pour résoudre un système. Il reste
    utile de savoir comment on l'inverse. Accolez l'identité à droite de \( A \), pour
    former \( [A \mid I] \), puis éliminez **au-dessus et au-dessous** de chaque pivot et
    divisez chaque ligne par son pivot : quand la partie gauche est devenue l'identité, la
    partie droite est \( A^{-1} \). Écrivez `inverse(A)` sur ce principe, et vérifiez avec
    `np.allclose(np.array(inverse(A)) @ np.array(A, dtype=float), np.eye(3))`. Pour la
    matrice de l'étape 1, la première ligne de l'inverse est `[-17, 3, 5]`.

### Étape 9. Translations, coordonnées homogènes, et l'ordre des transformations

Une matrice \( 2 \times 2 \) fait tourner, agrandit, réfléchit, mais elle ne peut pas
**déplacer** : elle envoie toujours l'origine sur l'origine. Or déplacer une figure est la
transformation la plus courante en infographie. L'astuce universelle consiste à ajouter une
troisième coordonnée, toujours égale à 1 : le point \( (x, y) \) devient \( (x, y, 1) \), et
la translation de vecteur \( (t_x, t_y) \) devient une matrice \( 3 \times 3 \) :

\[ T(t_x, t_y) = \begin{pmatrix} 1 & 0 & t_x \\ 0 & 1 & t_y \\ 0 & 0 & 1 \end{pmatrix} \]

La rotation s'écrit de même en \( 3 \times 3 \), en complétant par une ligne et une colonne
d'identité. Toutes les transformations du plan deviennent alors des produits de matrices,
et c'est exactement ce que fait votre carte graphique des millions de fois par seconde.

!!! question "Exercice 9.1 : l'ordre compte"
    Écrivez `translation(tx, ty)` et `rotation_h(angle)` qui renvoient des matrices
    \( 3 \times 3 \). Appliquez au point \( (1, 0) \) la translation de \( (3, 1) \) suivie
    de la rotation de 90°, puis la rotation suivie de la translation.

    **Résultat attendu :** \( (-1, 4) \) dans le premier cas, \( (3, 2) \) dans le second.
    Les deux résultats diffèrent.

    ??? success "Corrigé"
        ```python
        def translation(tx, ty):
            return np.array([[1.0, 0.0, tx],
                             [0.0, 1.0, ty],
                             [0.0, 0.0, 1.0]])

        def rotation_h(angle):
            c, s = np.cos(angle), np.sin(angle)
            return np.array([[c, -s, 0.0],
                             [s, c, 0.0],
                             [0.0, 0.0, 1.0]])

        point = np.array([1.0, 0.0, 1.0])
        T = translation(3, 1)
        R = rotation_h(np.pi / 2)

        print(np.round(R @ T @ point, 10))   # translation d'abord, puis rotation
        print(np.round(T @ R @ point, 10))   # rotation d'abord, puis translation
        ```

        Le produit se lit de droite à gauche : `R @ T @ point` applique `T` en premier.
        Déplacer puis tourner autour de l'origine n'est pas tourner puis déplacer, et
        c'est la source de la moitié des bogues d'affichage en jeu vidéo. Pour faire
        tourner une figure autour de son propre centre \( C \), on compose trois
        transformations : amener \( C \) à l'origine, tourner, ramener \( C \) chez lui,
        soit \( T(C)\, R(\theta)\, T(-C) \).

!!! tip "Pour aller plus loin"
    Reprenez la maison de l'étape 6, ajoutez-lui la ligne de 1, et faites-la tourner
    autour de son propre centre, puis autour de l'origine, sur le même tracé. Ajoutez une
    homothétie de rapport 2 centrée sur la porte. Vous aurez écrit en trente lignes le
    cœur d'un moteur de rendu 2D.

---

## Ce qu'il faut retenir

Une matrice se code par une liste de lignes, et attention à `[[0] * q] * n` qui partage la
même ligne. Le produit matriciel coûte \( n^{3} \) opérations, ce qui se mesure. Le pivot
de Gauss élimine puis remonte, et le pivot partiel n'est pas une coquetterie mais une
nécessité numérique ; la même élimination donne le déterminant, et, sur des fractions, une
solution exacte. Pour résoudre un système on écrit `solve`, jamais `inv`, et quand le
conditionnement explose, aucun algorithme sur des flottants ne sauvera un problème mal
posé. Enfin, en coordonnées homogènes, toute transformation du plan est un produit de
matrices, et l'ordre des facteurs compte.

## Auto-évaluation

Avant de passer au TP5, vous devez pouvoir, sans regarder le corrigé :

- [ ] écrire `[[0] * q for _ in range(n)]` et expliquer ce qui cloche dans
  `[[0] * q] * n` ;
- [ ] dire de combien le temps du produit est multiplié quand la taille double, et
  pourquoi ;
- [ ] expliquer en une phrase ce qu'est le pivot partiel et pourquoi il est nécessaire ;
- [ ] distinguer `A @ B` et `A * B` avec numpy ;
- [ ] dire pourquoi on écrit `solve(A, b)` et non `inv(A) @ b` ;
- [ ] expliquer ce que mesure le conditionnement, et ce qu'il signifie quand il approche
  \( 10^{16} \).

[Le QCM du TP4](qcm/qcm_tp4.html){ .md-button target=_blank }
[Passer au TP5](tp5-synthese.md){ .md-button .md-button--primary }
