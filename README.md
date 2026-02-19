Bien sûr ! Voici le contenu complet de ton fichier `README.md` prêt à être copié-collé. J'y ai inclus une structure professionnelle avec des badges, des sections claires et même un guide de dépannage.

```markdown
# 🚲 Bike Network Rebalancing & Logistics Optimizer

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Gurobi](https://img.shields.io/badge/Solver-Gurobi-green.svg)](https://www.gurobi.com/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](https://choosealicense.com/)

Ce projet est une solution industrielle complète pour optimiser le rééquilibrage des stations de vélos en libre-service. Il permet de passer de données brutes de remplissage à des feuilles de route précises pour les camions de régulation.



---

## 📌 Architecture du Pipeline

L'outil exécute 5 modules séquentiels orchestrés par `main.py` :

1.  **Data Processing** : Nettoyage des CSV bruts, gestion des types et unification des fréquences temporelles.
2.  **Demand Reconstruction** : Algorithme de décomposition tensorielle (Tucker) pour estimer la demande réelle, même quand une station est vide ou pleine (censure).
3.  **Strategy Evaluation** : Simulation vectorisée de l'évolution des stocks pour chaque station selon différents scénarios de régulation.
4.  **Pareto Frontiers** : Filtrage mathématique pour ne conserver que les stratégies offrant le meilleur compromis entre effort logistique et qualité de service.
5.  **Global Optimization** : Modélisation Gurobi (MILP) pour résoudre simultanément le plan de visite hebdomadaire et les tournées de véhicules (VRP).



---

## 📂 Structure du Projet

```text
.
├── main.py                 # Point d'entrée unique (Orchestrateur)
├── config.json             # Configuration centrale (Dates, Seuils, Chemins)
├── data/
│   ├── inputs/             # Fichiers sources (Remplissage_*.csv, attributs.csv)
│   │   └── metadata/       # Blacklist.csv, etc.
│   └── outputs/            # Résultats (Plannings, prédictions, graphiques)
└── src/
    └── rebalancing/        # Cœur algorithmie
        ├── processing.py   # Module 1
        ├── demand.py       # Module 2
        ├── evaluation.py   # Module 3
        ├── frontiers.py    # Module 4
        ├── optimization.py # Module 5
        └── utils.py        # Moteurs Gurobi (Weekplan, TruckRoutes)

```

---

## 🛠 Installation & Prérequis

### 1. Prérequis Système

* **Python 3.9** ou supérieur.
* **Gurobi Optimizer** installé avec une licence valide (Académique ou Commerciale).

### 2. Installation des dépendances

```bash
pip install pandas numpy scipy tensorly scikit-learn gurobipy matplotlib

```

---

## 🚀 Guide d'Utilisation

### 1. Configuration (`config.json`)

Avant de lancer le script, mettez à jour les dates dans `config.json`.

* `ancienne_semaine` : La semaine complète servant de base historique.
* `nouvelle_semaine` : Les jours déjà écoulés de la semaine en cours.
* `current_day` : Le jour actuel (ex: "Wed").

### 2. Exécution

Lancez simplement le chef d'orchestre :

```bash
python main.py

```

### 3. Analyse des résultats

Les fichiers générés dans `data/outputs/` sont :

* `planning_camions_final.csv` : **Le document opérationnel** (quelle heure, quelle station, quel camion).
* `RECONSTRUCTION_FINAL.csv` : Les flux de demande reconstruits.
* `evaluated_strategies.csv` : L'analyse d'impact théorique sur les stocks.

---

## ⚙️ Paramètres de Contrôle

Vous pouvez ajuster la stratégie dans le bloc `params` et `thresholds` du JSON :

* **`critere_vide` (0.22)** : On s'assure que la station garde au moins 22% de vélos libres.
* **`critere_plein` (0.66)** : On s'assure que la station garde au moins 34% (1 - 0.66) de bornes libres.
* **`n_truck_models`** : Augmentez cette valeur pour une optimisation de trajet plus fine (plus lent).

---

## ⚠️ Dépannage (FAQ)

**Q : Gurobi affiche "No license found"**

> Vérifiez que votre variable d'environnement `GRB_LICENSE_FILE` pointe vers votre fichier `gurobi.lic`.

**Q : Une station critique n'apparaît pas dans le planning**

> Vérifiez si elle n'est pas présente dans `data/inputs/metadata/blacklist.csv` ou si sa capacité est correctement renseignée dans `attributs.csv`.

**Q : Le calcul est trop long (> 10 min)**

> Réduisez le `n_truck_models` à 1 ou augmentez la valeur du `MIPGap` dans `utils.py`.

---

*Développé pour l'optimisation des réseaux de mobilité urbaine.*

```

```