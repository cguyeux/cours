# IA générative : LangChain et Mistral

Travaux pratiques de troisième année du BUT informatique, sur l'orchestration de modèles
de langage avec LangChain et l'API Mistral AI.

## Différence avec les TP de première année

Les TP d'[outils fondamentaux](../outils-fondamentaux/index.md) s'exécutent entièrement
dans votre navigateur, sans installation ni compte. Ceux-ci non : ils appellent une API
distante, ont besoin d'une clé personnelle, et s'exécutent donc **sur votre machine**,
après une courte [mise en route](demarrage.md). Les blocs de code sont affichés ici comme
référence et comme corrigé, pas comme éléments exécutables du site.

## Les séances

| Séance | Sujet | Ce que vous saurez faire |
|---|---|---|
| [Mise en route BUT3](demarrage.md) | Installation locale | clé API Mistral, environnement virtuel, dépendances |
| [TP1](tp1-premiers-pas.md) | Premiers pas | invoquer un modèle, composer une chaîne avec `\|`, prompt système/utilisateur |
| [TP2](tp2-sorties-structurees.md) | Sorties structurées | schéma Pydantic, `with_structured_output`, ce qu'il garantit vraiment |
| [TP3](tp3-rag-vecteurs.md) | RAG et bases vectorielles | embeddings, similarité cosinus, indexer et interroger un corpus avec FAISS |
| [TP4](tp4-agents.md) | Agents | patron ReAct, écrire ses propres outils, garde-fous d'un agent en production |
| [TP5](tp5-multimodalite.md) | Multimodalité | synthèse et transcription vocale, vision, génération d'image, pipeline complet |

Chaque TP publié se termine par une liste d'auto-évaluation et un QCM de dix questions
corrigées immédiatement :
[TP1](qcm/qcm_tp1.html){ target=_blank },
[TP2](qcm/qcm_tp2.html){ target=_blank },
[TP3](qcm/qcm_tp3.html){ target=_blank },
[TP4](qcm/qcm_tp4.html){ target=_blank },
[TP5](qcm/qcm_tp5.html){ target=_blank }.

## Le même pacte que le reste du site

Chaque TP contient un encadré « L'IA vous le donne en trois secondes » : demandez à
l'assistant de votre choix d'écrire le script attendu, puis cherchez ce qu'il tait ou
présente comme certain alors que ce ne l'est pas. Sur un module qui porte justement sur
l'orchestration de modèles de langage, cet exercice prend un relief particulier : vous
apprenez à construire avec l'outil dont vous apprenez, dans le même geste, à ne pas trop
vous fier.
