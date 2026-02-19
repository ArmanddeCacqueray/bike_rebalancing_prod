#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import json
import ast
from pathlib import Path
from sklearn.metrics.pairwise import haversine_distances

# Import de tes classes métier
from src.rebalancing.optim.planvisit import Weekplan
from src.rebalancing.optim.planrout import TruckRoutes
from src.rebalancing.optim.visualizer import TruckRoutesVisualizer

def load_optimization_data(config):
    """Charge les frontières et les coordonnées GPS pour le calcul des distances."""
    out_dir = Path(config["paths"]["output_dir"])
    in_dir = Path(config["paths"]["input_dir"])
    
    frontiers = pd.read_csv(out_dir / "frontiers_strategies.csv")
    lat_lon = pd.read_csv(in_dir / "attributs.csv")

    # Fusion pour avoir les coordonnées de chaque station à réguler
    stations_all = frontiers[["station", "sign"]].copy()
    stations_all = stations_all.merge(
        lat_lon[["station_code", "latitude", "longitude"]],
        left_on="station",
        right_on="station_code",
        how="left"
    )

    coords = stations_all[["latitude", "longitude"]].values
    coords_rad = np.radians(coords)
    # Conversion en matrice de distance (km)
    distance_matrix = haversine_distances(coords_rad) * 6371 

    return frontiers, stations_all, distance_matrix

def prepare_optimization_params(frontiers, stations_all, distance_matrix, config):
    """
    Transforme les données brutes du CSV en structures dictionnaire 
    compréhensibles par Weekplan et TruckRoutes.
    """
    
    def parse_frontiers_logic(cell):
        """
        Logique intégrée : 
        1. String -> Liste (ast.literal_eval)
        2. Nettoyage des crochets internes si nécessaire et conversion en entiers
        Ex: "['[0010]', '[0110]']" -> [[0,0,1,0], [0,1,1,0]]
        """
        if not isinstance(cell, str): return cell
        raw_list = ast.literal_eval(cell)
        # Gestion du format spécifique '[0010000]'
        return [list(map(int, x.strip("[]"))) for x in raw_list]

    params = {"vide": {}, "plein": {}, "routing": {}}
    nin_limit = config["params"].get("nin_limit", 50)
    
    for sens, sign_val in [("vide", 15), ("plein", -15)]:
        sub = frontiers[frontiers["sign"] == sign_val].copy()
        
        # Application du parsing sur les colonnes de frontières
        strategies_down = sub["frontiere_bas"].apply(parse_frontiers_logic).tolist()
        strategies_up = sub["frontiere_haut"].apply(parse_frontiers_logic).tolist()
        
        params[sens] = {
            "station_ids": sub["station"].tolist(),
            "strategies": {
                "down": strategies_down,
                "up": strategies_up
            },
            "Nin": nin_limit,
            "active_mask": (frontiers["sign"] == sign_val).values,
            "losses": 0
        }

    # Données pour le routage (TruckRoutes)
    params["routing"]["distance_matrix"] = distance_matrix
    params["routing"]["station_ids_global"] = stations_all["station_code"].tolist()
    params["routing"]["penalty_same_type"] = config["params"].get("penalty_same_type", 5)
    
    # Détermination dynamique du nombre de jours (N) à partir de la première stratégie trouvée
    try:
        sample_strat = params["vide"]["strategies"]["down"][0][0]
        n_days = len(sample_strat)
    except (IndexError, KeyError):
        n_days = 7

    dims = {
        "S_vide": range(len(params["vide"]["station_ids"])),
        "S_plein": range(len(params["plein"]["station_ids"])),
        "N": range(n_days)
    }
    
    return dims, params

def run_optimization(config):
    print("--- Début de l'Optimisation Logistique ---")
    out_dir = Path(config["paths"]["output_dir"])
    
    # Chargement
    frontiers, stations_all, dist_matrix = load_optimization_data(config)
    
    # Préparation avec parsing intégré
    dims, params = prepare_optimization_params(frontiers, stations_all, dist_matrix, config)

    # 1. Résolution stratégique (Weekplan)
    print("  Étape 1 : Calcul du plan de visite optimal...")
    wp = Weekplan(dims, params, verbose=False)
    wp.solve()
    wp.to_csv(out_dir / "plan_visites_theorique.csv")

    # 2. Résolution opérationnelle (Truck Routing)
    print("  Étape 2 : Calcul des tournées camions (VRP)...")
    n_models = config["params"].get("n_truck_models", 3)
    routs = TruckRoutes(dims, params, verbose=False, nmodels=n_models)
    
    for m in range(n_models):
        print(f"    Optimisation du modèle {m+1}/{n_models}...")
        routs.solve(m)
    
    routs.to_csv(out_dir / "planning_camions_final.csv", id_model=n_models-1)
    print(f"✅ Terminé ! Fichier : {out_dir / 'planning_camions_final.csv'}")

    # 3. Visualisation
    if config["params"].get("visualize", False):
        print("  Génération des cartes...")
        try:
            vis = TruckRoutesVisualizer(routs, stations_all)
            vis.extract_chains(m=n_models-1)
            vis.plot_routes(m=n_models-1)
        except Exception as e:
            print(f"  Note : Erreur visualisation ({e})")

if __name__ == "__main__":
    # Charger la config et lancer
    config_path = Path(__file__).parent.parent.parent / "config.json" # Ajuste selon ton arborescence
    if not config_path.exists():
        config_path = Path("config.json")
        
    with open(config_path, "r") as f:
        run_optimization(json.load(f))