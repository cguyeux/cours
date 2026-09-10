# TP1. Calcul numérique

**Durée : 1 h 45.**

## Objectifs

- Manipuler les deux familles de nombres de Python, les entiers et les flottants, et savoir
  laquelle ment.
- Écrire une boucle, une condition et une fonction.
- Comparer deux nombres à virgule correctement, ce que presque personne ne fait la première
  fois.

## Prérequis

La [mise en route](demarrage.md) : savoir exécuter une cellule et lire une erreur.

## Ressources

- Le [mémento Python](memento.md), à garder ouvert dans un autre onglet.
- [Le carnet de ce TP](/lite/notebooks/index.html?path=tp1.ipynb){ target=_blank }, où les
  énoncés sont déjà écrits.

---

## Étape 1. Les entiers (20 min)

Un entier en Python n'a pas de taille maximale. Ce n'est pas le cas dans la plupart des
langages, où un entier tient sur 32 ou 64 bits et déborde silencieusement au delà. Essayez :

```python
2 ** 10
```

```python
print(2 ** 200)
```

Le second nombre a soixante et un chiffres, et Python le calcule exactement. Retenez-le :
en Python, un calcul sur des entiers est **exact**, quelle que soit sa taille.

Les opérateurs sur les entiers :

| Opérateur | Sens | Exemple |
|---|---|---|
| `+` `-` `*` | somme, différence, produit | `7 * 6` vaut `42` |
| `**` | puissance | `2 ** 10` vaut `1024` |
| `//` | quotient de la division entière | `17 // 5` vaut `3` |
| `%` | reste de la division entière | `17 % 5` vaut `2` |
| `/` | division, **résultat à virgule** | `17 / 5` vaut `3.4` |

La distinction entre `/` et `//` est la source d'erreur numéro un des débutants, d'autant
qu'elle a changé entre Python 2 et Python 3 : beaucoup de code trouvé en ligne suppose
encore que `/` entre deux entiers donne un entier. Ici, `17 / 5` vaut `3.4`, et `17 / 5`
n'est pas un entier même quand la division tombe juste : `10 / 5` vaut `2.0`, pas `2`.

!!! question "Exercice 1.1 : division euclidienne"
    Faites afficher le quotient et le reste de la division de 2026 par 7, en une cellule.

    **Résultat attendu :** quotient `289`, reste `3`. Vérifiez que
    `289 * 7 + 3` redonne bien `2026`.

    ??? success "Corrigé"
        ```python
        n = 2026
        d = 7
        quotient = n // d
        reste = n % d
        print(quotient, reste)
        print(quotient * d + reste == n)
        ```

        La dernière ligne affiche `True`. C'est la propriété qui définit la division
        euclidienne, et c'est une bonne habitude de vérifier une propriété plutôt que de
        regarder si le résultat « a l'air correct ».

!!! question "Exercice 1.2 : dernier chiffre"
    Écrivez le calcul qui donne le dernier chiffre de 123456789, puis celui qui donne le
    nombre obtenu en enlevant ce dernier chiffre.

    **Résultat attendu :** `9`, puis `12345678`.

    ??? success "Corrigé"
        ```python
        n = 123456789
        print(n % 10)
        print(n // 10)
        ```

        Le reste par 10 donne le chiffre des unités, le quotient par 10 « décale » le
        nombre d'un cran. Ces deux opérations reviendront au TP2 pour décomposer un
        nombre, et elles sont au cœur de tout ce qui touche à la représentation des
        nombres en machine.

---

## Étape 2. Les nombres à virgule mentent (25 min)

Exécutez ceci, et regardez bien :

```python
0.1 + 0.2
```

Vous obtenez `0.30000000000000004`. Ce n'est pas un bug de Python : c'est vrai dans tous les
langages, sur tous les processeurs, depuis quarante ans. La raison est simple. Votre
machine écrit les nombres en base 2, et `0.1` en base 2 est un développement infini, exactement
comme `1/3` en base 10 s'écrit `0,333...` sans jamais s'arrêter. La machine coupe donc quelque
part, et la petite erreur commise se propage.

La conséquence pratique est immédiate et sérieuse :

```python
0.1 + 0.2 == 0.3
```

Ceci vaut `False`. Une comparaison d'égalité entre deux nombres à virgule est presque
toujours une erreur de programmation.

### Comment comparer, alors

On ne demande pas si deux flottants sont égaux, on demande s'ils sont **assez proches** :

```python
import math

a = 0.1 + 0.2
b = 0.3
print(abs(a - b) < 1e-9)
print(math.isclose(a, b))
```

Les deux lignes affichent `True`. La première compare l'écart à un seuil que vous choisissez,
la seconde utilise `math.isclose`, qui fait la même chose en tenant compte de l'ordre de
grandeur des nombres. Préférez `math.isclose` : comparer à `1e-9` n'a pas le même sens
selon qu'on manipule des millimètres ou des distances entre galaxies.

!!! question "Exercice 2.1 : l'erreur qui s'accumule"
    Ajoutez `0.1` à lui-même mille fois dans une boucle, en partant de `0`. Affichez le
    résultat, puis l'écart avec `100`.

    **Résultat attendu :** un nombre très proche de `100` mais pas égal, et un écart de
    l'ordre de `10⁻¹²`.

    ??? success "Corrigé"
        ```python
        total = 0.0
        for _ in range(1000):
            total = total + 0.1
        print(total)
        print(total - 100)
        ```

        L'écart est minuscule, mais il n'est pas nul, et il grandit avec le nombre
        d'additions. C'est pour cette raison qu'un logiciel bancaire ne stocke jamais des
        euros dans des flottants : il compte en centimes, avec des entiers, qui eux sont
        exacts.

!!! question "Exercice 2.2 : la fonction de comparaison"
    Écrivez une fonction `presque_egaux(a, b)` qui renvoie `True` quand deux nombres sont
    égaux à une tolérance près, et testez-la sur `0.1 + 0.2` et `0.3`.

    **Résultat attendu :** `True`, alors que `==` donnait `False`.

    ??? success "Corrigé"
        ```python
        def presque_egaux(a, b, tolerance=1e-9):
            """Dit si a et b sont égaux à la tolérance près."""
            return abs(a - b) <= tolerance

        print(presque_egaux(0.1 + 0.2, 0.3))
        print(presque_egaux(1.0, 1.5))
        ```

        Le paramètre `tolerance` a une valeur par défaut : on peut appeler la fonction
        avec deux arguments seulement, ou en imposer une troisième si le contexte le
        demande.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à l'assistant de votre choix : « écris une fonction Python qui teste si deux
    nombres décimaux sont égaux ». Regardez sa réponse. Si elle contient `a == b`, vous
    venez de trouver le piège. Si elle contient une tolérance, demandez-lui pourquoi une
    tolérance fixe de `1e-9` est mal choisie pour comparer deux nombres de l'ordre de
    `1e20`, et jugez sa réponse. Notez ce que vous en retenez.

---

## Étape 3. Conditions et boucles (25 min)

Une condition choisit entre plusieurs chemins :

```python
n = 17

if n % 2 == 0:
    print("pair")
else:
    print("impair")
```

Les deux points en fin de ligne et l'indentation ne sont pas décoratifs : en Python, c'est
l'alignement qui délimite les blocs, là où d'autres langages emploient des accolades. Quatre
espaces, toujours les mêmes.

Une boucle `for` répète un traitement pour chaque valeur d'une suite. `range(a, b)` produit
les entiers de `a` inclus à `b` **exclu**, ce qui surprend une fois puis devient naturel :

```python
for i in range(1, 6):
    print(i, i * i)
```

Une boucle `while` répète tant qu'une condition reste vraie. Elle sert quand on ne sait pas
d'avance combien de tours seront nécessaires :

```python
n = 1
while n * n < 1000:
    n = n + 1
print(n)
```

!!! question "Exercice 3.1 : la table de sept"
    Affichez la table de multiplication de 7, de `7 x 1` à `7 x 10`, une ligne par produit,
    sous la forme `7 x 3 = 21`.

    **Résultat attendu :** dix lignes, la dernière étant `7 x 10 = 70`.

    ??? success "Corrigé"
        ```python
        for i in range(1, 11):
            print(7, "x", i, "=", 7 * i)
        ```

        On peut aussi construire la ligne avec une chaîne formatée, notation que vous
        retrouverez partout :

        ```python
        for i in range(1, 11):
            print(f"7 x {i} = {7 * i}")
        ```

!!! question "Exercice 3.2 : une somme et sa formule"
    Calculez la somme des entiers de 1 à 100 avec une boucle. Comparez au résultat de la
    formule \( \frac{n(n+1)}{2} \).

    **Résultat attendu :** `5050` des deux côtés.

    ??? success "Corrigé"
        ```python
        n = 100
        total = 0
        for i in range(1, n + 1):
            total = total + i
        print(total)
        print(n * (n + 1) // 2)
        ```

        Remarquez le `//` dans la formule : `n * (n + 1)` est toujours pair, donc le
        quotient est exact et on veut un entier, pas un flottant. Avec `/` on obtiendrait
        `5050.0`, ce qui est la bonne valeur mais le mauvais type.

        Les deux méthodes donnent la même réponse, mais l'une fait cent additions et
        l'autre trois opérations. Sur une somme jusqu'à un milliard, la différence n'est
        plus théorique : c'est le sujet du TP2.

---

## Étape 4. Les fonctions (20 min)

Une fonction met un nom sur un calcul, pour pouvoir le réutiliser sans le récrire :

```python
def celsius_vers_fahrenheit(c):
    """Convertit une température de degrés Celsius en degrés Fahrenheit."""
    return c * 9 / 5 + 32

print(celsius_vers_fahrenheit(100))
print(celsius_vers_fahrenheit(-40))
```

Trois choses à retenir. Le mot `def` introduit la définition ; la chaîne entre triples
guillemets décrit ce que fait la fonction, et vous remerciera dans trois semaines ; `return`
renvoie le résultat, et n'est pas la même chose que `print`, qui se contente d'afficher.
Une fonction qui affiche sans renvoyer ne sert à rien : on ne peut pas réutiliser son
résultat.

!!! question "Exercice 4.1 : compter les chiffres"
    Écrivez une fonction `nombre_de_chiffres(n)` qui renvoie le nombre de chiffres d'un
    entier positif, sans le convertir en chaîne de caractères.

    **Résultat attendu :** `nombre_de_chiffres(2026)` vaut `4`, et
    `nombre_de_chiffres(7)` vaut `1`.

    ??? success "Corrigé"
        ```python
        def nombre_de_chiffres(n):
            """Renvoie le nombre de chiffres de l'entier positif n."""
            compte = 1
            while n >= 10:
                n = n // 10
                compte = compte + 1
            return compte

        print(nombre_de_chiffres(2026))
        print(nombre_de_chiffres(7))
        print(nombre_de_chiffres(10 ** 60))
        ```

        On divise par 10 jusqu'à n'avoir plus qu'un chiffre, en comptant les divisions.
        Le dernier appel montre au passage que la fonction gère un nombre de soixante et un
        chiffres sans effort, ce qu'aucun entier 64 bits ne permettrait.

        Le piège de l'énoncé est le cas `n = 0` : la fonction renvoie `1`, ce qui est la
        réponse attendue, mais uniquement parce que `compte` part de `1`. Une version qui
        partirait de `0` renverrait `0` chiffre pour le nombre `0`. Toujours essayer les
        cas limites.

---

## Étape 5. Une vraie méthode numérique : Héron (20 min)

Comment un ordinateur calcule-t-il une racine carrée ? Une méthode connue depuis
l'Antiquité, attribuée à Héron d'Alexandrie, consiste à partir d'une estimation quelconque
et à l'améliorer en la moyennant avec ce qu'elle devrait donner. Pour calculer
\( \sqrt{a} \), on part de \( x_0 = a \) puis on itère :

\[ x_{n+1} = \frac{1}{2}\left(x_n + \frac{a}{x_n}\right) \]

La suite converge très vite : le nombre de décimales exactes double à chaque tour.

!!! question "Exercice 5.1 : racine carrée de 2"
    Écrivez une fonction `heron(a)` qui calcule \( \sqrt{a} \) par cette méthode, en
    s'arrêtant quand deux estimations successives sont assez proches. Comparez à
    `math.sqrt`.

    **Résultat attendu :** un écart avec `math.sqrt(2)` inférieur à `1e-12`, atteint en
    moins de dix tours.

    ??? success "Corrigé"
        ```python
        import math

        def heron(a, tolerance=1e-12):
            """Racine carrée de a par la méthode de Héron."""
            if a < 0:
                raise ValueError("pas de racine carrée réelle pour un nombre négatif")
            if a == 0:
                return 0.0
            x = float(a)
            tours = 0
            while True:
                suivant = 0.5 * (x + a / x)
                tours = tours + 1
                if abs(suivant - x) <= tolerance * abs(suivant):
                    return suivant
                x = suivant

        print(heron(2))
        print(math.sqrt(2))
        print(abs(heron(2) - math.sqrt(2)) < 1e-12)
        ```

        Trois points méritent votre attention, et ce sont eux qui séparent un code
        d'étudiant d'un code de professionnel.

        Le cas `a = 0` est traité à part, sans quoi la première itération divise par zéro.
        Le cas `a < 0` lève une erreur explicite plutôt que de renvoyer un résultat
        absurde : mieux vaut un programme qui s'arrête en disant pourquoi qu'un programme
        qui continue avec une valeur fausse.

        Le critère d'arrêt est **relatif**, `abs(suivant - x) <= tolerance * abs(suivant)`,
        et non absolu. Un écart de `1e-12` n'a pas le même sens pour une racine de 2 et
        pour une racine de `1e30`. C'est exactement la remarque de l'exercice 2.2, et vous
        la retrouverez dans tout calcul numérique.

!!! tip "Pour aller plus loin"
    Modifiez `heron` pour qu'elle renvoie aussi le nombre de tours effectués, et observez
    combien il en faut pour `heron(2)`, `heron(1e6)` et `heron(1e30)`. Le nombre de tours
    croît beaucoup plus lentement que le nombre : c'est le signe d'une méthode qui converge
    quadratiquement, notion que vous retrouverez au TP3 avec la méthode de Newton, dont
    Héron n'est qu'un cas particulier.

---

## Ce qu'il faut retenir

Les entiers de Python sont exacts et sans limite de taille ; les flottants sont approchés,
et deux flottants ne se comparent jamais avec `==`. Une boucle `for` parcourt une suite
connue d'avance, une boucle `while` s'arrête sur une condition. Une fonction renvoie avec
`return` et se documente en une phrase. Et un critère d'arrêt sérieux est relatif, pas
absolu.

[Passer au TP2](tp2-arithmetique.md){ .md-button .md-button--primary }
