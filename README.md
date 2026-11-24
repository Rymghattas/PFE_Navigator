# PFE Navigator

Assistant de questions-réponses sur les documents du Projet de Fin d'Études (PFE) . Le projet est un notebook Python qui compare un grand modèle de langage (LLM) utilisé seul à un système de génération augmentée par récupération (RAG).

> **En bref :** le notebook lit cinq PDF, retrouve les passages les plus proches d'une question et demande à Ollama de répondre en français à partir de ces passages en citant les documents et les pages.

## Sommaire

- [Objectifs et fonctionnement](#objectifs-et-fonctionnement)
- [Pourquoi Gemini a été remplacé par Ollama](#pourquoi-gemini-a-été-remplacé-par-ollama)
- [Prérequis](#prérequis)
- [Installation pas à pas](#installation-pas-à-pas)
- [Exécuter le projet](#exécuter-le-projet)
- [Captures du notebook](#captures-du-notebook)
- [Résultats et évaluation](#résultats-et-évaluation)
- [Structure du dépôt](#structure-du-dépôt)
- [Dépannage](#dépannage)
- [Limites connues](#limites-connues)

## Objectifs et fonctionnement

Le projet permet de :

1. Poser des questions sur les documents PFE fournis.
2. Observer la réponse d'un LLM sans lui fournir de documents.
3. Comparer cette réponse à une réponse générée avec le contexte récupéré par le RAG.
4. Afficher les documents et les pages utilisés comme sources.
5. Enregistrer les résultats pour pouvoir les consulter ou les comparer.

Le pipeline du notebook est le suivant :

```mermaid
flowchart LR
    A[5 PDF du dossier documents] --> B[Extraction du texte par page]
    B --> C[Découpage en passages]
    C --> D[Embeddings multilingues]
    E[Question] --> F[Embedding de la question]
    D --> G[Recherche par similarité cosinus]
    F --> G
    G --> H[3 passages les plus pertinents]
    H --> I[Question + contexte + sources]
    I --> J[Ollama : Qwen 2.5 7B]
    J --> K[Réponse en français avec sources]
    K --> L[Fichier JSON de résultats]
```

Le notebook commence avec des passages de 400 mots (chevauchement de 50 mots). Après avoir observé qu'une recherche ne plaçait pas toujours l'information attendue parmi les trois premiers passages, il teste des passages plus petits de 200 mots (chevauchement de 40 mots). Les embeddings du modèle `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` sont normalisés ; leur produit scalaire sert alors à classer les passages par similarité cosinus.

## Pourquoi Gemini a été remplacé par Ollama

Une première approche utilisait Gemini via une API distante. Elle a été remplacée dans le notebook par **Ollama** avec le modèle **Qwen 2.5 7B (`qwen2.5:7b`)** afin de ne pas dépendre des quotas et limites d'une API externe pour les essais, et de pouvoir exécuter la génération localement.

L'exécution locale évite un quota par requête auprès d'un fournisseur d'API et peut donner des réponses plus rapides sur une machine suffisamment performante. **La vitesse n'est pas garantie :** elle dépend du processeur, de la mémoire, du GPU éventuel et du modèle choisi. Le premier téléchargement du modèle Ollama et du modèle d'embeddings nécessite une connexion Internet ; après leur mise en cache, la génération par Ollama se fait localement.

## Prérequis

- Git.
- Python 3.10 ou plus récent (le notebook du dépôt a été utilisé avec Python 3.13).
- [Ollama](https://ollama.com/download) installé et démarré.
- Le modèle Ollama `qwen2.5:7b` téléchargé (plusieurs Go d'espace disque sont à prévoir).
- Une connexion Internet lors de la première installation des dépendances et du téléchargement des modèles.
- Assez de mémoire pour le modèle 7B ; les performances dépendent du matériel disponible.

Le dépôt contient déjà les cinq documents PDF de test. Aucune clé Gemini ni fichier `.env` n'est nécessaire pour le notebook actuel.

## Installation pas à pas

### 1. Récupérer le dépôt

```bash
git clone https://github.com/Rymghattas/PFE_Navigator.git
cd PFE_Navigator
```

### 2. Installer et préparer Ollama

Installez Ollama depuis [ollama.com/download](https://ollama.com/download), puis ouvrez un terminal et téléchargez le modèle utilisé par le notebook :

```bash
ollama pull qwen2.5:7b
ollama list
```

`ollama list` doit afficher `qwen2.5:7b`. Vous pouvez vérifier le modèle indépendamment du notebook avec :

```bash
ollama run qwen2.5:7b
```

Posez une question de test, puis quittez l'invite Ollama avec `/bye`. L'application Ollama doit rester démarrée pendant l'exécution du notebook. Si le service n'est pas déjà lancé sur votre système, démarrez-le dans un terminal séparé avec `ollama serve`.

### 3. Créer un environnement Python

Depuis la racine du dépôt :

**Windows — PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Si PowerShell bloque l'activation du script, utilisez une nouvelle invite de commandes (`cmd.exe`) à la place :

```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 4. Installer les dépendances Python

Dans le même terminal, avec l'environnement virtuel activé :

```bash
python -m pip install -r requirements.txt
```

Le premier chargement de `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` peut télécharger des fichiers depuis Hugging Face et prendre quelques minutes. Une fois les modèles en cache, ils n'ont normalement pas besoin d'être téléchargés à chaque exécution.

## Exécuter le projet

1. Depuis la racine du dépôt, avec l'environnement virtuel activé et Ollama démarré, lancez JupyterLab :

   ```bash
   python -m jupyter lab
   ```

2. Dans JupyterLab, ouvrez `notebooks/PFE_Navigator_RAG.ipynb`.
3. Choisissez comme noyau celui de l'environnement `.venv` où les dépendances ont été installées.
4. Exécutez les cellules **dans l'ordre, du haut vers le bas**. Les sections importent les bibliothèques, vérifient Ollama, testent le LLM seul, préparent les PDF, construisent les embeddings, évaluent la recherche, puis exécutent et comparent les réponses RAG.
5. Attendez la fin de chaque cellule avant de lancer la suivante. Au premier passage, l'extraction, le calcul des embeddings et le chargement du modèle peuvent être plus longs.
6. Les fichiers de résultats sont écrits dans `results/` :
   - `results/llm_sans_rag.json` : réponses du modèle sans contexte documentaire.
   - `results/resultats_rag.json` : réponses RAG et sources récupérées.

Le notebook recherche le dossier `documents/` depuis la racine du dépôt (ou `../documents` si le notebook est lancé depuis son propre sous-dossier) et crée `results/` si nécessaire.

## Captures du notebook

Ces captures proviennent des sorties enregistrées dans le notebook du dépôt. Elles montrent la recherche sémantique et une réponse RAG avec ses sources.

![Résultat de recherche documentaire après ajustement de la taille des passages](docs/captures/recherche-chunks.png)

*Recherche de la question « Quelle est la durée du Projet de Fin d'études ? » après réduction des passages à 200 mots.*

![Réponse générée par le RAG avec ses sources](docs/captures/reponse-rag.png)

*Extrait d'une réponse RAG enregistrée, avec les documents et numéros de pages cités.*

## Résultats et évaluation

Le notebook utilise cinq questions prédéfinies portant notamment sur les dates de dépôt, la note du PFE, la mise en forme du rapport, les soutenances et une éventuelle bourse.

Le test sans RAG sert de référence : le modèle ne reçoit que la question et peut donc répondre avec des connaissances générales ou reconnaître qu'il lui manque le contexte. Dans le test RAG, la question est comparée aux passages des PDF, puis les trois passages les mieux classés sont envoyés à Qwen. Le prompt lui demande de ne pas inventer d'information et de citer les sources ; si les passages ne permettent pas de répondre, il doit indiquer : « Je ne sais pas d'après les documents fournis. »

Les résultats actuellement présents dans `results/` sont des exemples issus d'une exécution précédente. Relancer le notebook peut les remplacer. Il faut donc juger la qualité des réponses en vérifiant les passages cités dans les PDF, et pas seulement la formulation du modèle.

## Structure du dépôt

```text
PFE_Navigator/
├── documents/                    # Corpus PDF PFE (5 fichiers)
├── notebooks/
│   └── PFE_Navigator_RAG.ipynb   # Pipeline complet et cellules d'évaluation
├── results/
│   ├── llm_sans_rag.json         # Résultats du modèle seul
│   └── resultats_rag.json        # Résultats RAG et références
├── .gitignore                    # Ignore notamment .env et .venv/
├── README.md
└── requirements.txt
```

## Dépannage

| Problème | Vérification / solution |
|---|---|
| `Connection refused` ou Ollama inaccessible | Vérifiez que l'application Ollama est démarrée. Si nécessaire, lancez `ollama serve` dans un autre terminal. |
| Le notebook indique que `qwen2.5:7b` n'est pas installé | Exécutez `ollama pull qwen2.5:7b`, puis relancez le notebook depuis sa première cellule. |
| La liste des modèles Ollama est vide | Vérifiez Ollama avec `ollama list` et que vous utilisez le même compte/service que celui où le modèle a été téléchargé. |
| `ModuleNotFoundError` dans Jupyter | Vérifiez que le noyau sélectionné correspond à `.venv`, puis réinstallez les dépendances dans cet environnement avec `python -m pip install -r requirements.txt`. |
| Téléchargement d'embeddings en échec | Vérifiez la connexion Internet et relancez la cellule de création des embeddings. Le modèle utilisé est hébergé sur Hugging Face. |
| Réponses lentes ou mémoire insuffisante | Le modèle 7B sollicite les ressources de la machine. Fermez les applications inutiles ou utilisez une machine plus adaptée ; la vitesse locale varie selon le matériel. |
| Aucun texte extrait d'une page PDF | Le notebook utilise l'extraction de texte PDF et ne réalise pas d'OCR. Les pages composées uniquement d'images doivent être OCRisées séparément avant d'être exploitables. |

## Limites connues

- Il s'agit d'un notebook de démonstration et d'évaluation, pas d'une application avec interface utilisateur ou API.
- La recherche repose sur le classement des trois passages les plus similaires ; un passage pertinent peut ne pas figurer dans ce top 3.
- Un modèle local peut toujours se tromper ou mal respecter le contexte. Vérifiez les références dans les PDF.
- Les performances dépendent de la qualité du texte extrait, du découpage, des embeddings et du matériel.
- Les PDF scannés ou contenant du texte non extractible ne sont pas traités par OCR.
