# TP1. Premiers pas avec la génération de texte

**Durée : 1 h 30.**

## Objectifs

- Comprendre ce qu'apporte LangChain par rapport à un appel direct à une API de modèle
  de langage.
- Invoquer un modèle Mistral depuis un script Python, et lire sa réponse.
- Composer un prompt et un modèle en une **chaîne**, la brique de base de LangChain.
- Distinguer un prompt à un seul message d'un prompt hiérarchisé système/utilisateur.

## Prérequis

La [mise en route BUT3](demarrage.md) : une clé API Mistral valide, un environnement
virtuel actif, `langchain` et `langchain-mistralai` installés.

## Ressources

- [Documentation LangChain](https://python.langchain.com/docs/introduction/).
- [Documentation Mistral AI](https://docs.mistral.ai/).
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp1.html){ target=_blank }, à faire après la
  séance.

!!! info "Ce TP s'exécute sur votre machine, pas dans le navigateur"
    Les blocs de code de cette section appellent une API distante et consomment votre
    clé personnelle. Ils sont donc affichés à titre d'exemple mais non exécutables
    directement sur ce site : recopiez-les dans votre environnement local, comme indiqué
    à la [mise en route](demarrage.md).

---

## Étape 1. Ce que LangChain ajoute à un simple appel d'API (10 min)

Un modèle de langage se contacte, au fond, par une seule requête HTTP : un texte en
entrée, un texte en sortie. LangChain n'ajoute rien à cette mécanique, il l'habille pour
que vous n'ayez pas à la refaire à chaque projet. Il fournit en particulier :

- une interface **commune** à plusieurs fournisseurs (Mistral, OpenAI, et d'autres), pour
  changer de modèle sans réécrire votre logique ;
- des **chaînes**, qui enchaînent prompt, modèle et traitement de la sortie comme des
  tubes Unix qu'on relie avec `|` ;
- des **sorties structurées**, objet du TP2, pour contraindre la forme de la réponse ;
- des briques plus avancées (agents, mémoire, RAG) que vous ne verrez pas ici, mais que la
  documentation officielle couvre en détail.

!!! question "Exercice 1.1 : un cas d'usage"
    Décrivez en quelques phrases un cas d'usage, professionnel ou personnel, où appeler un
    modèle de langage depuis un programme apporterait quelque chose qu'une interface de
    chat classique n'apporte pas.

    **Résultat attendu :** il n'y a pas de bonne réponse unique, mais un cas d'usage valable
    doit expliquer pourquoi le traitement se fait **en programme** : un volume de requêtes
    trop grand pour être tapé à la main, une sortie qui doit être réutilisée par un autre
    programme, ou une tâche répétée identiquement sur beaucoup d'entrées.

    ??? success "Piste de réponse"
        Trier automatiquement les courriels entrants d'un formulaire de contact par
        catégorie (« commercial », « support », « spam ») avant de les router vers la
        bonne boîte. Une interface de chat exigerait de copier-coller chaque message à la
        main ; un script peut traiter des centaines de messages par minute, et sa sortie
        (l'étiquette de catégorie) est directement exploitable par le reste du système de
        routage. C'est exactement le problème que résout la **sortie structurée** du TP2.

## Étape 2. Première invocation (20 min)

Le plus petit programme possible avec LangChain et Mistral :

```python title="tp1_mistral.py"
from dotenv import load_dotenv
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatMistralAI(model="mistral-large-latest", temperature=0)

message = HumanMessage(content="Quelle est la capitale de l'Albanie ?")
response = llm.invoke([message])

print(response.content)
```

`response` n'est pas une simple chaîne de caractères : c'est un objet qui porte aussi les
métadonnées de l'appel. `response.content` en extrait le texte de la réponse.

!!! question "Exercice 2.1 : compter les jetons"
    Modifiez le script pour afficher `response.usage_metadata` en plus de
    `response.content`. Ce dictionnaire donne le nombre de jetons (*tokens*) consommés en
    entrée et en sortie.

    **Résultat attendu :** deux affichages, le texte de la réponse puis un dictionnaire
    contenant au moins les clés `input_tokens`, `output_tokens` et `total_tokens`.

    ??? success "Corrigé"
        ```python title="exercice 2.1"
        from dotenv import load_dotenv
        from langchain_mistralai.chat_models import ChatMistralAI
        from langchain_core.messages import HumanMessage

        load_dotenv()

        llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
        message = HumanMessage(content="Quelle est la capitale de l'Albanie ?")
        response = llm.invoke([message])

        print(response.content)
        print(response.usage_metadata)
        ```

        Un modèle de langage ne facture pas « une requête », il facture des jetons, une
        unité proche d'un mot ou d'un fragment de mot. C'est ce dictionnaire qui vous
        permet de chiffrer réellement le coût d'un appel, en le multipliant par le tarif
        public du modèle utilisé (annoncé en euros pour un million de jetons).

!!! question "Exercice 2.2 : la température n'est pas la clé de la reproductibilité"
    Exécutez deux fois le script précédent avec `temperature=0`, puis deux fois avec
    `temperature=0.9`. Comparez les quatre réponses.

    **Résultat attendu :** à `temperature=0.9`, des reformulations différentes à chaque
    exécution. À `temperature=0`, des réponses très proches, mais gardez le mot **proches** :
    rien ne garantit une réponse identique au caractère près, même à température nulle.

    ??? success "Corrigé"
        Il n'y a pas de code supplémentaire à écrire : c'est l'exécution répétée du script
        de l'exercice 2.1 qui constitue l'exercice. La température règle le tirage
        aléatoire fait sur les mots les plus probables ; à `0`, le modèle choisit presque
        toujours le mot le plus probable, ce qui rend la réponse stable mais pas
        strictement déterministe (le calcul en coulisses n'est pas garanti bit à bit
        identique d'un appel à l'autre). Retenez cette nuance : elle revient dans
        l'encadré ci-dessous.

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant d'écrire « un script Python qui appelle l'API Mistral et
    affiche la réponse ». Deux pièges classiques à chercher dans ce qu'il vous rend.
    D'abord, la clé : beaucoup de réponses écrivent `api_key="sk-..."` en dur dans le
    script plutôt que de la lire depuis une variable d'environnement, exactement l'erreur
    que la mise en route vous a appris à éviter. Ensuite, une affirmation du type
    « `temperature=0` garantit une réponse identique à chaque appel » : vous venez de
    vérifier à l'exercice 2.2 que c'est une approximation, pas une garantie. Notez ce que
    vous en retenez.

## Étape 3. Composer un prompt et un modèle en chaîne (30 min)

Un prompt qui contient une variable, un modèle, et un extracteur de texte se composent
avec l'opérateur `|`, comme des tubes Unix :

```python title="tp1_chain.py"
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI

load_dotenv()

prompt = ChatPromptTemplate.from_template("Fais-moi une blague sur le sujet : {sujet}")
model = ChatMistralAI(model="mistral-large-latest", temperature=0)
output_parser = StrOutputParser()

chain = prompt | model | output_parser

for sujet in ["pompier", "police"]:
    print(chain.invoke({"sujet": sujet}))
    print("-" * 10)
```

`chain.invoke({"sujet": "pompier"})` remplace `{sujet}` dans le gabarit, envoie le
résultat au modèle, puis passe la réponse à `StrOutputParser`, qui n'en garde que le
texte brut (sans `StrOutputParser`, `chain.invoke` renverrait l'objet `response` complet
de l'étape 2, avec ses métadonnées).

!!! question "Exercice 3.1 : une entrée qui ne plante jamais"
    Ajoutez un contrôle qui refuse d'appeler la chaîne si `sujet` est une chaîne vide ou ne
    contient que des espaces, et affiche un message d'erreur clair à la place.

    **Résultat attendu :** l'appel avec `sujet = "pompier"` fonctionne normalement, l'appel
    avec `sujet = "   "` affiche un message et ne consomme aucun jeton (pas d'appel à
    `chain.invoke`).

    ??? success "Corrigé"
        ```python title="exercice 3.1"
        def demande_blague(chain, sujet):
            if not sujet.strip():
                print("Sujet vide, aucun appel effectué.")
                return None
            return chain.invoke({"sujet": sujet})

        print(demande_blague(chain, "pompier"))
        print(demande_blague(chain, "   "))
        ```

        Ce garde-fou paraît anodin, mais c'est lui qui évite de facturer un appel pour
        rien dès qu'une interface web laisse passer un champ vide. En production, ce
        genre de contrôle se met **avant** l'appel réseau, jamais après.

!!! question "Exercice 3.2 : forcer une sortie JSON par le prompt"
    Réécrivez le prompt pour demander explicitement une réponse au format JSON avec les
    clés `"setup"` (l'amorce) et `"punchline"` (la chute).

    **Résultat attendu :** un texte qui ressemble à du JSON valide, mais qui reste un
    texte : rien ne garantit encore qu'il se charge avec `json.loads` sans erreur. C'est
    précisément la limite que le TP2 lève avec les sorties structurées.

    ??? success "Corrigé"
        ```python title="exercice 3.2"
        prompt_json = ChatPromptTemplate.from_template(
            "Fais-moi une blague sur le sujet : {sujet}. "
            "Réponds uniquement par un objet JSON avec deux clés : "
            '"setup" pour l\'amorce et "punchline" pour la chute, sans aucun texte autour.'
        )
        chain_json = prompt_json | model | output_parser

        sortie = chain_json.invoke({"sujet": "pompier"})
        print(sortie)

        import json
        try:
            print(json.loads(sortie))
        except json.JSONDecodeError as erreur:
            print("Ce n'est pas du JSON valide :", erreur)
        ```

        Demander du JSON dans le prompt est une **consigne**, pas une **contrainte** : le
        modèle peut ajouter une phrase d'introduction, entourer le JSON de triples
        apostrophes, ou simplement se tromper de syntaxe. Le `try/except` rend visible ce
        que la plupart des scripts trouvés en ligne cachent sous le tapis.

## Étape 4. Prompt hiérarchisé : système et utilisateur (20 min)

Jusqu'ici, chaque prompt tenait en un seul message. On peut aussi distinguer un message
**système**, qui fixe le comportement général du modèle, d'un message **utilisateur**, qui
porte la demande du moment :

```python title="tp1_systeme.py"
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI

load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un rédacteur de documentation technique, concis et précis."),
    ("user", "{input}"),
])

llm = ChatMistralAI(model="mistral-large-latest")
chain = prompt | llm

result = chain.invoke({"input": "Qu'est-ce que le modèle mistral-large-latest ?"})
print(result.content)
print(result.usage_metadata)
```

Le message système ne change pas d'une question à l'autre : c'est lui qui porte le
« personnage » ou les règles de forme, pendant que `{input}` transporte la vraie question.

!!! question "Exercice 4.1 : mesurer l'effet du message système"
    Gardez la même question, mais changez le message système pour demander un style très
    différent (par exemple « Tu réponds toujours en une seule phrase, sur un ton
    humoristique »). Comparez la longueur des deux réponses via
    `result.usage_metadata["output_tokens"]`.

    **Résultat attendu :** un nombre de jetons en sortie nettement plus petit pour la
    consigne « une seule phrase » que pour la consigne initiale. Le message système
    influence autant la **forme** que le **fond** de la réponse.

    ??? success "Corrigé"
        ```python title="exercice 4.1"
        for consigne in [
            "Tu es un rédacteur de documentation technique, concis et précis.",
            "Tu réponds toujours en une seule phrase, sur un ton humoristique.",
        ]:
            prompt = ChatPromptTemplate.from_messages([
                ("system", consigne),
                ("user", "{input}"),
            ])
            chain = prompt | llm
            result = chain.invoke({"input": "Qu'est-ce que le modèle mistral-large-latest ?"})
            print(consigne)
            print(result.content)
            print("jetons en sortie :", result.usage_metadata["output_tokens"])
            print()
        ```

        Le message système ne garantit rien de façon absolue (le modèle peut toujours
        déborder de la consigne), mais il déplace fortement la distribution des réponses.
        C'est le levier le plus économique pour réduire un coût d'API : une réponse plus
        courte coûte moins de jetons en sortie.

## Pour aller plus loin

- Les **vector stores** et les embeddings, qui permettent d'aller chercher de
  l'information dans vos propres documents avant de répondre (RAG).
- Les **agents**, qui laissent le modèle décider lui-même des outils à appeler et de
  l'ordre des étapes.
- Comparer le coût et la qualité des réponses entre Mistral et un autre fournisseur, sur
  une même tâche et le même prompt.

## Ce qu'il faut retenir

Une chaîne LangChain compose un prompt, un modèle et un traitement de sortie avec `|`,
comme des tubes Unix. `response.content` donne le texte d'une réponse,
`response.usage_metadata` donne son coût réel en jetons. La température rend une réponse
plus ou moins stable, jamais strictement déterministe. Un message système fixe le
comportement général du modèle, un message utilisateur porte la demande précise. Et
demander du JSON dans un prompt reste une consigne que le modèle peut ne pas suivre à la
lettre : le TP2 montre comment la transformer en contrainte vérifiée.

## Auto-évaluation

Avant de passer au TP2, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer ce que fait l'opérateur `|` entre un prompt, un modèle et un parseur ;
- [ ] lire `response.usage_metadata` et en déduire un coût en euros à partir d'un tarif ;
- [ ] écrire un prompt à message système et message utilisateur séparés ;
- [ ] dire pourquoi `temperature=0` ne garantit pas une réponse identique à chaque appel ;
- [ ] expliquer pourquoi demander du JSON dans un prompt ne garantit pas d'obtenir du JSON
      valide.

[Le QCM du TP1](qcm/qcm_tp1.html){ .md-button target=_blank }
[Passer au TP2](tp2-sorties-structurees.md){ .md-button .md-button--primary }
