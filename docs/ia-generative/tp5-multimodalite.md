# TP5. Multimodalité et IA générative

**Durée : 2 h.**

## Objectifs

- Comprendre ce que recouvre la multimodalité : un modèle qui lit ou produit du texte, de
  l'image et de l'audio, pas seulement du texte.
- Synthétiser une voix à partir d'un texte, et transcrire un audio en texte.
- Faire décrire une image par un modèle de vision, puis en générer une à partir d'un
  prompt textuel.
- Composer plusieurs modalités dans un pipeline complet.

## Prérequis

Les [TP1](tp1-premiers-pas.md) à [TP4](tp4-agents.md), pour l'aisance avec les appels
d'API et la structuration d'un script. Ce TP utilise l'API **OpenAI** plutôt que Mistral
(les deux ne sont pas liées : il vous faut une clé `OPENAI_API_KEY` distincte de votre clé
Mistral, sur le même principe que la [mise en route](demarrage.md)). Il faut aussi
`ffmpeg` installé sur votre machine, utilisé par `pydub` pour découper l'audio : sous
Ubuntu ou Debian, `sudo apt install ffmpeg` ; sous Windows, l'installateur officiel puis
ajout du dossier `bin` au `PATH`.

```bash
pip install --upgrade openai python-dotenv pydub pillow
```

## Ressources

- [Documentation OpenAI, guide de démarrage](https://platform.openai.com/docs/guides/setup).
- [Guide synthèse vocale (`audio.speech`)](https://platform.openai.com/docs/guides/text-to-speech).
- [Guide transcription (`audio.transcriptions`)](https://platform.openai.com/docs/guides/speech-to-text).
- [Le QCM d'auto-évaluation de ce TP](qcm/qcm_tp5.html){ target=_blank }, à faire après la
  séance.

!!! info "Ce TP s'exécute sur votre machine, pas dans le navigateur"
    Comme aux TP précédents, les blocs de code appellent une API distante et manipulent des
    fichiers locaux : ils sont donnés à titre d'exemple, à recopier dans votre environnement.

---

## Étape 1. Ce que change la multimodalité (10 min)

Les TP précédents ne faisaient transiter que du texte : une question en entrée, une
réponse en sortie. Un modèle multimodal élargit les deux bouts de la chaîne : il peut
**lire** une image ou un son, et **produire** une image ou un son, pas seulement du texte.
Les combinaisons les plus courantes en production restent texte ↔ image et texte ↔ audio.

!!! question "Exercice 1.1 : deux usages multimodaux"
    Pour un contexte professionnel de votre choix (support client, maintenance,
    médiation culturelle, veille scientifique...), identifiez deux tâches où une seule
    modalité (le texte seul) serait insuffisante, et précisez la combinaison entrée →
    sortie nécessaire (par exemple : image en entrée, texte en sortie).

    **Résultat attendu :** deux cas, chacun justifiant pourquoi une modalité additionnelle
    change réellement ce qui est possible, pas seulement la présentation du résultat.

    ??? success "Piste de réponse"
        Un service de maintenance industrielle où un technicien photographie une pièce
        endommagée (image en entrée) pour obtenir un diagnostic textuel (texte en sortie) :
        aucune description écrite ne remplace la photo elle-même. Et un guide touristique
        audio, où un lieu est décrit par un texte généré puis restitué en voix (texte en
        entrée, audio en sortie), pour un usage mains libres impossible avec du texte seul.

## Étape 2. Du texte vers la parole (20 min)

L'API `audio.speech` synthétise une voix à partir d'un texte :

```python title="tp5_tts.py"
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def synthetise(message: str, chemin_sortie: str, voix: str = "alloy") -> Path:
    """Génère un fichier MP3 à partir d'un texte."""
    sortie = Path(chemin_sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voix,
        input=message,
    ) as reponse:
        reponse.stream_to_file(sortie)

    return sortie

if __name__ == "__main__":
    chemin = synthetise("Bonjour, prêt à explorer la multimodalité ?", "sorties/audio/intro.mp3")
    print(f"Fichier généré : {chemin.resolve()}")
```

!!! question "Exercice 2.1 : comparer des voix"
    Générez le même message avec trois voix différentes (`alloy`, `verse`, `nova`), et
    écoutez les trois fichiers produits.

    **Résultat attendu :** trois fichiers `.mp3` distincts dans `sorties/audio/`, une
    préférence personnelle notée en une phrase, avec ce qui la justifie (débit, tonalité,
    naturel perçu).

    ??? success "Corrigé"
        ```python title="exercice 2.1"
        for voix in ["alloy", "verse", "nova"]:
            synthetise(
                "Bonjour, prêt à explorer la multimodalité ?",
                f"sorties/audio/intro_{voix}.mp3",
                voix=voix,
            )
        ```

        Il n'y a pas de « meilleure » voix dans l'absolu : le choix dépend de l'usage
        (une voix posée pour un guide touristique, une voix plus dynamique pour une
        notification). C'est un paramètre produit autant qu'un paramètre technique.

## Étape 3. De l'audio vers le texte (20 min)

Pour des fichiers longs, on découpe l'audio en segments avant de les transcrire un par
un, avec `pydub` pour le découpage :

```python title="tp5_stt.py"
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment

load_dotenv()
client = OpenAI()

def transcrit(chemin_mp3: str, minutes_par_segment: int = 2) -> str:
    """Transcrit un MP3 long en le découpant en segments."""
    audio = AudioSegment.from_file(chemin_mp3)
    duree_segment_ms = minutes_par_segment * 60 * 1000
    morceaux = []

    with tempfile.TemporaryDirectory() as dossier:
        for indice, debut in enumerate(range(0, len(audio), duree_segment_ms)):
            segment = audio[debut:debut + duree_segment_ms]
            if len(segment) < 1_000:
                continue
            chemin_segment = Path(dossier) / f"segment_{indice}.mp3"
            segment.export(chemin_segment, format="mp3")
            with chemin_segment.open("rb") as fichier:
                resultat = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=fichier,
                )
            morceaux.append(resultat.text.strip())

    return " ".join(morceaux)

if __name__ == "__main__":
    texte = transcrit("donnees/reunion.mp3")
    print(texte)
```

!!! question "Exercice 3.1 : mesurer le coût d'un découpage trop fin"
    Chronométrez `transcrit` avec `minutes_par_segment=2`, puis avec
    `minutes_par_segment=10`, sur le même fichier (utilisez `time.perf_counter`).
    Qu'est-ce qui varie, et qu'est-ce qui ne varie pas ?

    **Résultat attendu :** un nombre d'appels à l'API divisé par cinq environ entre les
    deux réglages (moins de segments), mais un temps total par appel plus long pour les
    segments de dix minutes : le total ne varie pas dans les mêmes proportions que le
    nombre d'appels, parce que chaque appel traite plus de contenu.

    ??? success "Corrigé"
        ```python title="exercice 3.1"
        import time

        for minutes in (2, 10):
            depart = time.perf_counter()
            transcrit("donnees/reunion.mp3", minutes_par_segment=minutes)
            duree = time.perf_counter() - depart
            print(f"{minutes} min/segment : {duree:.1f} s")
        ```

        Le découpage en segments n'existe pas pour accélérer la transcription : il existe
        parce que la plupart des API de transcription plafonnent la taille d'un fichier
        envoyé en une seule requête. Le bon réglage est le plus grand segment qui reste
        sous cette limite, pas le plus petit possible.

## Étape 4. Interroger une image (25 min)

Un appel multimodal peut mélanger texte et image dans une même requête. L'image locale
est encodée en base64 puis transmise comme une « data URL » :

```python title="tp5_vision.py"
import base64
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def image_en_data_url(chemin_image: str) -> str:
    """Encode une image locale en data URL (base64) prête pour l'API."""
    chemin = Path(chemin_image)
    type_mime, _ = mimetypes.guess_type(chemin.name)
    if type_mime is None:
        raise ValueError(f"Impossible de déduire le type de {chemin}")
    contenu = base64.b64encode(chemin.read_bytes()).decode("utf-8")
    return f"data:{type_mime};base64,{contenu}"

def decrit_image(chemin_image: str, question: str) -> str:
    data_url = image_en_data_url(chemin_image)
    reponse = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": question},
                {"type": "input_image", "image_url": data_url},
            ],
        }],
        temperature=0.1,
    )
    return response_text(reponse)

def response_text(reponse) -> str:
    morceaux = []
    for item in reponse.output:
        for contenu in item.content:
            if contenu.type == "output_text":
                morceaux.append(contenu.text.strip())
    return "\n".join(morceaux)

if __name__ == "__main__":
    print(decrit_image("img/capture.png", "Que peux-tu déduire de cette image ?"))
```

!!! question "Exercice 4.1 : contraindre le format de la réponse"
    Ajoutez à la question une consigne de format (par exemple « réponds sous forme de
    liste à puces »). Le résultat respecte-t-il la consigne aussi fidèlement qu'aux TP1 et
    TP2 sur un prompt purement textuel ?

    **Résultat attendu :** dans la plupart des cas, la consigne de format est respectée,
    mais retenez la leçon du TP2 : rien ici ne **garantit** la forme, contrairement à
    `with_structured_output`. Sur une entrée image, cette contrainte de forme est encore
    plus utile qu'ailleurs, car le contenu même de la réponse dépend de ce que le modèle
    « voit », pas seulement de ce que vous écrivez.

    ??? success "Corrigé"
        ```python title="exercice 4.1"
        print(decrit_image(
            "img/capture.png",
            "Que peux-tu déduire de cette image ? Réponds sous forme de liste à puces.",
        ))
        ```

        Si une sortie strictement structurée est nécessaire à partir d'une image
        (extraire des champs précis d'un document scanné, par exemple), la même logique
        que le TP2 s'applique : décrire un schéma Pydantic plutôt que de demander un
        format dans le texte du prompt.

## Étape 5. Générer une image, puis composer un pipeline (30 min)

La génération d'image ferme la boucle texte → image :

```python title="tp5_generation.py"
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def genere_image(prompt: str, chemin_sortie: str, taille: str = "1024x1024") -> Path:
    """Génère une image à partir d'un prompt textuel et la sauvegarde."""
    sortie = Path(chemin_sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)

    resultat = client.images.generate(model="gpt-image-1", prompt=prompt, size=taille)
    sortie.write_bytes(base64.b64decode(resultat.data[0].b64_json))
    return sortie

if __name__ == "__main__":
    chemin = genere_image(
        "Affiche minimaliste illustrant la rencontre entre audio et vision en IA.",
        "sorties/images/multimodal.png",
    )
    print(f"Image générée : {chemin.resolve()}")
```

Assemblez maintenant les briques des étapes précédentes en un seul pipeline : décrire une
image, puis restituer cette description en voix.

!!! question "Exercice 5.1 : un pipeline vision vers audio"
    Écrivez `analyse_en_audio(chemin_image, question)`, qui appelle `decrit_image` de
    l'étape 4, puis passe le texte obtenu à `synthetise` de l'étape 2.

    **Résultat attendu :** un fichier `.mp3` dans `sorties/audio/`, dont le contenu parlé
    est la description de l'image, pas un texte préécrit.

    ??? success "Corrigé"
        ```python title="exercice 5.1"
        def analyse_en_audio(chemin_image, question):
            resume = decrit_image(chemin_image, question)
            print("Résumé généré :", resume)
            return synthetise(f"Voici mon analyse : {resume}", "sorties/audio/analyse.mp3", voix="verse")

        analyse_en_audio("img/capture.png", "Identifie les éléments principaux de cette image.")
        ```

        Ce pipeline en trois briques, vision, texte, audio, est le patron général de
        beaucoup d'applications multimodales en production : chaque brique reste un appel
        d'API simple et testable isolément, comme dans les étapes précédentes ; c'est leur
        **composition** qui construit l'expérience complète, exactement comme une chaîne
        LangChain composait prompt, modèle et parseur au TP1.

## Pour aller plus loin

- Un chatbot vocal complet enchaîne micro en continu, transcription, réponse textuelle,
  puis synthèse vocale, en flux plutôt qu'en fichiers successifs.
- D'autres fournisseurs se spécialisent sur une seule modalité (transcription, génération
  d'image) et peuvent surpasser une offre généraliste sur ce point précis : comparer les
  résultats sur un même cas d'usage reste la seule façon fiable de choisir.
- Les métriques d'usage (`usage.total_tokens`, durée de traitement, coût par appel)
  deviennent indispensables dès qu'un pipeline multimodal passe en production, pour les
  mêmes raisons qu'au TP1 avec `usage_metadata`.

## Ce qu'il faut retenir

Un modèle multimodal étend les deux bouts de la chaîne texte du TP1 : il peut lire une
image ou un son en entrée, en produire un en sortie. La synthèse vocale (`audio.speech`)
et la transcription (`audio.transcriptions`) sont symétriques, texte vers audio et audio
vers texte. Un fichier audio long se découpe en segments avant transcription, pour rester
sous la limite de taille d'un appel, pas pour accélérer le traitement. Une image se
transmet à un modèle de vision encodée en base64 dans le prompt. Et un pipeline
multimodal se construit comme une chaîne LangChain : des briques simples, composées.

## Auto-évaluation

Vous devez pouvoir, sans regarder le corrigé :

- [ ] citer deux combinaisons de modalités courantes en production ;
- [ ] synthétiser un texte en audio, et transcrire un audio en texte ;
- [ ] expliquer pourquoi un audio long se découpe en segments avant transcription ;
- [ ] envoyer une image à un modèle de vision et obtenir une description textuelle ;
- [ ] décrire, en une phrase, un pipeline qui enchaîne au moins deux modalités.

[Le QCM du TP5](qcm/qcm_tp5.html){ .md-button target=_blank }
[Retour au module IA générative](index.md){ .md-button .md-button--primary }
