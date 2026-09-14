# Mise en route BUT3

**Durée : 15 minutes, à faire avant la première séance.**

Cette section suppose que vous savez déjà programmer en Python : elle ne revient pas sur
les bases, elle installe ce qu'il faut de plus pour parler à un modèle de langage depuis
un script. Contrairement aux TP de première année, rien ici ne s'exécute dans votre
navigateur : ces TP appellent une API distante et ont besoin d'une clé personnelle, donc
d'une installation locale.

## Objectifs

- Obtenir une clé API Mistral AI personnelle.
- Créer un environnement virtuel Python isolé pour ce module.
- Installer les bibliothèques nécessaires et garder votre clé hors de votre code.

## Créer un compte et une clé API Mistral AI

1. Rendez-vous sur [mistral.ai](https://mistral.ai/) et inscrivez-vous.
2. Choisissez l'offre gratuite ou expérimentale : elle suffit pour tous les TP de ce
   module.
3. Dans l'onglet **API → Clés API**, créez une nouvelle clé et copiez-la immédiatement :
   elle ne sera plus jamais affichée en clair ensuite.

!!! danger "Une clé API est un mot de passe"
    Elle donne accès à un service facturé à l'usage. Ne la collez jamais dans un script
    que vous poussez sur GitHub, ni dans un message, ni dans un notebook partagé. La
    section suivante montre comment l'en tenir à l'écart dès le premier script.

## Installer l'environnement de travail

Créez un dossier pour ce module, ouvrez-y un terminal, puis :

```bash
python3 -m venv .venv
```

Activez-le : `.venv\Scripts\activate` sous Windows, `source .venv/bin/activate` sous
macOS et Linux. Votre invite de commande doit maintenant afficher `(.venv)`.

Installez ensuite les bibliothèques utilisées dans ces TP :

```bash
pip install langchain langchain-mistralai python-dotenv pydantic
```

## Garder la clé hors du code

Ne l'écrivez jamais en clair dans un fichier `.py`. Créez à la place un fichier `.env`,
à la racine de votre dossier de travail, avec une seule ligne :

```env
MISTRAL_API_KEY="votre-cle-ici"
```

Puis, en tête de chaque script, chargez-le :

```python title="deux lignes à répéter en tête de chaque script"
from dotenv import load_dotenv

load_dotenv()
```

`os.environ["MISTRAL_API_KEY"]` (ou `os.getenv("MISTRAL_API_KEY")`) donne alors accès à
la clé dans le reste du script, sans qu'elle apparaisse jamais dans le code lui-même.
Ajoutez enfin `.env` à un fichier `.gitignore` si votre dossier est versionné : un `.env`
poussé par erreur sur un dépôt public est repéré et exploité par des robots en quelques
minutes, une clé Mistral compromise vous sera facturée avant que vous ne vous en
aperceviez.

## Vérifier que tout fonctionne

```python title="script de vérification, à exécuter localement avec votre clé"
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
reponse = llm.invoke([HumanMessage(content="Réponds uniquement par le mot OK.")])
print(reponse.content)
```

Si vous voyez `OK` s'afficher, votre installation est prête. Une erreur `401` signifie
que la clé n'est pas lue (vérifiez le nom du fichier `.env` et son emplacement), une
erreur de connexion signifie un réseau ou un pare-feu qui bloque l'appel.

## Et ensuite

[Passez au TP1](tp1-premiers-pas.md).
