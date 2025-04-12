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

    pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}\.\d{2}\.\d{2})\s+(.+?),\s+(.+?),\s+(-?\d[\d\.]*)")
    
    for line in lines:
        match = pattern.match(line)
        if match:
            book_date, value_date, description1, description2, amount = match.groups()
            transactions.append({
                "Könyvelés dátuma": book_date,
                "Értéknap": value_date,
                "Megnevezés": f"{description1}, {description2}",
                "Összeg": float(amount.replace('.', '').replace(',', '.'))
            })
    return transactions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "Nincs fájl feltöltve!", 400

    raw_text = extract_text_from_pdf(file)
    transactions = parse_transactions(raw_text)

    if not transactions:
        return "Nem sikerült tranzakciókat kinyerni a fájlból.", 400

    df = pd.DataFrame(transactions)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Kivonat')
    output.seek(0)

    return send_file(output, download_name="kivonat.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
