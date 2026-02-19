
---

# 🚲 Vélib Optimization Pipeline

Pipeline d’optimisation pour la régulation des stocks de vélos, basé sur des données de remplissage et régulation.

---

## 📋 Prérequis

* **Python 3.8+**
* **Gurobi Optimizer** (licence nécessaire pour `optimization.py`)
* Dépendances Python :

```bash
pip install pandas numpy scipy scikit-learn gurobipy matplotlib
```

---

## 📂 Données d'entrée DEUX MODES, init ou rolling
Le contrat: le but est de maintenir deux fichiers de stock traités:
-la semaine derniere complete pour du forecast (on considere que la demande est identique d'une semaine a la suivante)
-la semaine actuel entamée pour le passif du score hebdo et l'etat actuel du parc
* Mode `init` : traitement complet; on construit la semaine derniere et le debut de la semaine from scratch
* Mode `rolling` : intégration uniquement de la journée `today`; les fichiers existants sont mis à jour et roulés le dimanche.
* Les colonnes importantes (`time`, `station`) sont lues depuis `config.json` et vérifiées automatiquement.
*option: process_last_week = true ou false puisque last week ne change pas entre temps
---

## ⚙️ Lancement
0. Charger les donnees de remplissage et regulation pertinente dans raw
1. Modifier `config.json` pour définir `mode`, fichiers et colonnes.
2. Exécuter :

```bash
python main.py
```

> Le pipeline valide la présence des colonnes et renvoie une erreur claire si nécessaire.

---

## 🏗️ Étapes principales

1. **Processing** : nettoyage et préparation des données.
2. **Demand** : reconstitution de la demande latente.
3. **Evaluation** : analyse des stratégies par station.
4. **Frontières** : isolation des stratégies pertinentes.
5. **Optimization** : résolution du problème avec Gurobi.

---

## 📊 Sorties

* `data/outputs` : fichiers de planification et monitoring.
* Noms standardisés :

  * `CLEAN_last_week.csv`, `CLEAN_new_week.csv`
  * `CLEAN_last_week_20min.csv`, `CLEAN_new_week_20min.csv`

