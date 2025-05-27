@echo off
echo installation des dépendence
python -m pip install -r requirements.txt

echo === Initialisation de Flask pour le projet ===
set FLASK_APP=../inf349.py
set FLASK_DEBUG=True

echo Lancement de la base de données...
call init_db.bat

echo Lancement du serveur Flask...
flask run

pause