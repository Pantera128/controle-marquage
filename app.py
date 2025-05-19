import streamlit as st
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np
from pylibdmtx.pylibdmtx import decode as decode_datamatrix
import re
import io
import pandas as pd

st.set_page_config(page_title="Contrôle de marquage", layout="wide")
st.title("🧐 Contrôle automatique de calques de marquage")

st.markdown("""
Ce programme compare les informations sur les **fichiers de marquage PDF** avec une **ou plusieurs photos d’Ordre de Fabrication (OF)**.

Il vérifie automatiquement :
- ✅ La Référence Client (REF CLIENT)
- ✅ Le(s) Numéro(s) de lot (y compris les plages 210001-210005)
- ✅ La date de production (format YYMMDD)
- ✅ Le contenu du datamatrix
""")

# Chargement des fichiers
pdf_file = st.file_uploader("📄 Fichier PDF de marquage (1 seul)", type=["pdf"])
of_images = st.file_uploader("🖼️ Photo(s) des Ordres de Fabrication (OF)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

force_check = st.checkbox("🔍 Forcer la vérification même si certaines infos sont manquantes")

results = []

# Fonction OCR sur image
def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

# Fonction lecture datamatrix
def read_datamatrix(image):
    codes = decode(image)
    return [code.data.decode("utf-8") for code in codes]

# Analyse texte OF
def parse_of_text(text):
    data = []
    refs = re.findall(r"REF(?:\.\s?)?CLIENT\s*[:\-]?\s*(\S+)", text, re.IGNORECASE)
    lots = re.findall(r"Lot\s*[:\-]?\s*([A-Z0-9\-/]+)(?:\s*/\s*CE[:\-]?\s*\d+)?", text, re.IGNORECASE)
    dates = re.findall(r"YYMMDD[:\-]?\s*(\d{6})", text)

    for ref in refs:
        lot_list = []
        for lot in lots:
            if "-" in lot and lot.replace("-", "").isdigit():
                start, end = lot.split("-")
                lot_list.extend([str(i) for i in range(int(start), int(end)+1)])
            else:
                lot_list.append(lot)
        for lot in lot_list:
            for date in dates:
                data.append({"REF CLIENT": ref, "Lot": lot, "Date": date})
    return data

# Analyse texte PDF
@st.cache_data
def extract_text_from_pdf(pdf_file):
    pdf_data = []
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        text = extract_text_from_image(img)
        datamatrix = read_datamatrix(img)
        pdf_data.append({
            "page": page_num + 1,
            "text": text,
            "datamatrix": datamatrix
        })
    return pdf_data

if pdf_file and of_images:
    st.info("🔄 Analyse en cours...")

    of_data = []
    for image_file in of_images:
        image = Image.open(image_file).convert("RGB")
        text = extract_text_from_image(image)
        parsed = parse_of_text(text)
        of_data.extend(parsed)

    pdf_data = extract_text_from_pdf(pdf_file)

    # Comparaison
    for i, page in enumerate(pdf_data):
        page_text = page["text"]
        datamatrix = page["datamatrix"]
        match_found = False

        for entry in of_data:
            ref_ok = entry["REF CLIENT"] in page_text
            lot_ok = entry["Lot"] in page_text
            date_ok = entry["Date"] in page_text
            matrix_ok = all(
                entry["Lot"] in dm and entry["Date"] in dm
                for dm in datamatrix
            ) if datamatrix else False

            if ref_ok and lot_ok and date_ok and matrix_ok:
                results.append({"Page": i+1, **entry, "Datamatrix OK": "✅"})
                match_found = True
                break

        if not match_found:
            results.append({"Page": i+1, "REF CLIENT": "❌", "Lot": "❌", "Date": "❌", "Datamatrix OK": "❌"})

    # Affichage des résultats
    df = pd.DataFrame(results)
    st.subheader("📋 Résultats du contrôle")

    def highlight_errors(val):
        if val == "❌":
            return 'background-color: #ffcccc; color: red; font-weight: bold'
        return ''

    styled_df = df.style.applymap(highlight_errors)
    st.dataframe(styled_df, use_container_width=True)

    # Export CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📤 Télécharger les résultats au format CSV", csv, "controle_resultats.csv", "text/csv")

else:
    st.warning("Veuillez charger à la fois un fichier PDF de marquage et au moins une image d'OF.")
