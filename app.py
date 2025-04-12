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

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_transactions(raw_text):
    # Nyomtatjuk ki a kinyert szöveget
    print("Raw Text Output:")  
    print(raw_text)  # Kinyomtatjuk, hogy lássuk, mi van benne
    lines = raw_text.splitlines()
    transactions = []

    # Kategóriák szótár
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
            if key.lower() in description.lower():  # Kis-nagybetű figyelmen kívül hagyása
                return value
        return 'Egyéb'

    # Regex
    pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}\.\d{2}\.\d{2})\s+(.+?),\s+(.+?),\s+(-?\d[\d\.]*)")

    for line in lines:
        match = pattern.match(line)
        if match:
            book_date, value_date, description1, description2, amount = match.groups()
            transaction_description = f"{description1}, {description2}"

            # Összeg feldolgozása (csak a mínuszos számokat tartjuk meg)
            amount_value = float(amount.replace('.', '').replace(',', '.'))
            if amount_value > 0:
                continue  # Csak a negatív összegű tranzakciókat vesszük figyelembe.

            category = categorize(transaction_description)
            transactions.append({
                "Date": book_date,
                "Transaction Description": transaction_description,
                "Amount (HUF)": amount_value,
                "Category": category
            })

    return transactions




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
