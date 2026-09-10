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
        def resoudre(A, b):
            """Résout A x = b par le pivot de Gauss avec pivot partiel.

            A est une liste de lignes, b une liste. Ni A ni b ne sont modifiés.
            """
            n = len(A)
            # copie de travail, matrice augmentée [A | b]
            M = [list(A[i]) + [b[i]] for i in range(n)]

            for k in range(n):
                # pivot partiel : la ligne dont le coefficient est le plus grand en valeur absolue
                meilleure = max(range(k, n), key=lambda i: abs(M[i][k]))
                if abs(M[meilleure][k]) < 1e-14:
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

## Ce qu'il faut retenir

Une matrice se code par une liste de lignes, et attention à `[[0] * q] * n` qui partage la
même ligne. Le produit matriciel coûte \( n^{3} \) opérations, ce qui se mesure. Le pivot
de Gauss élimine puis remonte, et le pivot partiel n'est pas une coquetterie mais une
nécessité numérique. Enfin, pour résoudre un système on écrit `solve`, jamais `inv`, et
quand le conditionnement explose, aucun algorithme ne sauvera un problème mal posé.

[Passer au TP5](tp5-synthese.md){ .md-button .md-button--primary }
