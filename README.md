
==========================================
Le projet necessite:
-une licence GUROBI (pour un solveur d'optimisation commercial puissant)
-les packages suivants:
pip install pandas numpy scipy tensorly scikit-learn gurobipy matplotlib

-des donnees de stocks et régulations, a placer dans data/inputs:

-Stocks et regulations couvrant au moins la DERNIERE semaine complète 
-> servira pour le forecast de demande. On suppose que la demande est la meme d'une semaine a la suivante
-Stocks et regulations couvrants tout le debut de la semaine EN COURS 
-> calcul un passif de score pour la semaine en cours (moyenne de stocks aux horaires stratégiques qui seront compté dans la metrique metropole)
-> donne la derniere mise a jour des stocks pour initialiser le simulateur avec l'etat initial présent du parc velib

======================
ENSUITE:
-on configure le CONFIG.JSON : noms de fichiers/colonnes a jours, mettre a jour current day: Mon, Tue, Wed
-on lance MAIN.PY qui orchestre tout le pipeline

Structure:
processing.py
-> on process les fichiers bruts (<2 minutes)
demand.py
-> on reconstitue une demande latente pour la semaine dernière (<2 minutes)
evaluation.py
-> on évalue toutes les strategies possibles pour toutes les stations (<2 minutes)
frontieres.py
-> on materialise un ensemble de strategie pertinentes par station par ses frontieres (qq secondes)
optimization.py
-> on fait tourner le solveur (~10 minutes)

===========================================
OUTPUT:
Un plan de régulation 
D'autres fichiers utiles a chercher dans data/output

