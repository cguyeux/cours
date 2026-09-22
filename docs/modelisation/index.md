# Modélisations mathématiques

Travaux pratiques de troisième année du BUT informatique, ressource R5.Real.12. Trois
séances de deux heures, qui vont chercher les mathématiques qui se trouvent sous les
bibliothèques que vous utilisez déjà.

## Pourquoi ce module

Les deux autres modules de troisième année vous ont appris à **appeler** des bibliothèques :
un modèle de langue dans [IA générative](../ia-generative/index.md), un modèle prédictif
dans [IA prédictive](../ia-predictive/index.md). Celui-ci fait l'inverse. À chaque séance,
vous implémentez à la main l'objet mathématique qui est à l'intérieur, vous le comparez à la
bibliothèque, et vous mesurez l'écart. Le but n'est pas de vous faire réécrire numpy ; c'est
de vous rendre capables de choisir, de justifier ce choix par une mesure, et de reconnaître
le moment où la méthode que tout le monde emploie ne convient pas à votre problème.

C'est d'ailleurs l'énoncé exact de la compétence visée : choisir et utiliser des
bibliothèques et des méthodes dédiées à un domaine d'application.

## Les séances

| Séance | Sujet | Ce que vous saurez faire |
|---|---|---|
| [TP1](tp1-matrice-svd.md) | Ce qu'une matrice sait faire | valeurs singulières, approximation de rang faible, rang effectif, choisir entre décomposition complète et méthode itérative |
| [TP2](tp2-marche-aleatoire.md) | La marche aléatoire, du graphe au texte | matrice de transition, distribution stationnaire, PageRank, générateur de texte par bigrammes |
| [TP3](tp3-gradient-bifurcation.md) | Dériver, descendre, diverger | dérivation automatique par nombres duaux, descente de gradient, seuil exact du pas, et le régime chaotique qui sépare la convergence de la divergence |

## Ce que ce module ne refait pas

L'analyse en composantes principales et le fléau de la dimension sont traités dans le
[TP2bis d'IA prédictive](../ia-predictive/tp2bis-reduction-dimension.md), l'entropie et
l'information mutuelle dans le
[TP10](../ia-predictive/tp10-theorie-information.md). L'optimisation combinatoire, le
simplexe et les heuristiques relèvent d'une autre ressource du semestre. Les pages de ce
module renvoient vers ces séances plutôt que de les répéter.

## Comment travailler

Tout s'exécute avec numpy, matplotlib et pillow, sans clé d'API et sans téléchargement :
vous pouvez donc travailler dans le carnet fourni en tête de chaque TP, directement dans
votre navigateur, ou en local si vous préférez. **Le code de chaque corrigé est exécuté à
chaque construction du site** : chaque valeur annoncée dans un « résultat attendu » a été
réellement calculée par la machine, pas devinée.

## Projet et évaluation

Le module est validé par un **projet personnel** accompagné de **vos solutions aux TP**, le
tout dans un dépôt GitHub à m'envoyer **quatorze jours après la dernière séance**. Le sujet
du projet est libre, mais il doit exploiter réellement les notions vues ici, et c'est la
profondeur de cette exploitation qui fait la note.

[Ce qu'il faut rendre, quand, et comment c'est noté](evaluation.md){ .md-button .md-button--primary }
