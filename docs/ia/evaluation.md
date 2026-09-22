# Projet et évaluation des modules d'IA

Cette page couvre **les deux modules d'IA de troisième année**, générative et prédictive :
un seul dépôt, un seul projet, une seule note. Elle dit ce que vous avez à rendre, à quelle
date, par quel moyen, et comment votre travail sera noté. Lisez-la tôt : le choix du sujet
compte davantage que le nombre de lignes écrites.

## Ce qu'il faut rendre

Un dépôt GitHub, contenant deux choses distinctes et clairement séparées.

D'une part, **vos solutions aux TP** des deux modules : vos réponses aux exercices, telles
que vous les avez écrites en séance et retravaillées ensuite.

D'autre part, **un projet personnel** de votre choix. Il est libre, mais il doit mobiliser
les notions vues en TP. Du côté génératif : appels de modèles de langue, sorties
structurées, recherche augmentée par récupération, agents et outils, multimodalité. Du côté
prédictif : manipulation de données avec pandas, classification et régression, clustering,
réduction de dimension, gradient boosting, séries temporelles, prétraitement, explicabilité.
Vous pouvez vous appuyer sur un seul des deux versants ou sur les deux ; personne n'exige
les deux. C'est cette partie qui porte la note.

Rangez le tout dans des répertoires séparés, par exemple `tp-generative/`, `tp-predictive/`
et `projet/`, et dites-le dans le `README.md` à la racine.

!!! danger "Aucune clé d'API dans le dépôt, jamais"
    Les TP d'IA générative utilisent des clés personnelles. Une clé publiée sur GitHub est
    lue et exploitée par des robots en quelques minutes, et elle est facturée à son
    propriétaire. Les clés vivent dans un fichier `.env` **non suivi par Git**, et
    `.gitignore` doit le mentionner avant votre premier envoi. Vérifiez aussi votre
    historique : une clé effacée dans le dernier commit reste lisible dans les précédents,
    et il faut alors la révoquer plutôt que la masquer. Une clé trouvée dans un rendu est
    signalée et coûte des points, au titre de la qualité du travail.

## Pour quand

**Quatorze jours après votre dernière séance de TP.** La date exacte dépend de votre
groupe ; elle vous est confirmée en séance. Passé ce délai, le dépôt est considéré dans
l'état où il se trouve.

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
| Cœur du sujet | **Pertinence** : le sujet mobilise réellement les notions des modules, et pas seulement en surface | 4 |
| | **Profondeur d'exploitation** : jusqu'où vous poussez ces notions | 6 |
| | **Complexité et ambition**, rapportées à la taille du groupe | 4 |
| Second ordre | **Qualité du code** : lisibilité, structuration, noms de variables, absence de copier-coller massif | 2 |
| | **Documentation** : un `README` qui dit ce que fait le projet, comment le lancer, et ce qu'on doit en observer | 2 |
| | **Originalité et regard critique** : angle personnel, limites reconnues, résultats interprétés plutôt que simplement affichés | 2 |

Le critère le plus discriminant est de loin la **profondeur d'exploitation**. Sur ces
modules, il prend une forme particulière : appeler un modèle est devenu trivial, donc ce
n'est plus l'appel qui vaut des points, c'est ce que vous en faites et surtout **ce que vous
mesurez**.

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

Un même outil peut servir à presque rien ou porter tout un projet. Voici, sur ces modules,
trois manières de traiter un sujet, de la plus faible à la plus forte.

!!! failure "Faible : l'outil est présent, mais il ne fait rien"
    Un agent conversationnel qui relaie les réponses d'une API derrière une interface. Ou un
    carnet qui charge un jeu de données d'exemple, appelle `fit` puis `predict`, et affiche
    un taux de bonnes réponses de 0,93. Tout fonctionne, rien n'est faux, et pourtant aucune
    question n'a été posée : la bibliothèque est *appelée*, elle n'est pas *exploitée*, et
    le chiffre affiché ne veut rien dire tant que personne n'a demandé à quoi il se compare.

!!! warning "Correct : le système est construit et il est évalué"
    Une recherche augmentée par récupération sur vos propres documents, qui répond
    correctement à des questions que vous posez. Ou une comparaison de trois classifieurs en
    validation croisée, avec la métrique justifiée par la nature du problème plutôt que
    choisie par habitude. Il y a un système, un protocole, une conclusion. C'est un projet
    honnête.

!!! success "Fort : le système est construit, mesuré, et ses limites sont établies"
    Une recherche augmentée dont vous **mesurez** la qualité sur un jeu de questions que
    vous avez écrit, en quantifiant la part de réponses effectivement fondées sur les
    documents, et en étudiant ce que change la taille des fragments ou l'ajout d'un
    réordonnancement : le projet répond alors à « est-ce que ça marche, et dans quels cas
    est-ce que ça échoue ? » plutôt qu'à « est-ce que ça tourne ? ». Ou une chaîne à sorties
    structurées validée par schéma, dont vous mesurez le taux d'échec de validation sur
    plusieurs centaines d'appels et pour laquelle vous construisez une stratégie de reprise.
    Ou un pipeline prédictif complet où le prétraitement est ajusté **à l'intérieur** de la
    validation croisée pour éviter la fuite de données, où les probabilités sont calibrées,
    où l'explication par importance des variables sert à repérer une variable suspecte, et
    où vous discutez pour finir ce que le modèle établit et ce qu'il n'établit pas, la
    corrélation n'étant pas la causalité.

    Le point commun de ces trois-là : on y trouve un résultat que personne n'avait donné
    d'avance, obtenu par le code, et discuté. Notez aussi qu'aucun ne se contente d'un score
    global : chacun a cherché où le système se trompe.

## L'usage de l'intelligence artificielle

Il est **autorisé, et il n'est pas obligatoire pour avoir une bonne note**. Sur ces modules,
l'IA est d'ailleurs l'objet d'étude autant qu'un outil de travail : il serait absurde de
vous l'interdire.

Deux choses méritent d'être dites franchement. D'abord, un assistant produit très vite un
projet moyen : correct, propre, générique, et parfaitement interchangeable avec celui du
voisin. Ces projets se reconnaissent, et ils obtiennent des notes moyennes. Ensuite, à
quantité et à complexité égales, un travail visiblement assisté est attendu **plus haut** :
si la machine a fait le travail de frappe, elle vous a libéré du temps, et ce temps doit se
voir quelque part.

Ce qui est valorisé, c'est la **touche humaine** : un sujet qui vous ressemble, une question
que vous vous êtes posée, un protocole d'évaluation que vous avez conçu, un regard critique
sur vos propres résultats, une limite que vous avez identifiée vous-même, un détour par une
idée qui n'a pas marché et que vous expliquez. Sur des modules où l'outil fait beaucoup, le
jugement est précisément ce qui reste à l'humain, et c'est ce qui se note.

Si vous utilisez un assistant, dites-le simplement dans votre `README` : pour quoi, et ce
que vous avez vérifié vous-même. Cette honnêteté n'a jamais coûté de points.

## Quelques questions qui reviennent

**Peut-on travailler à plusieurs ?** Oui, et dites-le. Les attentes de quantité sont
proportionnelles : un binôme rend deux fois plus qu'un étudiant seul, un trinôme trois fois.
Précisez qui a fait quoi.

**Faut-il payer des appels d'API ?** Non. Un projet peut très bien tenir sur les offres
gratuites, sur un modèle exécuté localement, ou entièrement du côté prédictif, qui ne
demande aucune clé. Le budget dépensé n'entre dans aucun critère.

**Faut-il un gros jeu de données ?** Non. Un petit jeu que vous comprenez, dont vous
connaissez l'origine et les biais, vaut mieux qu'un gros jeu téléchargé sans examen. Une
part importante du travail sérieux consiste justement à regarder ses données avant de les
modéliser.

**Et si mon modèle donne de mauvais résultats ?** Rendez-le quand même, avec l'analyse. Un
modèle qui échoue et dont vous établissez *pourquoi* il échoue vaut plus qu'un score flatteur
non interrogé. C'est vrai en cours comme ailleurs : un résultat contre-intuitif bien mesuré
est un résultat.
