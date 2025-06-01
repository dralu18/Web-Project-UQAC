@echo off
echo === Initialisation de la base de donnees ===
set FLASK_APP=../inf349.py
flask init-db
