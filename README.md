# Natural Job

### LIVE: https://marinooo-naturaljob-app.hf.space

<img width="3840" height="1984" alt="CleanShot 2026-01-10 at 19 04 27@2x" src="https://github.com/user-attachments/assets/322a4626-789b-4d8b-9211-463b3a869c1a" />

Natural Job est une application web monopage pour explorer, analyser et postuler aux offres d’emploi dans la data (IA, BI, Data Science, Data Engineering, etc.). Elle combine un moteur de recherche intelligent basé sur le NLP et des outils de génération de documents pour accélérer chaque candidature.

## Fonctionnalités principales

- **Recherche intelligente** : moteur NLP (TFIDF + cosinus) pour trouver les offres les plus pertinentes selon vos critères. Posibiliter d'aimer / ne pas aimer des offres et affiner sa recherche ainsi que de joindre un CV.
- **Auto-adaptation des candidatures** : lettres de motivation et emails générés à partir de vos modèles et adaptés automatiquement à chaque offre grace au LLM Mistral.
- **Gestion documentaire** : CV, lettres, emails, templates et historique des candidatures au même endroit.
- **Analyse d’offres** : statistiques détaillées (catégories, salaires, géographie, tendances) pour mieux cibler les opportunités.
- **Sources officielles** : agrégation des offres depuis *Nos Talents Nos Emplois* et l’*APEC* + import d’offres externes.

## Structure de l’interface

1. **Viewer** : rechercher, filtrer et consulter les offres ; éditer les documents associés.
2. **Source** : synchroniser / enrichir les sources de données et importer des offres externes.
3. **Documents** : gérer CV, lettres, emails et retrouver les offres enregistrées.
4. **Console** : visualiser les statistiques et gérer les modèles NLP.

## Stack & Architecture

| Couche            | Technologies |
|-------------------|--------------|
| Backend           | Python, Flask |
| Frontend          | HTML / CSS, JS (communication via API Flask) |
| Bases de données  | `sqlite`, `sqlite-vec` (2 DB : `USER`, `OFFER`) |
| Data / NLP        | `scikit-learn`, `pandas`, `numpy` |
| Visualisation     | `plotly`, `leaflet`, `d3js` |
