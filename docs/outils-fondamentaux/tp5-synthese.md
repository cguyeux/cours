# TP5. Synthèse : chiffrer, déchiffrer, casser

**Durée : 1 h 45. Séance notée.**

## Objectifs

- Réinvestir l'arithmétique du TP2 sur un problème complet.
- Comprendre pourquoi une clé de chiffrement doit vérifier une condition mathématique, et
  ce qui se passe quand on l'ignore.
- Casser un chiffrement de deux manières, par force brute puis par analyse statistique, et
  comparer leurs coûts.

## Prérequis

Tous les TP précédents. Le TP2 en particulier : PGCD et arithmétique modulaire.

## Ressources

- Le [mémento Python](memento.md).
- [Le carnet de ce TP](/lite/notebooks/index.html?path=tp5.ipynb){ target=_blank }.

---

## Le problème

Le **chiffrement affine** transforme chaque lettre en une autre par une formule
arithmétique. On numérote les lettres de 0 à 25, puis on applique

\[ E(x) = (a\,x + b) \bmod 26 \]

où le couple \( (a, b) \) est la clé. Avec \( a = 1 \), on retrouve le chiffre de César,
connu depuis deux mille ans. Le procédé est aujourd'hui sans valeur cryptographique, ce qui
est précisément l'intérêt : vous allez le casser vous-même en fin de séance.

---

## Étape 1. Des lettres aux nombres (15 min)

Python donne le code d'un caractère avec `ord`, et le caractère d'un code avec `chr`. Les
lettres majuscules de l'alphabet latin se suivent, de `ord("A")` à `ord("Z")`.

```python
print(ord("A"), ord("Z"), chr(72))
```

!!! question "Exercice 1.1 : les deux conversions"
    Écrivez `lettre_vers_nombre(c)` et `nombre_vers_lettre(n)`, réciproques l'une de
    l'autre sur les majuscules.

    **Résultat attendu :** `lettre_vers_nombre("C")` vaut `2`, et
    `nombre_vers_lettre(2)` vaut `"C"`.

    ??? success "Corrigé"
        ```python
        def lettre_vers_nombre(c):
            """Numéro de 0 à 25 d'une lettre majuscule."""
            return ord(c) - ord("A")

        def nombre_vers_lettre(n):
            """Lettre majuscule correspondant à un numéro de 0 à 25."""
            return chr(n % 26 + ord("A"))

        print(lettre_vers_nombre("C"), nombre_vers_lettre(2))
        print([nombre_vers_lettre(lettre_vers_nombre(c)) == c for c in "ABCXYZ"])
        ```

        Le `% 26` dans la seconde fonction n'est pas superflu : il garantit qu'un nombre
        hors de l'intervalle attendu retombe sur une lettre valide, ce qui simplifie tout
        le reste du TP.

!!! question "Exercice 1.2 : nettoyer un texte"
    Écrivez `nettoyer(texte)` qui met tout en majuscules et ne garde que les lettres de A
    à Z, en supprimant espaces, ponctuation et accents.

    **Résultat attendu :** `nettoyer("Été, à Paris !")` vaut `"ETEAPARIS"`.

    ??? success "Corrigé"
        ```python
        import unicodedata

        def nettoyer(texte):
            """Majuscules sans accents, lettres A-Z uniquement."""
            sans_accent = unicodedata.normalize("NFD", texte)
            sans_accent = "".join(c for c in sans_accent if unicodedata.category(c) != "Mn")
            return "".join(c for c in sans_accent.upper() if "A" <= c <= "Z")

        print(nettoyer("Été, à Paris !"))
        ```

        La normalisation `NFD` sépare une lettre accentuée en deux caractères, la lettre
        et l'accent ; on jette ensuite les accents, repérés par leur catégorie Unicode
        `Mn`. C'est la manière correcte de faire, bien plus robuste qu'une table de
        remplacement écrite à la main, qui oublie toujours un caractère.

---

## Étape 2. Chiffrer (15 min)

!!! question "Exercice 2.1 : la fonction de chiffrement"
    Écrivez `chiffrer(texte, a, b)` qui applique \( E(x) = (ax + b) \bmod 26 \) à chaque
    lettre d'un texte déjà nettoyé.

    **Résultat attendu :** `chiffrer("ATTAQUEALAUBE", 5, 8)` vaut `"IZZIKECILIENC"`.

    ??? success "Corrigé"
        ```python
        def chiffrer(texte, a, b):
            """Chiffrement affine de texte avec la clé (a, b)."""
            resultat = []
            for c in nettoyer(texte):
                x = lettre_vers_nombre(c)
                resultat.append(nombre_vers_lettre((a * x + b) % 26))
            return "".join(resultat)

        message = "ATTAQUEALAUBE"
        print(chiffrer(message, 5, 8))
        print(chiffrer(message, 1, 3))   # le chiffre de César
        ```

        Avec \( a = 1 \) et \( b = 3 \), chaque lettre est simplement décalée de trois
        rangs : c'est le chiffre que Suétone attribue à Jules César.

---

## Étape 3. La condition sur la clé (25 min)

Déchiffrer demande de résoudre \( y = ax + b \) en \( x \), donc de diviser par \( a \)
modulo 26. Or diviser modulo 26 n'a pas toujours de sens. Il faut un entier \( a^{-1} \)
tel que \( a \times a^{-1} \equiv 1 \pmod{26} \), et un tel inverse **n'existe que si**
\( a \) et 26 sont premiers entre eux, c'est-à-dire si \( \mathrm{pgcd}(a, 26) = 1 \).

!!! question "Exercice 3.1 : les clés utilisables"
    Écrivez le code qui donne la liste des valeurs de `a` entre 1 et 25 pour lesquelles le
    chiffrement est déchiffrable. Combien y en a-t-il ?

    **Résultat attendu :** douze valeurs, toutes impaires et différentes de 13.

    ??? success "Corrigé"
        ```python
        def pgcd(a, b):
            while b != 0:
                a, b = b, a % b
            return a

        valides = [a for a in range(1, 26) if pgcd(a, 26) == 1]
        print(valides)
        print(len(valides), "valeurs possibles pour a")
        ```

        On obtient `[1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]`. Comme \( 26 = 2
        \times 13 \), il faut exclure tous les multiples de 2 et de 13. Le nombre total de
        clés est donc \( 12 \times 26 = 312 \), ce qui est ridiculement petit : retenez ce
        chiffre pour l'étape 5.

!!! question "Exercice 3.2 : l'inverse modulaire"
    Écrivez `inverse_modulaire(a, n)` qui renvoie l'inverse de `a` modulo `n`, ou lève une
    erreur s'il n'existe pas.

    **Résultat attendu :** l'inverse de 5 modulo 26 est 21, car \( 5 \times 21 = 105 =
    4 \times 26 + 1 \).

    ??? success "Corrigé"
        ```python
        def inverse_modulaire(a, n):
            """Inverse de a modulo n, par recherche exhaustive."""
            a = a % n
            for candidat in range(1, n):
                if (a * candidat) % n == 1:
                    return candidat
            raise ValueError(f"{a} n'est pas inversible modulo {n}")

        print(inverse_modulaire(5, 26))
        print((5 * 21) % 26)

        try:
            inverse_modulaire(4, 26)
        except ValueError as erreur:
            print("erreur attendue :", erreur)
        ```

        La recherche exhaustive convient parfaitement ici, puisque \( n = 26 \). Pour un
        module de trois cents chiffres, comme en cryptographie réelle, elle serait
        impraticable et l'on utilise l'algorithme d'Euclide étendu, qui donne l'inverse en
        quelques dizaines d'opérations. C'est le même écart qu'entre le test de primalité
        naïf et le crible du TP2.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez « écris un chiffrement affine en Python ». Puis essayez sa fonction avec
    \( a = 4 \) et \( b = 7 \). Presque toujours, le chiffrement fonctionne sans broncher,
    et le déchiffrement rend n'importe quoi, ou plante avec un message obscur.

    La raison est que 4 n'est pas inversible modulo 26, donc plusieurs lettres différentes
    sont chiffrées en la même lettre : l'information est détruite, aucun déchiffrement
    n'est possible. Vérifiez si le code proposé teste la validité de la clé. Un
    programme sérieux refuse une clé invalide au lieu de produire silencieusement un
    message irrécupérable, et c'est vous qui devez le savoir.

---

## Étape 4. Déchiffrer (15 min)

!!! question "Exercice 4.1 : la fonction de déchiffrement"
    Écrivez `dechiffrer(texte, a, b)`, en refusant les clés invalides. Vérifiez que
    déchiffrer ce qu'on a chiffré redonne le message d'origine.

    **Résultat attendu :** `dechiffrer(chiffrer(m, 5, 8), 5, 8)` redonne `m` nettoyé.

    ??? success "Corrigé"
        ```python
        def dechiffrer(texte, a, b):
            """Déchiffrement affine. Lève une erreur si la clé n'est pas inversible."""
            a_inverse = inverse_modulaire(a, 26)
            resultat = []
            for c in nettoyer(texte):
                y = lettre_vers_nombre(c)
                resultat.append(nombre_vers_lettre(a_inverse * (y - b) % 26))
            return "".join(resultat)

        message = nettoyer("Attaque a l aube")
        secret = chiffrer(message, 5, 8)
        print(secret)
        print(dechiffrer(secret, 5, 8))
        print(dechiffrer(secret, 5, 8) == message)

        # une clé invalide est refusée au lieu de produire un résultat faux
        try:
            dechiffrer(secret, 4, 7)
        except ValueError as erreur:
            print("cle refusee :", erreur)
        ```

        Le test aller-retour, chiffrer puis déchiffrer et comparer à l'original, est la
        bonne façon de vérifier ce genre de code. Il attrape toutes les erreurs de signe
        et de modulo d'un seul coup.

---

## Étape 5. Casser par force brute (20 min)

Il n'y a que 312 clés. Un ordinateur les essaie toutes en un clin d'œil : c'est ce qu'on
appelle une **attaque par force brute**, et elle suffit à condamner ce chiffrement.

!!! question "Exercice 5.1 : essayer toutes les clés"
    Écrivez `toutes_les_clefs(secret)` qui renvoie la liste des 312 déchiffrements
    possibles avec leur clé. Retrouvez le message clair à l'œil.

    **Résultat attendu :** parmi les 312 propositions, une seule est du français lisible.

    ??? success "Corrigé"
        ```python
        def toutes_les_clefs(secret):
            """Tous les déchiffrements possibles, sous forme de triplets (a, b, texte)."""
            resultats = []
            for a in valides:
                for b in range(26):
                    resultats.append((a, b, dechiffrer(secret, a, b)))
            return resultats

        essais = toutes_les_clefs(secret)
        print(len(essais), "clefs essayees")
        bons = [e for e in essais if e[2] == message]
        print("la bonne clef :", bons[0][0], bons[0][1])
        ```

        Trois cent douze essais, c'est instantané. Comparez avec une clé moderne de 128
        bits, qui offre \( 2^{128} \) possibilités, soit un nombre à trente-neuf chiffres :
        aucune machine existante ou concevable n'en viendrait à bout. La sécurité d'un
        chiffrement tient d'abord à la taille de son espace de clés.

---

## Étape 6. Casser par analyse de fréquences (25 min)

La force brute exige une inspection humaine des 312 résultats. On peut faire mieux et tout
automatiser, en exploitant une propriété du français : la lettre E y est de loin la plus
fréquente, environ 15 % des lettres, suivie de A et de S.

Comme le chiffrement affine envoie toujours la même lettre sur la même lettre, la lettre la
plus fréquente du message chiffré est très probablement l'image de E.

!!! question "Exercice 6.1 : casser automatiquement"
    Comptez les occurrences de chaque lettre du message chiffré, puis testez les clés qui
    envoient E sur la lettre la plus fréquente. Retrouvez le message sans intervention
    humaine.

    **Résultat attendu :** le message clair, trouvé parmi une poignée de candidats au
    lieu de 312.

    ??? success "Corrigé"
        ```python
        from collections import Counter

        texte_long = nettoyer(
            "Le chiffrement affine est un chiffrement par substitution monoalphabetique. "
            "Chaque lettre du message est remplacee par une autre lettre, toujours la meme, "
            "ce qui laisse intactes les frequences relatives des lettres et permet de casser "
            "le code sans essayer toutes les clefs possibles."
        )
        secret_long = chiffrer(texte_long, 7, 12)

        comptes = Counter(secret_long)
        lettre_frequente = comptes.most_common(1)[0][0]
        print("lettre la plus frequente du chiffre :", lettre_frequente)

        # on suppose que E (numero 4) a ete chiffre en cette lettre
        cible = lettre_vers_nombre(lettre_frequente)
        candidats = []
        for a in valides:
            # E -> cible impose b = cible - 4a mod 26
            b = (cible - 4 * a) % 26
            candidats.append((a, b, dechiffrer(secret_long, a, b)))

        print(len(candidats), "candidats au lieu de 312")
        for a, b, texte in candidats:
            if texte.startswith("LECHIFFREMENT"):
                print("trouve :", a, b)
                print(texte[:60])
        ```

        On passe de 312 essais à 12, et le bon apparaît immédiatement. La méthode a
        cependant besoin d'un texte assez long : sur `"ATTAQUEALAUBE"`, la lettre la plus
        fréquente est A et non E, et l'hypothèse tombe à côté. Essayez, c'est instructif.

        On peut alors rendre la méthode robuste en testant les trois lettres les plus
        fréquentes du chiffré contre les trois du français, ce qui donne neuf hypothèses,
        toujours bien moins que 312.

!!! tip "Pour aller plus loin"
    Automatisez complètement la décision, en notant chaque candidat par sa ressemblance
    avec le français : par exemple la somme, sur les lettres, du produit de la fréquence
    observée par la fréquence attendue. Le candidat de score maximal est presque toujours
    le bon, et vous n'avez plus rien à lire. C'est, en simplifié, la manière dont les
    chiffres classiques ont été cassés à Bletchley Park.

---

## Ce qui est évalué

Le rendu de cette séance est le carnet complet, avec :

1. les fonctions des étapes 1 à 4, testées par un aller-retour chiffrer puis déchiffrer ;
2. le refus explicite d'une clé non inversible, démontré par un exemple ;
3. l'attaque par force brute, avec le nombre de clés essayées ;
4. l'attaque par fréquences, avec une phrase expliquant pourquoi elle échoue sur un texte
   court ;
5. pour chaque encadré « L'IA vous le donne en trois secondes » rencontré dans les cinq
   TP, deux ou trois lignes disant ce que vous avez trouvé.

Le dernier point compte autant que les autres. Ce n'est pas un exercice de style : c'est la
compétence qui vous distinguera de quelqu'un qui se contente de coller une réponse.

---

## Ce qu'il faut retenir

Un chiffrement, même simple, repose sur une propriété mathématique précise, ici
l'inversibilité de \( a \) modulo 26 : la violer ne provoque pas d'erreur visible, elle
détruit silencieusement l'information. Un espace de clés trop petit rend le chiffrement
sans valeur, quelle que soit son élégance. Et une régularité statistique laissée intacte
par le chiffrement est une porte d'entrée, ce qui vaut encore aujourd'hui bien au delà de
ce petit exemple.
