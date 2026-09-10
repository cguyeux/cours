# Mise en route

**Durée : 30 minutes, à faire avant ou au début de la première séance.**

Cette page est la seule du site à parler de votre ordinateur. Toutes les autres ne parlent
que de Python, et fonctionnent à l'identique que vous soyez sous Windows, macOS ou Linux.

## Objectifs

- Exécuter votre premier programme Python, sans rien installer.
- Savoir lire un message d'erreur au lieu de le subir.
- Savoir sauvegarder votre travail, ce qui n'est pas automatique.

## Voie 1 : dans votre navigateur, sans rien installer

C'est la voie par défaut, celle que je vous recommande pour ce module. Python s'exécute
directement dans votre navigateur, sur n'importe quelle machine, sans compte et sans
installation.

[Ouvrir la console Python](/lite/repl/index.html?kernel=python&toolbar=1){ .md-button .md-button--primary target=_blank }
[Ouvrir les carnets des TP](/lite/tree/index.html){ .md-button target=_blank }

Le premier bouton ouvre une console, pratique pour essayer une ligne. Le second ouvre la
liste des carnets, un par TP, dans lesquels les énoncés sont déjà écrits : vous n'avez qu'à
remplir les cellules vides.

!!! tip "Le premier chargement prend quelques secondes"
    Votre navigateur télécharge un interpréteur Python complet la première fois. Ensuite,
    il le garde en mémoire et le démarrage est immédiat.

### Comment on exécute une cellule

Cliquez dans une cellule, écrivez votre code, puis appuyez sur ++shift+enter++. Le résultat
s'affiche juste en dessous, et le curseur passe à la cellule suivante. Pour exécuter sans
avancer, ++ctrl+enter++.

### Comment on sauvegarde, et pourquoi il faut y penser

!!! danger "Votre travail n'est pas dans le nuage"
    Les carnets sont enregistrés dans la mémoire de **votre navigateur, sur cette machine**.
    Si vous changez d'ordinateur, si vous videz l'historique, ou si vous ouvrez le site en
    navigation privée, vous ne retrouverez rien.

Prenez donc dès aujourd'hui l'habitude suivante : à la fin de chaque séance, menu
**File**, puis **Download**. Vous obtenez un fichier `.ipynb` que vous rangez dans votre
répertoire de travail habituel, comme n'importe quel devoir. Pour le reprendre plus tard,
menu **File**, puis **Open from Path** ou glissez-déposez le fichier dans la liste.

## Voie 2 : Python sur votre machine

Vous n'en avez pas besoin pour ce module, mais c'est ce que vous ferez en entreprise, et
les séances suivantes du BUT le demanderont. Autant s'y mettre tôt.

=== "Windows"

    1. Ouvrez [python.org/downloads](https://www.python.org/downloads/) et téléchargez la
       dernière version stable.
    2. Lancez l'installateur. **Cochez « Add python.exe to PATH »** sur le premier écran,
       c'est l'erreur classique et elle coûte une demi-heure.
    3. Installez [Visual Studio Code](https://code.visualstudio.com/), puis dans l'onglet
       des extensions, installez l'extension « Python » de Microsoft.
    4. Pour vérifier : ouvrez un terminal dans VS Code (menu Terminal, New Terminal) et
       tapez `python --version`. Vous devez voir un numéro de version.

=== "macOS"

    1. Le Python fourni par Apple est ancien : installez celui de
       [python.org/downloads](https://www.python.org/downloads/), ou passez par
       [Homebrew](https://brew.sh/) avec `brew install python`.
    2. Installez [Visual Studio Code](https://code.visualstudio.com/), puis l'extension
       « Python » de Microsoft.
    3. Pour vérifier : dans un terminal, `python3 --version`. Sur macOS la commande
       s'appelle `python3`, pas `python`.

=== "Linux"

    1. Python est déjà là. Vérifiez avec `python3 --version`.
    2. S'il manque l'outil d'environnements virtuels, installez-le : sur Debian et Ubuntu,
       `sudo apt install python3-venv python3-pip` ; sur Fedora,
       `sudo dnf install python3-pip`.
    3. Installez [Visual Studio Code](https://code.visualstudio.com/) et son extension
       « Python », ou utilisez l'éditeur que vous préférez.

Une fois Python installé, la bonne habitude est de créer un environnement isolé par projet,
pour que les bibliothèques d'un devoir ne cassent pas celles d'un autre :

```bash
python3 -m venv .venv
```

puis, pour l'activer, `.venv\Scripts\activate` sous Windows et `source .venv/bin/activate`
sous macOS et Linux.

## Voie 3 : les machines de la salle

Elles ont Python et VS Code déjà installés. Attention toutefois : votre travail n'y survit
pas forcément d'une séance à l'autre selon la salle. Téléchargez vos fichiers avant de
partir, ou envoyez-les vous par courriel.

## Votre premier programme

Ouvrez la console, ou un carnet, et tapez :

```python
print("Bonjour")
2 + 3 * 4
```

Vous devez voir `Bonjour`, puis `14`. Si vous obtenez `20`, c'est que vous avez recopié
autre chose : Python respecte la priorité des opérations.

!!! question "Exercice 0.1"
    Faites afficher à Python le nombre de secondes dans une année de 365 jours.

    **Résultat attendu :** `31536000`.

    ??? success "Corrigé"
        ```python
        print(365 * 24 * 60 * 60)
        ```

        On peut aussi rendre le calcul lisible en nommant les étapes, ce qui est
        toujours préférable dès que la formule dépasse deux ou trois facteurs :

        ```python
        secondes_par_jour = 24 * 60 * 60
        print(365 * secondes_par_jour)
        ```

## Lire un message d'erreur

Un message d'erreur n'est pas une punition, c'est l'information la plus utile que la machine
puisse vous donner. Essayez volontairement ceci :

```python title="Ce code est volontairement incorrect"
print("Bonjour"
```

Python répond quelque chose comme :

```text
  Cell In[1], line 1
    print("Bonjour"
         ^
SyntaxError: '(' was never closed
```

Trois choses à y lire, toujours dans cet ordre : **où** (ligne 1), **quoi**
(`SyntaxError`), et **quelle explication** (« la parenthèse n'a jamais été fermée »).
Les erreurs les plus fréquentes en début d'apprentissage :

| Message | Ce que ça veut dire |
|---|---|
| `SyntaxError` | la phrase n'est pas du Python, souvent une parenthèse ou un deux-points oublié |
| `NameError` | vous utilisez un nom que Python ne connaît pas : faute de frappe, ou cellule non exécutée |
| `TypeError` | vous mélangez des types incompatibles, par exemple additionner un texte et un nombre |
| `IndentationError` | l'alignement est faux ; en Python, les espaces au début de ligne comptent |
| `ZeroDivisionError` | vous avez divisé par zéro |

!!! warning "L'IA vous le donne en trois secondes"
    Collez le message d'erreur ci-dessus à un assistant et demandez-lui de corriger. Il y
    parviendra. Demandez-lui maintenant pourquoi la flèche `^` pointe sur la parenthèse
    ouvrante et non sur la fin de la ligne. Gardez sa réponse : vous serez capable de dire,
    à la fin du TP1, si elle est exacte.

## Et ensuite

Vous êtes prêt. [Passez au TP1](tp1-calcul-numerique.md).
