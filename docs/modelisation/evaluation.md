# Projet et évaluation

Cette page dit ce que vous avez à rendre pour ce module, à quelle date, par quel moyen, et
comment votre travail sera noté. Lisez-la dès la première séance : sur ce module plus
qu'ailleurs, c'est le choix du sujet qui décide de la note, et ce choix se fait tôt.

## Ce qu'il faut rendre

Un dépôt GitHub, contenant deux choses distinctes et clairement séparées.

D'une part, **vos solutions aux TP** du module : vos réponses aux exercices, telles que vous
les avez écrites en séance et retravaillées ensuite. Le carnet fourni en tête de chaque TP
est fait pour cela.

D'autre part, **un projet personnel** de votre choix. Il est libre, mais il doit mobiliser
les notions vues en TP : décomposition en valeurs singulières et approximation de rang
faible, méthodes itératives, matrices de transition et marches aléatoires, PageRank,
modèles de langue élémentaires et entropie, dérivation automatique, descente de gradient,
conditionnement. En pratique : numpy, et selon votre sujet networkx, scipy ou matplotlib.
C'est cette partie qui porte la note.

Rangez les deux dans des répertoires séparés, par exemple `tp/` et `projet/`, et dites-le
dans le `README.md` à la racine.

## Pour quand

**Quatorze jours après votre dernière séance de TP du module.** La date exacte dépend de
votre groupe ; elle vous est confirmée en séance. Passé ce délai, le dépôt est considéré
dans l'état où il se trouve.

## Comment l'envoyer

Envoyez le lien de votre dépôt par courriel à **christophe.guyeux@umlp.fr**, en indiquant
votre nom, votre groupe, et le nom des autres membres si vous travaillez à plusieurs.

Si votre dépôt est privé, pensez à m'y donner accès, ou rendez-le public le temps de la
correction. Un lien que je ne peux pas ouvrir équivaut à un rendu absent, et je ne relance
personne.

## Comment c'est noté

La note du **projet** est sur 20. Les **solutions de TP** la modulent ensuite de **deux
points en plus ou en moins**. La note finale reste évidemment comprise entre 0 et 20.

### Le projet, sur 20

| Bloc | Critère | Points |
|---|---|---|
| Cœur du sujet | **Pertinence** : le sujet mobilise réellement les notions du module, et pas seulement en surface | 4 |
| | **Profondeur d'exploitation** : jusqu'où vous poussez ces notions | 6 |
| | **Complexité et ambition**, rapportées à la taille du groupe | 4 |
| Second ordre | **Qualité du code** : lisibilité, structuration, noms de variables, absence de copier-coller massif | 2 |
| | **Documentation** : un `README` qui dit ce que fait le projet, comment le lancer, et ce qu'on doit en observer | 2 |
| | **Originalité et regard critique** : angle personnel, limites reconnues, résultats interprétés plutôt que simplement affichés | 2 |

Le critère le plus discriminant est de loin la **profondeur d'exploitation**. Ce module a
passé trois séances à faire la différence entre appeler une bibliothèque et comprendre ce
qu'elle calcule ; l'évaluation fait la même différence.

### La modulation par les TP, de -2 à +2

| Situation | Effet |
|---|---|
| Tous les TP traités et corrects, avec des essais personnels au-delà de l'énoncé | +2 |
| La grande majorité traitée et correcte | +1 |
| Environ la moitié, ou un traitement superficiel | 0 |
| Quelques exercices épars seulement | -1 |
| Aucune solution rendue | -2 |

Rendre ses TP n'est donc pas optionnel : c'est deux points d'écart, soit davantage que ce
qui sépare souvent deux projets voisins.

## Ce qui fait la différence : trois exemples

Un même outil peut servir à presque rien ou porter tout un projet. Voici, sur ce module,
trois manières de traiter un sujet, de la plus faible à la plus forte.

!!! failure "Faible : l'outil est présent, mais il ne fait rien"
    Un programme qui charge un graphe et l'affiche avec networkx, en couleurs. Ou qui
    applique `np.linalg.svd` à une image et montre le résultat pour trois valeurs de rang.
    Tout fonctionne, rien n'est faux, et pourtant aucune question n'a été posée : la
    bibliothèque est *appelée*, elle n'est pas *exploitée*. C'est le niveau qui déçoit le
    plus souvent, parce que le travail fourni est réel mais mal dirigé.

!!! warning "Correct : une notion est reconstruite et confrontée à la référence"
    Une implémentation de PageRank à partir de sa définition, comparée à celle de networkx,
    avec l'écart mesuré et l'effet de l'amortissement sur le classement. Il y a une vraie
    question, une mesure, et une conclusion. C'est un projet honnête.

!!! success "Fort : la notion sert à construire quelque chose qui tient debout"
    Un réseau réel (transports, citations, collaborations, pages d'un site) sur lequel vous
    extrayez un **arbre couvrant de poids minimal**, en comparant Kruskal et Prim, en
    mesurant leurs temps sur des tailles croissantes et en interprétant l'arbre obtenu ; ou
    un moteur de recommandation par SVD tronquée, où le rang retenu est **justifié** par
    l'énergie conservée plutôt que choisi au hasard, et dont la qualité est mesurée sur des
    données mises de côté ; ou un mini-système de dérivation automatique par nombres duaux
    qui entraîne une régression logistique, avec l'étude du seuil de pas au-delà duquel la
    descente cesse de converger ; ou un PageRank thématique sur un corpus que vous avez
    collecté, avec l'étude de ce que le choix du vecteur de personnalisation change au
    classement.

    Le point commun de ces quatre-là : on y trouve un résultat que personne n'avait donné
    d'avance, obtenu par le code, et discuté. C'est exactement ce que le module appelle
    mesurer l'écart.

## L'usage de l'intelligence artificielle

Il est **autorisé, et il n'est pas obligatoire pour avoir une bonne note**. Vous pouvez vous
en servir pour écrire du code, comprendre une erreur ou explorer une piste.

Deux choses méritent d'être dites franchement. D'abord, un assistant produit très vite un
projet moyen : correct, propre, générique, et parfaitement interchangeable avec celui du
voisin. Ces projets se reconnaissent, et ils obtiennent des notes moyennes. Ensuite, à
quantité et à complexité égales, un travail visiblement assisté est attendu **plus haut** :
si la machine a fait le travail de frappe, elle vous a libéré du temps, et ce temps doit se
voir quelque part.

Vous avez d'ailleurs rencontré la limite de ces outils à chaque séance, dans les encadrés
« L'IA vous le donne en trois secondes » : le code proposé s'exécute, ne lève aucune erreur,
et calcule autre chose que ce que vous croyez. Un projet qui repose sur du code non vérifié
finit par le payer, et la vérification, elle, ne s'automatise pas.

Ce qui est valorisé, c'est la **touche humaine** : un sujet qui vous ressemble, une question
que vous vous êtes posée, un regard critique sur vos propres résultats, une limite que vous
avez identifiée vous-même, un détour par une idée qui n'a pas marché et que vous expliquez.

Si vous utilisez un assistant, dites-le simplement dans votre `README` : pour quoi, et ce
que vous avez vérifié vous-même. Cette honnêteté n'a jamais coûté de points.

## Quelques questions qui reviennent

**Peut-on travailler à plusieurs ?** Oui, et dites-le. Les attentes de quantité sont
proportionnelles : un binôme rend deux fois plus qu'un étudiant seul, un trinôme trois fois.
Précisez qui a fait quoi.

**Faut-il réécrire numpy ?** Non, et ce n'est pas le but. Le module vous demande de savoir
ce qu'une bibliothèque calcule, pas de la remplacer. Une implémentation à la main **comparée
à la bibliothèque** est la démarche attendue ; une implémentation à la main qui ignore la
bibliothèque est un travail inutilement risqué.

**Mon sujet peut-il recouper un autre module ?** Oui, à condition que la partie notée ici
relève bien de ce module. Un projet qui prédit quelque chose avec un modèle tout fait relève
de l'IA prédictive ; le même projet devient recevable ici s'il s'appuie sur l'objet
mathématique, par exemple la réduction de dimension conduite et justifiée par vous.

**Et si mon projet ne marche pas complètement ?** Rendez-le quand même, en expliquant où ça
coince et ce que vous avez essayé. Un échec analysé rapporte plus qu'un silence, et ce
module passe son temps à montrer que ce qui échoue est instructif : Newton qui cycle,
Hilbert mal conditionnée, la descente qui devient chaotique.
