from flask import Flask, render_template, request
import os
import pandas as pd
from PyPDF2 import PdfReader

app = Flask(__name__)  # EZ KELL a gunicorn-hoz

def feldolgoz_pdf(fajlnev):
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(fajlnev)
        szoveg = ''
        for oldal in reader.pages:
            szoveg += oldal.extract_text() + '\n'
        
        tranzakciok = []
        for sor in szoveg.split('\n'):
            if 'Ft' in sor:
                tranzakciok.append({
                    'datum': '2025-01-01',
                    'kedvezmenyezett': 'Ismeretlen',
                    'osszeg': sor.strip(),
                    'cimke': 'egyéb'
                })

        return tranzakciok
    except Exception as e:
        print(f"Hiba a PDF feldolgozás során: {e}")
        return []


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Feltöltés elkezdődött")
        
        if 'pdf_file' not in request.files:
            print("Nincs fájl")
            return 'Nincs fájl'
        file = request.files['pdf_file']
        if file.filename == '':
            print("Fájl név üres")
            return 'Fájl név üres'

        print(f"Fájl feltöltve: {file.filename}")

        # Mentés
        file.save('feltoltott.pdf')
        print("Fájl mentve")

        # PDF feldolgozás
        tranzakciok = feldolgoz_pdf('feltoltott.pdf')
        print("PDF feldolgozva")

        # Ha nincs tranzakció, írj ki valamit
        if not tranzakciok:
            print("Nincsenek tranzakciók")
        
        # Eredmények visszaküldése
        return render_template('eredmeny.html', tranzakciok=tranzakciok)

    return render_template('index.html')
