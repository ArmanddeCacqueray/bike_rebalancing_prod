# 🚲 Vélib Optimization Pipeline

End-to-end pipeline to **reconstruct bike demand and optimize nightly rebalancing plans** for a bike-sharing system.

The pipeline processes station fill-level data and past regulation operations to estimate demand, evaluate station strategies, and compute an optimized regulation plan using **mixed-integer optimization**.

---

# 📦 Repository Overview

Pipeline structure:

```

raw data
↓
processing
↓
demand reconstruction
↓
station evaluation
↓
strategy frontier
↓
optimization (Gurobi)
↓
rebalancing plan

```

Main entrypoint:

```

python main.py

````

---

# 📋 Requirements

### Python

Python **3.8+**

### Python packages

```bash
pip install pandas numpy scipy scikit-learn gurobipy matplotlib
````

### Solver

The optimization stage requires:

**Gurobi Optimizer**

[https://www.gurobi.com/](https://www.gurobi.com/)

A valid license must be installed before running `optimization.py`.

---

# 📁 Data Structure

```
repo/
│
├── raw/                # raw input data
├── data/
│   └── outputs/        # pipeline outputs
│
├── config_time.json
├── config_params.json
│
├── main.py
└── README.md
```

---

# 📥 Raw Data

Raw files must be placed in:

```
raw/
```

and must follow the **naming pattern**:

```
remplissage_*
regulation_*
```

Examples:

```
remplissage_lastweek.csv
remplissage_mon.csv
regulation_wed.csv
```

### Naming rules

File names indicate **which period they represent**, but **the exact time range inside the file is flexible**.

Example:

At **Monday 09/03/2026**

```
remplissage_mon.csv
```

may contain data ranging from:

```
06/03/2026 10:11
to
11/03/2026 23:14
```

as long as **the full Monday data is included**.

This means:

* several files may **contain the same raw data**
* files may contain **multiple time segments**

Example:

```
remplissage_lastweek_mon_tue_wed.csv
```

is valid as long as **no naming conflicts occur**.

---

# ⚙️ Configuration

Two configuration files control the pipeline.

---

# `config_time.json`

Defines:

* which raw files must be processed
* which **night of regulation** must be solved

Example:

```json
{
  "to_solve": "wednesday"
}
```

Meaning:

We want to compute a **rebalancing plan for Wednesday night**.

The solver will use:

* Monday, Tuesday, Wednesday demand
* last week demand (stationary reference)
* last system state before regulation (≈ 22:00)

Assumption:

```
current week demand ≈ last week demand
```

---

# `config_params.json`

Defines pipeline parameters such as:

### Raw data columns

Example:

```
station_name
date_update
nb_bikes
nb_docks
```

### Demand reconstruction

Demand is reconstructed using:

* **local interpolation**
* **Gaussian convolution kernel**
* **structural regularization with Tucker decomposition**

### Evaluation

Station performance is evaluated using a **Metropolis-style metric**.

### Optimization

Parameters for the **Gurobi optimization model**.

---

# ▶️ Running the Pipeline

### 1 — Place raw files

Put required files into:

```
raw/
```

following the naming rules.

---

### 2 — Configure the pipeline

Edit:

```
config_time.json
config_params.json
```

---

### 3 — Run

```bash
python main.py
```

---

# 🏗️ Pipeline Steps

### 1 — Processing

Data cleaning and preprocessing.

Output:

```
clean station time series
```

---

### 2 — Demand Reconstruction

Reconstructs **latent bike demand** from fill-level variations using:

* local interpolation
* Gaussian smoothing
* Tucker tensor regularization

---

### 3 — Station Evaluation

Evaluates station strategies based on a **Metropolis performance metric**.

---

### 4 — Strategy Frontier

Filters the **Pareto-efficient station strategies**.

---

### 5 — Optimization

A **Mixed Integer Linear Program** solved with **Gurobi** computes the optimal regulation plan.

---

# 📊 Outputs

Generated files are stored in:

```
data/outputs/
```

Examples:

```
CLEAN_last_week_20min.csv
CLEAN_new_week_20min.csv
```

Typical outputs include:

* cleaned station time series
* reconstructed demand
* station performance metrics
* optimized rebalancing plan

---

# 🎯 Purpose of the Repository

This repository demonstrates a **complete pipeline for bike-sharing regulation optimization**, combining:

* signal processing
* tensor decomposition
* statistical evaluation
* mathematical optimization

```



→ ça transforme ton repo en **repo de recherche propre que les gens peuvent citer / forker facilement**.
```
