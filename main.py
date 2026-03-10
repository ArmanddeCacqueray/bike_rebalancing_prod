#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import time
from pathlib import Path

# Import des modules que nous avons industrialisés
from src.rebalancing.processing import run_processing
from src.rebalancing.demand import run_reconstruction
from src.rebalancing.evaluation import run_evaluation
from src.rebalancing.frontiers import run_frontiers
from src.rebalancing.optimization import run_optimization

def load_config(config_name="config.json"):
    """Charge la configuration en utilisant un chemin absolu basé sur l'emplacement de main.py."""
    # On construit le chemin complet vers le fichier config.json
    base_path = Path(__file__).resolve().parent
    config_path = base_path / config_name
    
    if not config_path.exists():
        raise FileNotFoundError(f"Le fichier de configuration est introuvable à l'adresse : {config_path}")
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_pipeline():
    """Exécute l'intégralité du pipeline de rééquilibrage."""
    
    # 0. Initialisation
    start_time = time.time()
    config_time = load_config("config_time.json")
    config_params = load_config("config_params.json")
    
    print("="*60)
    print("🚀 DÉMARRAGE DU PIPELINE DE RÉÉQUILIBRAGE LOGISTIQUE")
    print(f"   Jours a planifier : {config_time['to_solve']}")
    print("="*60)

    try:
        # ÉTAPE 1 : Nettoyage et Unification
        # Transforme les fichiers bruts en fichiers CLEAN.csv
        print("\n[ETAPE 1] Préparation des données brutes...")
        run_processing(config_time)

        # ÉTAPE 2 : Reconstruction de la demande (Tucker)
        # Calcule les flux de vélos réels cachés derrière les stocks
        if config["process_last_week"]:
            print("\n[ETAPE 2] Reconstruction de la demande latente (Algorithme Tucker)...")
            run_reconstruction(config)

        # ÉTAPE 3 : Évaluation des stratégies
        # Simule des milliers de scénarios pour chaque station
        print("\n[ETAPE 3] Simulation et évaluation des impacts stocks...")
        run_evaluation(config)

        # ÉTAPE 4 : Filtrage des Frontières de Pareto
        # Ne garde que les meilleures stratégies (compromis coût/service)
        print("\n[ETAPE 4] Calcul des frontières d'efficacité (Pareto)...")
        run_frontiers(config)

        # ÉTAPE 5 : Optimisation Gurobi (Visites + Routage)
        # Décide du planning final et du trajet des camions
        print("\n[ETAPE 5] Optimisation mathématique globale (Gurobi)...")
        run_optimization(config)

        # Fin du processus
        total_time = (time.time() - start_time) / 60
        print("\n" + "="*60)
        print(f"✅ PIPELINE TERMINÉ AVEC SUCCÈS en {total_time:.2f} minutes")
        print(f"   Les plannings sont disponibles dans : {config['paths']['output_dir']}")
        print("="*60)

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE durant le pipeline :")
        print(f"   {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
