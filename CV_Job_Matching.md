# CV Job Matching — Version 1

## 1. Idée générale du travail

L’objectif de ce module est de mettre en relation un **CV** et des **offres d’emploi** de manière automatique, en se basant uniquement sur le **contenu textuel**.

Concrètement, on cherche à répondre à la question suivante :

> À partir d’un CV fourni en format PDF, quelles sont les offres d’emploi les plus pertinentes parmi un grand nombre d’annonces ?

L’approche repose sur des **méthodes classiques de traitement automatique du langage naturel (NLP)** vues en cours, sans modèles opaques.  
Le système suit les étapes suivantes :
- extraction du texte du CV,
- nettoyage et normalisation des textes,
- transformation des textes en vecteurs numériques,
- calcul d’une similarité entre le CV et chaque offre.

---

## 2. Organisation générale du module

Le travail est découpé en plusieurs étapes indépendantes, chacune correspondant à un fichier Python spécifique :

```
cv/
 ├── parser.py
 ├── preprocess.py

nlp/
 ├── vectorizer.py
 ├── similarity.py
 ├── lsa.py
```

Chaque fichier a un rôle précis afin de garder un code lisible et réutilisable.

---

## 3. Extraction du texte du CV — `parser.py`

### Rôle
`parser.py` s’occupe uniquement de lire un CV au format PDF et d’en extraire le texte brut.

### Principe
- Lecture du PDF page par page avec **PyMuPDF**
- Extraction du texte sans nettoyage ni modification
- Chaque CV est stocké comme une chaîne de caractères

Cette étape est volontairement séparée pour pouvoir tester facilement la qualité de l’extraction.

---

## 4. Nettoyage et normalisation — `preprocess.py`

### Rôle
Transformer un texte brut (CV ou offre) en un texte propre et standardisé.

### Traitements appliqués
- minuscules
- suppression des emails et numéros de téléphone
- suppression des caractères spéciaux
- suppression des stopwords
- lemmatisation

Le **même pipeline** est appliqué aux CV et aux offres pour garantir une comparaison cohérente.

---

## 5. Vectorisation des offres — `vectorizer.py`

### Rôle
Transformer les offres d’emploi en vecteurs numériques grâce à la méthode **TF-IDF**.

### Principe
- Concaténation des champs textuels (titre, description, compétences)
- Chaque offre devient un document
- Pondération TF-IDF avec n-grammes (1,2)

Le modèle TF-IDF est entraîné **uniquement sur les offres**, jamais sur le CV.

---

## 6. Comparaison CV / offres — `similarity.py`

### Rôle
Calculer la similarité entre le CV et chaque offre.

### Principe
- Transformation du CV avec le même modèle TF-IDF
- Calcul de la similarité cosinus
- Classement des offres par ordre de pertinence

Le résultat est un **Top-N d’offres** pertinentes avec un score associé.

---

## 7. Amélioration sémantique — `lsa.py`

### Rôle
Améliorer la robustesse du matching grâce à la **LSA (Latent Semantic Analysis)** basée sur la **SVD**.

### Principe
- Projection des vecteurs TF-IDF dans un espace réduit
- Réduction du bruit lexical
- Mise en évidence de proximités sémantiques globales

Deux classements sont comparés :
- TF-IDF
- LSA

Cette comparaison montre que :
- TF-IDF est plus précis lexicalement
- LSA est plus général et plus robuste

---

## 8. État actuel du projet (Version 1)

Fonctionnalités disponibles :
- extraction automatique du CV PDF
- nettoyage et normalisation des textes
- vectorisation des offres
- calcul de similarité CV / offres
- classement par pertinence
- comparaison TF-IDF vs LSA

Les fonctionnalités de **clustering** et d’**interface utilisateur** ne sont pas incluses dans cette version.

---

## 9. Objectif de cette version

Cette première version constitue une base fonctionnelle et méthodologiquement solide pour :
- alimenter le rapport,
- justifier les choix NLP,
- démontrer un système opérationnel et interprétable.

Les extensions pourront être ajoutées dans des versions ultérieures.
