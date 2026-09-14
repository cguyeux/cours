# Mémento Python

Tout ce qui est nécessaire aux cinq TP, sur une seule page. C'est le seul document
autorisé pendant les évaluations : prenez l'habitude de le consulter plutôt que de chercher
ailleurs, vous saurez ainsi où trouver l'information le jour où cela compte.

## Les types de base

| Type | Exemple | À savoir |
|---|---|---|
| `int` | `42`, `2 ** 200` | exact, sans limite de taille |
| `float` | `3.14`, `1e-9` | approché, environ 15 chiffres significatifs |
| `bool` | `True`, `False` | résultat d'une comparaison |
| `str` | `"bonjour"` | texte, entre guillemets simples ou doubles |
| `list` | `[1, 2, 3]` | suite modifiable, indices à partir de 0 |

```python
type(42), type(3.14), type("a"), type([1, 2])
int("17") + 1        # texte vers entier
float("2.5")         # texte vers flottant
str(17) + " ans"     # nombre vers texte
```

## Opérateurs

| Opérateur | Sens | Exemple |
|---|---|---|
| `+` `-` `*` | somme, différence, produit | `7 * 6` donne `42` |
| `/` | division, toujours un flottant | `10 / 5` donne `2.0` |
| `//` | quotient entier | `17 // 5` donne `3` |
| `%` | reste | `17 % 5` donne `2` |
| `**` | puissance | `2 ** 10` donne `1024` |
| `==` `!=` | égal, différent | jamais entre deux flottants |
| `<` `<=` `>` `>=` | comparaisons | `2 <= x < 10` s'écrit tel quel |
| `and` `or` `not` | et, ou, non | `x > 0 and x < 10` |

## Conditions

```python
n = 17

if n % 2 == 0:
    print("pair")
elif n % 3 == 0:
    print("multiple de 3")
else:
    print("autre")
```

Les deux points terminent la ligne, et le bloc est délimité par l'indentation, quatre
espaces par niveau.

## Boucles

```python
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 11, 2):   # 2, 4, 6, 8, 10 : début, fin exclue, pas
    print(i)

for lettre in "python":     # parcourt les caractères
    print(lettre)

for x in [3, 5, 7]:         # parcourt une liste
    print(x)

n = 1
while n * n < 1000:         # tant que la condition est vraie
    n = n + 1
```

`break` sort de la boucle immédiatement, `continue` passe au tour suivant.

## Fonctions

```python
def aire_rectangle(largeur, hauteur=1):
    """Aire d'un rectangle. La hauteur vaut 1 par défaut."""
    return largeur * hauteur

aire_rectangle(3, 4)        # 12
aire_rectangle(3)           # 3, la valeur par défaut s'applique
aire_rectangle(hauteur=4, largeur=3)   # nommer les arguments, dans n'importe quel ordre
```

`return` renvoie une valeur et termine la fonction ; `print` se contente d'afficher. Une
fonction sans `return` renvoie `None`.

Pour refuser une entrée invalide :

```python
def racine(x):
    if x < 0:
        raise ValueError("x doit etre positif")
    return x ** 0.5
```

## Listes

```python
L = [4, 8, 15, 16, 23, 42]

L[0]          # 4, premier élément
L[-1]         # 42, dernier élément
L[1:3]        # [8, 15], du rang 1 inclus au rang 3 exclu
len(L)        # 6
L.append(99)  # ajoute à la fin
L[2] = 0      # modifie en place
15 in L       # True
sum(L), min(L), max(L), sorted(L)
```

Construire une liste par compréhension, notation très employée :

```python
carres = [x * x for x in range(10)]
pairs = [x for x in L if x % 2 == 0]
```

!!! danger "Le piège de la liste de listes"
    `[[0] * 3] * 2` crée **deux références vers la même ligne** : modifier l'une modifie
    l'autre. Pour une matrice, écrire `[[0] * 3 for _ in range(2)]`.

## Tuples, et l'affectation simultanée

```python
point = (3, 4)          # comme une liste, mais non modifiable
x, y = point            # déballage : x vaut 3, y vaut 4
a, b = 1071, 462
a, b = b, a % b         # échange et mise à jour en une seule ligne (Euclide)
for i, valeur in enumerate([10, 20, 30]):   # indice et valeur à la fois
    print(i, valeur)
for u, v in zip([1, 2, 3], [4, 5, 6]):      # deux listes parcourues ensemble
    print(u * v)
```

`a, b = b, a % b` évalue **d'abord** tout le membre de droite, puis affecte : c'est ce qui
rend l'échange possible sans variable temporaire.

## Dictionnaires et comptage

```python
ages = {"Alice": 20, "Bob": 22}
ages["Chloé"] = 19          # ajoute ou remplace
ages["Alice"]               # 20
"Bob" in ages               # True
ages.get("Zoé", 0)          # 0 : valeur par défaut si la clé manque
for nom, age in ages.items():
    print(nom, age)

from collections import Counter
comptes = Counter("ABRACADABRA")
comptes["A"]                # 5
comptes.most_common(2)      # [('A', 5), ('B', 2)]
```

Un dictionnaire sert aussi de mémoire pour ne pas recalculer ce qu'on a déjà obtenu :
`if n in deja: return deja[n]`.

## Chaînes de caractères

```python
s = "Bonjour"
s.upper(), s.lower()
s[0], s[-1], len(s)
"jour" in s
s.replace("Bon", "Beau")
"a,b,c".split(",")          # ['a', 'b', 'c']
"".join(["a", "b", "c"])    # 'abc'
ord("A"), chr(65)           # 65, 'A'
f"{s} : {len(s)} lettres"   # chaîne formatée
f"{3.14159:.2f}"            # '3.14', deux décimales
```

## Attraper une erreur

```python
try:
    x = int("abc")
except ValueError as erreur:
    print("entree invalide :", erreur)
```

À réserver aux erreurs que l'on sait traiter. Ne jamais écrire `except:` sans préciser
le type : on masquerait aussi les bogues.

## Fonctions anonymes et argument `key`

```python
L = [(3, "c"), (1, "a"), (2, "b")]
sorted(L, key=lambda couple: couple[1])   # trie selon la lettre
max(range(5), key=lambda i: abs(i - 2.6)) # l'indice qui maximise la distance à 2,6
```

`lambda` définit une fonction d'une ligne, sans nom, là où un `def` serait lourd. Le
pivot partiel du TP4 s'en sert pour choisir la ligne du plus grand coefficient.

## Calcul exact : `fractions`

```python
from fractions import Fraction

Fraction(1, 3) + Fraction(1, 6)     # Fraction(1, 2), exact
Fraction(0.1)                       # la vraie valeur du flottant 0.1
float(Fraction(22, 7))              # retour au flottant
```

Lent, mais sans aucun arrondi : pour vérifier un résultat, ou résoudre exactement un petit
système (TP4).

## Le module `math`

```python
import math

x, a, b = 1.0, 0.1 + 0.2, 0.3

math.sqrt(2)        # racine carrée
math.pi, math.e
math.cos(x), math.sin(x), math.exp(x), math.log(x)
math.floor(2.7), math.ceil(2.1)   # 2, 3
math.gcd(12, 18)    # 6, le PGCD
math.isclose(a, b)  # comparaison correcte de deux flottants
abs(-3), round(2.675, 2)
```

## Mesurer un temps

```python
import time

debut = time.perf_counter()
resultat = sum(range(100000))
duree = time.perf_counter() - debut
print(f"{duree:.4f} s")
```

## Le hasard : `random`

```python
import random

random.seed(42)             # rend les tirages reproductibles
random.random()             # flottant dans [0, 1[
random.randint(1, 6)        # entier entre 1 et 6 inclus
random.uniform(-1, 1)       # flottant dans [-1, 1]
random.choice("ABC")        # un élément au hasard
```

Toujours fixer `seed` dans un programme que l'on veut pouvoir rejouer à l'identique.

## Formater un nombre

| Écriture | Résultat | Sens |
|---|---|---|
| `f"{x:.3f}"` | `3.142` | trois décimales |
| `f"{x:.2e}"` | `3.14e+00` | notation scientifique |
| `f"{n:>6}"` | `    42` | aligné à droite sur six caractères |
| `f"{n:06}"` | `000042` | complété par des zéros |
| `f"{n:_}"` | `1_000_000` | séparateur de milliers |

## numpy, l'essentiel

```python
import numpy as np

A = np.array([[1.0, 2.0], [3.0, 4.0]])
b = np.array([5.0, 11.0])

A.shape             # (2, 2)
A.T                 # transposée
A @ A               # produit matriciel
A * A               # produit terme à terme, ce n'est PAS le produit matriciel
np.linalg.solve(A, b)   # résout A x = b : la bonne méthode
np.linalg.det(A), np.linalg.cond(A)
np.zeros((3, 3)), np.ones(4), np.eye(3)     # nulle, unités, identité
np.allclose(A, A)   # comparaison de tableaux à la tolérance près
```

!!! warning "Ne jamais écrire `np.linalg.inv(A) @ b`"
    Toujours `np.linalg.solve(A, b)` : plus rapide et plus précis. Voir le TP4.

## matplotlib, l'essentiel

```python
import matplotlib.pyplot as plt

xs = [i / 100 for i in range(-300, 301)]
ys = [x * x for x in xs]

plt.figure()
plt.plot(xs, ys, label="x au carre")
plt.scatter([0], [0])          # des points isolés
plt.axhline(0, linewidth=0.8)  # l'axe des abscisses
plt.xlabel("x")
plt.ylabel("y")
plt.title("Un titre")
plt.legend()
plt.axis("equal")              # même échelle sur les deux axes
plt.show()
```

## Lire une erreur

| Message | Cause la plus fréquente |
|---|---|
| `SyntaxError` | parenthèse ou deux-points manquant |
| `IndentationError` | alignement incohérent |
| `NameError` | nom inconnu : faute de frappe, ou cellule non exécutée |
| `TypeError` | types incompatibles, par exemple `"3" + 1` |
| `IndexError` | indice hors de la liste |
| `ZeroDivisionError` | division par zéro |
| `ValueError` | valeur du bon type mais impossible, par exemple `int("abc")` |

Lisez toujours la **dernière** ligne en premier, elle donne la nature de l'erreur, puis
remontez pour trouver la ligne fautive.

## Les cinq réflexes du module

1. Ne jamais comparer deux flottants avec `==` ; utiliser `math.isclose` ou une tolérance.
2. Vérifier un résultat par une propriété, pas en relisant son code.
3. Essayer les cas limites : `0`, `1`, un négatif, une liste vide.
4. Mesurer un temps plutôt que de supposer un coût.
5. Refuser explicitement une entrée invalide plutôt que de renvoyer un résultat faux.
