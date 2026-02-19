
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

## 📂 Données d'entrée

* Mode `init` : traitement complet depuis les fichiers bruts (`remplissage` et `regulation`) définis dans `config.json`.
* Mode `rolling` : intégration uniquement de la journée `today`; les fichiers existants sont mis à jour et roulés le dimanche.
* Les colonnes importantes (`time`, `station`) sont lues depuis `config.json` et vérifiées automatiquement.

---

## ⚙️ Lancement

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

