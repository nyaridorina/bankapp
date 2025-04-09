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
