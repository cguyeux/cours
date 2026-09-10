---
hide:
  - navigation
---

# Programmer, en 2026

Vous entrez en informatique l'année où une machine écrit du code mieux et plus vite
que vous ne le ferez avant longtemps. Vous allez le constater dès la première séance :
demandez à un assistant conversationnel un programme qui teste si un nombre est premier,
et vous l'aurez en trois secondes, correctement indenté, avec des commentaires.

Alors la question mérite d'être posée franchement, plutôt que d'être esquivée : à quoi bon
apprendre à programmer ?

## Ce qui a changé de place

La réponse tient en une phrase. On ne vous paiera pas pour taper du code, on vous paiera
pour décider s'il est bon. C'était déjà largement vrai avant, ça l'est devenu complètement.
Un développeur passe la majeure partie de son temps à lire, comprendre, corriger et
arbitrer, pas à produire des lignes.

Or un texte produit par un modèle de langue est un texte **plausible**. La plupart du temps
il est aussi juste, ce qui est précisément le problème : rien ne distingue à l'œil nu les
deux situations. Cinq raisons, que vous vérifierez vous-même dans les travaux pratiques
plutôt que de me croire sur parole.

**Un code plausible n'est pas un code juste.** Le test de primalité que vous obtiendrez en
trois secondes répond peut-être « oui » pour 1, ou « oui » pour un nombre négatif, ou tombe
en panne sur 2. Vous ne le saurez qu'en sachant ce qu'est un nombre premier et en pensant à
essayer ces cas. C'est le TP2.

**On ne demande bien que ce qu'on sait nommer.** Formuler une demande précise suppose de
connaître les objets dont on parle : une matrice, un système linéaire, un polynôme, un
invariant de boucle. Sans ce vocabulaire, vous obtiendrez une réponse à une autre question
que la vôtre, et vous ne le remarquerez pas.

**Les nombres de votre ordinateur mentent.** `0.1 + 0.2` ne vaut pas `0.3`, et aucun modèle
ne vous préviendra spontanément que la comparaison que vous venez d'écrire est fausse une
fois sur mille. Ces mille fois, c'est un virement bancaire ou une dose de médicament.
C'est le TP1.

**Juste ne veut pas dire utilisable.** Deux programmes peuvent donner la même réponse, l'un
en un dixième de seconde, l'autre en dix minutes. Sur un million de données, l'écart décide
si le produit existe ou non. Mesurer ce coût, c'est le fil rouge de tous les TP, et c'est
l'objet même de ce module.

**Et il reste les moments où vous êtes seul.** En examen, en entretien technique, devant un
client ou un collègue qui vous demande pourquoi ça plante en production. Là, ce que vous
savez est ce que vous avez.

## Le pacte

Dans ce module, utiliser une intelligence artificielle est autorisé et même encouragé.
Trois règles, et elles ne sont pas négociables.

1. Vous devez pouvoir expliquer chaque ligne que vous rendez, ligne par ligne, à l'oral.
2. Vous devez avoir cherché le cas où le code proposé se trompe, et l'avoir écrit.
3. Les évaluations se passent sans assistant. Ce que vous n'avez pas compris ne vous
   servira à rien ce jour-là.

Chaque TP contient un encadré qui vous demande explicitement de faire produire la solution
par l'assistant de votre choix, puis de la casser. C'est un exercice à part entière, et
c'est probablement le plus utile de tous.

## Par où commencer

[Le module en un coup d'œil](outils-fondamentaux/index.md){ .md-button .md-button--primary }
[Mise en route](outils-fondamentaux/demarrage.md){ .md-button }

Vous n'avez rien à installer : tous les exercices se font dans votre navigateur, sur
Windows, macOS ou Linux indifféremment. La page de mise en route explique aussi comment
installer Python sur votre machine si vous le souhaitez.
