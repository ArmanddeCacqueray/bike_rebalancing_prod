
---

# 🚲 Vélib Optimization Pipeline

Ce projet implémente un pipeline d'optimisation pour la régulation des stocks de vélos, basé sur des prévisions de demande latente et une résolution par solveur mathématique.

## 📋 Prérequis

### 1. Licence & Logiciels

* **Gurobi Optimizer** : Une licence valide est nécessaire pour le fonctionnement du module `optimization.py`.
* **Python 3.8+**

### 2. Dépendances Python

```bash
pip install pandas numpy scipy tensorly scikit-learn gurobipy matplotlib

```

---

## 📂 Données d'entrée (`data/inputs`)

Le modèle nécessite deux types de données temporelles pour fonctionner correctement :

| Données | Période requise | Rôle dans le pipeline |
| --- | --- | --- |
| **Historique Complet** | Dernière semaine complète | Calcul du **forecast de demande** (hypothèse de saisonnalité hebdomadaire). |
| **Données Temps Réel** | Début de semaine en cours | Calcul du **passif de score** et **initialisation** de l'état actuel du parc. |

---

## ⚙️ Configuration et Lancement

1. **Configuration** : Modifiez le fichier `CONFIG.JSON`.
* Vérifiez les noms des fichiers et des colonnes.
* Mettez à jour le champ `current_day` (ex: `Mon`, `Tue`, `Wed`).


2. **Exécution** : Lancez le script principal pour orchestrer le pipeline.

```bash
python main.py

```

---

## 🏗️ Structure du Pipeline

Le processus est divisé en 5 étapes clés orchestrées par `main.py` :

1. **`processing.py`** (~2 min) : Nettoyage et préparation des données brutes.
2. **`demand.py`** (~2 min) : Reconstitution de la demande latente basée sur la semaine précédente.
3. **`evaluation.py`** (~2 min) : Évaluation de toutes les stratégies possibles par station.
4. **`frontieres.py`** (<1 min) : Calcul des frontières de Pareto pour isoler les stratégies pertinentes.
5. **`optimization.py`** (~10 min) : Résolution du problème d'optimisation via **Gurobi**.

---

## 📊 Sorties (Output)

Une fois le script terminé, consultez le dossier `data/output` pour récupérer :

* ✅ **Le Plan de Régulation** : Instructions détaillées pour les équipes terrain.
* 📈 **Fichiers de monitoring** : Diagnostics sur l'optimisation et indicateurs de performance.

---
