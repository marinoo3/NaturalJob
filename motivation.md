# Documentation — Pipeline de génération de lettre de motivation
## Dossier `motivation/`

---

## 1. Rôle global du dossier `motivation/`

Le dossier `motivation/` contient toute la logique liée à la génération contrôlée
d’une lettre de motivation à partir :

- d’un CV structuré
- d’une offre d’emploi structurée
- d’un matching factuel
- de réponses utilisateur (optionnelles)

L’objectif n’est pas de “demander à une IA d’écrire une lettre”, mais de produire
une lettre **fiable, explicable et personnalisée**, sans invention.

---

## 2. `schemas.py`

### Rôle
Définir les structures de données standard utilisées dans tout le pipeline.

### Pourquoi il existe
Il garantit que tous les fichiers manipulent les mêmes formats
(CV, offre, matching), ce qui évite les incohérences et facilite la validation.

### Utilisation
Utilisé par :
- `cv_structurer.py`
- `job_structurer.py`
- `matcher.py`
- `pipeline_final.py`

---

## 3. `cv_structurer.py`

### Rôle
Transformer un texte brut de CV en informations exploitables.

### Entrée
- nom du CV
- texte brut du CV
- vocabulaire de compétences

### Sortie
- compétences détectées
- expériences
- formation
- projets
- réalisations

### Pourquoi c’est important
Le LLM ne travaille jamais sur du texte brut.
Il reçoit uniquement des **faits extraits et validés**.

---

## 4. `job_structurer.py`

### Rôle
Transformer une offre d’emploi en structure exploitable.

### Ce qui est extrait
- titre
- description
- compétences (si présentes)
- fallback si certaines colonnes sont absentes

### Intérêt
Permet de gérer des offres hétérogènes et mal structurées.

---

## 5. `matcher.py`

### Rôle
Comparer factuellement un CV à une offre.

### Résultats
- score de correspondance
- compétences communes
- compétences manquantes
- preuves présentes dans le CV

### Rôle clé
C’est la **barrière anti-hallucination** du projet.
Le LLM ne fait que reformuler ce qui est validé ici.

---

## 6. `llm_client.py`

### Rôle
Interface propre avec l’API Mistral.

### Fonctions
- chargement sécurisé de la clé API
- appel au modèle
- parsing JSON robuste
- nettoyage des caractères invalides

### Avantage
Aucune logique métier → facilement remplaçable.

---

## 7. `questions_llm.py`

### Rôle
Générer 3 questions ciblées pour personnaliser la lettre.

### Principe
Chaque question correspond à une information manquante
nécessaire pour une lettre convaincante.

### Format
JSON strict pour intégration facile.

---

## 8. `letter_llm.py`

### Rôle
Générer la lettre de motivation à partir :
- des faits extraits
- des réponses utilisateur

### Contraintes
- structure imposée
- interdiction d’inventer
- formulation prudente si information absente

---

## 9. `post_edit.py`

### Rôle
Améliorer la lettre générée.

### Fonctions
- variantes (classique / concise / orientée résultats)
- version ATS-friendly
- nettoyage stylistique

---

## 10. `pipeline_final.py`

### Rôle
Orchestration complète du pipeline.

### Étapes
1. structuration CV
2. structuration offre
3. matching factuel
4. génération des questions
5. génération de la lettre
6. post-traitement
7. sauvegarde des résultats
