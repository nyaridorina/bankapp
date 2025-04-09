import os
import pdfplumber
import pandas as pd
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["pdf_file"]
        if file and file.filename.endswith(".pdf"):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            df = extract_data_from_pdf(filepath)
            df["Kategória"] = df.apply(categorize, axis=1)
            output_path = os.path.join(UPLOAD_FOLDER, "kategorzalt.xlsx")
            df.to_excel(output_path, index=False)

            return send_file(output_path, as_attachment=True)

    return render_template("index.html")

def extract_data_from_pdf(filepath):
    data = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.split("\n"):
                if "Ft" in line:
                    parts = line.split()
                    try:
                        date = parts[0]
                        amount = parts[-2] + " " + parts[-1]
                        beneficiary = " ".join(parts[1:-2])
                        data.append([date, beneficiary, amount])
                    except IndexError:
                        continue
    return pd.DataFrame(data, columns=["Dátum", "Kedvezményezett", "Összeg"])

def categorize(row):
    text = row["Kedvezményezett"].lower()
    if any(x in text for x in ["aldi", "spar", "tesco"]):
        return "Élelmiszer"
    elif any(x in text for x in ["mol", "shell"]):
        return "Benzin"
    elif any(x in text for x in ["eon", "mvm"]):
        return "Közüzem"
    elif any(x in text for x in ["hm", "zara"]):
        return "Ruha"
    else:
        return "Egyéb"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)


