@echo off
title Klinik Sehat Digital - Cyber-Defense Showcase
echo ============================================================
echo      KLINIK SEHAT DIGITAL - SECURITY & HA WEB DEMO
echo ============================================================
echo.
echo Membuka aplikasi demo di browser default (http://localhost:8080)...
start http://localhost:8080
echo Server lokal sedang berjalan. Tekan Ctrl+C di terminal ini untuk berhenti.
echo.
python server.py
pause
