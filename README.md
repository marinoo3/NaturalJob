# Natural Job

> [!NOTE]
> Ce travail est un projet scolaire réalisé dans le cadre de notre 2<sup>ème</sup> année de Master en SISE.

## Présentation
### 🔗 LIVE: https://marinooo-naturaljob-app.hf.space

<img width="3840" height="1984" alt="App scrennshot" src="https://github.com/user-attachments/assets/322a4626-789b-4d8b-9211-463b3a869c1a" />

Natural Job est une application web monopage pour explorer, analyser et postuler aux offres d’emploi dans la data (IA, BI, Data Science, Data Engineering, etc.). Elle combine un moteur de recherche intelligent basé sur le NLP et des outils de génération de documents pour accélérer chaque candidature.

## Fonctionnalités principales

- **Recherche intelligente** : moteur NLP (TFIDF + cosinus) pour trouver les offres les plus pertinentes selon vos critères. Posibiliter d'aimer / ne pas aimer des offres et affiner sa recherche ainsi que de joindre un CV.
- **Auto-adaptation des candidatures** : lettres de motivation et emails générés à partir de vos modèles et adaptés automatiquement à chaque offre grace au LLM Mistral.
- **Gestion des documents** : CV, lettres, emails, templates et historique des candidatures au même endroit. Modifiable grace a l'éditeur Markdown intégré.
- **Analyse d’offres** : statistiques détaillées (catégories, salaires, géographie, tendances) pour mieux cibler les opportunités.
- **Sources officielles** : agrégation des offres depuis *Nos Talents Nos Emplois* et l’*APEC* + import d’offres externes.

## Structure de l’interface

1. **Viewer** : rechercher, filtrer et consulter les offres ; éditer les documents associés.
2. **Source** : synchroniser / enrichir les sources de données et importer des offres externes.
3. **Documents** : gérer CV, lettres, emails et retrouver les offres enregistrées.
4. **Console** : visualiser les statistiques et gérer les modèles NLP.

## Stack & Architecture

| Backend        | Frontend                              | Bases de données                               | Data / NLP                                    | Visualisation                |
|----------------|---------------------------------------|------------------------------------------------|-----------------------------------------------|------------------------------|
| Python, Flask  | HTML / CSS, JS (communication via API Flask) | `sqlite`, `sqlite-vec` (2 DB : `USER`, `OFFER`) | `scikit-learn`, `spacy`, `nltk`, `pandas`, `numpy` | `plotly`, `leaflet`, `d3js` |

![Architecture](https://github.com/user-attachments/assets/2942857f-1acb-4ee5-b6c1-0ae7c53515d3)

## Modèles

| Modèle            | Source           | Type                                  | Description |
|-------------------|------------------|---------------------------------------|-------------|
| TF-IDF            | TfidfVectorizer  | Vectorisation de texte                | Calcule l’importance relative des termes dans les documents en combinant fréquence locale et inverse de fréquence documentaire.
| SVD               | TruncatedSVD     | Réduction dimensionnelle linéaire     | Reduit les vecteurs de la TF-IDF en 50 dimensions pour faciliter le stoquage en base de donnée et accélérer les calcules de distances
| t-SNE             | openTSNE         | Réduction dimensionnelle non linéaire | Projection des vecteurs issues de la SVD en 3D. Méthode stochastique conservant les voisinages locaux.
| Kmeans            | KMeans           | Clustering                            | Algorithme non supervisé qui partitionne les points en K groupes en minimisant la variance intra-cluster.

Les modèles sont stockés au format joblib. Ils sont utilisés pour prédire ou transformer de nouvelles offres, requêtes et documents de l’utilisateur. Ils peuvent être tunés et réentraînés sur l’ensemble des offres directement depuis l’application.

## Bases de données

<p align="center">
  <img src="https://github.com/user-attachments/assets/25d4ac2a-c0b5-4654-993d-6f68364b73b3" alt="USER_DB" />
</p>
<p align="center"><b>Schema relationnel USER_DB</b></p>

<br>
<br>

<p align="center">
  <img src="https://github.com/user-attachments/assets/bec6930c-ce3e-4567-91b5-153919217d0a" alt="OFFER_DB" />
</p>
<p align="center"><b>Schema relationnel OFFER_DB</b></p>

## Structure de l'application
```
├── application/
│   ├── _process/
│   ├── custom/
│   │   ├── api/
│   │   ├── data/
│   │   ├── db/
│   │   ├── nlp/
│   │   ├── plot/
│   │   ├── scrapper/
│   │   └── utils/
│   ├── static/
│   │   ├── css/
│   │   ├── fonts/
│   │   ├── images/
│   │   └── js/
│   ├── templates/
│   ├── __init__.py
│   ├── ajax.py
│   └── routes.py
├── data/
│   ├── db/
│   ├── dist/
│   ├── model/
│   │   ├── metadata/
│   └── usr/
│       ├── coverletter/
│       ├── email/
│       └── resume/
├── app.py
├── Dockerfile
└── requirements.txt
```

## Faire tourner l'app en local

1. Cloner le repo

*On utilise Git LFS pour stoquer nos modèles, il faut donc installer lfs*
```bash
git lfs install
git clone https://github.com/marinoo3/NaturalJob
```

1. Aller dans le dossier racine
```bash
cd NaturalJob-main
```

2. Créer l'image docker
> Windows / Linux
```bash
docker build -t naturaljob .
```

> macOS (émulation x86_64)
```bash
docker buildx create --use --name mybuilder
docker buildx build --platform=linux/amd64 -t naturaljob --load .
```

3. Lancer l'image
```bash
docker run -p 7860:7860 -e MISTRAL_API_KEY={mistral_api_key} naturaljob
```

*L'application est hébergée localement et accessible sur le port 7860 (http://localhost:7860/)*
