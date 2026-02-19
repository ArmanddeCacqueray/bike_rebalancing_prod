import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Constantes pour la clarté du code
DEPOT = 0
VIDE  = 1
PLEIN = 2

def extract_chains_unified(arcs, nodes, node_type, depot=0, n_chains=5, tol=0.5):
    """
    Extrait les séquences de visites (chaînes) à partir du dictionnaire d'arcs optimisés.
    """
    chains = []
    used = set()
    for _ in range(n_chains):
        chain = [("depot", depot)]
        cur_node = depot
        while True:
            next_node = None
            for j in nodes:
                if j == cur_node:
                    continue
                # On cherche un arc activé (valeur proche de 1)
                if arcs.get((cur_node, j), 0) > tol and (cur_node, j) not in used:
                    next_node = j
                    break
            if next_node is None:
                break
            
            used.add((cur_node, next_node))
            label = "depot" if next_node == depot else next_node
            chain.append((label, next_node))
            
            if next_node == depot:
                break
            cur_node = next_node
        chains.append(chain)
    return chains

class TruckRoutesVisualizer:
    """
    Classe utilitaire pour visualiser les tournées calculées par TruckRoutes.
    """

    def __init__(self, truck_routes, stations_df):
        """
        truck_routes : instance de TruckRoutes résolue.
        stations_df : DataFrame contenant 'station_code', 'latitude' et 'longitude'.
        """
        self.tr = truck_routes
        self.stations_all = stations_df
        # Couleurs distinctes pour les différents camions
        self.truck_colors = plt.cm.tab10(np.linspace(0, 1, self.tr.C))
        self._init_positions()

    def _init_positions(self):
        """
        Initialise les positions GPS des nœuds. 
        Le dépôt est placé au centre géographique (barycentre) des stations.
        """
        self.tr.pos = {}
        lons, lats = [], []

        for i in self.tr.nodes:
            if i != 0:
                idx_global = self.tr.global_id[i]
                # Recherche des coordonnées dans le DataFrame fourni
                row = self.stations_all[self.stations_all["station_code"] == idx_global]
                if not row.empty:
                    lon, lat = row["longitude"].values[0], row["latitude"].values[0]
                    self.tr.pos[i] = (lon, lat)
                    lons.append(lon)
                    lats.append(lat)
                else:
                    self.tr.pos[i] = (0, 0)

        # Calcul du dépôt au barycentre pour une visualisation cohérente
        if lons and lats:
            self.tr.pos[0] = (np.mean(lons), np.mean(lats))
        else:
            self.tr.pos[0] = (0, 0)

    def extract_chains(self, m, tol=0.5):
        """
        Organise les arcs par camion et par jour pour faciliter le tracé.
        """
        for n in self.tr.N:
            arcs_day = {
                (i, j): self.tr.arcs_dict[m].get((i, j, n), 0) 
                for i in self.tr.nodes for j in self.tr.nodes
            }
            chains_day = extract_chains_unified(
                arcs=arcs_day,
                nodes=self.tr.nodes,
                node_type=self.tr.type,
                depot=0,
                n_chains=self.tr.C,
                tol=tol
            )
            for k, chain in enumerate(chains_day):
                # On transforme la chaîne en liste de tuples (départ, arrivée)
                arcs_camion = [(i[1], j[1]) for i, j in zip(chain[:-1], chain[1:])]
                self.tr.arcs_per_day[m][n][k] = arcs_camion

    def print_routes(self, m):
        """
        Affiche dans la console le détail textuel des tournées.
        """
        for n in self.tr.N:
            print(f"\n=== TOURNÉES JOUR {n} ===")
            for k, arcs in self.tr.arcs_per_day[m][n].items():
                if not arcs:
                    continue
                
                # Reconstitution de l'ordre de passage
                cur = 0
                path = ["D"]
                temp_arcs = arcs.copy()
                while temp_arcs:
                    next_step = [j for i, j in temp_arcs if i == cur]
                    if not next_step: break
                    cur = next_step[0]
                    label = "D" if cur == 0 else f"{'V' if self.tr.type[cur]==VIDE else 'P'}{self.tr.global_id[cur]}"
                    path.append(label)
                    # On retire pour éviter les boucles infinies en cas d'erreur de modèle
                    for pair in temp_arcs:
                        if pair[0] == path[-2] and pair[1] == cur: # Logique simplifiée
                            break
                    temp_arcs = [a for a in temp_arcs if not (a[0] == path[-2] and a[1] == cur)]

                print(f"Camion {k}: {' -> '.join(path)}")

    def plot_routes(self, m, day=None):
        """
        Génère les cartes Matplotlib des tournées.
        """
        days_to_plot = self.tr.N if day is None else [day]

        for n in days_to_plot:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 1. Dessiner les stations
            for node, pos in self.tr.pos.items():
                if node == 0:
                    ax.scatter(pos[0], pos[1], color='blue', marker='s', s=200, label="Dépôt", zorder=5)
                else:
                    color = 'green' if self.tr.type[node] == VIDE else 'red'
                    ax.scatter(pos[0], pos[1], color=color, s=100, edgecolors='black', alpha=0.8, zorder=4)

            # 2. Dessiner les trajectoires des camions
            for k, arcs in self.tr.arcs_per_day[m][n].items():
                if not arcs: continue
                color = self.truck_colors[k % self.tr.C]
                
                for i, j in arcs:
                    start = self.tr.pos[i]
                    end = self.tr.pos[j]
                    ax.annotate("", xy=end, xytext=start,
                                arrowprops=dict(arrowstyle="->", color=color, lw=2, alpha=0.7))

            ax.set_title(f"Optimisation du Routage - Jour {n}")
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            ax.grid(True, linestyle='--', alpha=0.6)
            
            # Légende unique
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), loc='upper right')
            
            plt.tight_layout()
            plt.show()