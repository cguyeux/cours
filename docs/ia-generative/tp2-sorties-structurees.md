# TP2. Sorties structurées avec Pydantic

**Durée : 1 h 30.**

## Objectifs

- Comprendre pourquoi une sortie de LLM non contrainte est fragile à exploiter dans un
  programme.
- Définir un schéma Pydantic et l'imposer à un modèle avec `with_structured_output`.
- Explorer plusieurs formes de contrainte : booléen, choix dans une liste fermée, note
  bornée, structure imbriquée.
- Savoir ce qu'une sortie structurée garantit vraiment, et ce qu'elle ne garantit pas.

## Prérequis

Le [TP1](tp1-premiers-pas.md) : appeler un modèle Mistral, composer une chaîne avec `|`.
Bibliothèque `pydantic` installée (voir la [mise en route](demarrage.md)).

## Ressources

- [Documentation LangChain, sorties structurées](https://python.langchain.com/docs/how_to/structured_output/).
- [Documentation Pydantic](https://docs.pydantic.dev/).
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp2.html){ target=_blank }, à faire après la
  séance.

!!! info "Ce TP s'exécute sur votre machine, pas dans le navigateur"
    Comme au TP1, les blocs de code ci-dessous appellent une API distante et sont donnés
    à titre d'exemple : recopiez-les dans votre environnement local pour les exécuter.

---

## Étape 1. Pourquoi contraindre une sortie (10 min)

Le TP1 s'est terminé sur un problème : demander du JSON dans un prompt est une consigne
que le modèle peut ignorer. Un texte libre est difficile à exploiter dans un programme,
pour trois raisons qui se cumulent : le format peut varier d'un appel à l'autre, un
`json.loads` peut échouer sur un texte presque-JSON, et rien ne garantit que les valeurs
respectent les bornes attendues (une note « entre 1 et 5 » qui vaudrait 7, par exemple).

Une **sortie structurée** répond à la première moitié du problème : elle décrit un schéma
(les champs attendus et leurs types) que LangChain transmet au modèle sous une forme qu'il
sait respecter presque toujours, puis elle valide la réponse contre ce schéma avant de
vous la rendre.

!!! question "Exercice 1.1 : un cas où une sortie libre a déjà posé problème"
    Dans un TP précédent ou dans votre expérience personnelle d'un assistant conversationnel,
    décrivez une fois où une réponse en texte libre a été difficile à réutiliser
    automatiquement (mauvais format de date, nombre écrit en toutes lettres, liste mêlée
    au texte, etc.).

    **Résultat attendu :** un exemple concret nommant précisément ce qui rendait le
    résultat inexploitable tel quel.

    ??? success "Piste de réponse"
        Demander à un assistant une liste de dix idées et devoir la recopier à la main
        dans un tableur parce qu'elle est numérotée en toutes lettres, mélangée à des
        phrases d'introduction et de conclusion, avec une numérotation qui recommence à 1
        au lieu de continuer. Un schéma `List[str]` imposé en sortie aurait rendu ce
        recopiage inutile.

## Étape 2. Cas le plus simple : une réponse booléenne (15 min)

Un schéma Pydantic est une classe qui décrit les champs attendus et leurs types :

```python title="tp2_bool.py"
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI

load_dotenv()

class Answer(BaseModel):
    answer: bool

prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu réponds par un booléen (True ou False) à la question posée."),
    ("human", "{question}"),
])
llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
chain = prompt | llm.with_structured_output(schema=Answer)

def repond(question):
    return chain.invoke({"question": question}).answer

for question in ["Noël est en hiver", "Il ne pleut jamais en été"]:
    reponse = repond(question)
    print(question, "->", reponse, f"(type : {type(reponse).__name__})")
```

`with_structured_output(schema=Answer)` remplace le parseur de texte libre du TP1 : la
chaîne renvoie directement un objet `Answer`, avec un champ `answer` dont Python **sait**
que c'est un `bool`, pas une chaîne de caractères qui ressemble à `"True"`.

!!! question "Exercice 2.1 : une question ambiguë"
    Ajoutez une troisième question volontairement ambiguë ou mal posée (par exemple une
    question qui n'appelle pas naturellement de réponse par oui ou non). Observez ce que
    le modèle renvoie.

    **Résultat attendu :** un `bool` est renvoyé dans tous les cas, même sur une question
    ambiguë : le schéma force une réponse dans les deux seules valeurs possibles, il ne
    rend pas le modèle plus sûr de sa réponse.

    ??? success "Corrigé"
        ```python title="exercice 2.1"
        for question in ["Noël est en hiver", "Il ne pleut jamais en été", "Le mieux est l'ennemi du bien"]:
            print(question, "->", repond(question))
        ```

        La dernière question n'a pas de valeur de vérité évidente : ce n'est pas une
        affirmation vérifiable, c'est un proverbe. Le schéma `Answer` n'empêche pas le
        modèle de trancher arbitrairement, il empêche seulement le programme de recevoir
        autre chose qu'un `True` ou un `False`. Contraindre la **forme** de la réponse ne
        contraint pas sa **justesse**.

!!! question "Exercice 2.2 : pourquoi le type importe"
    Sans sortie structurée, un modèle interrogé en texte libre pourrait répondre
    `"Oui, c'est exact."` à la place de `True`. Expliquez en une phrase pourquoi cette
    différence casserait un programme qui teste `if reponse:`.

    **Résultat attendu :** en Python, une chaîne de caractères non vide est toujours vraie
    dans un test `if`, y compris `"False"` ou `"Non"` : un texte libre mal interprété
    donnerait donc systématiquement `True`, quelle que soit la réponse réelle du modèle.

    ??? success "Corrigé"
        ```python
        print(bool("False"))
        print(bool("Non"))
        print(bool(""))
        ```

        Les deux premières lignes affichent `True` : seule une chaîne **vide** est fausse
        en Python. C'est un piège classique et silencieux quand on teste directement la
        sortie texte d'un modèle au lieu de passer par un schéma `bool`.

## Étape 3. Choisir une action dans une liste fermée (20 min)

`Field(..., enum=...)` restreint un champ texte à un ensemble de valeurs autorisées :

```python title="tp2_action.py"
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI

load_dotenv()

actions = ["Répondre à une nouvelle question", "Fournir plus d'éléments à la question précédente"]

class ProchaineAction(BaseModel):
    """Choisit la prochaine action à mener face à la demande de l'utilisateur."""
    action: str = Field(..., enum=actions, description="La prochaine action à mener")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu classes la demande d'un utilisateur parmi une liste fermée d'actions."),
    ("human", "{texte}"),
])
llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
chain = prompt | llm.with_structured_output(schema=ProchaineAction)

for texte in ["Peux-tu m'en dire plus ?", "Que sont les PPV ?"]:
    print(texte, "->", chain.invoke({"texte": texte}).action)
```

!!! question "Exercice 3.1 : ajouter une action de repli"
    Ajoutez une troisième action, `"Demander une clarification"`, et vérifiez qu'elle est
    choisie pour un message franchement confus (par exemple une phrase sans verbe ni
    sujet clair).

    **Résultat attendu :** les deux exemples déjà présents continuent de choisir l'une des
    deux premières actions, et le nouveau message confus déclenche `"Demander une
    clarification"` dans la plupart des essais (le résultat n'est pas garanti à 100 %,
    comme toujours avec un modèle probabiliste).

    ??? success "Corrigé"
        ```python title="exercice 3.1"
        actions = [
            "Répondre à une nouvelle question",
            "Fournir plus d'éléments à la question précédente",
            "Demander une clarification",
        ]

        class ProchaineAction(BaseModel):
            action: str = Field(..., enum=actions, description="La prochaine action à mener")

        chain = prompt | llm.with_structured_output(schema=ProchaineAction)
        for texte in ["Peux-tu m'en dire plus ?", "Que sont les PPV ?", "euh, ça, voilà, bon"]:
            print(texte, "->", chain.invoke({"texte": texte}).action)
        ```

        Remarquez que `prompt` n'a pas changé : c'est uniquement la liste `actions`, donc
        le schéma, qui a évolué. C'est l'intérêt d'une sortie structurée sur un prompt
        libre : faire évoluer le comportement du système en modifiant une donnée plutôt
        qu'en réécrivant des phrases dans un prompt.

!!! question "Exercice 3.2 : que garantit vraiment `enum` ?"
    `Field(..., enum=actions)` empêche-t-il le modèle de halluciner une action absente de
    la liste ? Cherchez la réponse dans la documentation LangChain ou en testant avec une
    question qui ne correspond à aucune des actions prévues.

    **Résultat attendu :** dans l'immense majorité des cas la contrainte est respectée,
    parce qu'elle est transmise au modèle comme faisant partie du schéma qu'il doit remplir,
    mais ce n'est pas une garantie absolue au sens mathématique : LangChain valide la
    réponse après coup avec Pydantic, et une valeur hors énumération lèverait une erreur
    de validation plutôt que de passer silencieusement.

    ??? success "Corrigé"
        Il n'y a pas de code à ajouter ici, la vérification se fait sur documentation : la
        sortie structurée fonctionne par un **appel de fonction** contraint côté modèle,
        renforcé par une **validation Pydantic** côté client. C'est cette seconde
        étape qui explique pourquoi l'étape suivante peut planter.

## Étape 4. Une contrainte numérique, et sa limite (20 min)

```python title="tp2_note.py"
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI

load_dotenv()

class TonMessage(BaseModel):
    """Évaluation du ton d'un message."""
    note_ton: int = Field(..., ge=1, le=5, description="1 = neutre, 5 = très aimable")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu notes de 1 à 5 le ton amical d'un message, 1 étant neutre et 5 très aimable."),
    ("human", "{texte}"),
])
llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
chain = prompt | llm.with_structured_output(schema=TonMessage)

messages = [
    "Bonjour, pourrais-tu m'aider s'il te plaît ?",
    "J'ai besoin de ça immédiatement.",
    "Merci beaucoup pour ton aide précieuse !",
]
for texte in messages:
    print(texte, "->", chain.invoke({"texte": texte}).note_ton)
```

`Field(..., ge=1, le=5)` (« *greater or equal*, *less or equal* ») est une contrainte
**Pydantic**, vérifiée du côté de votre programme, une fois la réponse reçue. Ce n'est pas
la même chose qu'une contrainte imposée au modèle pendant qu'il répond.

!!! question "Exercice 4.1 : provoquer la limite"
    Sans rien changer au schéma, enveloppez l'appel de la boucle précédente dans un
    `try/except`, et cherchez dans la documentation Pydantic quelle exception est levée
    quand une valeur ne respecte pas `ge`/`le`. Le modèle a-t-il déjà, dans vos essais,
    renvoyé une valeur hors bornes ?

    **Résultat attendu :** l'exception est une `pydantic.ValidationError`. En pratique elle
    est rare ici, parce que le modèle voit les bornes `1` à `5` dans le schéma qu'on lui
    transmet et les respecte presque toujours, mais « presque toujours » n'est pas
    « toujours » : sans `try/except`, un seul écart suffit à arrêter tout le programme.

    ??? success "Corrigé"
        ```python title="exercice 4.1"
        from pydantic import ValidationError

        for texte in messages:
            try:
                note = chain.invoke({"texte": texte}).note_ton
                print(texte, "->", note)
            except ValidationError as erreur:
                print(texte, "-> réponse hors schéma :", erreur)
        ```

        C'est le point le plus important du TP : une sortie structurée réduit fortement
        le risque d'un résultat inexploitable, elle ne l'élimine pas. Un programme qui
        appelle un LLM en production entoure toujours cet appel d'une gestion d'erreur,
        exactement comme il le ferait pour un appel réseau ou une lecture de fichier.

!!! question "Exercice 4.2 : agréger un champ structuré"
    Calculez la moyenne de `note_ton` sur la liste `messages` ci-dessus.

    **Résultat attendu :** un nombre décimal, moyenne des trois notes obtenues.

    ??? success "Corrigé"
        ```python title="exercice 4.2"
        notes = [chain.invoke({"texte": texte}).note_ton for texte in messages]
        print(notes)
        print(sum(notes) / len(notes))
        ```

        C'est précisément parce que `note_ton` est un `int` garanti, et non un fragment
        de texte à interpréter, que cette agrégation tient en une ligne. Avec une sortie
        texte libre, il aurait fallu d'abord extraire le chiffre du texte, avec tous les
        cas particuliers que cela suppose (« quatre sur cinq », « 4/5 », « plutôt bon »...).

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant d'écrire le script de cette étape. Il produira presque
    toujours une boucle `for texte in messages: print(chain.invoke(...).note_ton)`,
    **sans aucun `try/except` autour de l'appel**. Demandez-lui ensuite explicitement si
    `with_structured_output` garantit que la réponse respecte les bornes `ge=1, le=5`. La
    plupart des assistants répondent d'abord « oui », avant de nuancer si vous insistez.
    Vous venez de vérifier à l'exercice 4.1 que la bonne réponse est « presque toujours,
    pas garanti, et l'erreur possible s'appelle `ValidationError` ». Notez ce que vous en
    retenez.

## Étape 5. Une structure imbriquée (15 min)

Un schéma peut contenir d'autres schémas, pour structurer un raisonnement en plusieurs
étapes :

```python title="tp2_raisonnement.py"
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI

load_dotenv()

class Etape(BaseModel):
    explication: str
    resultat_intermediaire: str

class ReponseMath(BaseModel):
    etapes: list[Etape]
    reponse_finale: str

prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un professeur de mathématiques pédagogue."),
    ("human", "{exercice}"),
])
llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
chain = prompt | llm.with_structured_output(schema=ReponseMath)

resultat = chain.invoke({"exercice": "Résous 8x + 31 = 2"})
for etape in resultat.etapes:
    print("-", etape.explication, "->", etape.resultat_intermediaire)
print("Réponse finale :", resultat.reponse_finale)
```

!!! question "Exercice 5.1 : forcer une vérification"
    Ajoutez à `ReponseMath` un champ `verification: str`, et demandez dans le message
    système que ce champ contienne la vérification de la solution trouvée (remplacer `x`
    par sa valeur dans l'équation de départ).

    **Résultat attendu :** un champ `verification` non vide dans la réponse, qui décrit
    un calcul de contrôle. Rien ne garantit encore que ce contrôle soit correct : le
    schéma impose la **présence** du champ, pas son exactitude.

    ??? success "Corrigé"
        ```python title="exercice 5.1"
        class ReponseMath(BaseModel):
            etapes: list[Etape]
            reponse_finale: str
            verification: str

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Tu es un professeur de mathématiques pédagogue. "
                       "Termine toujours par la vérification de ta réponse, "
                       "en remplaçant l'inconnue par sa valeur dans l'équation de départ."),
            ("human", "{exercice}"),
        ])
        chain = prompt | llm.with_structured_output(schema=ReponseMath)
        resultat = chain.invoke({"exercice": "Résous 8x + 31 = 2"})
        print(resultat.verification)
        ```

        C'est la même leçon qu'à l'étape 4, transposée à un champ texte : un schéma
        structure la **forme** de la réponse (un champ appelé `verification` existera
        toujours), il ne garantit jamais le **fond** (que le calcul qu'il contient soit
        juste). Vérifier le fond reste votre travail, ou celui d'un second appel.

## Pour aller plus loin

- Combiner une sortie structurée avec un agent LangChain, pour que le modèle choisisse
  lui-même entre plusieurs schémas selon la situation.
- Relier une sortie structurée à un stockage (base SQL, fichier) pour automatiser un
  petit pipeline de bout en bout.
- Comparer le comportement de `with_structured_output` entre Mistral et un autre
  fournisseur : le schéma Pydantic, lui, ne change pas.

## Ce qu'il faut retenir

`with_structured_output(schema=...)` remplace un texte libre par un objet Python
typé, validé contre un schéma Pydantic. C'est la réponse au problème posé à la fin du
TP1. Cette garantie porte sur la **forme** : le type de chaque champ, ses bornes
éventuelles (`ge`, `le`), son appartenance à une liste fermée (`enum`). Elle ne porte
jamais sur le **fond** : rien n'assure que la réponse est correcte, seulement qu'elle est
exploitable sans planter sur un format inattendu. Et « exploitable sans planter » n'est
vrai que si vous entourez l'appel d'un `try/except pydantic.ValidationError` : le schéma
réduit le risque d'échec, il ne l'annule pas.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] écrire un schéma Pydantic avec un champ `bool`, un champ `str` contraint par `enum`,
      et un champ `int` contraint par `ge`/`le` ;
- [ ] expliquer la différence entre demander du JSON dans un prompt et utiliser
      `with_structured_output` ;
- [ ] dire ce qu'une sortie structurée garantit, et ce qu'elle ne garantit pas ;
- [ ] nommer l'exception que lève Pydantic quand une contrainte n'est pas respectée, et
      dire pourquoi il faut l'intercepter ;
- [ ] écrire un schéma avec un champ qui est lui-même une liste d'un autre schéma.

[Le QCM du TP2](qcm/qcm_tp2.html){ .md-button target=_blank }
[Passer au TP3](tp3-rag-vecteurs.md){ .md-button .md-button--primary }
