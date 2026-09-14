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
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp1.html){ target=_blank }, à faire après la séance.

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

## Entraînement et approfondissement

Les exercices qui suivent ne tiennent pas dans la séance. Faites-les chez vous, ou en
séance si vous avez terminé : ils sont au programme de l'évaluation, sauf ceux marqués
« pour aller plus loin ». Ils reprennent la question centrale du TP, comment la machine
écrit les nombres et ce que cela lui fait perdre, et la poussent un cran plus loin.

### Étape 6. Comment la machine écrit les nombres

Vous savez que la machine compte en base 2. Python sait vous le montrer : `bin(n)` donne
l'écriture binaire d'un entier, et `int(texte, 2)` fait le chemin inverse.

```python
print(bin(37))
print(int("100101", 2))
```

Un flottant, lui, est écrit en binaire avec un nombre fixe de chiffres, cinquante-deux
après la virgule pour le type `float`. C'est là que `0.1` pose problème : son écriture
binaire ne se termine jamais, donc elle est coupée. Le module `fractions` permet de voir
exactement quel nombre la machine a gardé à la place de `0.1` :

```python
from fractions import Fraction

print(Fraction(0.1))
```

Ce n'est pas `1/10`. C'est une fraction dont le dénominateur est une puissance de 2, la plus
proche possible de `1/10`, et l'écart entre les deux est l'erreur que vous avez vue
s'accumuler à l'exercice 2.1.

!!! question "Exercice 6.1 : conversion en binaire, à la main"
    Écrivez `vers_binaire(n)` qui renvoie l'écriture binaire d'un entier positif sous forme
    de chaîne de caractères, **sans utiliser `bin`**. Indication : le reste de la division
    par 2 donne le dernier chiffre, comme le reste par 10 donnait le chiffre des unités à
    l'exercice 1.2.

    **Résultat attendu :** `vers_binaire(37)` vaut `"100101"`, et `vers_binaire(0)` vaut
    `"0"`.

    ??? success "Corrigé"
        ```python
        def vers_binaire(n):
            """Écriture binaire de l'entier positif n, sans le préfixe 0b."""
            if n == 0:
                return "0"
            chiffres = ""
            while n > 0:
                chiffres = str(n % 2) + chiffres
                n = n // 2
            return chiffres

        print(vers_binaire(37), vers_binaire(0), vers_binaire(1024))
        print(all(vers_binaire(n) == bin(n)[2:] for n in range(2000)))
        ```

        La dernière ligne compare votre fonction à celle de Python sur deux mille valeurs.
        C'est la manière rapide de tester une fonction dont on connaît une référence : on
        ne relit pas le code, on le confronte.

        Le cas `n = 0` est traité à part, comme à l'exercice 4.1 : la boucle ne ferait
        aucun tour et renverrait une chaîne vide.

!!! question "Exercice 6.2 : l'epsilon de la machine"
    Le plus petit nombre `eps` tel que `1.0 + eps` soit différent de `1.0` s'appelle
    l'epsilon machine. Trouvez-le en partant de `eps = 1.0` et en le divisant par 2 tant
    que `1.0 + eps / 2` reste différent de `1.0`. Comparez à `sys.float_info.epsilon`.

    **Résultat attendu :** environ `2.2e-16`, soit \( 2^{-52} \).

    ??? success "Corrigé"
        ```python
        import sys

        eps = 1.0
        while 1.0 + eps / 2 != 1.0:
            eps = eps / 2

        print(eps)
        print(sys.float_info.epsilon)
        print(eps == 2 ** -52)
        ```

        Cinquante-deux chiffres binaires après la virgule, c'est environ seize chiffres
        décimaux significatifs. Au delà, la machine ne voit plus la différence entre deux
        nombres. Vérifiez : `1e15 + 1 == 1e15` est faux, mais `1e16 + 1 == 1e16` est
        vrai. Un flottant ne peut pas représenter l'entier \( 10^{16} + 1 \), alors qu'un
        `int` de Python le fait sans effort.

### Étape 7. Quand une soustraction efface tout

L'erreur d'arrondi sur un flottant est minuscule, de l'ordre de \( 10^{-16} \) en valeur
relative. Il existe pourtant une opération qui la transforme en erreur énorme : soustraire
deux nombres presque égaux. Le résultat est petit, mais son erreur est celle des grands
nombres de départ, et elle devient dominante. On parle d'**élimination catastrophique**.

L'exemple classique est la résolution de l'équation du second degré
\( ax^{2} + bx + c = 0 \) par la formule que vous connaissez :

\[ x = \frac{-b \pm \sqrt{b^{2} - 4ac}}{2a} \]

!!! question "Exercice 7.1 : la formule du lycée en difficulté"
    Écrivez `racines_naif(a, b, c)` qui applique la formule ci-dessus, et appliquez-la à
    \( x^{2} - 10^{8}x + 1 = 0 \). Le produit des deux racines doit valoir \( c/a = 1 \) :
    vérifiez-le.

    **Résultat attendu :** la grande racine vaut `1e8`, mais la petite vaut environ
    `7.45e-9` au lieu de `1e-8`, et le produit des racines vaut `0.745` au lieu de `1`.

    ??? success "Corrigé"
        ```python
        import math

        def racines_naif(a, b, c):
            """Racines réelles de ax² + bx + c par la formule classique."""
            delta = b * b - 4 * a * c
            if delta < 0:
                raise ValueError("pas de racine réelle")
            r = math.sqrt(delta)
            return (-b - r) / (2 * a), (-b + r) / (2 * a)

        petite, grande = racines_naif(1.0, -1e8, 1.0)
        print(petite, grande)
        print("produit :", petite * grande, "attendu : 1")
        ```

        Une erreur de 25 % sur une racine, avec une formule mathématiquement exacte.
        Ici \( b^{2} = 10^{16} \) et \( 4ac = 4 \) : la racine carrée du discriminant vaut
        \( 10^{8} \) à \( 2 \times 10^{-8} \) près, et c'est cette toute petite
        différence que la formule \( -b - \sqrt{\Delta} \) doit calculer. Elle est noyée
        dans l'arrondi de \( \sqrt{\Delta} \), qui est de l'ordre de \( 10^{8} \times
        10^{-16} = 10^{-8} \), le même ordre de grandeur que la réponse. Le résultat
        n'a donc plus qu'un chiffre de vrai, et c'est encore de la chance.

!!! question "Exercice 7.2 : la formule stable"
    La grande racine, elle, est calculée correctement, car on **additionne** deux nombres
    de même signe. Or le produit des racines vaut \( c/a \) : la petite racine s'obtient
    donc par \( x_2 = c / (a\,x_1) \), sans aucune soustraction. Écrivez
    `racines(a, b, c)` qui calcule la racine « sûre » par la formule, puis l'autre par le
    produit, et comparez.

    **Résultat attendu :** les deux racines `1e-08` et `1e8`, un produit égal à `1`, et
    en chacune un résidu \( a x^{2} + bx + c \) nul à la précision des flottants, soit
    de l'ordre de \( 10^{-16} \) fois la taille des termes en jeu.

    ??? success "Corrigé"
        ```python
        def racines(a, b, c):
            """Racines réelles de ax² + bx + c, sans élimination catastrophique."""
            delta = b * b - 4 * a * c
            if delta < 0:
                raise ValueError("pas de racine réelle")
            r = math.sqrt(delta)
            # on choisit le signe qui additionne au lieu de soustraire
            if b >= 0:
                sure = (-b - r) / (2 * a)
            else:
                sure = (-b + r) / (2 * a)
            autre = c / (a * sure)
            return min(sure, autre), max(sure, autre)

        petite, grande = racines(1.0, -1e8, 1.0)
        print(petite, grande)
        print("produit :", petite * grande)
        for x in (petite, grande):
            residu = x * x - 1e8 * x + 1
            print(f"residu : {residu:.1e}, soit {residu / max(x * x, 1.0):.1e} en relatif")
        ```

        Le résidu de la grande racine vaut `1.0`, ce qui surprend avant qu'on regarde
        les termes : \( x^{2} \) et \( 10^{8} x \) valent tous deux \( 10^{16} \), et un
        écart de 1 sur \( 10^{16} \) est exactement l'epsilon machine de l'exercice
        6.2. C'est pourquoi on juge un résidu **relativement** à la taille des nombres
        qu'il compare, jamais dans l'absolu : encore la leçon de l'exercice 2.2.

        La fonction fait strictement le même nombre d'opérations que la version naïve.
        Elle ne coûte rien de plus, et elle est juste. C'est le résumé de tout ce TP : en
        calcul numérique, deux formules mathématiquement équivalentes ne sont pas
        équivalentes pour la machine, et savoir laquelle choisir est une compétence.

!!! question "Exercice 7.3 : calculer exactement, quand c'est possible"
    Le module `fractions` fait de l'arithmétique **exacte** sur les rationnels, sans aucun
    arrondi. Refaites l'exercice 2.1 en additionnant mille fois `Fraction(1, 10)`.

    **Résultat attendu :** exactement `100`, et `Fraction(1, 10) + Fraction(2, 10) ==
    Fraction(3, 10)` vaut `True`.

    ??? success "Corrigé"
        ```python
        total = Fraction(0)
        for _ in range(1000):
            total = total + Fraction(1, 10)
        print(total, total == 100)
        print(Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10))
        ```

        Alors pourquoi ne pas toujours calculer ainsi ? Parce que c'est lent, cent à
        mille fois plus que sur des flottants, et parce que les dénominateurs grossissent
        à chaque opération jusqu'à devenir ingérables. Les fractions exactes servent quand
        le résultat doit être irréprochable et que les données sont peu nombreuses : vous
        les retrouverez au TP4, pour résoudre exactement un système que les flottants
        massacrent.

!!! tip "Pour aller plus loin : le module decimal"
    Le module `decimal` calcule en base 10 avec un nombre de chiffres que vous choisissez.
    Essayez `from decimal import Decimal, getcontext`, puis `getcontext().prec = 50` et
    `Decimal(1) / Decimal(7)`. C'est ainsi que les logiciels de comptabilité manipulent
    les montants, et c'est la réponse correcte à la remarque de l'exercice 2.1 sur les
    logiciels bancaires.

---

## Ce qu'il faut retenir

Les entiers de Python sont exacts et sans limite de taille ; les flottants sont approchés,
et deux flottants ne se comparent jamais avec `==`. Une boucle `for` parcourt une suite
connue d'avance, une boucle `while` s'arrête sur une condition. Une fonction renvoie avec
`return` et se documente en une phrase. Un critère d'arrêt sérieux est relatif, pas
absolu. Et deux formules égales sur le papier ne le sont pas pour la machine dès qu'une
soustraction efface les chiffres significatifs.

## Auto-évaluation

Avant de passer au TP2, vous devez pouvoir, sans regarder le corrigé :

- [ ] dire ce que valent `17 // 5`, `17 % 5` et `17 / 5`, et de quel type est chacun ;
- [ ] expliquer en deux phrases pourquoi `0.1 + 0.2 == 0.3` est faux ;
- [ ] écrire une boucle `for` qui affiche les carrés de 1 à 10, et la même en `while` ;
- [ ] écrire une fonction avec une valeur par défaut, et la documenter ;
- [ ] expliquer la différence entre un critère d'arrêt absolu et un critère relatif.

[Le QCM du TP1](qcm/qcm_tp1.html){ .md-button target=_blank }
[Passer au TP2](tp2-arithmetique.md){ .md-button .md-button--primary }
