#!/bin/bash

# 🚀 Lancement du backend iAngel...
echo "🚀 Lancement du backend iAngel..."
python3 backend/iangel_coeur.py &

# 🕒 Lancement du watchdog (surveillance des tâches différées)
echo "🕒 Lancement du watchdog mémoire..."
python3 backend/utils/watchdog.py &

# ⚡️ Préparation du frontend React...
echo "⚡️ Lancement du frontend React (npm run dev)..."
cd frontend
npm run dev
