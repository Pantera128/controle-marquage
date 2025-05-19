import streamlit as st
from PIL import Image
import pytesseract
import re
import io
import pandas as pd
import fitz  # PyMuPDF

st.title("🔍 Contrôle simple sans installation supplémentaire")

pdf_file = st.file_uploader("Charge ton PDF marquage", type=["pdf"])
of_images = st.file_uploader("Charge les photos OF (png/jpeg)", type=["png","jpg","jpeg"], accept_multiple_files=True)

def extract_text(image):
    return pytesseract.image_to_string(image)

def parse_of_text(text):
    refs = re.findall(r"REF(?:\.\s?)?CLIENT\s*[:\-]?\s*(\S+)", text, re.IGNORECASE)
    lots = re.findall(r"Lot\s*[:\-]?\s*([A-Z0-9\-/]+)", text, re.IGNORECASE)
    dates = re.findall(r"\b(\d{6})\b", text)  # Date YYMMDD simplifiée
    return refs, lots, dates

if pdf_file and of_images:
    st.info("Analyse en cours...")

    of_data = []
    for img_file in of_images:
        img = Image.open(img_file)
        text = extract_text(img)
        refs, lots, dates = parse_of_text(text)
        of_data.append({"refs": refs, "lots": lots, "dates": dates})

    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pdf_text = ""
    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        pdf_text += extract_text(img)

    results = []
    for entry in of_data:
        for ref in entry["refs"]:
            ref_ok = ref in pdf_text
            for lot in entry["lots"]:
                lot_ok = lot in pdf_text
                for date in entry["dates"]:
                    date_ok = date in pdf_text
                    results.append({
                        "REF CLIENT": ref,
                        "Lot": lot,
                        "Date": date,
                        "Présent dans PDF": ref_ok and lot_ok and date_ok
                    })

    df = pd.DataFrame(results)
    st.dataframe(df)

else:
    st.warning("Charge à la fois un PDF et au moins une image OF.")
