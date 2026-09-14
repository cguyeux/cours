# Outils fondamentaux : les mathématiques en Python

Bienvenue dans la partie pratique de la ressource **R1.07, outils mathématiques
fondamentaux**, du BUT informatique, premier semestre. Cinq séances de travaux pratiques,
plus une séance de prolongement, pendant lesquelles vous apprendrez Python en le faisant
travailler sur des objets mathématiques : des entiers, des nombres premiers, des
polynômes, des fonctions, des matrices, et pour finir des points et des figures du plan.

## Ce que vise ce module

Le programme national assigne à cette ressource une compétence précise, qu'il vaut la peine
de citer telle quelle : « proposer des applications informatiques optimisées en fonction de
critères spécifiques, temps d'exécution, précision, consommation de ressources ».

Retenez les trois mots. On ne vous demandera pas seulement d'écrire un programme qui donne
la bonne réponse. On vous demandera de savoir **combien de temps** il met, **avec quelle
précision** il répond, et **ce qu'il coûte**. Un programme juste mais mille fois trop lent
est un programme inutilisable ; un programme rapide mais faux est un programme dangereux.
C'est exactement ce qui sépare quelqu'un qui sait programmer de quelqu'un qui sait recopier
du code.

## Les cinq séances

| Séance | Sujet | Ce que vous saurez faire |
|---|---|---|
| [Mise en route](demarrage.md) | Exécuter du Python | lancer un programme, lire une erreur, sauvegarder son travail |
| [TP1](tp1-calcul-numerique.md) | Calcul numérique | entiers exacts, flottants approchés, boucles, fonctions |
| [TP2](tp2-arithmetique.md) | Arithmétique et nombres premiers | divisibilité, Euclide, crible, et mesurer un temps de calcul |
| [TP3](tp3-polynomes-fonctions.md) | Polynômes et fonctions | évaluer, dériver, tracer, trouver une racine |
| [TP4](tp4-matrices-gauss.md) | Matrices et systèmes | produit matriciel, pivot de Gauss, numpy |
| [TP5](tp5-synthese.md) | Synthèse | un problème complet, de bout en bout |
| [TP6](tp6-geometrie-plan.md) | Géométrie du plan, en prolongement | vecteurs, aires, intersections, point dans un polygone |

Chaque TP se termine par une liste d'auto-évaluation, ce que vous devez savoir faire avant
la séance suivante, et par un QCM de dix questions corrigées immédiatement, à faire après
la séance pour vérifier ce qui est resté :
[TP1](qcm/qcm_tp1.html){ target=_blank },
[TP2](qcm/qcm_tp2.html){ target=_blank },
[TP3](qcm/qcm_tp3.html){ target=_blank },
[TP4](qcm/qcm_tp4.html){ target=_blank },
[TP5](qcm/qcm_tp5.html){ target=_blank },
[TP6](qcm/qcm_tp6.html){ target=_blank }.

Le [mémento Python](memento.md) rassemble sur une seule page tout ce dont vous avez besoin
pour ces séances. C'est le seul document autorisé pendant les évaluations, alors prenez
l'habitude de le consulter dès maintenant plutôt que de chercher ailleurs.

## Comment travailler

Chaque TP est écrit pour être fait dans l'ordre, du début à la fin, en une séance. Les
exercices sont numérotés et chacun annonce le **résultat attendu** : vous savez donc seul si
vous avez réussi, sans attendre que je passe dans les rangs.

Sous chaque exercice se trouve un corrigé, replié. Ouvrez-le sans culpabilité si vous êtes
bloqué plus de dix minutes, mais lisez-le vraiment au lieu de le recopier : un corrigé lu
et compris vaut mieux qu'un exercice raté, un corrigé recopié ne vaut rien.

Chaque TP se termine par une partie « Entraînement et approfondissement », qui ne tient pas
dans la séance : elle est à faire chez vous, ou en séance si vous avez terminé, et elle
**est** au programme de l'évaluation. Un TP fait en séance et jamais rouvert ensuite est
un TP à moitié fait.

Certaines parties sont marquées « pour aller plus loin ». Elles, en revanche, ne sont pas
au programme de l'évaluation. Faites-les si vous avez terminé, ignorez-les sinon, et ne
vous laissez pas intimider par ceux qui les font.

## Intelligence artificielle : le pacte

Vous avez tous accès à un assistant capable d'écrire ces programmes. L'interdire serait
absurde et invérifiable. Le pacte de ce module, rappelé depuis la [page d'accueil](../index.md),
tient donc en trois règles : vous devez pouvoir expliquer chaque ligne rendue, vous devez
avoir cherché où le code proposé se trompe, et les évaluations se passent sans assistant.

Chaque TP contient un encadré de ce genre :

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à l'assistant de votre choix d'écrire la fonction de l'exercice, puis
    trouvez un cas où sa réponse est fausse, trop lente, ou répond à côté. Notez ce cas.
    C'est un exercice à part entière, et vous serez interrogé dessus.

Ce n'est pas un exercice de défiance. C'est la compétence que l'on vous paiera pour avoir.

## Une remarque sur les nombres premiers

Le programme national de cette ressource parle de calcul numérique et algébrique, de
matrices, de polynômes et de fonctions. Les nombres premiers n'y figurent pas explicitement,
et pourtant ils occupent une séance entière. C'est délibéré : ils offrent le meilleur
terrain qui soit pour éprouver le coût d'un algorithme. Le même problème, tester si un
nombre est premier, se résout de trois manières qui donnent toutes la bonne réponse, et
dont les temps de calcul diffèrent d'un facteur un million. Aucun autre sujet du programme
ne rend cette leçon aussi tangible en une séance.
