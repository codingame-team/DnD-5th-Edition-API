#!/bin/bash

# Script de lancement de la démo Flask D&D 5e

echo "🎲 Démarrage de la démo Flask D&D 5e..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier si les dépendances sont installées
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
fi

# Créer le répertoire de sauvegardes si nécessaire
mkdir -p data/saves

# Lancer l'application
echo "🚀 Lancement de l'application..."
echo "📍 URL: http://localhost:5000"
echo "⏹️  Appuyez sur Ctrl+C pour arrêter"
echo ""

python3 app.py
