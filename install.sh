#!/bin/bash

echo "[+] Installing Python dependencies..."
pip install -r requirements.txt

echo "[+] Installing Playwright browsers..."
playwright install chromium

echo "[+] Done! You can now run the tool."
echo "Usage: python pyWebShotx.py -i subdominios.txt"