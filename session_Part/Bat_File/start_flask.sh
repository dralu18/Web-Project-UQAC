#!/bin/bash
echo "Installation des dependances"
python3 -m pip install -r requirements.txt

echo "=== Initialisation de Flask pour le projet ==="
export FLASK_APP=../inf349.py
export FLASK_DEBUG=1

echo "Lancement de la base de donnees..."
bash init_db.sh

echo "Lancement du serveur Flask..."
flask run