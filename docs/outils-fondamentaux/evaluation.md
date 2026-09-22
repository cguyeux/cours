# Projet et évaluation

Cette page dit ce que vous avez à rendre pour ce module, à quelle date, par quel moyen, et
comment votre travail sera noté. Lisez-la dès maintenant plutôt que la veille du rendu : le
choix du sujet compte davantage que le nombre de lignes écrites, et ce choix se fait tôt.

## Ce qu'il faut rendre

Un dépôt GitHub, contenant deux choses distinctes et clairement séparées.

D'une part, **vos solutions aux TP** du module. Ce sont vos réponses aux exercices, telles
que vous les avez écrites pendant les séances et retravaillées après. On n'attend pas la
perfection : on attend un travail réel, qui montre ce que vous avez compris et où vous avez
buté.

D'autre part, **un projet personnel** de votre choix. Il est libre, mais il doit mobiliser
les notions vues en TP : calcul numérique et flottants, arithmétique, polynômes et recherche
de racines, matrices et systèmes linéaires, géométrie du plan. C'est cette partie qui porte
la note.

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

Le critère le plus discriminant est de loin la **profondeur d'exploitation**, et c'est celui
sur lequel les projets se séparent le plus. La section suivante le détaille par l'exemple.

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
    Un programme qui trace la courbe d'une fonction avec matplotlib et calcule quelques
    PGCD. Tout fonctionne, rien n'est faux, et pourtant il n'y a aucun problème résolu :
    les notions du module sont *affichées*, pas *employées*. C'est le niveau qui déçoit le
    plus souvent, parce que le travail fourni est réel mais mal dirigé.

!!! warning "Correct : une notion est implémentée et mise à l'épreuve"
    Une implémentation de la méthode de Newton, comparée à la dichotomie sur plusieurs
    fonctions, avec le nombre d'itérations de chacune et un cas où Newton échoue. Il y a une
    vraie question, une mesure, et une conclusion. C'est un projet honnête.

!!! success "Fort : la notion sert à construire quelque chose qui tient debout"
    Un solveur d'équations qui **détecte** les situations où Newton cycle ou diverge et
    bascule automatiquement sur la dichotomie, en justifiant le critère de bascule par des
    mesures ; ou un chiffrement RSA jouet, appuyé sur l'exponentiation modulaire rapide et
    l'algorithme d'Euclide étendu, accompagné d'une attaque par factorisation qui établit
    expérimentalement la taille de clé à partir de laquelle l'attaque devient hors de
    portée ; ou encore un tracé des bassins d'attraction de Newton dans le plan complexe,
    avec l'étude de la frontière entre bassins.

    Le point commun de ces trois-là : on y trouve un résultat que personne n'avait donné
    d'avance, obtenu par le code, et discuté.

## L'usage de l'intelligence artificielle

Il est **autorisé, et il n'est pas obligatoire pour avoir une bonne note**. Vous pouvez vous
en servir pour écrire du code, comprendre une erreur ou explorer une piste.

Deux choses méritent d'être dites franchement. D'abord, un assistant produit très vite un
projet moyen : correct, propre, générique, et parfaitement interchangeable avec celui du
voisin. Ces projets se reconnaissent, et ils obtiennent des notes moyennes. Ensuite, à
quantité et à complexité égales, un travail visiblement assisté est attendu **plus haut** :
si la machine a fait le travail de frappe, elle vous a libéré du temps, et ce temps doit se
voir quelque part.

Ce qui est valorisé, c'est la **touche humaine** : un sujet qui vous ressemble, une question
que vous vous êtes posée, un regard critique sur vos propres résultats, une limite que vous
avez identifiée vous-même, un détour par une idée qui n'a pas marché et que vous expliquez.
Cela ne s'obtient pas en trois secondes, et cela se voit tout autant.

Si vous utilisez un assistant, dites-le simplement dans votre `README` : pour quoi, et ce
que vous avez vérifié vous-même. Cette honnêteté n'a jamais coûté de points.

## Quelques questions qui reviennent

**Peut-on travailler à plusieurs ?** Oui, et dites-le. Les attentes de quantité sont
proportionnelles : un binôme rend deux fois plus qu'un étudiant seul, un trinôme trois fois.
Précisez qui a fait quoi.

**Faut-il un sujet spectaculaire ?** Non. Un sujet modeste creusé sérieusement vaut mieux
qu'un sujet ambitieux resté en surface. Le barème récompense la profondeur, pas l'affiche.

**Peut-on utiliser une bibliothèque qui fait tout le travail ?** Vous pouvez l'utiliser,
mais elle ne comptera pas à votre crédit. Si le cœur de votre projet est un appel de
fonction, le cœur de votre projet est vide. Employez-la plutôt comme point de comparaison
avec votre propre implémentation : c'est exactement la démarche des TP.

**Et si mon projet ne marche pas complètement ?** Rendez-le quand même, en expliquant où ça
coince et ce que vous avez essayé. Un échec analysé rapporte plus qu'un silence, et ce
module passe son temps à montrer que ce qui échoue est instructif.
