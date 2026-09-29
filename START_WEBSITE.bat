@echo off
cd /d "%~dp0"
echo Starting SAMANVAY-WX local web server...
start "SAMANVAY-WX" http://127.0.0.1:5500/index.html
py -m http.server 5500
pause
