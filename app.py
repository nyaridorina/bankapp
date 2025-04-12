from flask import Flask, render_template, request, send_file
import pandas as pd
import re
from PyPDF2 import PdfReader
import io

app = Flask(__name__)

# PDF-ből szöveg kinyerése
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Tranzakciók kinyerése és feldolgozása
def parse_transactions(raw_text):
    print("Raw Text Output:")  
    print(raw_text)  # Kinyomtatjuk a nyers szöveget
    lines = raw_text.splitlines()
    transactions = []

    # Kategorizálás
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

    # Regex minta
    pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}\.\d{2}\.\d{2})\s+(.+?),\s+(.+?),\s+(-?\d[\d\.]*)")

    for line in lines:
        match = pattern.match(line)
        if match:
            book_date, value_date, description1, description2, amount = match.groups()
            transaction_description = f"{description1}, {description2}"

            # Összeg feldolgozása (csak a mínuszos számokat vesszük figyelembe)
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

# Főoldal route
@app.route('/')
def index():
    return render_template('index.html')

# Feltöltési route
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['pdf_file']
    if not file:
        return "Nincs fájl feltöltve!", 400

    raw_text = extract_text_from_pdf(file)
    transactions = parse_transactions(raw_text)

    if not transactions:
        return "Nem sikerült tranzakciókat kinyerni a fájlból.", 400

    # DataFrame létrehozása és Excel fájlba mentés
    df = pd.DataFrame(transactions)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tranzakciók')
    output.seek(0)

    # Excel fájl letöltése
    return send_file(output, as_attachment=True, download_name="transactions.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    app.run(debug=True)
