import os, webbrowser, threading
from time import sleep

print("="*50)
print("🔍 Google Search Scraper")
print("="*50)

try:
    from flask import Flask
    print("✅ Flask ready")
except:
    os.system("pip install flask flask-cors requests beautifulsoup4")

def open_browser():
    sleep(2)
    webbrowser.open("http://localhost:5000")
    print("🌐 http://localhost:5000")

threading.Thread(target=open_browser).start()
print("🚀 Server spuštěn (Ctrl+C pro ukončení)\n")

from app import app
app.run(debug=True, port=5000)