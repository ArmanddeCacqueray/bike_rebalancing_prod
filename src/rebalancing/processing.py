#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from typing import Dict, List
from pathlib import Path

# ============================================================
# UTILS (LOGIQUE INTERNE)
# ============================================================

def get_metadata_paths(config_paths: dict):
    """Gère l'emplacement des fichiers de suivi des stations."""
    meta_dir = Path(config_paths["input_dir"]) / "metadata"
    meta_dir.mkdir(exist_ok=True)
    return meta_dir / "withlist.csv", meta_dir / "blacklist.csv"

def read_csv_smart(path: Path, col_station: str, config_paths: dict, apply_blacklist=True, filter = None) -> pd.DataFrame:
    """Lit un CSV et gère dynamiquement la withlist/blacklist."""
    with open(path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ';' if ';' in first_line else ','

    df = pd.read_csv(path, sep=sep)
    if filter is not None:
        df = filter_dates(df, filter["col"], filter["start"], filter["end"])
    
    if apply_blacklist:
        with_path, black_path = get_metadata_paths(config_paths)
        current_stations = set(df[col_station].astype(str))
        
        # Chargement/Initialisation
        try:
            withlist = set(pd.read_csv(with_path)["station"].astype(str))
        except FileNotFoundError:
            withlist = current_stations.copy()
            pd.DataFrame({"station": list(withlist)}).to_csv(with_path, index=False)
        
        try:
            blacklist = set(pd.read_csv(black_path)["station"].astype(str))
        except FileNotFoundError:
            blacklist = set()

        # Mise à jour de la logique de stabilité des stations
        removed = withlist - current_stations
        new_black = (current_stations - withlist)
        blacklist.update(removed)
        blacklist.update(new_black)
        withlist = withlist & current_stations

        # Sauvegarde persistante
        pd.DataFrame({"station": list(withlist)}).to_csv(with_path, index=False)
        pd.DataFrame({"station": list(blacklist)}).to_csv(black_path, index=False)

    return df

def filter_dates(df: pd.DataFrame, col: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col])
    return df[(df[col] >= start) & (df[col] < end + pd.Timedelta(days=1))]

def load_regulation(path: Path, cols: Dict[str,str], config_paths: dict) -> pd.DataFrame:
    reg = read_csv_smart(path, cols["station_pick"], config_paths, apply_blacklist=False)
    reg["date_debut"] = pd.to_datetime(reg[cols["date_start"]], dayfirst=True)
    reg["date_fin"]   = pd.to_datetime(reg[cols["date_end"]], dayfirst=True)
    delta = pd.Timedelta(minutes=15)
    
    reg_events = pd.concat([
        reg.assign(
            station=reg[cols["station_pick"]],
            start=reg["date_debut"] - delta,
            end=reg["date_fin"] + delta # Correction logique ici
        )[["station","start","end"]],
        reg.assign(
            station=reg[cols["station_drop"]],
            start=reg["date_debut"] - delta,
            end=reg["date_fin"] + delta
        )[["station","start","end"]]
    ])
    reg_events["station"] = reg_events["station"].astype(int)
    return reg_events

def enforce_bounds(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    start_dt = start.floor("D")
    end_dt   = end.floor("D") + pd.Timedelta(hours=23, minutes=59)
    cols = df.columns.tolist()
    dtypes = df.dtypes
    outs = []

    for st, g in df.groupby("station", sort=False):
        g = g.sort_values("time").set_index("time")
        bounds = pd.DatetimeIndex([start_dt, end_dt])
        g = g.reindex(g.index.union(bounds)).sort_index().ffill().bfill()
        g["station"] = st
        g.index.name = "time"
        g = g.reset_index()
        outs.append(g)

    out = pd.concat(outs, ignore_index=True)
    return out[cols].astype(dtypes.to_dict())

def build_station_columns(df: pd.DataFrame, reg: pd.DataFrame, cols: Dict[str,str], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    df = df.copy()
    df[cols["time"]] = pd.to_datetime(df[cols["time"]])
    
    dispo_cols = [c for c in df.columns if cols["available_pattern"] in c and cols["not_available_pattern"] not in c]
    indispo_cols = [c for c in df.columns if cols["not_available_pattern"] in c]

    df["stock"] = df[dispo_cols].fillna(0).sum(axis=1)
    df["indispo"] = df[indispo_cols].fillna(0).sum(axis=1)
    df["diapasons"] = df[cols["docks_free"]].fillna(0) + df[cols["cable_free"]].fillna(0)

    df["not_regulated"] = 1
    for _, row in reg.iterrows():
        mask = (df[cols["time"]] >= row.start) & (df[cols["time"]] <= row.end) & (df[cols["station"]] == row.station)
        df.loc[mask, "not_regulated"] = 0

    df = df.rename(columns={cols["station"]:"station", cols["time"]:"time"})
    df = df[["station","time","stock","indispo","diapasons","not_regulated"]]
    return enforce_bounds(df, start, end)

def build_stock_resampled(df_clean: pd.DataFrame, freq: str) -> pd.DataFrame:
    outs = []
    for st, g in df_clean.groupby("station"):
        g = g.sort_values("time").set_index("time")
        g = g.resample(freq).first()
        g["not_regulated"] = g["not_regulated"].fillna(1)
        g = g.ffill().reset_index()
        g["station"] = st
        outs.append(g)
    out = pd.concat(outs, ignore_index=True)
    out["capacity"] = out[["stock", "indispo", "diapasons"]].sum(axis=1)
    return out

# ==================== PIPELINE PRINCIPAL ====================

def run_processing(config: dict):
    """
    Fonction orchestratrice appelée par main.py
    """
    in_dir = Path(config["paths"]["input_dir"])
    out_dir = Path(config["paths"]["input_dir"])/ "metadata"
    
    # Mapping colonnes (on peut les mettre dans le JSON aussi)
    cols_fill = config.get("cols_fill", {
        "station": "station_code", "time": "last_update_date",
        "available_pattern": "available", "not_available_pattern": "not_available",
        "docks_free": "nb_free_dock", "cable_free": "nb_free_cable"
    })
    cols_reg = config.get("cols_reg", {
        "station_pick": "Station prise", "station_drop": "Station dépose",
        "date_start": "Date début", "date_end": "Date fin"
    })

    # 1. Traitement de l'ancienne semaine
    print("--- Processing Ancienne Semaine ---")
    d_start = pd.Timestamp(config["dates"]["ancienne_semaine"][0])
    d_end = pd.Timestamp(config["dates"]["ancienne_semaine"][1])
    ref_ancienne = config["dates"]["ref_ancienne"]

    input_remplissage = in_dir / f"Remplissage_{config['dates']['ancienne_semaine'][0]}.csv"
    input_regulation = in_dir / f"Régulation_semaine_du_{ref_ancienne}.csv"

    df = read_csv_smart(input_remplissage, cols_fill["station"], config["paths"], filter = {"col":  cols_fill["time"], "start": d_start, "end": d_end})
    reg = load_regulation(input_regulation, cols_reg, config["paths"])
    
    df_clean = build_station_columns(df, reg, cols_fill, d_start, d_end)
    df_clean.to_csv(out_dir / "CLEAN.csv", index=False)

    df_20 = build_stock_resampled(df_clean, config["params"]["sample_freq"])
    df_20.to_csv(out_dir / "CLEAN_20MIN.csv", index=False)

    # 2. Traitement de la nouvelle semaine (si définie)
    if config.get("dates", {}).get("nouvelle_semaine"):
        print("--- Processing Nouvelle Semaine ---")
        dfs_new = []
        jns_dates = config["dates"]["nouvelle_semaine"]
        jns_refs = config["dates"]["ref_nouvelle"]

        for date_str, ref_str in zip(jns_dates, jns_refs):
            print(f"  Jour : {date_str}")
            d_jour = pd.Timestamp(date_str)
            
            f_remplissage = in_dir / f"Remplissage_{date_str}.csv"
            f_regulation = in_dir / f"Régulation_semaine_du_{ref_str}.csv"
            
            df_j = read_csv_smart(f_remplissage, cols_fill["station"], config["paths"], filter = {"col":  cols_fill["time"], "start": d_jour, "end": d_jour})
            reg_j = load_regulation(f_regulation, cols_reg, config["paths"])
            
            df_clean_j = build_station_columns(df_j, reg_j, cols_fill, d_jour, d_jour)
            df_20_j = build_stock_resampled(df_clean_j, config["params"]["sample_freq"])
            dfs_new.append(df_20_j)

        # Unification nouvelle semaine
        jname = "".join(jns_refs)
        df_new_week = pd.concat(dfs_new, ignore_index=True).sort_values(["station", "time"])
        df_new_week.to_csv(out_dir / f"CLEAN{jname}.csv", index=False)
        print(f"✅ Unifié généré : CLEAN{jname}.csv")

    print("🚀 Fin du processing.")