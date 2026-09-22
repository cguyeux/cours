# TP2. La marche aléatoire, du graphe au texte

**Durée : 2 h.**

## Objectifs

- Écrire un graphe comme une matrice de transition, et vérifier ce qui fait d'une matrice
  une matrice de transition.
- Suivre une marche aléatoire pas à pas, et constater qu'elle finit par oublier son point
  de départ.
- Reconstruire PageRank depuis sa définition, comprendre à quoi sert l'amortissement, et
  comparer votre résultat à celui de networkx.
- Découvrir que le même objet mathématique, appliqué à du texte, est un modèle de langue.
- Mesurer ce qu'un modèle à deux caractères fait gagner, en bits, sur le pur hasard.

## Prérequis

Le [TP1](tp1-matrice-svd.md) pour le produit matriciel et la méthode de la puissance
itérée, que vous allez retrouver ici sous un autre nom. Aucune clé d'API, aucun
téléchargement : le corpus de texte est écrit dans l'énoncé.

```bash
pip install numpy matplotlib networkx
```

## Ressources

- [Le carnet de ce TP](/lite/notebooks/index.html?path=modelisation-tp2.ipynb){ target=_blank },
  qui s'exécute dans votre navigateur, sans rien installer.
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp2.html){ target=_blank }, à faire après la
  séance.
- Sergey Brin et Lawrence Page, *The anatomy of a large-scale hypertextual web search
  engine*, 1998 : l'article qui a fondé Google, et dont l'étape 3 reprend le calcul.
- Claude Shannon, *A Mathematical Theory of Communication*, 1948, dont la partie sur les
  approximations successives de l'anglais est exactement l'étape 5.
- Le corpus est constitué de deux fables de Jean de La Fontaine (1668), dans le domaine
  public.

---

## Étape 1. Un graphe est une matrice (15 min)

Prenons un petit site de sept pages qui se citent les unes les autres. La matrice
d'adjacence `A` vaut 1 en ligne `i`, colonne `j` s'il existe un lien de la page `i` vers la
page `j`, et 0 sinon.

```python
import matplotlib.pyplot as plt
import numpy as np

PAGES = ["accueil", "cours", "tp", "exos", "biblio", "contact", "plan"]
LIENS = [
    ("accueil", "cours"), ("accueil", "tp"), ("accueil", "plan"),
    ("cours", "tp"), ("cours", "exos"),
    ("tp", "exos"), ("tp", "accueil"),
    ("exos", "tp"),
    ("biblio", "cours"), ("biblio", "accueil"),
    ("contact", "accueil"),
    ("plan", "accueil"), ("plan", "cours"), ("plan", "tp"),
    ("plan", "biblio"), ("plan", "contact"),
]

index = {nom: i for i, nom in enumerate(PAGES)}
A = np.zeros((len(PAGES), len(PAGES)))
for depart, arrivee in LIENS:
    A[index[depart], index[arrivee]] = 1

print("liens sortants :", A.sum(axis=1).astype(int))
print("liens entrants :", A.sum(axis=0).astype(int))
```

Un internaute qui suit un lien au hasard depuis la page `i` a une chance sur `A[i].sum()`
d'arriver sur chacune des pages citées. Diviser chaque ligne par sa somme donne la
**matrice de transition** `P` :

```python
P = A / A.sum(axis=1, keepdims=True)
print("chaque ligne somme à 1 :", np.allclose(P.sum(axis=1), 1))
print("depuis accueil :", P[index["accueil"]].round(3))
```

!!! question "Exercice 1.1 : ce qui fait une matrice de transition"
    `P` est dite stochastique parce que chacune de ses lignes somme à 1. Pourquoi est-ce
    exigé ? Et que vaudrait la somme d'une **colonne** de `P` ?

    **Résultat attendu :** une ligne somme à 1 parce qu'à chaque pas, l'internaute part
    quelque part avec certitude : c'est la loi de probabilité de sa destination. Une
    colonne, elle, n'a aucune raison de sommer à 1 : vérifiez-le, `P.sum(axis=0)` donne
    `[2.2, 1.033, 2.033, 1.0, 0.2, 0.2, 0.333]`. Notez la quatrième valeur, qui vaut
    exactement 1 : une coïncidence de comptage, pas une propriété.

    ??? success "Corrigé"
        ```python
        print("sommes par colonne :", P.sum(axis=0).round(3))
        ```

        La distinction n'a rien d'une coquetterie : une ligne est une **loi de
        probabilité**, une colonne est un agrégat de flux entrants qui ne décrit aucune
        expérience aléatoire. Confondre les deux, c'est-à-dire normaliser par colonnes, est
        l'erreur la plus fréquente sur ce calcul, et l'étape 3 vous montrera qu'elle ne
        provoque aucun message d'erreur.

## Étape 2. Où est-on après n pas ? (25 min)

Si `v` est la loi de probabilité de la position courante, alors `v @ P` est celle de la
position au pas suivant. Après `n` pas, c'est donc `v @ P^n`. Partons de la page `contact`,
c'est-à-dire d'une certitude :

```python
depart = np.zeros(len(PAGES))
depart[index["contact"]] = 1.0

for n in [1, 2, 5, 10, 30]:
    position = depart @ np.linalg.matrix_power(P, n)
    print(f"n={n:3d} : {position.round(4)}")
```

!!! question "Exercice 2.1 : la marche oublie d'où elle vient"
    Refaites le calcul à `n = 30` en partant cette fois d'une loi **uniforme**, où
    l'internaute a autant de chances de démarrer sur chacune des sept pages. Comparez les
    deux résultats.

    **Résultat attendu :** les deux distributions coïncident à `2.53e-04` près, alors que
    les points de départ n'ont rien à voir. La marche converge vers une distribution qui ne
    dépend que du graphe : la **distribution stationnaire**.

    ??? success "Corrigé"
        ```python
        uniforme = np.ones(len(PAGES)) / len(PAGES)
        a = depart @ np.linalg.matrix_power(P, 30)
        b = uniforme @ np.linalg.matrix_power(P, 30)
        print("depuis contact  :", a.round(4))
        print("depuis uniforme :", b.round(4))
        print(f"écart maximal : {np.abs(a - b).max():.2e}")
        ```

        Vous venez de faire tourner, sans le savoir, la méthode de la puissance itérée du
        [TP1](tp1-matrice-svd.md) : la distribution stationnaire est le vecteur propre à
        gauche de `P` pour la valeur propre 1, et multiplier répétitivement par `P` aligne
        n'importe quel vecteur de départ sur cette direction. Deux algorithmes que tout
        oppose en apparence, une seule mathématique.

!!! question "Exercice 2.2 : le puits qui vide le site"
    Supposons que la page `contact` perde tous ses liens sortants, ce qui est le cas de
    presque toute page terminale d'un vrai site. Reconstruisez `P` dans ces conditions, en
    laissant la ligne de `contact` entièrement nulle, et suivez la **masse totale** de
    probabilité au fil des pas.

    **Résultat attendu :** la masse ne se conserve plus. Elle vaut `0.857143` après un pas,
    `0.741572` après dix, et `0.203199` après cent. La marche fuit par le trou.

    ??? success "Corrigé"
        ```python
        A_puits = A.copy()
        A_puits[index["contact"]] = 0
        sommes = A_puits.sum(axis=1, keepdims=True)
        P_puits = np.divide(A_puits, sommes, out=np.zeros_like(A_puits), where=sommes > 0)

        v = np.ones(len(PAGES)) / len(PAGES)
        for n in [0, 1, 5, 10, 30, 100]:
            print(f"n={n:4d} : masse = {(v @ np.linalg.matrix_power(P_puits, n)).sum():.6f}")
        ```

        Une ligne nulle n'est pas une loi de probabilité, donc `P_puits` n'est plus
        stochastique et tout le raisonnement s'effondre : il n'y a plus de distribution
        stationnaire vers laquelle converger, seulement une distribution qui s'évapore.
        C'est le premier des deux problèmes que PageRank doit régler, et c'est pour cela
        qu'il existe.

## Étape 3. PageRank, depuis sa définition (25 min)

L'idée de Brin et Page tient en une phrase : une page est importante si des pages
importantes la citent. Formellement, on cherche le vecteur `r` tel que `r = r @ P`, avec
deux corrections. À chaque pas, l'internaute suit un lien avec probabilité `d`, et **saute
sur une page au hasard** avec probabilité `1 - d`. Ce saut règle d'un coup le problème du
puits et celui des groupes de pages dont on ne ressort jamais.

```python
def pagerank(P, amortissement=0.85, iterations=200, tolerance=1e-12):
    n = P.shape[0]
    v = np.ones(n) / n
    for k in range(iterations):
        suivant = amortissement * (v @ P) + (1 - amortissement) / n
        if np.abs(suivant - v).max() < tolerance:
            return suivant, k + 1
        v = suivant
    return v, iterations

rangs, iterations = pagerank(P)
print(f"convergence en {iterations} itérations, somme = {rangs.sum():.10f}")
for nom, score in sorted(zip(PAGES, rangs), key=lambda couple: -couple[1]):
    print(f"  {nom:8s} {score:.4f}")
```

!!! question "Exercice 3.1 : compter les liens ne suffit pas"
    `accueil` et `tp` reçoivent **exactement quatre liens entrants chacune**. Pourtant
    PageRank les sépare nettement. De combien, et comment l'expliquez-vous ?

    **Résultat attendu :** `tp` obtient `0.3167` et `accueil` `0.2152`, soit dix points
    d'écart à nombre de liens entrants identique. L'explication tient dans la **qualité**
    des liens, et dans le partage : `tp` est citée par `exos`, qui ne cite qu'elle et lui
    reverse donc l'intégralité de son rang. `accueil` est certes citée par `tp`, la page la
    mieux classée, mais `tp` partage son rang entre deux destinations ; ses trois autres
    citations viennent de `plan`, `biblio` et `contact`, les pages les plus faibles du
    site, dont `plan` répartit encore son rang entre cinq destinations.

    ??? success "Corrigé"
        ```python
        for nom in ["accueil", "tp"]:
            entrants = [d for d, a in LIENS if a == nom]
            print(f"{nom:8s} rang {rangs[index[nom]]:.4f}  cité par {entrants}")
        print("liens sortants de exos :", [a for d, a in LIENS if d == "exos"])
        ```

        C'est toute la différence entre PageRank et un simple comptage de citations, et
        c'est la raison pour laquelle l'algorithme a résisté au référencement abusif bien
        plus longtemps qu'un décompte. On ne truque pas facilement une quantité qui se
        définit par récurrence sur elle-même.

!!! question "Exercice 3.2 : à quoi sert l'amortissement"
    Faites varier `amortissement` entre `0.5`, `0.85` et `0.99`, et observez le nombre
    d'itérations nécessaires ainsi que l'écart entre le rang le plus fort et le plus
    faible.

    **Résultat attendu :** `27`, `63` puis `104` itérations, et un écart qui passe de
    `0.1491` à `0.2812` puis `0.3420`. Plus l'amortissement est proche de 1, plus le
    classement est contrasté, et plus le calcul est lent à converger.

    ??? success "Corrigé"
        ```python
        for d in [0.5, 0.85, 0.99]:
            r_d, it = pagerank(P, amortissement=d)
            print(f"d={d:4.2f} : {it:3d} itérations, écart {r_d.max() - r_d.min():.4f}")
        ```

        La valeur `0.85` retenue par Brin et Page n'a rien d'une constante de la nature :
        c'est un arbitrage entre le contraste du classement et le coût du calcul, à
        l'échelle du web de 1998. Un modèle utile comporte presque toujours un paramètre de
        ce genre, réglé et non démontré, et savoir lequel est une part du métier.

!!! tip "L'IA vous le donne en trois secondes"
    Demandez un PageRank à un assistant conversationnel. Une version sur deux normalise la
    matrice d'adjacence **par colonnes**, `A / A.sum(axis=0)`, parce que la littérature
    écrit souvent la matrice dans l'autre sens. Le code s'exécute, le vecteur obtenu somme
    encore à `1.0` et rien ne signale quoi que ce soit, mais le classement change : `tp`
    perd la première place au profit de `accueil`. Vérifiez-le. Il n'existe aucune
    assertion simple qui attrape cette erreur : seule la question « une ligne de ma matrice
    est-elle une loi de probabilité ? » la détecte.

    ```python
    P_colonnes = A / A.sum(axis=0, keepdims=True)
    faux, _ = pagerank(P_colonnes)
    print("lignes stochastiques :", np.allclose(P_colonnes.sum(axis=1), 1))
    print("somme du résultat    :", round(float(faux.sum()), 4))
    print("classement correct :", [PAGES[i] for i in np.argsort(-rangs)])
    print("classement faux    :", [PAGES[i] for i in np.argsort(-faux)])
    ```

Comparons maintenant à l'implémentation de référence :

```python
import scipy  # voir l'encadré ci-dessous : networkx.pagerank passe par scipy
import networkx as nx

G = nx.DiGraph()
G.add_nodes_from(PAGES)
G.add_edges_from(LIENS)
reference = nx.pagerank(G, alpha=0.85, tol=1e-12)
ecart = max(abs(reference[nom] - rangs[index[nom]]) for nom in PAGES)
print(f"écart maximal avec networkx : {ecart:.2e}")
```

!!! info "Pourquoi cet `import scipy` qui ne sert à rien"
    Il sert, et c'est instructif. `networkx.pagerank` n'est qu'une façade : le calcul réel
    est délégué à scipy, importé **à l'intérieur** de la fonction. Or le noyau Python de
    votre navigateur ne télécharge un paquet que s'il le voit comme import de premier
    niveau dans le code que vous exécutez. Sans cette ligne, l'appel échoue sur
    `ModuleNotFoundError: No module named 'scipy'` alors que scipy est pourtant disponible.
    Sur votre machine, où tout est installé d'avance, la ligne ne change rien. Retenez la
    forme générale : **les dépendances d'une bibliothèque ne sont pas toujours celles que
    votre code déclare**, et l'environnement d'exécution décide du reste.

Vingt lignes retrouvent la bibliothèque à `4e-13` près, c'est-à-dire la précision des
flottants. Ce n'est pas une raison pour réécrire networkx en production : la bibliothèque
gère les puits, les graphes non connexes, les poids et les matrices creuses de plusieurs
millions de nœuds. Mais vous savez maintenant ce qu'elle calcule, ce qui est la seule façon
de repérer le jour où elle ne calcule pas ce que vous croyez.

## Étape 4. Le même objet, sur du texte (30 min)

Remplaçons les pages par des caractères, et les liens par « quel caractère suit lequel ».
Le corpus est écrit ici même, pour que rien ne soit téléchargé :

```python
import unicodedata

CORPUS = """Maitre Corbeau, sur un arbre perche, tenait en son bec un fromage.
Maitre Renard, par l'odeur alleche, lui tint a peu pres ce langage :
He ! bonjour, Monsieur du Corbeau. Que vous etes joli ! que vous me semblez beau !
Sans mentir, si votre ramage se rapporte a votre plumage,
vous etes le Phenix des hotes de ces bois. A ces mots le Corbeau ne se sent pas de joie ;
et pour montrer sa belle voix, il ouvre un large bec, laisse tomber sa proie.
Le Renard s'en saisit, et dit : Mon bon Monsieur, apprenez que tout flatteur
vit aux depens de celui qui l'ecoute : cette lecon vaut bien un fromage, sans doute.
Le Corbeau, honteux et confus, jura, mais un peu tard, qu'on ne l'y prendrait plus.
La Cigale, ayant chante tout l'ete, se trouva fort depourvue quand la bise fut venue :
pas un seul petit morceau de mouche ou de vermisseau.
Elle alla crier famine chez la Fourmi sa voisine,
la priant de lui preter quelque grain pour subsister jusqu'a la saison nouvelle.
Je vous paierai, lui dit-elle, avant l'aout, foi d'animal, interet et principal.
La Fourmi n'est pas preteuse : c'est la son moindre defaut.
Que faisiez-vous au temps chaud ? dit-elle a cette emprunteuse.
Nuit et jour a tout venant je chantais, ne vous deplaise.
Vous chantiez ? j'en suis fort aise. Eh bien ! dansez maintenant."""


def nettoyer(texte):
    sans_accent = "".join(
        c for c in unicodedata.normalize("NFD", texte.lower())
        if unicodedata.category(c) != "Mn"
    )
    return "".join(c if c.isalpha() and c.isascii() else " " for c in sans_accent)


propre = " ".join(nettoyer(CORPUS).split())
alphabet = sorted(set(propre))
position = {c: i for i, c in enumerate(alphabet)}
print("longueur du corpus :", len(propre))
print("alphabet :", len(alphabet), "symboles :", repr("".join(alphabet)))
```

On compte ensuite les transitions, exactement comme on comptait les liens :

```python
comptes = np.zeros((len(alphabet), len(alphabet)))
for avant, apres in zip(propre, propre[1:]):
    comptes[position[avant], position[apres]] += 1

print("transitions :", int(comptes.sum()), "| cases non nulles :",
      int((comptes > 0).sum()), "sur", comptes.size)

sommes = comptes.sum(axis=1, keepdims=True)
M = np.divide(comptes, sommes, out=np.zeros_like(comptes), where=sommes > 0)
```

```python
plt.figure(figsize=(6, 5))
plt.imshow(M, cmap="viridis")
plt.xticks(range(len(alphabet)), alphabet, fontsize=7)
plt.yticks(range(len(alphabet)), alphabet, fontsize=7)
plt.title("M[a, b] = probabilité que b suive a")
plt.colorbar()
plt.show()
```

!!! question "Exercice 4.1 : ce que la matrice a appris toute seule"
    Affichez les trois successeurs les plus probables de `'q'`, de `'u'` et de l'espace.
    Que constatez-vous pour `'q'` ? Combien de cases de la matrice sont non nulles, et
    qu'est-ce que cela dit de ce qu'on peut faire d'un corpus de cette taille ?

    **Résultat attendu :** après `'q'`, la probabilité de `'u'` vaut `1.00` et toutes les
    autres sont nulles : la matrice a appris la règle orthographique du français sans que
    personne la lui énonce. L'alphabet ne compte que `25` symboles, parce que ni `k` ni `w`
    n'apparaissent dans ces deux fables. Et seules `195` cases sur `625` sont non nulles,
    pour `1228` transitions observées.

    ??? success "Corrigé"
        ```python
        for lettre in ["q", "u", " "]:
            ligne = M[position[lettre]]
            trois = np.argsort(-ligne)[:3]
            details = ", ".join(f"{alphabet[i]!r} {ligne[i]:.2f}" for i in trois)
            print(f"après {lettre!r} : {details}")
        ```

        Les deux tiers des cases valent zéro, ce qui n'a rien d'anodin : le modèle affirme
        que certaines paires sont **impossibles** alors qu'il n'a simplement jamais eu
        l'occasion de les voir. C'est le problème du zéro non observé, et toute la
        modélisation statistique du langage consiste, depuis Shannon, à lui trouver des
        remèdes. Retenez-en la forme générale : un modèle ne distingue pas tout seul ce
        qu'il a vu être faux de ce qu'il n'a pas vu.

## Étape 5. Générer, et compter les bits (25 min)

Une marche aléatoire sur cette matrice produit du texte. Le paramètre `temperature`
déforme la loi avant le tirage : en dessous de 1, elle accentue les transitions déjà
probables ; au-dessus, elle les aplatit.

```python
def generer(depart=" ", longueur=120, temperature=1.0, graine=0):
    tirage = np.random.default_rng(graine)
    sortie = [depart]
    for _ in range(longueur - 1):
        ligne = M[position[sortie[-1]]]
        if ligne.sum() == 0:
            sortie.append(" ")
            continue
        if temperature != 1.0:
            poids = np.where(ligne > 0, ligne ** (1 / temperature), 0.0)
            ligne = poids / poids.sum()
        sortie.append(alphabet[tirage.choice(len(alphabet), p=ligne)])
    return "".join(sortie)

print(repr(generer()))
```

!!! question "Exercice 5.1 : ce que règle la température"
    Générez trois textes avec `temperature` valant `0.3`, `1.0` puis `3.0`, à graine
    identique. Décrivez ce qui change, et rattachez-le à un réglage que vous connaissez
    déjà.

    **Résultat attendu :** à `0.3` le texte se fige sur quelques syllabes très fréquentes
    et se répète (`de de t pr pan t s`) ; à `1.0` il produit des morceaux plausibles de
    français (`on assereus s paurai cise yanse coralut`) ; à `3.0` il part vers des
    séquences improbables (`ppl quenttephehauci`). C'est exactement le paramètre
    `temperature` des modèles de langue que vous avez appelés au module
    [IA générative](../ia-generative/index.md).

    ??? success "Corrigé"
        ```python
        for t in [0.3, 1.0, 3.0]:
            print(f"T={t} : {generer(temperature=t)!r}")
        ```

        Aucun de ces textes n'a de sens, et c'est normal : le modèle ne regarde qu'un
        caractère en arrière. Mais la mécanique du réglage est rigoureusement celle d'un
        grand modèle de langue. Ce qui sépare cette matrice 25 × 25 d'un modèle
        contemporain n'est pas la nature de l'objet, c'est la longueur du contexte et le
        nombre de paramètres.

!!! question "Exercice 5.2 : combien de bits le modèle fait-il gagner ?"
    Comparez trois quantités, en bits par caractère : l'incertitude d'un tirage uniforme
    sur l'alphabet, celle d'un tirage selon les fréquences des lettres, et l'entropie
    conditionnelle du modèle à un caractère de contexte.

    **Résultat attendu :** `4.6439` bits pour l'uniforme, `3.9813` pour les fréquences
    seules, `2.9321` pour le modèle de bigrammes. Connaître la lettre précédente fait donc
    gagner plus d'un bit par caractère par rapport aux seules fréquences.

    ??? success "Corrigé"
        ```python
        frequences = sommes.ravel() / sommes.sum()
        conditionnelle = 0.0
        for i in range(len(alphabet)):
            ligne = M[i][M[i] > 0]
            if ligne.size:
                conditionnelle += frequences[i] * (-np.sum(ligne * np.log2(ligne)))
        marginale = -np.sum(frequences[frequences > 0] * np.log2(frequences[frequences > 0]))
        print(f"uniforme  : {np.log2(len(alphabet)):.4f} bits/caractère")
        print(f"fréquences: {marginale:.4f} bits/caractère")
        print(f"bigrammes : {conditionnelle:.4f} bits/caractère")
        ```

        Ces trois nombres sont une entropie, une entropie conditionnelle, et leur écart est
        une information mutuelle : les notions du
        [TP10 d'IA prédictive](../ia-predictive/tp10-theorie-information.md), appliquées
        ici au langage. Et cette quantité a un nom dans le monde des modèles de langue :
        `2` puissance l'entropie conditionnelle est la **perplexité**, la mesure par
        laquelle on compare deux modèles depuis soixante-dix ans.

## Ce qu'il faut retenir

Une matrice de transition n'est rien d'autre qu'un tableau de lois de probabilité rangées
en lignes, et cette contrainte est tout ce qui distingue le calcul juste du calcul faux.
Multiplier répétitivement par cette matrice fait converger n'importe quel point de départ
vers la distribution stationnaire, ce qui est la puissance itérée du TP1 sous un autre nom.
PageRank ajoute à cela un saut aléatoire, qui répare les puits et contraste le classement,
et il montre qu'une citation vaut ce que vaut celui qui cite. Enfin, le même objet appliqué
à du texte est un modèle de langue : la matrice apprend seule que `q` appelle `u`, la
température y règle le même curseur que dans un grand modèle, et l'entropie conditionnelle
dit en bits ce que le contexte fait gagner.

## Auto-évaluation

- [ ] Je sais construire une matrice de transition à partir d'un graphe, et dire pourquoi
      ce sont les lignes qui somment à 1.
- [ ] Je sais calculer la distribution après `n` pas, et j'ai constaté qu'elle oublie son
      point de départ.
- [ ] Je sais expliquer ce qu'un nœud sans lien sortant fait à la masse de probabilité.
- [ ] Je sais implémenter PageRank en une vingtaine de lignes et retrouver networkx.
- [ ] Je sais dire pourquoi deux pages à nombre de citations égal n'ont pas le même rang.
- [ ] Je sais construire une matrice de bigrammes sur un texte et l'interpréter.
- [ ] Je sais ce que fait la température, et ce que mesure l'entropie conditionnelle.

[Le QCM du TP2](qcm/qcm_tp2.html){ .md-button target=_blank }
[Passer au TP3](tp3-gradient-bifurcation.md){ .md-button .md-button--primary }
[Revenir au TP1](tp1-matrice-svd.md){ .md-button }
