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
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp5.html){ target=_blank }, à faire après la séance.

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

## Entraînement et approfondissement

Cette séance est notée, et les exercices ci-dessous n'en font pas partie. Ils sont là pour
ceux qui veulent voir jusqu'où mène la piste ouverte à l'étape 6, et pour préparer le cours
de cryptographie de deuxième année.

### Étape 7. Mesurer si un texte « ressemble » à une langue

L'attaque de l'étape 6 repose sur une intuition : un texte chiffré par substitution garde
les fréquences du français. On peut mesurer cette ressemblance par un seul nombre,
l'**indice de coïncidence**, qui est la probabilité que deux lettres tirées au hasard dans
le texte soient identiques :

\[ IC = \frac{\sum_{\ell} n_\ell (n_\ell - 1)}{N (N - 1)} \]

où \( n_\ell \) est le nombre d'occurrences de la lettre \( \ell \) et \( N \) la
longueur du texte. Pour un texte où toutes les lettres seraient équiprobables, il vaut
\( 1/26 \approx 0{,}038 \). Pour du français, il est nettement plus élevé, entre 0,07 et
0,08 sur un texte long.

!!! question "Exercice 7.1 : l'indice de coïncidence"
    Écrivez `indice_coincidence(texte)`. Calculez-le sur `texte_long`, sur `secret_long`,
    et sur une suite de lettres tirées au hasard de même longueur.

    **Résultat attendu :** la même valeur pour le clair et pour le chiffré affine, environ
    0,087 sur ce texte court, contre environ 0,039 pour les lettres au hasard.

    ??? success "Corrigé"
        ```python
        import random

        def indice_coincidence(texte):
            """Probabilité que deux lettres tirées au hasard dans le texte coïncident."""
            N = len(texte)
            comptes = Counter(texte)
            return sum(n * (n - 1) for n in comptes.values()) / (N * (N - 1))

        random.seed(1)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        hasard = "".join(random.choice(alphabet) for _ in range(len(texte_long)))

        print(f"clair    : {indice_coincidence(texte_long):.4f}")
        print(f"affine   : {indice_coincidence(secret_long):.4f}")
        print(f"hasard   : {indice_coincidence(hasard):.4f}")
        ```

        Le chiffrement affine ne change pas l'indice : il permute les lettres, donc il
        permute les \( n_\ell \) sans changer leur somme. C'est une signature, et elle
        suffit à dire, sans même essayer de déchiffrer, qu'un texte a été chiffré par
        substitution simple. La valeur est un peu haute ici parce que le texte est court
        et répétitif ; sur un roman, elle tombe vers 0,075.

### Étape 8. Vigenère, ou comment casser l'indice

Le chiffre de Vigenère, au seizième siècle, corrige la faiblesse de la substitution :
on choisit un mot-clé, et l'on décale chaque lettre du message du rang de la lettre
correspondante du mot-clé, en recommençant le mot-clé quand il est épuisé. Une même lettre
du clair n'est plus toujours chiffrée de la même façon, et les fréquences sont aplaties.

!!! question "Exercice 8.1 : chiffrer par Vigenère"
    Écrivez `vigenere(texte, cle)`. Chiffrez `texte_long` avec la clé `"CLE"`, et calculez
    l'indice de coïncidence du résultat.

    **Résultat attendu :** un indice d'environ 0,055, intermédiaire entre le français et
    le hasard. L'attaque par fréquences de l'étape 6 ne s'applique plus telle quelle.

    ??? success "Corrigé"
        ```python
        def vigenere(texte, cle):
            """Chiffre de Vigenère : chaque lettre est décalée par la lettre de la clé en face."""
            resultat = []
            for i, c in enumerate(nettoyer(texte)):
                decalage = lettre_vers_nombre(cle[i % len(cle)])
                resultat.append(nombre_vers_lettre(lettre_vers_nombre(c) + decalage))
            return "".join(resultat)

        secret_vigenere = vigenere(texte_long, "CLE")
        print(secret_vigenere[:40])
        print(f"IC vigenere : {indice_coincidence(secret_vigenere):.4f}")
        ```

        La fonction `nombre_vers_lettre` de l'étape 1 fait le `% 26` pour nous : c'est
        pour cela qu'on l'avait écrite ainsi. Avec trois décalages différents mélangés,
        l'indice descend, et sur une clé longue il rejoindrait celui du hasard.

!!! question "Exercice 8.2 : retrouver la longueur de la clé"
    Si la clé a \( L \) lettres, alors les lettres du chiffré de rangs \( 0, L, 2L, \dots \)
    ont toutes subi le même décalage : c'est un chiffre de César, et son indice de
    coïncidence est celui du français. Pour chaque longueur candidate `L` de 1 à 7,
    découpez le chiffré en `L` colonnes, calculez l'indice moyen des colonnes, et repérez
    les longueurs où il remonte.

    **Résultat attendu :** l'indice moyen bondit à environ 0,09 pour `L = 3` et
    `L = 6`, et reste vers 0,055 pour les autres longueurs. La clé a donc trois lettres,
    ou un multiple de trois.

    ??? success "Corrigé"
        ```python
        for L in range(1, 8):
            colonnes = [secret_vigenere[i::L] for i in range(L)]
            moyenne = sum(indice_coincidence(col) for col in colonnes) / L
            print(f"L = {L} : indice moyen {moyenne:.4f}")
        ```

        La notation `texte[i::L]` prend une lettre sur `L` à partir de la position `i`.
        Une fois la longueur connue, chaque colonne se casse comme un César, par la
        méthode de l'étape 6 : la lettre la plus fréquente de la colonne est l'image de E,
        ce qui donne le décalage, donc la lettre de la clé. Vous avez tous les outils pour
        finir : faites-le, et vous aurez cassé sans aucune indication un chiffre resté
        réputé incassable pendant trois siècles.

        Ce qui l'a finalement mis à terre, c'est exactement ce que vous venez de faire :
        une statistique, l'indice de coïncidence, et un peu de calcul. C'est aussi la
        raison pour laquelle les chiffrements modernes sont conçus pour qu'aucune
        régularité du clair ne survive dans le chiffré.

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

## Auto-évaluation

- [ ] expliquer pourquoi \( a \) doit être premier avec 26, et ce qui se passe sinon ;
- [ ] calculer de tête le nombre de clés du chiffrement affine ;
- [ ] écrire le test aller-retour qui valide un couple chiffrer, déchiffrer ;
- [ ] dire pourquoi l'attaque par fréquences échoue sur un texte court ;
- [ ] expliquer ce que mesure l'indice de coïncidence et pourquoi une substitution ne le
  change pas.

[Le QCM du TP5](qcm/qcm_tp5.html){ .md-button target=_blank }
[La séance de prolongement : géométrie du plan](tp6-geometrie-plan.md){ .md-button .md-button--primary }
