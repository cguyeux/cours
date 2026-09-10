# À propos

Ce site rassemble les supports de travaux pratiques de Christophe Guyeux, département
informatique de l'IUT Nord Franche-Comté, université Marie et Louis Pasteur.

## Pourquoi ce site existe

Ces supports étaient hébergés sur le serveur `cours-info` de l'IUT. Depuis la rentrée 2026,
sa consultation exige une connexion au réseau privé de l'université, dont les étudiants ne
disposent pas. Un support de cours qu'on ne peut pas ouvrir chez soi ne sert à rien : le
voici donc sur une adresse publique, sans compte à créer, sans réseau privé, et lisible sur
un téléphone.

Le site est entièrement statique. Il ne dépose aucun cookie, n'embarque aucune mesure
d'audience, et ne charge aucune ressource depuis un service tiers : ni police de caractères
distante, ni bibliothèque externe. Votre adresse IP ne part nulle part ailleurs qu'ici.

## Contenu et licence

Le contenu est publié sous licence [Creative Commons BY-NC-SA
4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr) : vous pouvez le reprendre,
le modifier et l'utiliser, à condition de citer l'auteur, de ne pas en faire un usage
commercial, et de partager vos modifications aux mêmes conditions. Les collègues qui
souhaitent réutiliser ces TP sont les bienvenus.

## Une erreur, une coquille, un corrigé qui ne marche pas

Les corrigés de ce site sont exécutés automatiquement à chaque mise en ligne, donc ils
tournent. Il reste que la bonne réponse à un exercice n'est pas toujours celle qu'on
attendait, et que les coquilles existent. Signalez-les moi par courriel ou en séance, elles
seront corrigées le jour même.

## Comment ce site est fabriqué

Les pages sont écrites en Markdown et transformées en site statique par MkDocs et son thème
Material. Python s'exécute dans votre navigateur grâce à JupyterLite et Pyodide, une version
de Python compilée en WebAssembly : rien n'est installé sur votre machine, et rien de ce que
vous écrivez ne quitte votre navigateur. L'ensemble est servi par un conteneur nginx hébergé
en France.
