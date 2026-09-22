# TP1. Ce qu'une matrice sait faire

**Durée : 2 h.**

## Objectifs

- Voir une image comme une matrice, et une matrice comme une somme de couches.
- Calculer une décomposition en valeurs singulières, lire son spectre, et reconstruire la
  matrice tronquée au rang `k`.
- Vérifier sur la machine le théorème qui dit que cette troncature est la **meilleure**
  approximation de rang `k`, et mesurer l'erreur qu'elle coûte.
- Découvrir que la compression de rang faible échoue sur une photographie, et savoir dire
  pourquoi.
- Choisir entre une bibliothèque qui calcule tout et un algorithme qui ne calcule que ce
  dont vous avez besoin, en mesurant les deux.

## Prérequis

Le [TP4 d'outils fondamentaux](../outils-fondamentaux/tp4-matrices-gauss.md) : matrices,
produit matriciel, systèmes linéaires. La notion de vecteur propre, revue dans le
[TP2bis d'IA prédictive](../ia-predictive/tp2bis-reduction-dimension.md), aide mais n'est
pas indispensable : ce TP construit ce dont il a besoin.

Aucune clé d'API, aucun téléchargement. L'image de travail est fournie par matplotlib.

```bash
pip install numpy matplotlib pillow
```

## Ressources

- [Le carnet de ce TP](/lite/notebooks/index.html?path=modelisation-tp1.ipynb){ target=_blank },
  qui s'exécute dans votre navigateur, sans rien installer.
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp1.html){ target=_blank }, à faire après la
  séance.
- Carl Eckart et Gale Young, *The approximation of one matrix by another of lower rank*,
  Psychometrika, 1936 : le théorème que vous allez vérifier expérimentalement.
- La photographie utilisée est celle de Grace Hopper, distribuée avec matplotlib comme
  donnée d'exemple.

---

## Étape 1. Une image est une matrice (20 min)

Une image en niveaux de gris de 600 lignes et 512 colonnes, c'est exactement une matrice
600 × 512 dont chaque coefficient est une intensité entre 0 et 255. Rien de plus.

```python
import matplotlib.cbook as cbook
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

with cbook.get_sample_data("grace_hopper.jpg") as fichier:
    image = Image.open(fichier).convert("L")

A = np.asarray(image, dtype=float)
print("forme :", A.shape)
print("intensités : de", A.min(), "à", A.max())
print("nombre de coefficients :", A.size)
```

```python
plt.imshow(A, cmap="gray")
plt.title("A, une matrice 600 x 512")
plt.axis("off")
plt.show()
```

!!! question "Exercice 1.1 : le rang de la photographie"
    Le rang d'une matrice est le nombre de ses lignes linéairement indépendantes. Une
    matrice de 600 lignes et 512 colonnes a un rang au plus égal à 512. Calculez le rang de
    `A` avec `np.linalg.matrix_rank`, et dites ce que le résultat vous apprend sur la
    possibilité de « résumer » cette image par quelques lignes bien choisies.

    **Résultat attendu :** le rang vaut `512`, c'est-à-dire le maximum possible. Aucune
    colonne de cette image n'est combinaison linéaire exacte des autres.

    ??? success "Corrigé"
        ```python
        print("rang :", np.linalg.matrix_rank(A))
        print("rang maximal possible :", min(A.shape))
        ```

        Le rang est maximal, donc il n'existe **aucune** façon exacte de reconstruire cette
        image à partir de moins de 512 colonnes indépendantes. Si l'histoire s'arrêtait là,
        il n'y aurait rien à compresser. Tout ce TP consiste à remplacer la question
        « peut-on reconstruire exactement ? », dont la réponse est non, par la question
        « peut-on reconstruire presque, et à quel prix ? », dont la réponse est beaucoup
        plus intéressante.

## Étape 2. Décomposer : les valeurs singulières (25 min)

Toute matrice réelle `A` s'écrit `A = U S Vᵀ`, où `U` et `V` ont des colonnes orthonormées
et où `S` est diagonale à coefficients positifs décroissants, les **valeurs singulières**.
Autrement dit, `A` est une somme de couches de rang 1, chacune pondérée par sa valeur
singulière :

\[ A = \sum_{i} \sigma_i \, u_i v_i^{\top} \]

```python
U, S, Vt = np.linalg.svd(A, full_matrices=False)
print("U :", U.shape, " S :", S.shape, " Vt :", Vt.shape)
print("cinq plus grandes valeurs singulières :", S[:5].round(1))
print("cinq plus petites :", S[-5:].round(2))
```

Attention à la forme de ce que renvoie numpy : la troisième valeur de retour est `Vᵀ`, déjà
transposée, et non `V`. C'est la source d'erreur numéro un sur cette fonction, et vous la
retrouverez à l'étape 3.

!!! warning "Vos valeurs singulières ne seront pas exactement les miennes"
    Les valeurs brutes affichées ci-dessus dépendent du décodeur JPEG, qui n'est pas le
    même dans votre navigateur et sur une machine de bureau : la photographie décodée y
    diffère de quelques dizaines d'unités d'intensité sur 307 200 pixels, et la première
    valeur singulière change à la première décimale. En revanche, **toutes les quantités
    relatives de ce TP coïncident sur quatre décimales** : fractions d'énergie, erreurs
    relatives, seuils de rang. C'est une raison de plus de raisonner en relatif, comme vous
    l'avez appris en première année sur les flottants.

```python
plt.semilogy(S)
plt.xlabel("indice de la valeur singulière")
plt.ylabel("valeur singulière (échelle logarithmique)")
plt.title("Le spectre décroît de quatre ordres de grandeur")
plt.show()
```

!!! question "Exercice 2.1 : où est l'information ?"
    L'« énergie » d'une matrice est la somme des carrés de ses valeurs singulières. Quelle
    fraction de l'énergie totale les dix plus grandes valeurs singulières portent-elles ?
    Et les cinquante plus grandes ?

    **Résultat attendu :** environ `0.9297` pour les dix premières, soit près de 93 %, et
    `0.9881` pour les cinquante premières, soit plus de 98 %. Dix couches sur cinq cent
    douze portent l'essentiel de l'image.

    ??? success "Corrigé"
        ```python
        energie = np.sum(S ** 2)
        for k in [1, 10, 50]:
            print(f"{k:3d} premières : {np.sum(S[:k] ** 2) / energie:.4f}")
        ```

        La première valeur singulière vaut à elle seule près de quatre fois la deuxième :
        elle porte surtout la luminosité moyenne de l'image, qui est la même partout. C'est ce déséquilibre massif entre les premières et les dernières valeurs
        singulières qui rend la suite possible. Une matrice dont toutes les valeurs
        singulières seraient égales, comme une matrice de bruit pur, n'aurait rien à céder.

## Étape 3. Reconstruire au rang k (25 min)

Garder les `k` plus grandes couches et jeter les autres donne une matrice de rang `k` :

```python
def reconstruire(k):
    return U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]

figure, axes = plt.subplots(1, 4, figsize=(12, 4))
for ax, k in zip(axes, [1, 5, 20, 100]):
    ax.imshow(reconstruire(k), cmap="gray")
    ax.set_title(f"k = {k}")
    ax.axis("off")
plt.show()
```

Le théorème d'Eckart-Young dit que cette troncature n'est pas seulement *une* approximation
de rang `k` : c'est **la meilleure**, au sens de la norme de Frobenius. Et il donne l'erreur
exacte, sans qu'il soit besoin de reconstruire quoi que ce soit : c'est la racine de la
somme des carrés des valeurs singulières jetées.

!!! question "Exercice 3.1 : vérifier le théorème plutôt que le croire"
    Pour `k` valant 1, 5, 10, 20, 50, 100 et 200, calculez l'erreur relative
    `‖A − A_k‖_F / ‖A‖_F` de deux façons : en reconstruisant réellement `A_k`, et par la
    formule théorique qui n'utilise que les valeurs singulières jetées. Comparez.

    **Résultat attendu :** les deux colonnes coïncident sur les quatre décimales, pour tous
    les `k`. L'erreur relative vaut `0.5185` à k = 1, `0.2651` à k = 10, `0.1090` à k = 50
    et `0.0267` à k = 200.

    ??? success "Corrigé"
        ```python
        norme = np.linalg.norm(A, "fro")
        for k in [1, 5, 10, 20, 50, 100, 200]:
            mesuree = np.linalg.norm(A - reconstruire(k), "fro") / norme
            theorique = np.sqrt(np.sum(S[k:] ** 2)) / norme
            print(f"k={k:4d}  mesurée {mesuree:.4f}   théorique {theorique:.4f}")
        ```

        L'égalité n'est pas une coïncidence numérique : les couches sont orthogonales entre
        elles, donc l'erreur commise en jetant les dernières se lit directement dans leurs
        valeurs singulières. L'intérêt pratique est considérable : vous pouvez décider du
        `k` acceptable **avant** de reconstruire quoi que ce soit, en lisant le seul
        vecteur `S`.

!!! tip "L'IA vous le donne en trois secondes"
    Demandez à un assistant conversationnel un code de compression d'image par SVD. Il y a
    de bonnes chances qu'il écrive la reconstruction avec `V` plutôt que `Vᵀ`, sous une
    forme comme `U[:, :k] @ np.diag(S[:k]) @ Vt.T[:20, :]`. Ici, `A` est rectangulaire mais
    `Vt` est carrée : **la forme du résultat reste correcte, aucune exception n'est levée**,
    et l'image produite ressemble vaguement à quelque chose. Mesurez l'erreur relative de
    cette version : elle dépasse `1.4` contre `0.1919` pour la bonne, c'est-à-dire que la
    reconstruction est plus éloignée de l'image que ne le serait une matrice de zéros.
    Vérifiez-le, et retenez la leçon générale : un code qui ne lève pas d'exception n'est
    pas un code qui a raison, et seule une métrique le dit.

    ```python
    faux = U[:, :20] @ np.diag(S[:20]) @ Vt.T[:20, :]
    bon = reconstruire(20)
    print("mêmes formes :", faux.shape == bon.shape)
    print(f"erreur du faux : {np.linalg.norm(A - faux, 'fro') / np.linalg.norm(A, 'fro'):.4f}")
    print(f"erreur du bon  : {np.linalg.norm(A - bon, 'fro') / np.linalg.norm(A, 'fro'):.4f}")
    ```

## Étape 4. La compression qui n'en est pas une (20 min)

Stocker `A_k` ne veut pas dire stocker les 307 200 coefficients d'une matrice 600 × 512 :
il suffit de garder `k` colonnes de `U`, `k` valeurs singulières et `k` lignes de `Vᵀ`, soit
`k × (600 + 512 + 1)` nombres. Le gain n'existe donc que si ce total reste inférieur à
307 200.

```python
m, n = A.shape
print("coefficients de A :", m * n)
for k in [10, 50, 100, 200, 300]:
    stockes = k * (m + n + 1)
    print(f"k={k:4d}  stockés = {stockes:7d}  ratio = {stockes / (m * n):.2f}")
```

!!! question "Exercice 4.1 : jusqu'où peut-on aller, et est-ce que cela suffit ?"
    Deux questions qui doivent se poser ensemble. D'abord, à partir de quel `k` la
    « compression » stocke-t-elle plus que l'image d'origine ? Ensuite, quel `k` faut-il
    pour descendre sous 10 %, 5 % puis 1 % d'erreur relative ? Concluez.

    **Résultat attendu :** le seuil est `k = 276`. Or il faut `k = 57` pour passer sous
    10 % d'erreur (ratio de stockage `0.21`), `k = 125` pour passer sous 5 % (ratio `0.45`)
    et `k = 307` pour passer sous 1 %, ce qui correspond à un ratio de `1.11`. **Atteindre
    1 % d'erreur sur cette photographie par troncature de rang coûte donc plus cher que de
    stocker l'image entière.**

    ??? success "Corrigé"
        ```python
        seuil = (m * n) / (m + n + 1)
        print(f"k* = {seuil:.1f}")

        erreurs = np.sqrt(np.cumsum(S[::-1] ** 2)[::-1]) / norme
        for cible in [0.10, 0.05, 0.01]:
            k = int(np.argmax(erreurs < cible))
            print(f"erreur < {cible:.0%} dès k = {k:3d}  "
                  f"(erreur {erreurs[k]:.4f}, stockage {k * (m + n + 1) / (m * n):.2f})")
        ```

        C'est le résultat le plus important de la séance, et il est négatif : **la
        troncature de rang n'est pas un bon compresseur d'images photographiques.** Une
        photographie n'est pas de rang faible, son spectre décroît trop lentement. JPEG ne
        procède d'ailleurs pas ainsi : il découpe l'image en blocs de 8 × 8 et travaille
        dans une base fixe de cosinus, ce qui est une tout autre stratégie.

        Alors pourquoi apprendre ceci ? Parce que la troncature de rang est excellente sur
        les matrices qui, elles, **sont** de rang presque faible : matrices de préférences
        utilisateurs, matrices de cooccurrences de mots, matrices de poids d'un réseau de
        neurones. L'étape 6 y revient. Savoir qu'une méthode échoue sur une classe d'objets
        fait partie de savoir la choisir.

## Étape 5. Le rang effectif, quand il y a du bruit (15 min)

Fabriquons une matrice de rang 3 exact, puis ajoutons-lui un bruit faible :

```python
generateur = np.random.default_rng(0)
B = generateur.normal(size=(200, 3)) @ generateur.normal(size=(3, 150))
bruit = generateur.normal(scale=0.5, size=(200, 150))

for nom, M in [("sans bruit", B), ("avec bruit", B + bruit)]:
    s = np.linalg.svd(M, compute_uv=False)
    print(f"{nom:11s} : six premières {s[:6].round(2)}  rang calculé {np.linalg.matrix_rank(M)}")
```

!!! question "Exercice 5.1 : le rang ment, le spectre non"
    Le rang calculé par numpy passe de 3 à 150 quand on ajoute un bruit d'écart-type 0,5,
    alors que la structure sous-jacente n'a pas changé. Que montre le spectre, lui ?

    **Résultat attendu :** les trois premières valeurs singulières restent aux alentours de
    `177`, `165` et `139`, presque inchangées, et toutes les suivantes s'écrasent autour de
    `12,5`. Il y a un décrochement net entre la troisième et la quatrième, alors que le
    rang calculé, lui, vaut 150.

    ??? success "Corrigé"
        ```python
        s_bruit = np.linalg.svd(B + bruit, compute_uv=False)
        print("rapport entre valeurs consécutives :", (s_bruit[:6] / s_bruit[1:7]).round(2))
        ```

        Le rapport entre la troisième valeur singulière et la quatrième vaut `10.86`, quand
        tous les autres rapports consécutifs valent entre `1.0` et `1.2` : le décrochement
        n'a pas besoin d'être jugé à l'œil, il se lit dans un tableau de nombres.

        Le rang au sens algébrique est une notion binaire, et donc fragile : la moindre
        perturbation le fait sauter au maximum. Le spectre, lui, est une notion continue,
        et il montre où est la structure. C'est ce qu'on appelle le **rang effectif**, et
        c'est cette quantité, pas le rang, qui gouverne ce que vous pourrez comprimer,
        débruiter ou factoriser. Un jeu de données réel n'a jamais un rang faible ; il a
        souvent un rang effectif faible.

## Étape 6. Choisir sa méthode, et mesurer (20 min)

`np.linalg.svd` calcule **toutes** les valeurs singulières et tous les vecteurs. Si vous
n'avez besoin que de la plus grande, il existe bien plus économique : la méthode de la
puissance itérée, qui multiplie un vecteur au hasard par `AᵀA` jusqu'à ce qu'il s'aligne sur
la direction dominante.

```python
import time

def puissance_iteree(M, iterations=100, graine=0):
    rng = np.random.default_rng(graine)
    v = rng.normal(size=M.shape[1])
    v /= np.linalg.norm(v)
    for _ in range(iterations):
        v = M.T @ (M @ v)
        v /= np.linalg.norm(v)
    return np.linalg.norm(M @ v)

debut = time.perf_counter()
np.linalg.svd(A, full_matrices=False)
temps_svd = time.perf_counter() - debut

debut = time.perf_counter()
sigma1 = puissance_iteree(A)
temps_puissance = time.perf_counter() - debut

print(f"svd complet      : {temps_svd * 1000:.0f} ms")
print(f"puissance itérée : {temps_puissance * 1000:.0f} ms")
print(f"σ₁ exact {S[0]:.4f} | σ₁ par puissance itérée {sigma1:.4f}")
```

!!! question "Exercice 6.1 : combien d'itérations faut-il vraiment ?"
    Faites varier `iterations` entre 1 et 50 et mesurez l'écart relatif à la vraie valeur
    `S[0]`. À partir de combien d'itérations l'écart devient-il négligeable devant la
    précision des flottants ?

    **Résultat attendu :** une seule itération donne déjà un écart relatif de l'ordre de
    `4e-03`, cinq itérations descendent vers `1e-12`, et dès dix itérations l'écart est de
    l'ordre de `1e-16`, c'est-à-dire la précision machine. Les quatre-vingt-dix itérations
    suivantes n'apportent rien.

    ??? success "Corrigé"
        ```python
        for iterations in [1, 5, 10, 50]:
            estimation = puissance_iteree(A, iterations=iterations)
            print(f"{iterations:3d} itérations : écart relatif {abs(estimation - S[0]) / S[0]:.1e}")
        ```

        La puissance itérée est de l'ordre de cinq à dix fois plus rapide que la
        décomposition complète, et ce rapport varie d'une machine à l'autre et d'une
        exécution à l'autre : c'est l'ordre de grandeur qui compte, jamais le chiffre que
        vous lirez. Le point à retenir est ailleurs. Vous venez de
        choisir entre deux méthodes selon ce dont vous aviez besoin, et non selon celle que
        vous connaissiez : c'est exactement la compétence que cette ressource vise.

!!! question "Exercice 6.2 : une couche de réseau de neurones"
    Une couche dense qui transforme un vecteur de 768 nombres en un vecteur de 768 nombres
    est une matrice 768 × 768. Combien de paramètres compte-t-elle ? Combien en
    compterait-elle si on l'écrivait comme un produit de deux matrices de rang 8 ? Quel
    ratio ?

    **Résultat attendu :** `589 824` paramètres pleins, `12 288` en rang 8, soit un ratio de
    `0.0208`, c'est-à-dire environ 2 %.

    ??? success "Corrigé"
        ```python
        entree, sortie, rang = 768, 768, 8
        plein = entree * sortie
        factorise = rang * (entree + sortie)
        print(f"plein {plein} | rang {rang} : {factorise} | ratio {factorise / plein:.4f}")
        ```

        C'est le principe des méthodes d'adaptation de rang faible qui permettent de
        spécialiser un grand modèle de langue en n'entraînant qu'une poignée de paramètres.
        La justification est celle de l'étape 5 : la **modification** qu'on applique aux
        poids d'un modèle déjà entraîné a un rang effectif faible, même si les poids
        eux-mêmes n'en ont pas. Rien de plus que ce que vous venez de faire sur une
        photographie, appliqué à une matrice dont la structure s'y prête, elle.

## Ce qu'il faut retenir

Une matrice est une somme de couches de rang 1, et les valeurs singulières disent
exactement ce que chaque couche apporte. Tronquer donne la meilleure approximation de rang
`k` possible, et l'erreur se lit dans les valeurs singulières jetées sans rien reconstruire.
Mais la question « est-ce que ça comprime ? » ne se répond pas par « le spectre décroît » :
il faut compter ce qu'on stocke, et sur une photographie le compte est perdant dès qu'on
exige de la fidélité. Enfin, le rang algébrique est fragile et le rang effectif ne l'est
pas ; c'est le second qui gouverne tout.

## Auto-évaluation

- [ ] Je sais dire ce que contiennent `U`, `S` et `Vt`, et pourquoi la troisième valeur de
      retour est déjà transposée.
- [ ] Je sais reconstruire une matrice au rang `k` et calculer son erreur relative.
- [ ] Je sais prédire cette erreur sans reconstruire, à partir du seul vecteur `S`.
- [ ] Je sais calculer le seuil au-delà duquel une troncature de rang ne comprime plus.
- [ ] Je sais expliquer pourquoi une photographie se comprime mal ainsi, et quelles
      matrices s'y prêtent.
- [ ] Je sais distinguer le rang d'une matrice de son rang effectif.
- [ ] Je sais choisir entre une décomposition complète et une méthode itérative, et
      justifier ce choix par une mesure.

[Le QCM du TP1](qcm/qcm_tp1.html){ .md-button target=_blank }
[Passer au TP2](tp2-marche-aleatoire.md){ .md-button .md-button--primary }
