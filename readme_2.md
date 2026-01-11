# Natural Job

> [!NOTE]
> Ce travail est un projet scolaire réalisé dans le cadre de notre **2ᵉ année de Master SISE (Statistique et Informatique pour la Science des Données)** à l’Université Lumière Lyon 2.

---

## 1. Contexte académique et motivation

Ce projet s’inscrit dans le cadre du module **NLP / Text Mining**, dont l’objectif est de concevoir une **application web interactive** permettant l’exploration, l’analyse et l’interprétation d’un corpus textuel réel à l’aide de techniques avancées de traitement automatique du langage naturel.

Nous avons choisi de travailler sur un **corpus d’offres d’emploi** issues du domaine de la **data** (Data Science, IA, BI, Data Engineering…), car il s’agit d’un domaine :
- riche sémantiquement,
- fortement structuré mais hétérogène,
- directement relié à des problématiques réelles de matching, d’analyse de compétences et d’aide à la décision.

Le projet **Natural Job** répond ainsi à une double ambition :
1. **Académique** : appliquer concrètement les méthodes de NLP, de vectorisation, de réduction dimensionnelle et de clustering.
2. **Pratique** : proposer un outil réellement utile pour guider un utilisateur dans sa recherche d’emploi.

---

## 2. Présentation générale de l’application

### 🔗 Application en ligne
https://marinooo-naturaljob-app.hf.space

Natural Job est une **application web monopage** permettant :
- de rechercher intelligemment des offres d’emploi,
- de les analyser statistiquement et géographiquement,
- de mettre en relation ces offres avec un ou plusieurs CV utilisateur,
- et de générer automatiquement des documents de candidature personnalisés.

L’application combine :
- un **moteur de recherche sémantique**,
- un **système de matching CV–offres**,
- un **LLM (Mistral)** pour la génération de texte,
- une **architecture data complète** (scraping, base, modèles, visualisation).

---

## 3. Objectifs détaillés du projet

Les objectifs principaux sont :

- Construire un **corpus d’offres d’emploi data** à partir de sources fiables.
- Mettre en place une **pipeline NLP complète**, de l’extraction jusqu’à la visualisation.
- Dépasser la recherche par mots-clés grâce à une **recherche sémantique**.
- Permettre à l’utilisateur de **charger plusieurs CV** et d’obtenir des offres adaptées à chacun.
- Automatiser la **rédaction de lettres de motivation et d’emails**, tout en restant personnalisable.
- Fournir des **analyses statistiques et territoriales** pour mieux comprendre le marché.

---

## 4. Fonctionnalités principales

### 4.1 Recherche intelligente d’offres

- Recherche libre via une barre dédiée.
- Vectorisation des requêtes avec **TF-IDF**.
- Calcul de similarité cosinus entre requête et offres.
- Classement des résultats par pertinence sémantique.
- Possibilité de **liker / disliker** des offres afin d’affiner les résultats.

### 4.2 Matching CV – Offres

L’utilisateur peut importer **un ou plusieurs CV** (format texte/PDF).

Pipeline de matching :
1. Nettoyage et normalisation du texte (NLP).
2. Vectorisation du CV avec **TF-IDF**.
3. Réduction dimensionnelle via **LSA (SVD)**.
4. Comparaison CV ↔ annonces par similarité cosinus.
5. Classement des offres selon leur adéquation avec le CV sélectionné.

Chaque CV devient ainsi un **profil vectoriel**, permettant une recommandation contextualisée.

### 4.3 Génération automatique de candidatures

- Génération de **lettres de motivation** adaptées à :
  - une offre précise,
  - un CV donné,
  - un modèle fourni par l’utilisateur.
- Génération d’**emails de candidature** cohérents avec l’offre et la lettre.
- Utilisation du **LLM Mistral** pour produire des textes naturels, professionnels et contextualisés.

### 4.4 Gestion des documents

- Centralisation des CV, lettres et emails.
- Historique des candidatures.
- Édition directe via un **éditeur Markdown intégré**.

### 4.5 Analyse et visualisation

- Statistiques globales sur les offres :
  - catégories de postes,
  - salaires,
  - répartition géographique,
  - tendances.
- Analyses croisées CV ↔ marché.
- Cartographie interactive des opportunités.

### 4.6 Sources de données

- Scraping automatique depuis :
  - APEC
  - Nos Talents Nos Emplois
- Import manuel d’offres externes.
- Gestion des doublons.

---

## 5. Architecture et stack technique

### Backend
- Python
- Flask

### Frontend
- HTML / CSS
- JavaScript
- Communication via API Flask

### Bases de données
- SQLite
- sqlite-vec
- Deux bases distinctes : USER_DB et OFFER_DB

### Data & NLP
- scikit-learn
- spaCy
- nltk
- pandas
- numpy

### Visualisation
- Plotly
- Leaflet
- D3.js

---

## 6. Modèles utilisés

- **TF-IDF** : vectorisation textuelle
- **SVD (LSA)** : réduction dimensionnelle
- **t-SNE** : visualisation non linéaire
- **K-Means** : clustering des offres

Les modèles sont sauvegardés au format **joblib** et peuvent être réentraînés depuis l’application.

---

## 7. Bases de données

Deux bases distinctes :
- **USER_DB** : utilisateurs, CV, documents, historique
- **OFFER_DB** : offres, sources, embeddings, métadonnées

Cette séparation permet une meilleure modularité et évolutivité.

---

## 8. Structure de l’application

```text
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
│   ├── templates/
│   ├── ajax.py
│   └── routes.py
├── data/
│   ├── db/
│   ├── model/
│   └── usr/
├── app.py
├── Dockerfile
└── requirements.txt
```

---

## 9. Déploiement et exécution locale

### Clonage
```bash
git lfs install
git clone https://github.com/marinoo3/NaturalJob
```

### Build Docker
```bash
docker build -t naturaljob .
```

### Lancement
```bash
docker run -p 7860:7860 -e MISTRAL_API_KEY={mistral_api_key} naturaljob
```

---

## 10. Conclusion

Natural Job est un projet complet combinant **NLP, data engineering, visualisation, web et IA générative**. Il répond pleinement aux exigences académiques du module tout en proposant une application réaliste, cohérente et extensible, orientée utilisateur.

Ce projet illustre notre capacité à concevoir une **pipeline NLP de bout en bout**, depuis la collecte des données jusqu’à l’aide à la décision.
