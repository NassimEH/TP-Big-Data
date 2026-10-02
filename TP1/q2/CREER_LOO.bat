@echo off
REM Lance Looping + le SQL a coller pour generer le .loo en 30 secondes
start "" "%LOCALAPPDATA%\Looping\Looping.exe"
start "" notepad "%~dp0mcd_source.sql"
echo.
echo === CREER LE FICHIER .loo EN 30 SECONDES ===
echo 1. Dans Looping : bouton Nouveau (page blanche)
echo 2. Clic droit sur le fond du schema
echo 3. Cliquer "Retroconception"
echo 4. Coller le contenu du Notepad (Ctrl+A puis Ctrl+C / Ctrl+V)
echo 5. Bouton Importer
echo 6. Fichier Enregistrer : TP1\q2\TP1_MCD.loo
echo.
pause
