from flask import Flask, render_template, request, send_file
import pandas as pd
import io
import re
from PyPDF2 import PdfReader

app = Flask(__name__)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_transactions(raw_text):
    lines = raw_text.splitlines()
    transactions = []

    # Minta a tranzakciókhoz, ha a PDF fájl formátuma megfelel
    pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}\.\d{2}\.\d{2})\s+(.+?),\s+(.+?),\s+(-?\d[\d\.]*)")
    
    # Kategóriák egyszerű logikája (példa, itt fejleszthető)
    def categorize(description):
        categories = {
            'Google': 'Vásárlás',
            'Spotify': 'Előfizetés',
            'NETFLIX': 'Előfizetés',
            'ALDI': 'Bevásárlás',
            'ROSSMANN': 'Drogéria',
            'Aegon': 'Megtakarítás',
            'Szabadka': 'Vásárlás',
            'Shell': 'Üzemanyag',
            'HÉTKORONA': 'Gyógyszertár',
            'OTPdirekt': 'Bankköltség',
            'SZEMÉLYI KÖLCSÖN TÖRLESZTÉS': 'Hitel',
        }
        for key, value in categories.items():
            if key in description:
                return value
        return 'Egyéb'  # Ha nincs megfelelő kategória, 'Egyéb'-et adunk

    for line in lines:
        match = pattern.match(line)
        if match:
            book_date, value_date, description1, description2, amount = match.groups()
            transaction_description = f"{description1}, {description2}"
            category = categorize(transaction_description)
            
            transactions.append({
                "Date": book_date,
                "Transaction Description": transaction_description,
                "Amount (HUF)": float(amount.replace('.', '').replace(',', '.')),
                "Category": category
            })

    return transactions


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['pdf_file']
    if not file:
        return "Nincs fájl feltöltve!", 400

    raw_text = extract_text_from_pdf(file)
    transactions = parse_transactions(raw_text)

    if not transactions:
        return "Nem sikerült tranzakciókat kinyerni a fájlból.", 400

    return render_template('eredmeny.html', tranzakciok=transactions)

if __name__ == '__main__':
    app.run(debug=True)
